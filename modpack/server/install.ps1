# Gearwright's Hollow server (Windows): downloads the mods (checked by SHA-1) and installs NeoForge on first run.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Set-Location $PSScriptRoot
$NF = '21.1.262'
New-Item -ItemType Directory -Force mods | Out-Null
$failed = $false
foreach ($line in Get-Content server-mods.txt) {
    if ($line -match '^\s*(#|$)') { continue }
    $sum, $url = $line -split '\s+', 2
    $name = [uri]::UnescapeDataString(($url -split '/')[-1])
    $dst = Join-Path 'mods' $name
    if ((Test-Path -LiteralPath $dst) -and ((Get-FileHash -LiteralPath $dst -Algorithm SHA1).Hash.ToLower() -eq $sum)) { continue }
    Write-Host "Downloading $name"
    try {
        Invoke-WebRequest -Uri $url -OutFile "$dst.part" -UseBasicParsing
        if ((Get-FileHash -LiteralPath "$dst.part" -Algorithm SHA1).Hash.ToLower() -ne $sum) { throw 'checksum mismatch' }
        Move-Item -Force -LiteralPath "$dst.part" -Destination $dst
    } catch {
        Write-Host "  FAILED: $name ($_)"
        Remove-Item -ErrorAction SilentlyContinue -LiteralPath "$dst.part"
        $failed = $true
    }
}
if ($failed) { Write-Host 'Some mods failed to download. Run start.bat again to retry.'; exit 1 }
if (-not (Test-Path run.bat)) {
    Write-Host "Installing NeoForge $NF"
    Invoke-WebRequest -Uri "https://maven.neoforged.net/releases/net/neoforged/neoforge/$NF/neoforge-$NF-installer.jar" -OutFile neoforge-installer.jar -UseBasicParsing
    & java -jar neoforge-installer.jar --install-server .
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Remove-Item -ErrorAction SilentlyContinue neoforge-installer.jar, neoforge-installer.jar.log
}
if (-not ((Test-Path user_jvm_args.txt) -and (Select-String -Path user_jvm_args.txt -Pattern '^-Xmx' -Quiet))) {
    Add-Content user_jvm_args.txt "`r`n-Xms4G`r`n-Xmx8G"
}
exit 0
