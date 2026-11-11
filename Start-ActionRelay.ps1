param(
    [ValidateRange(1, 65535)]
    [int] $Port = 8000
)

$formPath = Join-Path $PSScriptRoot 'data/actionrelay-forms/IDNYC-application-English.pdf'
$expectedDigest = 'e4a56d635597d19c92ab5f02ea45c67f098d031a0088353b145fe2642e238248'
if (!(Test-Path -LiteralPath $formPath -PathType Leaf)) {
    throw 'The verified local IDNYC application PDF is missing.'
}
if ((Get-FileHash -LiteralPath $formPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedDigest) {
    throw 'The local IDNYC PDF does not match the approved file.'
}

Push-Location -LiteralPath $PSScriptRoot
try {
    $env:ACTIONRELAY_IDNYC_PDF = $formPath
    $env:ACTIONRELAY_IDNYC_SHA256 = $expectedDigest
$env:ACTIONRELAY_ENABLE_LIVE_TRIAGE = '1'
    & '.\.venv\Scripts\python.exe' -m uvicorn cdit_support_mao.main:app --app-dir src --host 127.0.0.1 --port $Port
    if ($LASTEXITCODE -ne 0) { throw "ActionRelay exited with code $LASTEXITCODE." }
} finally {
    Pop-Location
}
