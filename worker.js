// worker.js
var OK_ID = /^[A-Za-z0-9_.-]{2,24}$/;
var DAY = 86400;
var TOKEN_DAYS = 30;
var WORKER_VERSION = "2026-08-20";
var worker_default = {
  async fetch(req, env) {
    const origin = env.ALLOWED_ORIGIN || "*";
    const cors = {
      "access-control-allow-origin": origin,
      "access-control-allow-headers": "content-type,authorization",
      "access-control-allow-methods": "POST,OPTIONS",
      "vary": "origin"
    };
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });
    const json = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: { ...cors, "content-type": "application/json" } });
    try {
      const path = new URL(req.url).pathname.replace(/\/+$/, "") || "/";
      const body = req.method === "POST" ? await req.json().catch(() => ({})) : {};
      if (path === "/") return json({
        ok: true,
        service: "info-notebook",
        version: WORKER_VERSION,
        routes: [
          "/auth/register",
          "/auth/login",
          "/auth/change",
          "/auth/reset",
          "/data/get",
          "/data/put",
          "/users",
          "/repo/list"
        ]
      });
      if (path === "/auth/register") return json(await register(env, body));
      if (path === "/auth/login") return json(await login(env, body));
      const me = await requireAuth(req, env);
      if (path === "/auth/change") return json(await changePw(env, me, body));
      if (path === "/auth/reset") return json(await adminReset(env, me, body));
      if (path === "/data/get") return json(await dataGet(env, me, body));
      if (path === "/data/put") return json(await dataPut(env, me, body));
      if (path === "/users") return json(await listUsers(env, me));
      if (path === "/repo/list") return json(await repoList(env, body));
      return json({ error: "없는 주소입니다" }, 404);
    } catch (e) {
      const status = e.status || 500;
      return json({ error: e.message || "서버 오류" }, status);
    }
  }
};
var fail = (msg, status = 400) => {
  const e = new Error(msg);
  e.status = status;
  throw e;
};
var enc = new TextEncoder();
var hex = (buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
var sha256hex = async (s) => hex(await crypto.subtle.digest("SHA-256", enc.encode(s)));
async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return hex(await crypto.subtle.sign("HMAC", key, enc.encode(msg)));
}
var b64url = (s) => btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
var unb64url = (s) => atob(s.replace(/-/g, "+").replace(/_/g, "/"));
var pwHash = (env, id, clientHash) => hmac(env.SESSION_SECRET, `pw:${id}:${clientHash}`);
async function makeToken(env, id, admin) {
  const payload = b64url(JSON.stringify({ id, admin, exp: Math.floor(Date.now() / 1e3) + TOKEN_DAYS * DAY }));
  return `${payload}.${await hmac(env.SESSION_SECRET, payload)}`;
}
async function readToken(env, token) {
  const [payload, sig] = String(token || "").split(".");
  if (!payload || !sig) return null;
  if (sig !== await hmac(env.SESSION_SECRET, payload)) return null;
  try {
    const p = JSON.parse(unb64url(payload));
    if (p.exp < Math.floor(Date.now() / 1e3)) return null;
    return p;
  } catch {
    return null;
  }
}
async function requireAuth(req, env) {
  const t = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  const p = await readToken(env, t);
  if (!p) fail("로그인이 필요합니다", 401);
  return p;
}
var GH = (env) => `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}`;
var ghHeaders = (env) => ({
  authorization: `Bearer ${env.GITHUB_TOKEN}`,
  accept: "application/vnd.github+json",
  "user-agent": "info-notebook-worker"
});
function b64encodeUtf8(str) {
  const bytes = enc.encode(str);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}
function b64decodeUtf8(b64) {
  const bin = atob(b64.replace(/\s/g, ""));
  const bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}
