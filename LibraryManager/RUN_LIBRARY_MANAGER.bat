@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3.10 --version >nul 2>nul
  if not errorlevel 1 (py -3.10 "%~dp0library_manager.py" %* & goto :done)
  py -3 --version >nul 2>nul
  if not errorlevel 1 (py -3 "%~dp0library_manager.py" %* & goto :done)
)
where python >nul 2>nul
if not errorlevel 1 (
  python --version
  python "%~dp0library_manager.py" %*
  goto :done
)
echo Python 3.10 or newer was not found. Install Python and enable Add Python to PATH.
pause
exit /b 2
:done
echo.
pause
