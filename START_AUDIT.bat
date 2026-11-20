@echo off
chcp 65001 >nul
setlocal
 title POP PUNK GUITAR ULTIMATE - Acoustic Audit
set "PYTHON=%LOCALAPPDATA%\PythonPortable\python.exe"
set "SCRIPT=%USERPROFILE%\Desktop\acoustic_signal_audit.py"

echo ==================================================
echo POP PUNK GUITAR ULTIMATE - ACOUSTIC SIGNAL AUDIT
echo ==================================================
echo.

if not exist "%PYTHON%" (
  echo ERROR: Python not found: "%PYTHON%"
  pause
  exit /b 1
)
if not exist "%SCRIPT%" (
  echo ERROR: Script not found: "%SCRIPT%"
  pause
  exit /b 1
)

echo Preparing script safely...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=$env:USERPROFILE+'\Desktop\acoustic_signal_audit.py'; $lines=Get-Content -LiteralPath $p; $i=[Array]::IndexOf($lines,'import wave'); if($i -lt 0){Write-Host 'ERROR: Python start not found; file left unchanged.' -ForegroundColor Red; exit 2}; if($i -gt 0){$tmp=$p+'.cleaning'; [System.IO.File]::WriteAllLines($tmp,[string[]]$lines[$i..($lines.Count-1)],[System.Text.UTF8Encoding]::new($false)); Move-Item -LiteralPath $tmp -Destination $p -Force}; Write-Host 'Script ready.' -ForegroundColor Green"
if errorlevel 1 (
  echo.
  echo Preparation failed. Original WAV files were not changed.
  pause
  exit /b 1
)

echo.
echo Running audit. Keep this window open.
echo Original WAV files are read, not modified.
echo.
"%PYTHON%" "%SCRIPT%"
set "RC=%ERRORLEVEL%"
echo.
echo ==================================================
if "%RC%"=="0" (
  echo Audit process completed. Check Desktop for CSV and TXT reports.
) else (
  echo Audit returned error code %RC%.
)
echo ==================================================
pause
exit /b %RC%