async function ghRead(env, path) {
  const r = await fetch(`${GH(env)}/contents/${path}?ref=${env.GITHUB_BRANCH || "main"}`, { headers: ghHeaders(env) });
  if (r.status === 404) return { json: null, sha: null };
  if (!r.ok) fail(`깃허브 읽기 실패 (${r.status})`, 502);
  const j = await r.json();
  try {
    return { json: JSON.parse(b64decodeUtf8(j.content)), sha: j.sha };
  } catch {
    return { json: null, sha: j.sha };
  }
}
async function ghWrite(env, path, obj, message) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const { sha } = await ghRead(env, path);
    const r = await fetch(`${GH(env)}/contents/${path}`, {
      method: "PUT",
      headers: { ...ghHeaders(env), "content-type": "application/json" },
      body: JSON.stringify({
        message,
        content: b64encodeUtf8(JSON.stringify(obj, null, 1)),
        branch: env.GITHUB_BRANCH || "main",
        ...sha ? { sha } : {}
      })
    });
    if (r.ok) return true;
    if (r.status !== 409 && r.status !== 422) fail(`깃허브 저장 실패 (${r.status})`, 502);
    await new Promise((res) => setTimeout(res, 250 * (attempt + 1)));
  }
  fail("깃허브 저장이 계속 충돌합니다. 잠시 뒤 다시 시도해 주세요", 503);
}
var ACCOUNTS = "userdata/_accounts.json";
var userFile = (id) => `userdata/${id}.json`;
function checkCreds(body) {
  const id = String(body.id || "").trim();
  const pw = String(body.pw || "");
  if (!OK_ID.test(id)) fail("아이디는 영문·숫자·_.- 2~24자여야 합니다");
  if (!/^[0-9a-f]{64}$/.test(pw)) fail("비밀번호 형식이 올바르지 않습니다");
  return { id, pw };
}
async function register(env, body) {
  const { id, pw } = checkCreds(body);
  const { json: accs } = await ghRead(env, ACCOUNTS);
  const all = accs || {};
  if (all[id]) fail("이미 있는 아이디입니다");
  all[id] = { h: await pwHash(env, id, pw), joined: (new Date()).toISOString() };
  await ghWrite(env, ACCOUNTS, all, `계정 추가: ${id}`);
  const admin = id === env.ADMIN_ID;
  return { id, admin, token: await makeToken(env, id, admin) };
}
async function login(env, body) {
  const { id, pw } = checkCreds(body);
  const { json: accs } = await ghRead(env, ACCOUNTS);
  const rec = accs?.[id];
  if (!rec) fail("없는 아이디입니다. 계정을 먼저 만들어 주세요");
  if (rec.h !== await pwHash(env, id, pw)) fail("아이디 또는 비밀번호가 맞지 않습니다");
  const admin = id === env.ADMIN_ID;
  return { id, admin, temp: !!rec.temp, token: await makeToken(env, id, admin) };
}
async function changePw(env, me, body) {
  const cur = String(body.cur || ""), next = String(body.next || "");
  if (!/^[0-9a-f]{64}$/.test(cur) || !/^[0-9a-f]{64}$/.test(next)) fail("비밀번호 형식이 올바르지 않습니다");
  if (cur === next) fail("이전과 다른 비밀번호를 쓰세요");
  const { json: accs } = await ghRead(env, ACCOUNTS);
  const rec = accs?.[me.id];
  if (!rec) fail("계정을 찾을 수 없습니다", 404);
  if (rec.h !== await pwHash(env, me.id, cur)) fail("현재 비밀번호가 맞지 않습니다");
  rec.h = await pwHash(env, me.id, next);
  rec.changedAt = (new Date()).toISOString();
  delete rec.temp;
  await ghWrite(env, ACCOUNTS, accs, `비밀번호 변경: ${me.id}`);
  return { ok: true };
}
async function adminReset(env, me, body) {
  if (!me.admin) fail("관리자만 할 수 있습니다", 403);
  const id = String(body.id || "").trim();
  if (!OK_ID.test(id)) fail("잘못된 아이디입니다");
  if (id === env.ADMIN_ID && me.id !== env.ADMIN_ID) fail("관리자 계정은 초기화할 수 없습니다", 403);
  const { json: accs } = await ghRead(env, ACCOUNTS);
  const rec = accs?.[id];
  if (!rec) fail("없는 아이디입니다");
  const bytes = crypto.getRandomValues(new Uint8Array(6));
  const temp = "tmp" + [...bytes].map((b) => "abcdefghjkmnpqrstuvwxyz23456789"[b % 31]).join("");
  rec.h = await pwHash(env, id, await sha256hex(temp));
  rec.temp = true;
  rec.resetAt = (new Date()).toISOString();
  await ghWrite(env, ACCOUNTS, accs, `비밀번호 초기화: ${id}`);
  return { ok: true, temp };
}
function checkTarget(me, target) {
  const t = String(target || "");
  if (t !== "_shared" && !OK_ID.test(t)) fail("잘못된 사용자 이름입니다");
  return t;
}
async function dataGet(env, me, body) {
  const t = checkTarget(me, body.user);
  if (t !== me.id && t !== "_shared" && !me.admin) fail("다른 사람의 기록은 볼 수 없습니다", 403);
  const { json } = await ghRead(env, userFile(t));
  return { data: json };
}
async function dataPut(env, me, body) {
  const t = checkTarget(me, body.user);
  if (t === "_shared") {
    if (!me.admin) fail("공용 편집은 관리자만 할 수 있습니다", 403);
  } else if (t !== me.id) fail("다른 사람의 기록은 고칠 수 없습니다", 403);
  const data = body.data;
  if (!data || typeof data !== "object") fail("저장할 내용이 없습니다");
  if (JSON.stringify(data).length > 9e5) fail("기록이 너무 큽니다. 오답 노트를 정리해 주세요");
  await ghWrite(env, userFile(t), data, `기록 저장: ${t}`);
  return { ok: true };
}
async function listUsers(env, me) {
  if (!me.admin) fail("관리자만 볼 수 있습니다", 403);
  const { json: accs } = await ghRead(env, ACCOUNTS);
  return {
    users: Object.entries(accs || {}).map(([id, v]) => ({
      id,
      joined: v.joined || null,
      resetAt: v.resetAt || null,
      temp: !!v.temp
      // 임시 비밀번호를 아직 안 바꾼 계정
    }))
  };
}
async function repoList(env, body) {
  const dir = String(body.dir || "notebooks").replace(/[^A-Za-z0-9_./-]/g, "");
  const r = await fetch(`${GH(env)}/contents/${dir}?ref=${env.GITHUB_BRANCH || "main"}`, { headers: ghHeaders(env) });
  if (r.status === 404) fail("노트북 폴더를 찾을 수 없습니다", 404);
  if (!r.ok) fail(`깃허브 목록 조회 실패 (${r.status})`, 502);
  const items = await r.json();
  return { items: items.map((f) => ({ name: f.name, path: f.path, type: f.type })) };
}
export {
  worker_default as default
};
