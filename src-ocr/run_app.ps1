$venvPython = Join-Path $PSScriptRoot 'venv\Scripts\python.exe'
if (Test-Path $venvPython) {
    Write-Host "Using virtual environment Python from venv"
    & $venvPython -m streamlit run "$PSScriptRoot\app.py"
} else {
    Write-Host "Virtual environment not found." -ForegroundColor Yellow
    Write-Host "Create one with: python -m venv venv"
    Write-Host "Then install dependencies with: venv\Scripts\python.exe -m pip install -r requirements.txt"
}
