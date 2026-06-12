@echo off
setlocal
if exist venv\Scripts\python.exe (
    echo Using virtual environment Python from venv
    venv\Scripts\python.exe -m streamlit run app.py
) else (
    echo Virtual environment not found.
    echo Create one with: python -m venv venv
    echo Then install dependencies with: venv\Scripts\python.exe -m pip install -r requirements.txt
)
endlocal
