# Run snippet editor dialog tests
$env:PYTHONPATH = $PWD

Write-Host "Running snippet editor dialog tests..." -ForegroundColor Cyan
& .venv\Scripts\pytest.exe tests/test_snippet_editor_dialog.py -v --tb=short
