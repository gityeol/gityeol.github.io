$ErrorActionPreference = "Stop"

function Fail($msg) {
	Write-Host "❌ $msg" -ForegroundColor Red
	exit 1
}

Write-Host "[0/6] Moving to repo dir" -ForegroundColor Cyan
Set-Location -Path $PSScriptRoot

# Ensure UTF-8 for Python
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# Clean any stuck rebase state proactively
if (Test-Path ".git/rebase-merge") {
	Write-Host "Found rebase-merge directory. Cleaning up..." -ForegroundColor Yellow
	try { git rebase --abort 2>$null } catch {}
	Remove-Item -Recurse -Force ".git/rebase-merge" -ErrorAction SilentlyContinue
}

# 1) Pull latest
try {
	Write-Host "[1/6] git fetch" -ForegroundColor Cyan
	git fetch origin | Out-Null

	Write-Host "[2/6] git rebase origin/main (ours)" -ForegroundColor Cyan
	git rebase origin/main --strategy-option=ours | Out-Null
} catch {
	Write-Host "Rebase failed; resetting to origin/main" -ForegroundColor Yellow
	try { git rebase --abort 2>$null } catch {}
	git reset --hard origin/main
}

# 2) Generate posts
Write-Host "[3/6] Generating posts (python generate_posts.py)" -ForegroundColor Cyan
python generate_posts.py
if ($LASTEXITCODE -ne 0) { Fail "Python generation failed" }

# 3) Add & commit
Write-Host "[4/6] git add/commit" -ForegroundColor Cyan
try {
	git add .
	$msg = "자동 생성 글 업데이트"
	git commit -m $msg --allow-empty | Out-Null
} catch {
	Fail "git commit failed"
}

# 4) Push via SSH
Write-Host "[5/6] git push origin main" -ForegroundColor Cyan
try {
	git push -u origin main
} catch {
	Fail "git push failed"
}

Write-Host "[6/6] ✅ Done. GitHub Pages updated." -ForegroundColor Green
