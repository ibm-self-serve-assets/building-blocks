# backup.ps1 - Creates a timestamped backup of all source files for factory-pulse-streamhouse.
# Run from the workspace root:  powershell -ExecutionPolicy Bypass -File scripts/backup.ps1

$workspaceRoot = "C:\Build_Lab\01-Streamhouse-bob\factory-pulse-streamhouse"
$timestamp     = Get-Date -Format "yyyyMMdd_HHmmss"
$dest          = "$workspaceRoot\backups\backup_$timestamp"

$items = @(
    "server\app.py",
    "server\kafka.py",
    "server\simulation.py",
    "server\context.py",
    "server\mcp.py",
    "server\plants.py",
    "server\schemas.py",
    "frontend\src\App.jsx",
    "frontend\src\main.jsx",
    "frontend\src\styles.scss",
    "frontend\src\sql.js",
    "frontend\src\components\FactoryTwin.jsx",
    "frontend\src\components\PlantMap.jsx",
    "frontend\src\sim\api.js",
    "frontend\src\sim\localBackend.js",
    "frontend\src\twin\lineControl.js",
    "frontend\src\twin\plantProfiles.js",
    "frontend\src\twin\plantSim.js",
    "frontend\vite.config.js",
    "frontend\package.json",
    ".env.example",
    "README.md",
    "start.py",
    "start.sh",
    "start.cmd",
    "setup-demo.sh",
    "setup-demo.cmd",
    ".dockerignore",
    ".gitignore"
)

Write-Host ""
Write-Host "Factory Pulse -- Source Backup" -ForegroundColor Cyan
Write-Host "Workspace  : $workspaceRoot" -ForegroundColor Cyan
Write-Host "Destination: $dest" -ForegroundColor Cyan
Write-Host ""

$ok = 0
$skip = 0
$skippedList = @()

foreach ($rel in $items) {
    $src    = "$workspaceRoot\$rel"
    $target = "$dest\$rel"

    if (-not (Test-Path $src)) {
        Write-Host "  SKIP  $rel" -ForegroundColor Yellow
        $skip++
        $skippedList += $rel
        continue
    }

    $targetDir = Split-Path $target -Parent
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    Copy-Item -Path $src -Destination $target -Force
    Write-Host "  OK    $rel" -ForegroundColor Green
    $ok++
}

# Write manifest
$manifestPath = "$dest\MANIFEST.txt"
$lines = @(
    "Factory Pulse Streamhouse - Backup Manifest",
    "Created    : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "Timestamp  : $timestamp",
    "Files OK   : $ok",
    "Files Skip : $skip",
    "",
    "Backed-up files:"
)
foreach ($rel in $items) {
    $tag = if ($skippedList -contains $rel) { "[SKIP]" } else { "[OK]  " }
    $lines += "  $tag $rel"
}
$lines | Set-Content -Path $manifestPath -Encoding UTF8

Write-Host ""
Write-Host "Done. $ok file(s) backed up, $skip skipped." -ForegroundColor Cyan
Write-Host "Backup folder: $dest" -ForegroundColor Cyan
Write-Host ""
