# This script helps to set everything up for your to start working
# Always run this script if you dont see a (venv) at the start of the prompt

cd .\capybara_clean
git pull

if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Output "Virtual environment not found. Creating one..."
    python -m venv .\venv
}
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
