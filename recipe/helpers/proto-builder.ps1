@"
FROM mcr.microsoft.com/windows/servercore:ltsc2022
RUN powershell -Command `
    Set-ExecutionPolicy Bypass -Scope Process -Force; `
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1')); `
    choco install protobuf -y; `
    choco install buf -y
WORKDIR /workspace
"@ | Out-File -FilePath Dockerfile.windows -Encoding utf8

docker build -t local/proto-builder:latest .

$makefileContent = Get-Content -Path Makefile -Raw
$updatedContent = $makefileContent -replace 'protoImageName=ghcr.io/cosmos/proto-builder:\$\(protoVer\)', 'protoImageName=local/proto-builder:latest'
$updatedContent | Out-File -FilePath Makefile -Encoding utf8
