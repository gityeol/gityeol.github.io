param(
    [Parameter(Mandatory=$true)][string]$GitHubUser,
    [Parameter(Mandatory=$true)][string]$RepoName
)

$ErrorActionPreference = "Stop"

Write-Host "[1/3] Moving to repo directory..." -ForegroundColor Cyan
Set-Location -Path $PSScriptRoot

Write-Host "[2/3] Initializing git repo if needed..." -ForegroundColor Cyan
if (-not (Test-Path ".git")) {
	git init | Out-Null
}

Write-Host "[3/3] Setting SSH remote..." -ForegroundColor Cyan
$remoteUrl = "git@github.com:$GitHubUser/$RepoName.git"
if ((git remote) -notcontains "origin") {
	git remote add origin $remoteUrl
} else {
	git remote set-url origin $remoteUrl
}

git branch -M main
Write-Host "✅ SSH remote set to $remoteUrl" -ForegroundColor Green

