# Helper script to run Quick Snippet Overlay with proper environment
$env:PYTHONPATH = $PWD
& .\.venv\Scripts\python.exe src\main.py
