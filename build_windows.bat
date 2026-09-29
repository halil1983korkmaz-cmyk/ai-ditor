@echo off
setlocal
cd /d "%~dp0"
python -m unittest discover -s tests -q
if errorlevel 1 exit /b 1
python -m PyInstaller gastroia_editor_windows.spec --noconfirm
if errorlevel 1 exit /b 1
iscc gastroia_editor_setup.iss
if errorlevel 1 exit /b 1
echo Ready: dist\GastroiaEditor_Setup.exe
