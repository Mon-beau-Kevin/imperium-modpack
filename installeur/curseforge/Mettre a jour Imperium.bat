@echo off
title Mise a jour du modpack Imperium
cd /d "%~dp0"
set "PACK=https://raw.githubusercontent.com/Mon-beau-Kevin/imperium-modpack/main/pack.toml"

if not exist "packwiz-installer-bootstrap.jar" (
  echo Le fichier packwiz-installer-bootstrap.jar est introuvable.
  echo Remets les deux fichiers de la mise a jour dans le dossier de ton instance Imperium.
  pause
  exit /b 1
)

rem --- On cherche Java : d'abord celui installe par CurseForge, sinon celui de l'ordinateur ---
set "JAVA="
for /d %%D in ("%~dp0..\..\Install\runtime\*") do if not defined JAVA if exist "%%~D\bin\java.exe" set "JAVA=%%~D\bin\java.exe"
for /d %%D in ("%USERPROFILE%\curseforge\minecraft\Install\runtime\*") do if not defined JAVA if exist "%%~D\bin\java.exe" set "JAVA=%%~D\bin\java.exe"
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
echo Imperium est a jour ! Tu peux lancer le jeu depuis CurseForge.
timeout /t 5 >nul
