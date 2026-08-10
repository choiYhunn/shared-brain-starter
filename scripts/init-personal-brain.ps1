param(
    [Parameter(Mandatory=$true)]
    [string]$TargetDir,

    [switch]$Force,
    [switch]$InitGit
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$StarterRoot = Split-Path -Parent $ScriptDir
$TemplateRoot = Join-Path $StarterRoot 'templates\brain'
$Target = if ([System.IO.Path]::IsPathRooted($TargetDir)) {
    [System.IO.Path]::GetFullPath($TargetDir)
} else {
    [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $TargetDir))
}

if (-not (Test-Path $TemplateRoot)) {
    throw "Template directory not found: $TemplateRoot"
}

if (Test-Path $Target) {
    $items = @(Get-ChildItem -Force $Target)
    if ($items.Count -gt 0 -and -not $Force) {
        throw "Target directory is not empty. Review it first or pass -Force: $Target"
    }
} else {
    New-Item -ItemType Directory -Path $Target | Out-Null
}

$BrainTarget = Join-Path $Target 'brain'
New-Item -ItemType Directory -Force -Path $BrainTarget | Out-Null
Copy-Item -Path (Join-Path $TemplateRoot '*') -Destination $BrainTarget -Recurse -Force

@(
    'brain\knowledge',
    'brain\academics',
    'brain\career',
    'brain\memory',
    'sources',
    'inbox\pending'
) | ForEach-Object {
    New-Item -ItemType Directory -Force -Path (Join-Path $Target $_) | Out-Null
}

$PrivateReadme = @'
# My Private Shared Brain

This repository contains private personal context. Keep it private unless you have deliberately reviewed every file for publication.

Principles:
- one canonical durable fact;
- current explicit corrections beat old notes;
- actual project repositories remain authoritative for current code/config/tests/logs;
- uncertain claims stay UNKNOWN/NEEDS_VERIFICATION;
- raw exports and credentials stay outside this repository whenever possible.
'@
Set-Content -Path (Join-Path $Target 'README.md') -Value $PrivateReadme -Encoding UTF8

$Gitignore = @'
# Never commit raw bootstrap inputs or credentials
raw/
vault/
secrets/
exports/
*.env
.env.*
.dev.vars

# Local tooling
__pycache__/
*.pyc
.venv/
.DS_Store
Thumbs.db
'@
Set-Content -Path (Join-Path $Target '.gitignore') -Value $Gitignore -Encoding UTF8

if ($InitGit) {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw 'git is not installed or not on PATH.'
    }
    Push-Location $Target
    try {
        if (-not (Test-Path '.git')) {
            git init -b main | Out-Host
        }
    } finally {
        Pop-Location
    }
}

Write-Host "Created private Shared Brain skeleton: $Target"
Write-Host 'Next:'
Write-Host "  1. Use bootstrap\NOTEBOOKLM_BOOTSTRAP_PROMPT.md from the starter kit."
Write-Host "  2. Import with: python scripts\import_notebooklm.py <export.md> --root `"$Target`""
Write-Host "  3. Validate with: python scripts\validate_brain.py `"$Target`""
Write-Host '  4. Review generated claims manually before committing.'
