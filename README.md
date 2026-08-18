# 해피해피 짭코랩

구글 클래스룸에서 받은 코랩 파일을 깃허브에 올려두면, 웹에서 읽고 실행하고 문제로 확인할 수 있는 사이트입니다.

- 노트북 뷰어 — 코드·주석·마크다운·저장된 출력을 코랩과 비슷하게 표시
- 브라우저 안 파이썬 실행 (Pyodide)
- 셀 편집 — 각자 자기 브라우저/계정에만 남습니다
- 문제 자동 출제 — 빈칸, 출력 예측, 값 계산, 개념, 순서, 서술형
- 오답 노트 — 두 번 연속 맞히면 자동으로 사라짐
- 관리자 화면 — 회원별 진행 상황, 수정 내역, 대리 보기, 공용 편집

---

## 1단계 — 저장소 만들기

깃허브에서 **공개(public)** 저장소를 하나 만들고 이렇게 구성합니다.

```
INFSUB/
├─ index.html          ← 이 파일
├─ notebooks/          ← 수업 코랩 파일(.ipynb)을 여기에 올립니다
│   ├─ 01-파이썬-기초.ipynb
│   └─ 02-리스트.ipynb
├─ pdfs/               ← 수업 PDF (선택)
└─ userdata/           ← 학습 기록이 자동으로 쌓이는 곳 (2단계 이후)
```

`notebooks/` 폴더에 파일을 새로 올리면 사이트에 자동으로 나타납니다. 코드를 고칠 필요 없습니다.

## 2단계 — GitHub Pages 켜기

저장소 **Settings → Pages → Source** 를 `Deploy from a branch`, 브랜치를 `main / (root)` 으로 두고 저장합니다.
1~2분 뒤 `https://namu578.github.io/INFSUB/` 으로 열립니다.

## 3단계 — index.html 설정 고치기

`index.html` 위쪽의 `CONFIG` 블록만 고치면 됩니다.

```js
const CONFIG = {
  GITHUB_OWNER : 'NAMU578',
  GITHUB_REPO  : 'INFSUB',
  GITHUB_BRANCH: 'main',
  NOTEBOOK_DIR : 'notebooks',
  WORKER_URL   : '',          // 4단계에서 채웁니다
  ADMIN_ID     : 'ohh5259',
  MIN_PW_LEN   : 8,           // 가입 시 최소 비밀번호 길이
  QUIZ_COUNT   : 10,
};
```

여기까지만 해도 사이트는 동작합니다. 다만 이 상태(**로컬 모드**)에서는 학습 기록이 각자 브라우저에만 저장되고, 서술형 문제는 쓸 수 없습니다.

### 계정 만들기

**계정 만들기** 를 누르면 아이디 · 비밀번호 · 비밀번호 확인을 입력하는 창이 뜹니다.
비밀번호는 `MIN_PW_LEN` 자 이상이어야 하고, 아이디를 포함하거나 숫자·영문 한 종류로만 이루어져 있으면 거부됩니다.

`index.html` 에는 비밀번호와 관련된 값이 하나도 들어가지 않습니다. 커밋할 것도, 붙여넣을 것도 없습니다.

| 모드 | 저장되는 것 | 저장되지 않는 것 |
|---|---|---|
| 로컬 | 브라우저 localStorage 에 SHA-256 해시 | 비밀번호 원문 |
| Worker | `userdata/_accounts.json` 에 `HMAC-SHA256(SESSION_SECRET, 아이디+해시)` | 비밀번호 원문 |

관리자도 회원의 비밀번호를 볼 수 없습니다. 잊은 회원에게는 **회원 관리 → 비번 초기화** 로 임시 비밀번호를 발급하고, 회원은 로그인 후 헤더의 **비밀번호 바꾸기** 로 자기 것으로 바꿉니다.

## 4단계 — Worker 붙이기 (기록 저장 + 서술형)

이걸 붙이면 이렇게 달라집니다.

| | 로컬 모드 | Worker 모드 |
|---|---|---|
| 학습 기록 | 그 브라우저에만 | 깃허브 `userdata/아이디.json` 에 저장, 기기 바뀌어도 유지 |
| 계정 | 브라우저마다 따로 | 모두가 공유하는 진짜 계정 |
| 관리자 회원 목록 | 같은 브라우저 사용자만 | 전체 회원 |
| 서술형 문제 | ✗ | ✓ |

### 왜 서버가 필요한가

깃허브 쓰기 토큰과 Claude API 키를 `index.html` 안에 넣으면, 사이트에 들어온 누구나 개발자 도구로 그 값을 꺼낼 수 있습니다. 키가 새면 남이 대신 쓰고 **요금은 형님 앞으로 청구됩니다.** 그래서 키는 서버에만 두고, 브라우저는 서버에 요청만 보냅니다.

Cloudflare Workers 무료 플랜은 하루 10만 요청까지라 학급 단위로는 넉넉합니다.

### 4-1. 깃허브 토큰 발급

깃허브 **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**

