@echo off
setlocal EnableExtensions

echo ============================================================
echo Advanced Audio Converter OldWin - 0.11.1 PRE-STABLE UNIFIED INSTALLER
echo One setup.exe + setup-1.bin for XP/Win7/8/10/11
echo Runtime: 32-bit OldWin/XP-compatible
echo ============================================================

cd /d "%~dp0"

set PYTHON=C:\Python34\python.exe
set ISCC_X86=C:\Program Files (x86)\Inno Setup 5\ISCC.exe
set ISCC_X64=C:\Program Files\Inno Setup 5\ISCC.exe
set BUILD_BAT=build_oldwin_pyqt4_v0136ca_prestable_unified_onedir.bat
set ISS=Advanced_Audio_Converter_OldWin_Inno5_v0136ca_prestable_unified_setup_data.iss
set OUT=installer_output_oldwin_unified
set RELEASE=release_setup_data_bundle_oldwin

if not exist "%PYTHON%" (
    echo ERROR: Python 3.4 x86 not found.
    exit /b 1
)

set ISCC=
if exist "%ISCC_X86%" set ISCC=%ISCC_X86%
if exist "%ISCC_X64%" set ISCC=%ISCC_X64%

if "%ISCC%"=="" (
    echo ERROR: Inno Setup 5 ISCC.exe not found.
    exit /b 1
)

if not exist "%BUILD_BAT%" (
    echo ERROR: Missing %BUILD_BAT%
    exit /b 1
)

if not exist "%ISS%" (
    echo ERROR: Missing %ISS%
    exit /b 1
)

if not exist "INSTALL_MINIMUM_REQUIREMENTS_OLDWIN.txt" (
    echo ERROR: Missing INSTALL_MINIMUM_REQUIREMENTS_OLDWIN.txt
    exit /b 1
)

echo.
echo [1/4] Building runtime...
call "%BUILD_BAT%"
if errorlevel 1 (
    echo ERROR: runtime build failed.
    exit /b 1
)

if not exist "dist\Advanced_Audio_Converter_OldWin\Advanced_Audio_Converter_OldWin.exe" (
    echo ERROR: app exe missing from dist.
    exit /b 1
)

if not exist "dist\Advanced_Audio_Converter_OldWin\INSTALL_MINIMUM_REQUIREMENTS.txt" (
    echo ERROR: minimum requirements file missing from dist.
    exit /b 1
)

if not exist "dist\Advanced_Audio_Converter_OldWin\licenses\INSTALL_LICENSE_ACCEPTANCE.txt" (
    echo ERROR: license acceptance file missing from dist.
    exit /b 1
)

echo.
echo [2/4] Cleaning installer outputs...
rmdir /s /q "%OUT%" 2>nul
rmdir /s /q "%RELEASE%" 2>nul
mkdir "%RELEASE%" 2>nul

echo.
echo [3/4] Compiling unified installer...
"%ISCC%" "%ISS%"
if errorlevel 1 (
    echo ERROR: Inno Setup compilation failed.
    exit /b 1
)

if not exist "%OUT%\setup.exe" (
    echo ERROR: setup.exe missing.
    exit /b 1
)

if not exist "%OUT%\setup-1.bin" (
    echo ERROR: setup-1.bin missing.
    exit /b 1
)

echo.
echo [4/4] Creating release_setup_data_bundle_oldwin...
copy /y "%OUT%\setup.exe" "%RELEASE%\setup.exe" >nul
copy /y "%OUT%\setup-1.bin" "%RELEASE%\setup-1.bin" >nul

(
echo Advanced Audio Converter OldWin 0.13.6c pre-stable unified installer
echo.
echo Keep setup.exe and setup-1.bin together.
echo Do not rename setup-1.bin.
echo Run setup.exe.
echo.
echo Target:
echo   Windows XP SP3 x86
echo   Windows 7/8/10 32-bit
echo   Windows 7/8/10/11 64-bit via WOW64
echo.
echo Minimum RAM:
echo   384 MB absolute minimum
echo   512 MB recommended minimum
) > "%RELEASE%\README_INSTALL.txt"

dir "%RELEASE%"

echo.
echo ============================================================
echo DONE.
echo Final unified installer bundle:
echo   %CD%\%RELEASE%
echo ============================================================
endlocal
