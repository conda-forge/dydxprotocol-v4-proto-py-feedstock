function Set-Dockerfile {
    param (
        [string]$FilePath
    )
    @"
FROM mcr.microsoft.com/windows/servercore:ltsc2022
RUN powershell -Command `
    `"Set-ExecutionPolicy Bypass -Scope Process -Force; `
    `[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
    `iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1')); `
    `choco install protobuf -y; `
    `choco install buf -y`"
WORKDIR /workspace
"@ | Out-File -FilePath $FilePath -Encoding utf8
}

function Update-Makefile {
    param (
        [string]$MakefilePath
    )

    $makefileContent = Get-Content -Path $MakefilePath -Raw
    $updatedContent = $makefileContent -replace 'protoImageName=ghcr.io/cosmos/proto-builder:\$\(protoVer\)', 'protoImageName=local/proto-builder:latest'
    $updatedContent | Out-File -FilePath $MakefilePath -Encoding utf8
}

Set-Dockerfile -FilePath "$env:SRC_DIR/Dockerfile"
Get-Content -Path "$env:SRC_DIR/Dockerfile" -Raw

docker build -t local/proto-builder:latest $env:SRC_DIR

Update-Makefile -MakefilePath "$env:SRC_DIR/Makefile"
