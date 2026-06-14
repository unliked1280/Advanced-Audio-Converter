@echo off
setlocal EnableExtensions

echo ============================================================
echo Advanced Audio Converter OldWin - PyQt4 0.13.6c pre-stable unified runtime
echo Runtime: 32-bit OldWin/XP-compatible
echo ============================================================

cd /d "%~dp0"

set PYTHON=C:\Python34\python.exe
set APP=audio_converter_pyqt4_oldwin_v0136ca_prestable.py
set NAME=Advanced_Audio_Converter_OldWin

if not exist "%PYTHON%" (
    echo ERROR: Python 3.4 x86 not found at %PYTHON%
    exit /b 1
)

if not exist "%APP%" (
    echo ERROR: Missing %APP%
    exit /b 1
)

if not exist "icon.ico" (
    echo ERROR: Missing icon.ico
    exit /b 1
)

if not exist "ffmpeg\ffmpeg.exe" (
    echo ERROR: Missing ffmpeg\ffmpeg.exe
    exit /b 1
)

if not exist "ffmpeg\ffprobe.exe" (
    echo ERROR: Missing ffmpeg\ffprobe.exe
    exit /b 1
)

"%PYTHON%" -c "from PyQt4 import QtCore, QtGui; print('PyQt4 OK', QtCore.PYQT_VERSION_STR, QtCore.QT_VERSION_STR)"
if errorlevel 1 (
    echo ERROR: PyQt4 check failed.
    exit /b 1
)

"%PYTHON%" -m PyInstaller --version
if errorlevel 1 (
    echo ERROR: PyInstaller check failed.
    exit /b 1
)

echo Cleaning old build folders...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q "%NAME%.spec" 2>nul

echo Building PyInstaller onedir...
"%PYTHON%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onedir ^
    --windowed ^
    --name "%NAME%" ^
    --icon "icon.ico" ^
    --add-binary "ffmpeg\ffmpeg.exe;ffmpeg" ^
    --add-binary "ffmpeg\ffprobe.exe;ffmpeg" ^
    --exclude-module wx ^
    --exclude-module PySide6 ^
    --exclude-module PyQt5 ^
    --exclude-module tkinter ^
    "%APP%"

if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    exit /b 1
)

if not exist "dist\%NAME%\%NAME%.exe" (
    echo ERROR: EXE was not created.
    exit /b 1
)

call prepare_setup_payload_oldwin_v0136ca_prestable.bat
if errorlevel 1 (
    echo ERROR: payload preparation failed.
    exit /b 1
)

echo.
echo Runtime build OK:
echo dist\%NAME%\%NAME%.exe
echo.
endlocal
