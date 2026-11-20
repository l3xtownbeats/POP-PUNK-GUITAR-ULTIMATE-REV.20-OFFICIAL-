@echo off
setlocal
cd /d "%~dp0"
if not exist reports\build_verification mkdir reports\build_verification
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

py -3.11 -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
py -3.11 -m pip install -r requirements-build.txt
if errorlevel 1 exit /b 1

echo [1/5] Compile Manager Python modules...
py -3.11 -m compileall -q . > reports\build_verification\compile.log 2>&1
if errorlevel 1 (
  type reports\build_verification\compile.log
  exit /b 1
)

echo [2/5] Run complete Manager regression suite...
py -3.11 -m unittest discover -v -p "test_*.py" > reports\build_verification\tests.log 2>&1
if errorlevel 1 (
  type reports\build_verification\tests.log
  exit /b 1
)
type reports\build_verification\tests.log

echo [3/5] Build Windows x64 onedir application...
py -3.11 -m PyInstaller --noconfirm --clean --windowed --onedir --name POP_PUNK_GUITAR_LIBRARY_MANAGER --paths . --add-data "ppgu_skin;ppgu_skin" --add-data "PORTABLE_USER_GUIDE_RU.md;." --collect-all soundfile --collect-all _soundfile_data manager_gui.py
if errorlevel 1 exit /b 1
if not exist "dist\POP_PUNK_GUITAR_LIBRARY_MANAGER\POP_PUNK_GUITAR_LIBRARY_MANAGER.exe" exit /b 1

echo [4/5] Mark and smoke-test relocatable Portable mode...
powershell -NoProfile -Command "[guid]::NewGuid().ToString('N') | Set-Content -NoNewline 'dist\POP_PUNK_GUITAR_LIBRARY_MANAGER\portable.mode'"
if errorlevel 1 exit /b 1
powershell -NoProfile -Command "$exe='dist\POP_PUNK_GUITAR_LIBRARY_MANAGER\POP_PUNK_GUITAR_LIBRARY_MANAGER.exe'; $p=Start-Process -FilePath (Resolve-Path $exe).Path -PassThru; Start-Sleep -Seconds 5; $p.Refresh(); if($p.HasExited){throw ('Portable startup failed: '+$p.ExitCode)}; Stop-Process -Id $p.Id -Force; if(!(Test-Path 'dist\POP_PUNK_GUITAR_LIBRARY_MANAGER\UserData')){throw 'Portable UserData was not created'}"
if errorlevel 1 exit /b 1
if exist "dist\POP_PUNK_GUITAR_LIBRARY_MANAGER\UserData" rmdir /s /q "dist\POP_PUNK_GUITAR_LIBRARY_MANAGER\UserData"

echo [5/5] Create Portable ZIP and optional Installer EXE...
powershell -NoProfile -Command "$zip='dist\POP_PUNK_GUITAR_LIBRARY_MANAGER-windows-x64.zip'; Compress-Archive -Path 'dist\POP_PUNK_GUITAR_LIBRARY_MANAGER' -DestinationPath $zip -Force; if(!(Test-Path $zip) -or (Get-Item $zip).Length -lt 1MB){throw 'Portable ZIP missing or unexpectedly small'}; $entries=tar -tf $zip; if($LASTEXITCODE -ne 0){throw 'Cannot inspect Portable ZIP'}; foreach($required in @('POP_PUNK_GUITAR_LIBRARY_MANAGER.exe','python311.dll','portable.mode','PORTABLE_USER_GUIDE_RU.md','ppgu_skin/theme.json','ppgu_skin/assets/hero.png')){if(!($entries -match [regex]::Escape($required))){throw ('Portable ZIP missing required entry: '+$required)}}; if($entries -match 'UserData/'){throw 'Portable ZIP contains smoke-test user data'}"
if errorlevel 1 exit /b 1
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
  "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" "%~dp0POP_PUNK_GUITAR_LIBRARY_MANAGER.iss"
  if errorlevel 1 exit /b 1
  if not exist "dist\installer\POP-PUNK-GUITAR-LIBRARY-MANAGER-Setup-Windows-x64.exe" (
    echo ERROR: Installer compiler exited without producing the expected EXE.
    exit /b 1
  )
  for %%A in ("dist\installer\POP-PUNK-GUITAR-LIBRARY-MANAGER-Setup-Windows-x64.exe") do if %%~zA LSS 1048576 (
    echo ERROR: Installer EXE is unexpectedly small.
    exit /b 1
  )
) else (
echo Inno Setup not found. Portable ZIP is ready; install Inno Setup to build installer EXE.
)
echo.
echo BUILD FINISHED.
echo Test log: %~dp0reports\build_verification\tests.log
echo Compile log: %~dp0reports\build_verification\compile.log
echo Portable ZIP: %~dp0dist\POP_PUNK_GUITAR_LIBRARY_MANAGER-windows-x64.zip
if exist "dist\installer\POP-PUNK-GUITAR-LIBRARY-MANAGER-Setup-Windows-x64.exe" echo Installer: %~dp0dist\installer\POP-PUNK-GUITAR-LIBRARY-MANAGER-Setup-Windows-x64.exe
endlocal
