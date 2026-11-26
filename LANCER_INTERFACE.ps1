$ErrorActionPreference = 'Stop'
$taskPython = (Get-Command python -ErrorAction Stop).Source
if (-not (Test-Path -LiteralPath $taskPython)) {
    throw 'Python my_env introuvable. Adapter taskPython dans ce lanceur.'
}
Set-Location -LiteralPath $PSScriptRoot
& $taskPython -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502 --server.headless true --browser.gatherUsageStats false
