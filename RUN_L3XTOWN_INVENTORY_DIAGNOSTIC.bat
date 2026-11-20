@echo off
setlocal
title L3XTOWN INVENTORY - DIAGNOSTIC RUN
set "LOG=%~dp0L3XTOWN_RUN_LOG.txt"
echo ============================================================ 
echo L3XTOWN INVENTORY - DIAGNOSTIC RUN
echo Log: "%LOG%"
echo ============================================================
echo.
if not exist "%~dp0RUN_L3XTOWN_FULL_INVENTORY.bat" (
  echo ERROR: RUN_L3XTOWN_FULL_INVENTORY.bat is missing beside this diagnostic file.
  >"%LOG%" echo ERROR: RUN_L3XTOWN_FULL_INVENTORY.bat is missing.
  goto :finish
)
echo Running the current inventory BAT. Output is being captured...
call "%~dp0RUN_L3XTOWN_FULL_INVENTORY.bat" > "%LOG%" 2>&1
set "RC=%ERRORLEVEL%"
echo.
echo Inventory BAT returned exit code: %RC%
echo.
echo ---------------- CAPTURED OUTPUT ----------------
type "%LOG%"
echo.
echo --------------------------------------------------
echo Diagnostic log saved as:
echo "%LOG%"
:finish
echo.
echo This window will remain open. Press any key to close.
pause >nul
endlocal
