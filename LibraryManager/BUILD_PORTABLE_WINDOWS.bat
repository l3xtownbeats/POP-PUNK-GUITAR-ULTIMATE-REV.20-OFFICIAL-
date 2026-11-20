@echo off
setlocal
cd /d "%~dp0"
py -3.11 -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
py -3.11 -m pip install -r requirements-build.txt
if errorlevel 1 exit /b 1
py -3.11 -m PyInstaller --noconfirm --clean --windowed --onedir --name POP_PUNK_GUITAR_LIBRARY_MANAGER --paths . --collect-all soundfile --collect-all _soundfile_data manager_gui.py
if errorlevel 1 exit /b 1
echo.
echo Build completed: %~dp0dist\POP_PUNK_GUITAR_LIBRARY_MANAGER
echo Copy the entire folder to the target Windows PC.
endlocal
