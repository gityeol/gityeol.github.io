@echo off
chcp 65001

REM -----------------------------
REM Git + Python 풀 자동화 배치
REM -----------------------------

REM 1. 저장소 폴더로 이동
set REPO_DIR=%~dp0
cd /d "%REPO_DIR%"

REM 2. 원격 pull + rebase (충돌 시 로컬 우선)
echo [1/5] 원격 내용 pull 중...
git fetch origin
git rebase origin/main --strategy-option=ours
if %errorlevel% neq 0 (
    echo 충돌 발생! 로컬 우선으로 자동 해결
    git rebase --abort
    git reset --hard origin/main
)

REM 3. 글 생성
echo [2/5] 글 생성 중...
python generate_posts.py

REM 4. Git add / commit
echo [3/5] Git add & commit
git add .
git commit -m "자동 생성 글 업데이트" --allow-empty

REM 5. Git push
echo [4/5] Git push 중...
git push -u origin main

echo GitHub Pages 업데이트 완료.
pause
