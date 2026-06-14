@echo off
setlocal
cd /d "%~dp0"

set DIST=dist\Advanced_Audio_Converter_OldWin
if not exist "%DIST%" (
    echo ERROR: %DIST% not found. Build first.
    exit /b 1
)

echo Preparing minimal runtime payload for Advanced Audio Converter OldWin...

rem Do not ship build/install tools inside the installed application.
del /q "%DIST%\*.ps1" 2>nul
del /q "%DIST%\*.bat" 2>nul
del /q "%DIST%\*.spec" 2>nul
del /q "%DIST%\PyQt4-*.exe" 2>nul
del /q "%DIST%\python-*.msi" 2>nul
del /q "%DIST%\innosetup-*.exe" 2>nul

mkdir "%DIST%\licenses" 2>nul

if not exist "LICENSE_MIT_Advanced_Audio_Converter_OldWin.txt" (
    echo ERROR: LICENSE_MIT_Advanced_Audio_Converter_OldWin.txt not found.
    exit /b 1
)

if not exist "THIRD_PARTY_NOTICES_OLDWIN.txt" (
    echo ERROR: THIRD_PARTY_NOTICES_OLDWIN.txt not found.
    exit /b 1
)

if not exist "INSTALL_MINIMUM_REQUIREMENTS_OLDWIN.txt" (
    echo ERROR: INSTALL_MINIMUM_REQUIREMENTS_OLDWIN.txt not found.
    exit /b 1
)

echo INSTALLER LICENSE ACCEPTANCE>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo Advanced Audio Converter OldWin>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo Version: 0.13.6c pre-stable OldWin packaging line>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo Before installing Advanced Audio Converter OldWin, you must accept the license terms below.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo Summary:>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo - Application source code: MIT License.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo - Binary package includes third-party runtime components.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo - PyQt4 GPL and the tested GPL-enabled FFmpeg build require GPL-aware redistribution.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo - This notice is informational and is not legal advice.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo ===============================================================================>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo PART 1: ADVANCED AUDIO CONVERTER OLDWIN - MIT LICENSE>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo ===============================================================================>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
type "LICENSE_MIT_Advanced_Audio_Converter_OldWin.txt" >> "%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo ===============================================================================>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo PART 2: THIRD-PARTY NOTICES>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo ===============================================================================>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
echo.>>"%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
type "THIRD_PARTY_NOTICES_OLDWIN.txt" >> "%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"

copy /y icon.ico "%DIST%\icon.ico" >nul
copy /y LICENSE_MIT_Advanced_Audio_Converter_OldWin.txt "%DIST%\licenses\LICENSE_MIT.txt" >nul
copy /y THIRD_PARTY_NOTICES_OLDWIN.txt "%DIST%\licenses\THIRD_PARTY_NOTICES.txt" >nul
copy /y INSTALL_MINIMUM_REQUIREMENTS_OLDWIN.txt "%DIST%\INSTALL_MINIMUM_REQUIREMENTS.txt" >nul

if exist "README_OLDWIN_v0107_UNIFIED_INSTALLER.txt" (
    copy /y README_OLDWIN_v0107_UNIFIED_INSTALLER.txt "%DIST%\README.txt" >nul
)

if exist "%DIST%\licenses\INSTALL_LICENSE_ACCEPTANCE.txt" (
    echo Installer license acceptance file: OK
) else (
    echo ERROR: INSTALL_LICENSE_ACCEPTANCE.txt was not created.
    exit /b 1
)

if exist "%DIST%\INSTALL_MINIMUM_REQUIREMENTS.txt" (
    echo Minimum requirements file: OK
) else (
    echo ERROR: INSTALL_MINIMUM_REQUIREMENTS.txt was not copied.
    exit /b 1
)

if exist "%DIST%\ffmpeg\ffmpeg.exe" (
    echo FFmpeg runtime: OK
) else (
    echo ERROR: bundled ffmpeg missing in payload.
    exit /b 1
)

if exist "%DIST%\ffmpeg\ffprobe.exe" (
    echo FFprobe runtime: OK
) else (
    echo ERROR: bundled ffprobe missing in payload.
    exit /b 1
)

if exist "%DIST%\Advanced_Audio_Converter_OldWin.exe" (
    echo App EXE: OK
) else (
    echo ERROR: app exe missing in payload.
    exit /b 1
)

echo OldWin payload prepared: %DIST%
endlocal
