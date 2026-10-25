@echo off
title Mise a jour du modpack Imperium
cd /d "%~dp0"
set "PACK=https://raw.githubusercontent.com/Mon-beau-Kevin/imperium-modpack/main/pack.toml"
rem --- Dernier commit sur GitHub : on telecharge le pack fige a ce commit (evite les copies en cache a moitie a jour) ---
set "SHA="
for /f "usebackq delims=" %%S in (`powershell -NoProfile -ExecutionPolicy Bypass -Command "try { (Invoke-RestMethod -Uri 'https://api.github.com/repos/Mon-beau-Kevin/imperium-modpack/commits/main' -Headers @{Accept='application/vnd.github.sha'} -TimeoutSec 10).Trim() } catch { '' }"`) do set "SHA=%%S"
if defined SHA set "PACK=https://raw.githubusercontent.com/Mon-beau-Kevin/imperium-modpack/%SHA%/pack.toml"

if not exist "packwiz-installer-bootstrap.jar" (
  echo Le fichier packwiz-installer-bootstrap.jar est introuvable.
  echo Remets les deux fichiers de la mise a jour dans le dossier de ton instance Imperium.
  pause
  exit /b 1
)

rem --- On cherche Java : d'abord celui installe par CurseForge, sinon celui de l'ordinateur ---
set "JAVA="
for %%C in ("%~dp0..\..\Install" "%USERPROFILE%\curseforge\minecraft\Install") do (
  for /d %%D in ("%%~C\java\*") do if not defined JAVA if exist "%%~D\bin\java.exe" set "JAVA=%%~D\bin\java.exe"
  for /d %%D in ("%%~C\runtime\*") do (
    if not defined JAVA if exist "%%~D\bin\java.exe" set "JAVA=%%~D\bin\java.exe"
    for /d %%E in ("%%~D\windows-x64\*") do if not defined JAVA if exist "%%~E\bin\java.exe" set "JAVA=%%~E\bin\java.exe"
  )
)
if not defined JAVA (
  where java >nul 2>nul && set "JAVA=java"
)
if not defined JAVA (
  echo Java est introuvable. Lance une fois le jeu depuis CurseForge, puis reessaie.
  pause
  exit /b 1
)

echo ============================================
echo    Mise a jour du modpack Imperium...
echo ============================================
echo.
"%JAVA%" -jar packwiz-installer-bootstrap.jar -s client "%PACK%"
if errorlevel 1 (
  echo.
  echo La mise a jour a echoue. Verifie ta connexion internet et reessaie.
  pause
  exit /b 1
)
echo.
echo Imperium est a jour !
set "CF="
set "CFOW="
for %%P in ("%LOCALAPPDATA%\Programs\CurseForge Windows\CurseForge.exe" "%ProgramFiles%\CurseForge Windows\CurseForge.exe") do if not defined CF if exist "%%~P" set "CF=%%~P"
set "OW=%ProgramFiles(x86)%\Overwolf\OverwolfLauncher.exe"
if not defined CF if exist "%OW%" set "CFOW=1"
if defined CF start "" "%CF%"
if defined CFOW start "" "%OW%" -launchapp cchhcaiapeikjbdbpfplgmpobbcdkdaphclbmkbj -from-desktop
if defined CF echo CurseForge s'ouvre : clique sur Jouer.
if defined CFOW echo CurseForge s'ouvre : clique sur Jouer.
if not defined CF if not defined CFOW echo Relance le jeu depuis CurseForge.
timeout /t 8 >nul
exit
