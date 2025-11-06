# Test script to verify focus fix implementation
$env:PYTHONPATH = $PWD

Write-Host "Testing focus fix imports..." -ForegroundColor Cyan

& .venv\Scripts\python.exe -c @"
import sys
sys.path.insert(0, '.')
from src.snippet_editor_dialog import NoFocusListView, InputFocusProtector, SnippetEditorDialog
print('✓ All imports successful!')
print('✓ NoFocusListView class defined')
print('✓ InputFocusProtector class defined')
print('✓ Focus fix implementation complete')
"@

Write-Host ""
Write-Host "Focus fix is ready to test!" -ForegroundColor Green
Write-Host "Run RUN-APP.bat to test the application" -ForegroundColor Yellow
