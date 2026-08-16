#!/usr/bin/env bash
# NAMU578/INFSUB 에 사이트를 올립니다.
# 이 스크립트가 있는 폴더에 index.html, worker.js, wrangler.toml, README.md 가 함께 있어야 합니다.
set -e

REPO_URL="https://github.com/NAMU578/INFSUB.git"
WORK="$HOME/INFSUB"

# 1) 저장소 받아오기 (이미 받아뒀으면 최신으로 맞춥니다)
if [ -d "$WORK/.git" ]; then
  cd "$WORK" && git pull --rebase
else
  git clone "$REPO_URL" "$WORK"
  cd "$WORK"
fi

# 2) 폴더 만들기 — 빈 폴더는 깃이 무시하므로 표시 파일을 하나씩 둡니다
mkdir -p notebooks pdfs userdata
[ -f notebooks/.gitkeep ] || touch notebooks/.gitkeep
[ -f pdfs/.gitkeep ]      || touch pdfs/.gitkeep
[ -f userdata/.gitkeep ]  || touch userdata/.gitkeep

# 3) 다운로드한 파일 복사 (스크립트가 있는 폴더에서 가져옵니다)
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SRC/index.html" "$SRC/worker.js" "$SRC/wrangler.toml" "$SRC/README.md" .

# 4) 커밋 & 푸시
git add -A
git commit -m "정보수업 노트북 사이트 추가" || echo "변경사항 없음 — 넘어갑니다"
git push origin main

echo
echo "완료. 이제 저장소 Settings > Pages 에서 Source 를 'Deploy from a branch', main / (root) 로 설정하세요."
echo "1~2분 뒤: https://namu578.github.io/INFSUB/"
