function Update-Makefile {
    param (
        [string]$MakefilePath
    )

    $makefileContent = Get-Content -Path $MakefilePath -Raw
    $updatedContent = $makefileContent -replace 'protoImageName=ghcr.io/cosmos/proto-builder:\$\(protoVer\)', 'protoImageName=local/proto-builder:latest'
    $updatedContent | Out-File -FilePath $MakefilePath -Encoding utf8
}

Copy-Item -Path "$env:RECIPE_DIR/helpers/Dockerfile.windows" -Destination "$env:SRC_DIR/Dockerfile" -Force

Get-Content -Path "$env:SRC_DIR/Dockerfile" -Raw

docker build -t local/proto-builder:latest $env:SRC_DIR

Update-Makefile -MakefilePath "$env:SRC_DIR/Makefile"
