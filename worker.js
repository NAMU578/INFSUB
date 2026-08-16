/**
 * 정보수업 노트북 — Cloudflare Worker
 *
 * 하는 일
 *  1. 로그인·가입 처리 (비밀번호는 서버 비밀값을 섞어 해시로만 보관)
 *  2. 회원별 학습 기록을 깃허브 저장소의 userdata/<아이디>.json 으로 저장
 *  3. 노트북 목록 조회 (깃허브 API 사용 한도를 브라우저 대신 흡수)
 *  4. Claude API 중계 — API 키는 이 서버에만 있고 브라우저로 나가지 않습니다
 *
 * 필요한 환경 변수 (wrangler secret put / 대시보드에서 설정)
 *  GITHUB_TOKEN       저장소 contents 읽기·쓰기 권한이 있는 파인그레인드 토큰
 *  SESSION_SECRET     아무 긴 무작위 문자열 (로그인 토큰 서명용)
 *  ANTHROPIC_API_KEY  Claude API 키 (서술형 문제를 안 쓸 거면 생략 가능)
 *
 * 일반 변수 (wrangler.toml [vars])
 *  GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH, ADMIN_ID, ALLOWED_ORIGIN, MODEL
 */

const OK_ID = /^[A-Za-z0-9_.-]{2,24}$/;
const DAY = 86400;
const TOKEN_DAYS = 30;

export default {
  async fetch(req, env) {
    const origin = env.ALLOWED_ORIGIN || '*';
    const cors = {
      'access-control-allow-origin': origin,
      'access-control-allow-headers': 'content-type,authorization',
      'access-control-allow-methods': 'POST,OPTIONS',
      'vary': 'origin',
    };
    if (req.method === 'OPTIONS') return new Response(null, { headers: cors });

    const json = (obj, status = 200) =>
      new Response(JSON.stringify(obj), { status, headers: { ...cors, 'content-type': 'application/json' } });

    try {
      const path = new URL(req.url).pathname.replace(/\/+$/, '') || '/';
      const body = req.method === 'POST' ? await req.json().catch(() => ({})) : {};

      if (path === '/')              return json({ ok: true, service: 'info-notebook' });
      if (path === '/auth/register') return json(await register(env, body));
      if (path === '/auth/login')    return json(await login(env, body));

      // 여기부터는 로그인 필요
      const me = await requireAuth(req, env);
      if (path === '/data/get')  return json(await dataGet(env, me, body));
      if (path === '/data/put')  return json(await dataPut(env, me, body));
      if (path === '/users')     return json(await listUsers(env, me));
      if (path === '/repo/list') return json(await repoList(env, body));
      if (path === '/ai')        return json(await ai(env, body));

      return json({ error: '없는 주소입니다' }, 404);
    } catch (e) {
      const status = e.status || 500;
      return json({ error: e.message || '서버 오류' }, status);
    }
  },
};

/* ── 오류 도우미 ───────────────────────────────────────── */
const fail = (msg, status = 400) => { const e = new Error(msg); e.status = status; throw e; };

/* ── 암호 / 토큰 ───────────────────────────────────────── */
const enc = new TextEncoder();
const hex = buf => [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');

async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return hex(await crypto.subtle.sign('HMAC', key, enc.encode(msg)));
}
const b64url = s => btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64url = s => atob(s.replace(/-/g, '+').replace(/_/g, '/'));

/** 비밀번호는 브라우저에서 이미 SHA-256을 거쳐 옵니다. 서버 비밀값을 섞어 한 번 더 돌립니다. */
const pwHash = (env, id, clientHash) => hmac(env.SESSION_SECRET, `pw:${id}:${clientHash}`);

async function makeToken(env, id, admin) {
  const payload = b64url(JSON.stringify({ id, admin, exp: Math.floor(Date.now() / 1000) + TOKEN_DAYS * DAY }));
  return `${payload}.${await hmac(env.SESSION_SECRET, payload)}`;
}
async function readToken(env, token) {
  const [payload, sig] = String(token || '').split('.');
  if (!payload || !sig) return null;
  if (sig !== await hmac(env.SESSION_SECRET, payload)) return null;
  try {
    const p = JSON.parse(unb64url(payload));
    if (p.exp < Math.floor(Date.now() / 1000)) return null;
    return p;
  } catch { return null; }
}
async function requireAuth(req, env) {
  const t = (req.headers.get('authorization') || '').replace(/^Bearer\s+/i, '');
  const p = await readToken(env, t);
  if (!p) fail('로그인이 필요합니다', 401);
  return p;
}

