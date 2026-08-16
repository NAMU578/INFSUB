#!/usr/bin/env bash
# setup.sh 에서 "cannot pull with rebase" 오류가 났을 때 쓰는 재시도 스크립트.
# ~/INFSUB 폴더에 이 파일을 넣고 Git Bash에서
#   bash retry-push.sh
# 로 실행하세요.
set -e

WORK="$HOME/INFSUB"
cd "$WORK" || { echo "INFSUB 폴더를 못 찾았습니다: $WORK"; exit 1; }

echo "── 지금 위치 ──"
pwd

echo "── 1) 지금 있는 파일들을 먼저 커밋합니다 ──"
git add -A
git commit -m "정보수업 노트북 사이트 추가" || echo "(커밋할 변경사항이 없습니다 — 넘어갑니다)"

echo "── 2) 원격 저장소와 합칩니다 (겹치는 파일은 방금 만든 우리 파일을 우선합니다) ──"
git pull origin main --no-rebase -X ours --no-edit

echo "── 3) 올립니다 ──"
git push origin main

echo
echo "완료. https://namu578.github.io/INFSUB/ 에서 1~2분 뒤 확인해 보세요."
echo "(Settings > Pages 에서 Source가 'main / (root)'로 켜져 있어야 합니다)"
