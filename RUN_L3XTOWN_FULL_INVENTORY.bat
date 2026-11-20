@echo off
setlocal EnableExtensions
title L3XTOWN GUITAR - FULL PATH INVENTORY
set "LOG=%~dp0L3XTOWN_INVENTORY_RUN_LOG.txt"
set "SAMPLE_MAP=%~dp0L3XTOWN_SAMPLE_MAP.csv"
set "SCRIPT=%~dp0BUILD_L3XTOWN_INVENTORY.py"
set "LIBRARY_ROOT=F:\POP PUNK GUITAR ULTIMATE\Samples\SourceLibraries\L3XTOWN GUITAR"
set "PYTHON=%LOCALAPPDATA%\PythonPortable\python.exe"
set "RC=2"

echo ============================================================
echo L3XTOWN GUITAR - FULL PATH INVENTORY
echo READ-ONLY SCAN - NO AUDIO OR PLUGIN TESTS
echo ============================================================
echo.
> "%LOG%" echo L3XTOWN inventory started: %DATE% %TIME%

echo [1/4] Checking required files...
if not exist "%SAMPLE_MAP%" (
  echo ERROR: L3XTOWN_SAMPLE_MAP.csv is missing beside this BAT.
  >>"%LOG%" echo ERROR: Sample map missing beside BAT.
  goto :finish
)
if not exist "%SCRIPT%" (
  echo ERROR: BUILD_L3XTOWN_INVENTORY.py is missing beside this BAT.
  echo Download both files from the same GitHub folder.
  >>"%LOG%" echo ERROR: Python inventory script missing beside BAT.
  goto :finish
)
if not exist "%LIBRARY_ROOT%" (
  echo ERROR: Source library folder not found:
  echo "%LIBRARY_ROOT%"
  >>"%LOG%" echo ERROR: Source library folder not found.
  goto :finish
)

echo [2/4] Checking Python...
if exist "%PYTHON%" goto :python_ready
set "PYTHON="
where py >nul 2>nul
if not errorlevel 1 set "PYTHON=py"
if not defined PYTHON (
  echo ERROR: Python 3 was not found.
  echo Install Python 3 with the Windows "py" launcher, then run this BAT again.
  >>"%LOG%" echo ERROR: Python 3 / py launcher not found.
  goto :finish
)

:python_ready
echo [3/4] Starting read-only inventory.
echo This may take several minutes. Source WAV files will not be changed.
>>"%LOG%" echo Starting read-only inventory...

if /i "%PYTHON%"=="py" (
  py "%SCRIPT%" --root "%LIBRARY_ROOT%" --sample-map "%SAMPLE_MAP%" --out "%~dp0L3XTOWN_FULL_INVENTORY.csv" --report "%~dp0L3XTOWN_INVENTORY_RECONCILIATION.csv" >>"%LOG%" 2>&1
) else (
  "%PYTHON%" "%SCRIPT%" --root "%LIBRARY_ROOT%" --sample-map "%SAMPLE_MAP%" --out "%~dp0L3XTOWN_FULL_INVENTORY.csv" --report "%~dp0L3XTOWN_INVENTORY_RECONCILIATION.csv" >>"%LOG%" 2>&1
)
set "RC=%ERRORLEVEL%"

echo [4/4] Finished.
if "%RC%"=="0" (
  echo SUCCESS: Two CSV reports created beside this BAT.
  >>"%LOG%" echo SUCCESS: Inventory reports created.
) else (
  echo ERROR: Scan failed. Full details are in the log.
  >>"%LOG%" echo ERROR: Scan exit code %RC%.
)

:finish
echo.
echo Log: "%LOG%"
echo Window remains open. Press any key to close.
pause >nul
exit /b %RC%