/* ── 깃허브 파일 읽기·쓰기 ─────────────────────────────── */
const GH = env => `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}`;
const ghHeaders = env => ({
  authorization: `Bearer ${env.GITHUB_TOKEN}`,
  accept: 'application/vnd.github+json',
  'user-agent': 'info-notebook-worker',
});

function b64encodeUtf8(str) {
  const bytes = enc.encode(str);
  let bin = '';
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}
function b64decodeUtf8(b64) {
  const bin = atob(b64.replace(/\s/g, ''));
  const bytes = Uint8Array.from(bin, c => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

async function ghRead(env, path) {
  const r = await fetch(`${GH(env)}/contents/${path}?ref=${env.GITHUB_BRANCH || 'main'}`, { headers: ghHeaders(env) });
  if (r.status === 404) return { json: null, sha: null };
  if (!r.ok) fail(`깃허브 읽기 실패 (${r.status})`, 502);
  const j = await r.json();
  try { return { json: JSON.parse(b64decodeUtf8(j.content)), sha: j.sha }; }
  catch { return { json: null, sha: j.sha }; }
}

async function ghWrite(env, path, obj, message) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const { sha } = await ghRead(env, path);
    const r = await fetch(`${GH(env)}/contents/${path}`, {
      method: 'PUT',
      headers: { ...ghHeaders(env), 'content-type': 'application/json' },
      body: JSON.stringify({
        message,
        content: b64encodeUtf8(JSON.stringify(obj, null, 1)),
        branch: env.GITHUB_BRANCH || 'main',
        ...(sha ? { sha } : {}),
      }),
    });
    if (r.ok) return true;
    if (r.status !== 409 && r.status !== 422) fail(`깃허브 저장 실패 (${r.status})`, 502);
    await new Promise(res => setTimeout(res, 250 * (attempt + 1)));   // 같은 파일에 동시 쓰기 → 잠깐 뒤 재시도
  }
  fail('깃허브 저장이 계속 충돌합니다. 잠시 뒤 다시 시도해 주세요', 503);
}

const ACCOUNTS = 'userdata/_accounts.json';
const userFile = id => `userdata/${id}.json`;

/* ── 가입 / 로그인 ─────────────────────────────────────── */
function checkCreds(body) {
  const id = String(body.id || '').trim();
  const pw = String(body.pw || '');
  if (!OK_ID.test(id)) fail('아이디는 영문·숫자·_.- 2~24자여야 합니다');
  if (!/^[0-9a-f]{64}$/.test(pw)) fail('비밀번호 형식이 올바르지 않습니다');
  return { id, pw };
}

async function register(env, body) {
  const { id, pw } = checkCreds(body);
  const { json: accs } = await ghRead(env, ACCOUNTS);
  const all = accs || {};
  if (all[id]) fail('이미 있는 아이디입니다');
  all[id] = { h: await pwHash(env, id, pw), joined: new Date().toISOString() };
  await ghWrite(env, ACCOUNTS, all, `계정 추가: ${id}`);
  const admin = id === env.ADMIN_ID;
  return { id, admin, token: await makeToken(env, id, admin) };
}

async function login(env, body) {
  const { id, pw } = checkCreds(body);
  const { json: accs } = await ghRead(env, ACCOUNTS);
  const rec = accs?.[id];
  if (!rec) fail('없는 아이디입니다. 계정을 먼저 만들어 주세요');
  if (rec.h !== await pwHash(env, id, pw)) fail('아이디 또는 비밀번호가 맞지 않습니다');
  const admin = id === env.ADMIN_ID;
  return { id, admin, token: await makeToken(env, id, admin) };
}

/* ── 학습 기록 ─────────────────────────────────────────── */
function checkTarget(me, target) {
  const t = String(target || '');
  if (t !== '_shared' && !OK_ID.test(t)) fail('잘못된 사용자 이름입니다');
  return t;
}

async function dataGet(env, me, body) {
  const t = checkTarget(me, body.user);
  if (t !== me.id && t !== '_shared' && !me.admin) fail('다른 사람의 기록은 볼 수 없습니다', 403);
  const { json } = await ghRead(env, userFile(t));
  return { data: json };
}

async function dataPut(env, me, body) {
  const t = checkTarget(me, body.user);
  if (t === '_shared') { if (!me.admin) fail('공용 편집은 관리자만 할 수 있습니다', 403); }
  else if (t !== me.id) fail('다른 사람의 기록은 고칠 수 없습니다', 403);
  const data = body.data;
  if (!data || typeof data !== 'object') fail('저장할 내용이 없습니다');
  if (JSON.stringify(data).length > 900_000) fail('기록이 너무 큽니다. 오답 노트를 정리해 주세요');
  await ghWrite(env, userFile(t), data, `기록 저장: ${t}`);
  return { ok: true };
}

