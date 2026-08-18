var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// worker.js
var OK_ID = /^[A-Za-z0-9_.-]{2,24}$/;
var DAY = 86400;
var TOKEN_DAYS = 30;
var WORKER_VERSION = "2026-08-17-probe";
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
    const json = /* @__PURE__ */ __name((obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: { ...cors, "content-type": "application/json" } }), "json");
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
          "/repo/list",
          "/ai",
          "/diag"
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
      if (path === "/ai") return json(await ai(env, body));
      if (path === "/diag") return json(await diag(env, me));
      return json({ error: "\uC5C6\uB294 \uC8FC\uC18C\uC785\uB2C8\uB2E4" }, 404);
    } catch (e) {
      const status = e.status || 500;
      return json({ error: e.message || "\uC11C\uBC84 \uC624\uB958" }, status);
    }
  }
};
var fail = /* @__PURE__ */ __name((msg, status = 400) => {
  const e = new Error(msg);
  e.status = status;
  throw e;
}, "fail");
var enc = new TextEncoder();
var hex = /* @__PURE__ */ __name((buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join(""), "hex");
var sha256hex = /* @__PURE__ */ __name(async (s) => hex(await crypto.subtle.digest("SHA-256", enc.encode(s))), "sha256hex");
async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return hex(await crypto.subtle.sign("HMAC", key, enc.encode(msg)));
}
__name(hmac, "hmac");
var b64url = /* @__PURE__ */ __name((s) => btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""), "b64url");
var unb64url = /* @__PURE__ */ __name((s) => atob(s.replace(/-/g, "+").replace(/_/g, "/")), "unb64url");
var pwHash = /* @__PURE__ */ __name((env, id, clientHash) => hmac(env.SESSION_SECRET, `pw:${id}:${clientHash}`), "pwHash");
async function makeToken(env, id, admin) {
  const payload = b64url(JSON.stringify({ id, admin, exp: Math.floor(Date.now() / 1e3) + TOKEN_DAYS * DAY }));
  return `${payload}.${await hmac(env.SESSION_SECRET, payload)}`;
}
__name(makeToken, "makeToken");
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
__name(readToken, "readToken");
async function requireAuth(req, env) {
  const t = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  const p = await readToken(env, t);
  if (!p) fail("\uB85C\uADF8\uC778\uC774 \uD544\uC694\uD569\uB2C8\uB2E4", 401);
  return p;
}
__name(requireAuth, "requireAuth");
var GH = /* @__PURE__ */ __name((env) => `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}`, "GH");
var ghHeaders = /* @__PURE__ */ __name((env) => ({
  authorization: `Bearer ${env.GITHUB_TOKEN}`,
  accept: "application/vnd.github+json",
  "user-agent": "info-notebook-worker"
}), "ghHeaders");
function b64encodeUtf8(str) {
  const bytes = enc.encode(str);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}
__name(b64encodeUtf8, "b64encodeUtf8");
function b64decodeUtf8(b64) {
  const bin = atob(b64.replace(/\s/g, ""));
  const bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}