- Repository access: `Only select repositories` → 이 저장소 하나만
- Permissions → Repository permissions → **Contents: Read and write**
- 만료일은 원하는 대로 (만료되면 다시 발급해서 넣어주면 됩니다)

생성 직후 한 번만 보이니 바로 복사해 두세요.

### 4-2. Claude API 키 발급

[console.anthropic.com](https://console.anthropic.com) 에서 키를 만들고, **Billing** 에서 사용 한도(예: 월 $5)를 걸어두세요. 서술형을 안 쓸 거면 이 단계는 건너뛰어도 됩니다.

### 4-3. 배포

컴퓨터에 Node.js가 있어야 합니다.

```bash
npm install -g wrangler
wrangler login

# worker.js 와 wrangler.toml 이 있는 폴더에서
# wrangler.toml 의 GITHUB_OWNER / GITHUB_REPO / ALLOWED_ORIGIN 을 먼저 고쳐두세요

wrangler secret put GITHUB_TOKEN        # 4-1에서 만든 토큰
wrangler secret put SESSION_SECRET      # 아무 긴 무작위 문자열
wrangler secret put ANTHROPIC_API_KEY   # 4-2에서 만든 키 (건너뛰어도 됨)

wrangler deploy
```

`SESSION_SECRET` 은 아무 값이나 길게 넣으면 됩니다. 만들기 귀찮으면:

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

배포가 끝나면 `https://info-notebook.<계정>.workers.dev` 같은 주소가 나옵니다.
이 주소를 `index.html` 의 `WORKER_URL` 에 넣고 커밋하세요.

```js
WORKER_URL : 'https://info-notebook.<계정>.workers.dev',
```

### 4-4. 관리자 계정 만들기

**`ADMIN_ID` 로 지정한 아이디가 가입하면 자동으로 관리자**가 됩니다.

배포 직후 사이트에서 아이디 `ohh5259` 로 **계정 만들기** 를 먼저 하세요. 비밀번호는 그때 정하는 값이 그대로 쓰입니다. 먼저 선점당하지 않도록 친구들에게 주소를 알려주기 전에 해두는 게 좋습니다.

---

## 알아둘 점

**실행되는 것과 안 되는 것.** Pyodide는 기본 파이썬 문법, `numpy`, `pandas`, `matplotlib` 까지 돌립니다. TensorFlow·PyTorch, 구글 드라이브 연동(`drive.mount`), 파일 읽기(`open`, `read_csv`), `input()`, `!pip`·`%matplotlib` 같은 코랩 전용 명령은 동작하지 않습니다. 문제 출제기도 이런 셀은 자동으로 건너뜁니다.

**로그인의 성격.** 정적 사이트의 로그인은 자물쇠라기보다 명찰에 가깝습니다. Worker를 붙이면 비밀번호 검증과 권한 확인이 서버에서 일어나 훨씬 단단해지지만, 성적처럼 민감한 정보를 넣을 용도로는 만들지 마세요.

**기록이 공개된다는 점.** `userdata/` 는 공개 저장소 안에 있으므로 누가 몇 점인지 주소만 알면 볼 수 있습니다. 곤란하면 저장소를 비공개로 바꾸고 (Pages는 유료 플랜 필요) 노트북만 따로 공개하거나, 아이디를 별명으로 쓰게 하세요.

**편집은 서로 안 섞입니다.** 각자 자기 파일에만 쓰기 때문에 충돌이 날 구조가 아닙니다. 관리자가 **공용 편집 모드** 를 켜고 고친 셀만 모두에게 기본값으로 적용되고, 개인이 따로 고친 셀은 개인 것이 우선합니다.

**API 요금.** 서술형은 문제 생성에 1회, 채점에 1회 호출합니다. 한 세션에 서술형 2문제면 4회입니다. 반 인원이 매일 풀어도 월 몇 달러 수준이지만, 콘솔에서 한도는 꼭 걸어두세요.

---

## 문제가 생기면

| 증상 | 확인할 것 |
|---|---|
| 노트북 목록이 비어 있음 | `NOTEBOOK_DIR` 이름, 파일 확장자가 `.ipynb` 인지, Pages가 최신 커밋을 반영했는지 |
| 목록 불러오기 실패 (403) | 로컬 모드는 시간당 60회 제한입니다. 학교처럼 같은 네트워크를 여러 명이 쓰면 금방 걸립니다 → Worker를 붙이면 해결됩니다 |
| Python 준비가 안 끝남 | 첫 실행 때 약 10MB를 내려받습니다. 두 번째부터는 캐시됩니다 |
| 서술형 버튼이 꺼져 있음 | `WORKER_URL` 이 비어 있거나 `ANTHROPIC_API_KEY` 를 안 넣은 경우입니다 |
| 로그인은 되는데 저장이 안 됨 | `GITHUB_TOKEN` 의 Contents 권한, `wrangler.toml` 의 저장소 이름 |
| CORS 오류 | `wrangler.toml` 의 `ALLOWED_ORIGIN` 이 실제 Pages 주소와 정확히 같아야 합니다 (끝에 `/` 없이) |