async function listUsers(env, me) {
  if (!me.admin) fail('관리자만 볼 수 있습니다', 403);
  const { json: accs } = await ghRead(env, ACCOUNTS);
  return { users: Object.entries(accs || {}).map(([id, v]) => ({ id, joined: v.joined || null })) };
}

/* ── 노트북 목록 ───────────────────────────────────────── */
async function repoList(env, body) {
  const dir = String(body.dir || 'notebooks').replace(/[^A-Za-z0-9_./-]/g, '');
  const r = await fetch(`${GH(env)}/contents/${dir}?ref=${env.GITHUB_BRANCH || 'main'}`, { headers: ghHeaders(env) });
  if (r.status === 404) fail('노트북 폴더를 찾을 수 없습니다', 404);
  if (!r.ok) fail(`깃허브 목록 조회 실패 (${r.status})`, 502);
  const items = await r.json();
  return { items: items.map(f => ({ name: f.name, path: f.path, type: f.type })) };
}

/* ── Claude API 중계 ───────────────────────────────────── */
const MAKE_SYS = `너는 한국 고등학교 정보 과목의 출제 교사다.
주어진 수업 노트북 내용에서 핵심 개념 하나를 골라 서술형 문제 1개를 낸다.

규칙
- 한국어로 쓴다.
- 노트북에 실제로 나온 개념만 다룬다. 노트북 밖 지식을 요구하지 않는다.
- 서술형이므로 답이 한 단어로 끝나면 안 된다. "왜", "어떻게", "무슨 차이", "어떤 일이 일어나는지" 같은 설명을 요구한다.
- 코드가 필요하면 code 필드에 짧은 파이썬 코드를 넣고, 필요 없으면 빈 문자열로 둔다.
- rubric에는 정답으로 인정할 핵심 요소를 2~4개 적는다.

출력은 아래 형태의 JSON 하나뿐이다. 설명, 인사말, 마크다운 코드펜스를 절대 붙이지 않는다.
{"question":"...","code":"","rubric":"...","model_answer":"..."}`;

const GRADE_SYS = `너는 한국 고등학교 정보 과목의 채점 교사다. 학생 답안을 채점 기준에 비추어 평가한다.

규칙
- 한국어로 쓴다.
- 핵심 요소를 대체로 담았으면 맞은 것으로 본다. 표현이 서툴러도 뜻이 맞으면 인정한다.
- feedback은 두 문장 이내로, 무엇이 좋았고 무엇이 빠졌는지 구체적으로 짚는다. 학생을 깎아내리지 않는다.
- model_answer에는 모범 답안을 세 문장 이내로 쓴다.

출력은 아래 형태의 JSON 하나뿐이다. 설명, 인사말, 마크다운 코드펜스를 절대 붙이지 않는다.
{"correct":true,"feedback":"...","model_answer":"..."}`;

async function callClaude(env, system, user, maxTokens = 1200) {
  if (!env.ANTHROPIC_API_KEY) fail('서술형 기능이 설정되지 않았습니다 (ANTHROPIC_API_KEY 없음)', 503);
  const r = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: env.MODEL || 'claude-sonnet-5',
      max_tokens: maxTokens,
      system,
      messages: [{ role: 'user', content: user }],
    }),
  });
  if (!r.ok) {
    const t = await r.text().catch(() => '');
    fail(`Claude 호출 실패 (${r.status}) ${t.slice(0, 160)}`, 502);
  }
  const j = await r.json();
  const text = (j.content || []).filter(c => c.type === 'text').map(c => c.text).join('\n');
  const clean = text.replace(/```json|```/g, '').trim();
  try { return JSON.parse(clean); }
  catch {
    const m = clean.match(/\{[\s\S]*\}/);
    if (m) { try { return JSON.parse(m[0]); } catch {} }
    fail('AI 응답을 이해하지 못했습니다. 다시 시도해 주세요', 502);
  }
}

async function ai(env, body) {
  if (body.task === 'make') {
    const ctx = String(body.context || '').slice(0, 6000);
    if (!ctx.trim()) fail('노트북 내용이 비어 있습니다');
    return await callClaude(env, MAKE_SYS,
      `노트북 이름: ${String(body.notebook || '').slice(0, 80)}\n\n=== 노트북 내용 ===\n${ctx}`);
  }
  if (body.task === 'grade') {
    return await callClaude(env, GRADE_SYS,
      `문제: ${String(body.question || '').slice(0, 1500)}\n\n채점 기준: ${String(body.rubric || '').slice(0, 1500)}\n\n학생 답안: ${String(body.answer || '').slice(0, 3000)}`,
      700);
  }
  fail('알 수 없는 요청입니다');
}