__name(b64decodeUtf8, "b64decodeUtf8");
async function ghRead(env, path) {
  const r = await fetch(`${GH(env)}/contents/${path}?ref=${env.GITHUB_BRANCH || "main"}`, { headers: ghHeaders(env) });
  if (r.status === 404) return { json: null, sha: null };
  if (!r.ok) fail(`\uAE43\uD5C8\uBE0C \uC77D\uAE30 \uC2E4\uD328 (${r.status})`, 502);
  const j = await r.json();
  try {
    return { json: JSON.parse(b64decodeUtf8(j.content)), sha: j.sha };
  } catch {
    return { json: null, sha: j.sha };
  }
}
__name(ghRead, "ghRead");
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
    if (r.status !== 409 && r.status !== 422) fail(`\uAE43\uD5C8\uBE0C \uC800\uC7A5 \uC2E4\uD328 (${r.status})`, 502);
    await new Promise((res) => setTimeout(res, 250 * (attempt + 1)));
  }
  fail("\uAE43\uD5C8\uBE0C \uC800\uC7A5\uC774 \uACC4\uC18D \uCDA9\uB3CC\uD569\uB2C8\uB2E4. \uC7A0\uC2DC \uB4A4 \uB2E4\uC2DC \uC2DC\uB3C4\uD574 \uC8FC\uC138\uC694", 503);
}
__name(ghWrite, "ghWrite");
var ACCOUNTS = "userdata/_accounts.json";
var userFile = /* @__PURE__ */ __name((id) => `userdata/${id}.json`, "userFile");
function checkCreds(body) {
  const id = String(body.id || "").trim();
  const pw = String(body.pw || "");
  if (!OK_ID.test(id)) fail("\uC544\uC774\uB514\uB294 \uC601\uBB38\xB7\uC22B\uC790\xB7_.- 2~24\uC790\uC5EC\uC57C \uD569\uB2C8\uB2E4");
  if (!/^[0-9a-f]{64}$/.test(pw)) fail("\uBE44\uBC00\uBC88\uD638 \uD615\uC2DD\uC774 \uC62C\uBC14\uB974\uC9C0 \uC54A\uC2B5\uB2C8\uB2E4");
  return { id, pw };
}
__name(checkCreds, "checkCreds");
async function register(env, body) {
  const { id, pw } = checkCreds(body);
  const { json: accs } = await ghRead(env, ACCOUNTS);
  const all = accs || {};
  if (all[id]) fail("\uC774\uBBF8 \uC788\uB294 \uC544\uC774\uB514\uC785\uB2C8\uB2E4");
  all[id] = { h: await pwHash(env, id, pw), joined: (/* @__PURE__ */ new Date()).toISOString() };
  await ghWrite(env, ACCOUNTS, all, `\uACC4\uC815 \uCD94\uAC00: ${id}`);
  const admin = id === env.ADMIN_ID;
  return { id, admin, token: await makeToken(env, id, admin) };
}
__name(register, "register");
async function login(env, body) {
  const { id, pw } = checkCreds(body);
  const { json: accs } = await ghRead(env, ACCOUNTS);
  const rec = accs?.[id];
  if (!rec) fail("\uC5C6\uB294 \uC544\uC774\uB514\uC785\uB2C8\uB2E4. \uACC4\uC815\uC744 \uBA3C\uC800 \uB9CC\uB4E4\uC5B4 \uC8FC\uC138\uC694");
  if (rec.h !== await pwHash(env, id, pw)) fail("\uC544\uC774\uB514 \uB610\uB294 \uBE44\uBC00\uBC88\uD638\uAC00 \uB9DE\uC9C0 \uC54A\uC2B5\uB2C8\uB2E4");
  const admin = id === env.ADMIN_ID;
  return { id, admin, temp: !!rec.temp, token: await makeToken(env, id, admin) };
}
__name(login, "login");
async function changePw(env, me, body) {
  const cur = String(body.cur || ""), next = String(body.next || "");
  if (!/^[0-9a-f]{64}$/.test(cur) || !/^[0-9a-f]{64}$/.test(next)) fail("\uBE44\uBC00\uBC88\uD638 \uD615\uC2DD\uC774 \uC62C\uBC14\uB974\uC9C0 \uC54A\uC2B5\uB2C8\uB2E4");
  if (cur === next) fail("\uC774\uC804\uACFC \uB2E4\uB978 \uBE44\uBC00\uBC88\uD638\uB97C \uC4F0\uC138\uC694");
  const { json: accs } = await ghRead(env, ACCOUNTS);
  const rec = accs?.[me.id];
  if (!rec) fail("\uACC4\uC815\uC744 \uCC3E\uC744 \uC218 \uC5C6\uC2B5\uB2C8\uB2E4", 404);
  if (rec.h !== await pwHash(env, me.id, cur)) fail("\uD604\uC7AC \uBE44\uBC00\uBC88\uD638\uAC00 \uB9DE\uC9C0 \uC54A\uC2B5\uB2C8\uB2E4");
  rec.h = await pwHash(env, me.id, next);
  rec.changedAt = (/* @__PURE__ */ new Date()).toISOString();
  delete rec.temp;
  await ghWrite(env, ACCOUNTS, accs, `\uBE44\uBC00\uBC88\uD638 \uBCC0\uACBD: ${me.id}`);
  return { ok: true };
}
__name(changePw, "changePw");
async function adminReset(env, me, body) {
  if (!me.admin) fail("\uAD00\uB9AC\uC790\uB9CC \uD560 \uC218 \uC788\uC2B5\uB2C8\uB2E4", 403);
  const id = String(body.id || "").trim();
  if (!OK_ID.test(id)) fail("\uC798\uBABB\uB41C \uC544\uC774\uB514\uC785\uB2C8\uB2E4");
  if (id === env.ADMIN_ID && me.id !== env.ADMIN_ID) fail("\uAD00\uB9AC\uC790 \uACC4\uC815\uC740 \uCD08\uAE30\uD654\uD560 \uC218 \uC5C6\uC2B5\uB2C8\uB2E4", 403);
  const { json: accs } = await ghRead(env, ACCOUNTS);
  const rec = accs?.[id];
  if (!rec) fail("\uC5C6\uB294 \uC544\uC774\uB514\uC785\uB2C8\uB2E4");
  const bytes = crypto.getRandomValues(new Uint8Array(6));
  const temp = "tmp" + [...bytes].map((b) => "abcdefghjkmnpqrstuvwxyz23456789"[b % 31]).join("");
  rec.h = await pwHash(env, id, await sha256hex(temp));
  rec.temp = true;
  rec.resetAt = (/* @__PURE__ */ new Date()).toISOString();
  await ghWrite(env, ACCOUNTS, accs, `\uBE44\uBC00\uBC88\uD638 \uCD08\uAE30\uD654: ${id}`);
  return { ok: true, temp };
}
__name(adminReset, "adminReset");
function checkTarget(me, target) {
  const t = String(target || "");
  if (t !== "_shared" && !OK_ID.test(t)) fail("\uC798\uBABB\uB41C \uC0AC\uC6A9\uC790 \uC774\uB984\uC785\uB2C8\uB2E4");
  return t;
}
__name(checkTarget, "checkTarget");
async function dataGet(env, me, body) {
  const t = checkTarget(me, body.user);
  if (t !== me.id && t !== "_shared" && !me.admin) fail("\uB2E4\uB978 \uC0AC\uB78C\uC758 \uAE30\uB85D\uC740 \uBCFC \uC218 \uC5C6\uC2B5\uB2C8\uB2E4", 403);
  const { json } = await ghRead(env, userFile(t));
  return { data: json };
}
__name(dataGet, "dataGet");
async function dataPut(env, me, body) {
  const t = checkTarget(me, body.user);
  if (t === "_shared") {
    if (!me.admin) fail("\uACF5\uC6A9 \uD3B8\uC9D1\uC740 \uAD00\uB9AC\uC790\uB9CC \uD560 \uC218 \uC788\uC2B5\uB2C8\uB2E4", 403);
  } else if (t !== me.id) fail("\uB2E4\uB978 \uC0AC\uB78C\uC758 \uAE30\uB85D\uC740 \uACE0\uCE60 \uC218 \uC5C6\uC2B5\uB2C8\uB2E4", 403);
  const data = body.data;
  if (!data || typeof data !== "object") fail("\uC800\uC7A5\uD560 \uB0B4\uC6A9\uC774 \uC5C6\uC2B5\uB2C8\uB2E4");
  if (JSON.stringify(data).length > 9e5) fail("\uAE30\uB85D\uC774 \uB108\uBB34 \uD07D\uB2C8\uB2E4. \uC624\uB2F5 \uB178\uD2B8\uB97C \uC815\uB9AC\uD574 \uC8FC\uC138\uC694");
  await ghWrite(env, userFile(t), data, `\uAE30\uB85D \uC800\uC7A5: ${t}`);
  return { ok: true };
}
__name(dataPut, "dataPut");
async function listUsers(env, me) {
  if (!me.admin) fail("\uAD00\uB9AC\uC790\uB9CC \uBCFC \uC218 \uC788\uC2B5\uB2C8\uB2E4", 403);
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
__name(listUsers, "listUsers");
async function repoList(env, body) {
  const dir = String(body.dir || "notebooks").replace(/[^A-Za-z0-9_./-]/g, "");
  const r = await fetch(`${GH(env)}/contents/${dir}?ref=${env.GITHUB_BRANCH || "main"}`, { headers: ghHeaders(env) });
  if (r.status === 404) fail("\uB178\uD2B8\uBD81 \uD3F4\uB354\uB97C \uCC3E\uC744 \uC218 \uC5C6\uC2B5\uB2C8\uB2E4", 404);
  if (!r.ok) fail(`\uAE43\uD5C8\uBE0C \uBAA9\uB85D \uC870\uD68C \uC2E4\uD328 (${r.status})`, 502);
  const items = await r.json();
  return { items: items.map((f) => ({ name: f.name, path: f.path, type: f.type })) };
}
__name(repoList, "repoList");
var MAKE_SYS = `\uB108\uB294 \uD55C\uAD6D \uACE0\uB4F1\uD559\uAD50 \uC815\uBCF4 \uACFC\uBAA9\uC758 \uCD9C\uC81C \uAD50\uC0AC\uB2E4.
\uC8FC\uC5B4\uC9C4 \uC218\uC5C5 \uB178\uD2B8\uBD81 \uB0B4\uC6A9\uC5D0\uC11C \uD575\uC2EC \uAC1C\uB150 \uD558\uB098\uB97C \uACE8\uB77C \uC11C\uC220\uD615 \uBB38\uC81C 1\uAC1C\uB97C \uB0B8\uB2E4.

\uADDC\uCE59
- \uD55C\uAD6D\uC5B4\uB85C \uC4F4\uB2E4.
- \uB178\uD2B8\uBD81\uC5D0 \uC2E4\uC81C\uB85C \uB098\uC628 \uAC1C\uB150\uB9CC \uB2E4\uB8EC\uB2E4. \uB178\uD2B8\uBD81 \uBC16 \uC9C0\uC2DD\uC744 \uC694\uAD6C\uD558\uC9C0 \uC54A\uB294\uB2E4.
- \uC8FC\uC5B4\uC9C4 \uC124\uBA85\uACFC \uCF54\uB4DC \uC870\uAC01\uB9CC \uBCF4\uACE0 \uB2F5\uD560 \uC218 \uC788\uC5B4\uC57C \uD55C\uB2E4. \uB178\uD2B8\uBD81\uC758 \uB2E4\uB978 \uC140\uC774\uB098 \uC55E\uB4A4 \uB9E5\uB77D\uC744 \uC54C\uC544\uC57C\uB9CC \uD480\uB9AC\uB294 \uBB38\uC81C\uB294 \uC808\uB300 \uB0B4\uC9C0 \uC54A\uB294\uB2E4.
- \uBB38\uC81C \uC548\uC5D0 \uD544\uC694\uD55C \uC815\uBCF4\uB97C \uBAA8\uB450 \uB2F4\uB294\uB2E4. "\uC704\uC5D0\uC11C \uB9CC\uB4E0 \uBC30\uC5F4", "\uC544\uAE4C \uC815\uC758\uD55C \uD568\uC218"\uCC98\uB7FC \uD654\uBA74\uC5D0 \uC5C6\uB294 \uAC83\uC744 \uAC00\uB9AC\uD0A4\uC9C0 \uC54A\uB294\uB2E4.
- \uC11C\uC220\uD615\uC774\uBBC0\uB85C \uB2F5\uC774 \uD55C \uB2E8\uC5B4\uB85C \uB05D\uB098\uBA74 \uC548 \uB41C\uB2E4. "\uC65C", "\uC5B4\uB5BB\uAC8C", "\uBB34\uC2A8 \uCC28\uC774", "\uC5B4\uB5A4 \uC77C\uC774 \uC77C\uC5B4\uB098\uB294\uC9C0" \uAC19\uC740 \uC124\uBA85\uC744 \uC694\uAD6C\uD55C\uB2E4.
- \uCF54\uB4DC\uAC00 \uD544\uC694\uD558\uBA74 code \uD544\uB4DC\uC5D0 \uC9E7\uC740 \uD30C\uC774\uC36C \uCF54\uB4DC\uB97C \uB123\uACE0, \uD544\uC694 \uC5C6\uC73C\uBA74 \uBE48 \uBB38\uC790\uC5F4\uB85C \uB454\uB2E4.
- rubric\uC5D0\uB294 \uC815\uB2F5\uC73C\uB85C \uC778\uC815\uD560 \uD575\uC2EC \uC694\uC18C\uB97C 2~4\uAC1C \uC801\uB294\uB2E4.

\uCD9C\uB825\uC740 \uC544\uB798 \uD615\uD0DC\uC758 JSON \uD558\uB098\uBFD0\uC774\uB2E4. \uC124\uBA85, \uC778\uC0AC\uB9D0, \uB9C8\uD06C\uB2E4\uC6B4 \uCF54\uB4DC\uD39C\uC2A4\uB97C \uC808\uB300 \uBD99\uC774\uC9C0 \uC54A\uB294\uB2E4.
{"question":"...","code":"","rubric":"...","model_answer":"..."}`;
var GRADE_SYS = `\uB108\uB294 \uD55C\uAD6D \uACE0\uB4F1\uD559\uAD50 \uC815\uBCF4 \uACFC\uBAA9\uC758 \uCC44\uC810 \uAD50\uC0AC\uB2E4. \uD559\uC0DD \uB2F5\uC548\uC744 \uCC44\uC810 \uAE30\uC900\uC5D0 \uBE44\uCD94\uC5B4 \uD3C9\uAC00\uD55C\uB2E4.

\uADDC\uCE59
- \uD55C\uAD6D\uC5B4\uB85C \uC4F4\uB2E4.
- \uD575\uC2EC \uC694\uC18C\uB97C \uB300\uCCB4\uB85C \uB2F4\uC558\uC73C\uBA74 \uB9DE\uC740 \uAC83\uC73C\uB85C \uBCF8\uB2E4. \uD45C\uD604\uC774 \uC11C\uD234\uB7EC\uB3C4 \uB73B\uC774 \uB9DE\uC73C\uBA74 \uC778\uC815\uD55C\uB2E4.
- feedback\uC740 \uB450 \uBB38\uC7A5 \uC774\uB0B4\uB85C, \uBB34\uC5C7\uC774 \uC88B\uC558\uACE0 \uBB34\uC5C7\uC774 \uBE60\uC84C\uB294\uC9C0 \uAD6C\uCCB4\uC801\uC73C\uB85C \uC9DA\uB294\uB2E4. \uD559\uC0DD\uC744 \uAE4E\uC544\uB0B4\uB9AC\uC9C0 \uC54A\uB294\uB2E4.
- model_answer\uC5D0\uB294 \uBAA8\uBC94 \uB2F5\uC548\uC744 \uC138 \uBB38\uC7A5 \uC774\uB0B4\uB85C \uC4F4\uB2E4.

\uCD9C\uB825\uC740 \uC544\uB798 \uD615\uD0DC\uC758 JSON \uD558\uB098\uBFD0\uC774\uB2E4. \uC124\uBA85, \uC778\uC0AC\uB9D0, \uB9C8\uD06C\uB2E4\uC6B4 \uCF54\uB4DC\uD39C\uC2A4\uB97C \uC808\uB300 \uBD99\uC774\uC9C0 \uC54A\uB294\uB2E4.
{"correct":true,"feedback":"...","model_answer":"..."}`;
var CHAT_SYS = `너는 한국 고등학교 정보 과목의 보조 교사다. 학생이 수업 노트북에서 직접 고른 부분에 대해 질문한다.

규칙
- 한국어로, 세 문단을 넘기지 않게 짧게 답한다.
- 학생이 고른 부분을 근거로 설명한다. 거기에 없는 내용을 말할 때는 추측임을 밝힌다.
- 코드 예시는 필요할 때만, 짧게 넣는다.
- 과제 답을 통째로 대신 써 주지 않는다. 스스로 풀도록 원리와 힌트를 준다.
- 정보 과목·프로그래밍과 관계없는 잡담에는 답하지 않고 한 줄로 거절한다.

마크다운으로 답한다.`;
async function callClaude(env, system, user, maxTokens = 1200, raw = false) {
  if (!env.ANTHROPIC_API_KEY) fail("\uC11C\uC220\uD615 \uAE30\uB2A5\uC774 \uC124\uC815\uB418\uC9C0 \uC54A\uC558\uC2B5\uB2C8\uB2E4 (ANTHROPIC_API_KEY \uC5C6\uC74C)", 503);
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": String(env.ANTHROPIC_API_KEY).trim(),
      "anthropic-version": "2023-06-01",
      // user-agent 가 없으면 방화벽이 자동화 요청으로 보고 막는 경우가 있습니다.
      "user-agent": "INFSUB/1.0 (+https://namu578.github.io/INFSUB)"
    },
    body: JSON.stringify({
      model: env.MODEL || "claude-sonnet-5",
      max_tokens: maxTokens,
      system,
      messages: Array.isArray(user) ? user : [{ role: "user", content: user }]
    })
  });
  if (!r.ok) {
    const t = await r.text().catch(() => "");
    if (r.status === 401) fail("Claude API \uD0A4\uAC00 \uC62C\uBC14\uB974\uC9C0 \uC54A\uC2B5\uB2C8\uB2E4. wrangler secret put ANTHROPIC_API_KEY \uB85C \uB2E4\uC2DC \uB123\uC5B4 \uC8FC\uC138\uC694", 502);
    if (r.status === 403) fail("Claude API\uAC00 \uC774 \uC694\uCCAD\uC744 \uAC70\uBD80\uD588\uC2B5\uB2C8\uB2E4 (403). \uD0A4\uAC00 \uD3D0\uAE30\uB418\uC5C8\uAC70\uB098, \uACB0\uC81C\uAC00 \uC124\uC815\uB418\uC9C0 \uC54A\uC558\uAC70\uB098, \uACC4\uC815\uC5D0 \uC774 \uBAA8\uB378 \uAD8C\uD55C\uC774 \uC5C6\uC744 \uB54C \uB0A9\uB2C8\uB2E4. console.anthropic.com \uC5D0\uC11C \uD0A4\uC640 \uACB0\uC81C \uC0C1\uD0DC\uB97C \uD655\uC778\uD574 \uC8FC\uC138\uC694", 502);
    if (r.status === 404) fail(`\uC694\uCCAD\uD55C \uBAA8\uB378\uC744 \uCC3E\uC744 \uC218 \uC5C6\uC2B5\uB2C8\uB2E4 (${env.MODEL || "claude-sonnet-5"}). wrangler.toml \uC758 MODEL \uAC12\uC744 \uD655\uC778\uD574 \uC8FC\uC138\uC694`, 502);
    if (r.status === 429) fail("\uC694\uCCAD\uC774 \uBAB0\uB838\uC2B5\uB2C8\uB2E4. \uC7A0\uC2DC \uB4A4 \uB2E4\uC2DC \uC2DC\uB3C4\uD574 \uC8FC\uC138\uC694", 502);
    fail(`Claude \uD638\uCD9C \uC2E4\uD328 (${r.status}) ${t.slice(0, 160)}`, 502);
  }
  const j = await r.json();
  const text = (j.content || []).filter((c) => c.type === "text").map((c) => c.text).join("\n");
  if (raw) return { text };
  const clean = text.replace(/```json|```/g, "").trim();
  try {
    return JSON.parse(clean);
  } catch {
    const m = clean.match(/\{[\s\S]*\}/);
    if (m) {
      try {
        return JSON.parse(m[0]);
      } catch {
      }
    }
    fail("AI \uC751\uB2F5\uC744 \uC774\uD574\uD558\uC9C0 \uBABB\uD588\uC2B5\uB2C8\uB2E4. \uB2E4\uC2DC \uC2DC\uB3C4\uD574 \uC8FC\uC138\uC694", 502);
  }
}
__name(callClaude, "callClaude");
async function diag(env, me) {
  if (!me.admin) fail("\uAD00\uB9AC\uC790\uB9CC \uBCFC \uC218 \uC788\uC2B5\uB2C8\uB2E4", 403);
  const key = env.ANTHROPIC_API_KEY;
  const model = env.MODEL || "claude-sonnet-5";
  const out = { model, keySet: !!key, probes: [] };
  if (!key) {
    out.verdict = "\uC774 \uC6CC\uCEE4\uC5D0 ANTHROPIC_API_KEY \uAC00 \uC5C6\uC2B5\uB2C8\uB2E4. Cloudflare \uB300\uC2DC\uBCF4\uB4DC\uC5D0\uC11C \uB123\uC5B4 \uC8FC\uC138\uC694.";
    return out;
  }
  out.keyLength = key.length;
  out.keyHead = key.slice(0, 14);
  out.hasSpace = /^\s|\s$/.test(key);
  out.looksLikeApiKey = key.trim().startsWith("sk-ant-api");
  out.looksLikeOAuth = key.trim().startsWith("sk-ant-oat");
  const k = key.trim();
  const msgBody = JSON.stringify({ model, max_tokens: 4, messages: [{ role: "user", content: "hi" }] });
  async function probe(name, url, init) {
    try {
      const r = await fetch(url, init);
      const txt = (await r.text().catch(() => "")).replace(/\s+/g, " ").slice(0, 120);
      out.probes.push({
        name,
        status: r.status,
        requestId: r.headers.get("request-id") || r.headers.get("x-request-id") || null,
        cfRay: r.headers.get("cf-ray") || null,
        body: txt
      });
      return r.status;
    } catch (e) {
      out.probes.push({ name, status: 0, error: String(e).slice(0, 120) });
      return 0;
    }
  }
  __name(probe, "probe");
  const H = /* @__PURE__ */ __name((extra) => ({ "content-type": "application/json", "anthropic-version": "2023-06-01", ...extra }), "H");
  const s1 = await probe(
    "\uAE30\uBCF8",
    "https://api.anthropic.com/v1/messages",
    { method: "POST", headers: H({ "x-api-key": k }), body: msgBody }
  );
  const s2 = await probe(
    "UA \uCD94\uAC00",
    "https://api.anthropic.com/v1/messages",
    { method: "POST", headers: H({ "x-api-key": k, "user-agent": "INFSUB/1.0 (+https://namu578.github.io/INFSUB)" }), body: msgBody }
  );
  const s3 = await probe(
    "\uD0A4 \uC5C6\uC774",
    "https://api.anthropic.com/v1/models",
    { method: "GET", headers: H({}) }
  );
  const s4 = await probe(
    "\uBAA8\uB378 \uBAA9\uB85D",
    "https://api.anthropic.com/v1/models",
    { method: "GET", headers: H({ "x-api-key": k }) }
  );
  out.status = s1;
  out.reached = !!out.probes[0].requestId;
  if (out.hasSpace) out.verdict = "\uD0A4 \uC55E\uB4A4\uC5D0 \uACF5\uBC31\uC774\uB098 \uC904\uBC14\uAFC8\uC774 \uBD99\uC5B4 \uC788\uC2B5\uB2C8\uB2E4. \uB2E4\uC2DC \uB123\uC5B4 \uC8FC\uC138\uC694.";
  else if (out.looksLikeOAuth) out.verdict = "Claude Code \uC6A9 OAuth \uD1A0\uD070\uC785\uB2C8\uB2E4. sk-ant-api \uB85C \uC2DC\uC791\uD558\uB294 \uD0A4\uAC00 \uD544\uC694\uD569\uB2C8\uB2E4.";
  else if (!out.looksLikeApiKey) out.verdict = "API \uD0A4 \uD615\uC2DD\uC774 \uC544\uB2D9\uB2C8\uB2E4. \uC0C8\uB85C \uBC1C\uAE09\uD574 \uC8FC\uC138\uC694.";
  else if (s1 === 200) out.verdict = "\uC815\uC0C1\uC785\uB2C8\uB2E4. AI \uAE30\uB2A5\uC774 \uB3D9\uC791\uD574\uC57C \uD569\uB2C8\uB2E4.";
  else if (s1 === 401) out.verdict = "\uD0A4\uAC00 \uC720\uD6A8\uD558\uC9C0 \uC54A\uC2B5\uB2C8\uB2E4. \uD3D0\uAE30\uB418\uC5C8\uAC70\uB098 \uC798\uBABB \uBCF5\uC0AC\uB418\uC5C8\uC2B5\uB2C8\uB2E4.";
  else if (s1 === 403 && s2 === 200)
    out.verdict = "user-agent \uD5E4\uB354\uAC00 \uC5C6\uC5B4\uC11C \uB9C9\uD614\uC2B5\uB2C8\uB2E4. \uCF54\uB4DC\uC5D0 user-agent \uB97C \uCD94\uAC00\uD558\uBA74 \uD574\uACB0\uB429\uB2C8\uB2E4.";
  else if (s1 === 403 && s3 === 403)
    out.verdict = "\uD0A4 \uC5C6\uC774 \uBCF4\uB0B8 \uC694\uCCAD\uB3C4 403 \uC785\uB2C8\uB2E4. \uD0A4\uC640 \uBB34\uAD00\uD558\uAC8C \uC774 \uC6CC\uCEE4\uC758 \uCD9C\uBC1C\uC9C0\uAC00 \uCC28\uB2E8\uB41C \uC0C1\uD0DC\uC785\uB2C8\uB2E4.";
  else if (s1 === 403 && (s3 === 401 || s3 === 200))
    out.verdict = "\uAE38\uC740 \uB6AB\uB824 \uC788\uB294\uB370 \uC774 \uD0A4\uB85C \uBCF4\uB0B8 \uC694\uCCAD\uB9CC 403 \uC785\uB2C8\uB2E4. \uD0A4 \uAD8C\uD55C\uC774\uB098 \uC6CC\uD06C\uC2A4\uD398\uC774\uC2A4 \uC9C0\uCD9C \uD55C\uB3C4\uB97C \uD655\uC778\uD574 \uC8FC\uC138\uC694.";
  else if (s1 === 404) out.verdict = `\uBAA8\uB378 \uC774\uB984\uC774 \uC798\uBABB\uB418\uC5C8\uC2B5\uB2C8\uB2E4 (${model}).`;
  else out.verdict = "\uC544\uB798 \uD0D0\uCE68 \uACB0\uACFC\uB97C \uD655\uC778\uD574 \uC8FC\uC138\uC694.";
  return out;
}
__name(diag, "diag");
async function ai(env, body) {
  if (body.task === "make") {
    const ctx = String(body.context || "").slice(0, 6e3);
    if (!ctx.trim()) fail("\uB178\uD2B8\uBD81 \uB0B4\uC6A9\uC774 \uBE44\uC5B4 \uC788\uC2B5\uB2C8\uB2E4");
    return await callClaude(
      env,
      MAKE_SYS,
      `\uB178\uD2B8\uBD81 \uC774\uB984: ${String(body.notebook || "").slice(0, 80)}

=== \uB178\uD2B8\uBD81 \uB0B4\uC6A9 ===
${ctx}`
    );
  }
  if (body.task === "grade") {
    return await callClaude(
      env,
      GRADE_SYS,
      `\uBB38\uC81C: ${String(body.question || "").slice(0, 1500)}

\uCC44\uC810 \uAE30\uC900: ${String(body.rubric || "").slice(0, 1500)}

\uD559\uC0DD \uB2F5\uC548: ${String(body.answer || "").slice(0, 3e3)}`,
      700
    );
  }
  if (body.task === "chat") {
    const ctx = String(body.context || "").slice(0, 3e3);
    if (!ctx.trim()) fail("\uC9C8\uBB38\uD560 \uBD80\uBD84\uC774 \uBE44\uC5B4 \uC788\uC2B5\uB2C8\uB2E4");
    const msgs = (Array.isArray(body.messages) ? body.messages : []).slice(-16).map((m) => ({
      role: m.role === "assistant" ? "assistant" : "user",
      content: String(m.content || "").slice(0, 2e3)
    })).filter((m) => m.content);
    if (!msgs.length || msgs[msgs.length - 1].role !== "user") fail("\uC9C8\uBB38\uC774 \uBE44\uC5B4 \uC788\uC2B5\uB2C8\uB2E4");
    return await callClaude(env, `${CHAT_SYS}

=== \uD559\uC0DD\uC774 \uACE0\uB978 \uBD80\uBD84 ===
${ctx}`, msgs, 700, true);
  }
  fail("\uC54C \uC218 \uC5C6\uB294 \uC694\uCCAD\uC785\uB2C8\uB2E4");
}
__name(ai, "ai");
export {
  worker_default as default
};
//# sourceMappingURL=worker.js.map
