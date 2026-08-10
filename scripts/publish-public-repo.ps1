param(
    [string]$Owner = 'choiYhunn',
    [string]$RepoName = 'shared-brain-starter',
    [string]$Description = 'Privacy-first Git-backed personal AI memory bootstrap kit',
    [switch]$KeepTemp
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'git is required.'
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw 'GitHub CLI (gh) is required. Install it, then run: gh auth login'
}

gh auth status | Out-Host
if ($LASTEXITCODE -ne 0) {
    throw 'GitHub CLI is not authenticated. Run: gh auth login'
}

$FullName = "$Owner/$RepoName"
$RemoteUrl = "https://github.com/$FullName.git"

# Repository absence is expected on first publish. Windows PowerShell 5.1 can
# surface native stderr as NativeCommandError when ErrorActionPreference=Stop,
# so temporarily allow the probe to fail and inspect only the process exit code.
$SavedErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    & gh repo view $FullName --json nameWithOwner 1>$null 2>$null
    $RepoViewExitCode = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $SavedErrorActionPreference
}
$RepoExists = ($RepoViewExitCode -eq 0)

# If a previous publish attempt created the repository but failed before the
# initial branch was pushed (for example because the OAuth token lacked the
# workflow scope), reuse that empty repository. Refuse to overwrite any repo
# that already has a main branch.
if ($RepoExists) {
    $SavedErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $ExistingMain = (& git ls-remote $RemoteUrl refs/heads/main 2>$null | Out-String).Trim()
        $LsRemoteExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $SavedErrorActionPreference
    }
    if ($LsRemoteExitCode -ne 0) {
        throw "Could not inspect existing repository: $FullName"
    }
    if ($ExistingMain) {
        throw "Repository already contains a main branch; refusing to overwrite it: $FullName"
    }
    Write-Host "Reusing existing empty repository: $FullName"
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$StarterRoot = Split-Path -Parent $ScriptDir
if (-not (Test-Path (Join-Path $StarterRoot 'LICENSE'))) {
    throw 'LICENSE is missing; refusing to publish an ambiguous public package.'
}

$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("shared-brain-starter-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $TempRoot | Out-Null

try {
    Get-ChildItem -Force $StarterRoot | ForEach-Object {
        if ($_.Name -ne '.git') {
            Copy-Item -LiteralPath $_.FullName -Destination $TempRoot -Recurse -Force
        }
    }

    Push-Location $TempRoot
    try {
        git init -b main | Out-Host
        git add --all
        git commit -m 'Initial public Shared Brain starter' | Out-Host
        if ($LASTEXITCODE -ne 0) { throw 'git commit failed' }

        if ($RepoExists) {
            git remote add origin $RemoteUrl | Out-Host
            git push -u origin main | Out-Host
            if ($LASTEXITCODE -ne 0) {
                throw 'git push failed. If GitHub mentions .github/workflows, run: gh auth refresh -h github.com -s workflow'
            }
        } else {
            gh repo create $FullName --public --description $Description --source . --remote origin --push
            if ($LASTEXITCODE -ne 0) {
                throw 'gh repo create failed. If GitHub mentions .github/workflows, run: gh auth refresh -h github.com -s workflow'
            }
        }

        Write-Host "Published: https://github.com/$FullName"
        Write-Host 'Review repository visibility, README, security settings, and license before sharing widely.'
    } finally {
        Pop-Location
    }
} finally {
    if ($KeepTemp) {
        Write-Host "Temporary publish workspace kept at: $TempRoot"
    } elseif (Test-Path $TempRoot) {
        Remove-Item -Recurse -Force $TempRoot
    }
}
