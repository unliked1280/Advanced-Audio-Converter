# Build Notes - OldWin

Expected local build root:

```text
C:\AudioConverter_XP
```

Required legacy stack:

```text
Python 3.4.4 x86
PyQt4 4.11.4 GPL for Python 3.4 / Qt 4.8.7 x86
PyInstaller 3.4
Inno Setup 5.6.1
FFmpeg 3.0 win32 static
```

Checks:

```powershell
C:\Python34\python.exe --version
C:\Python34\python.exe -c "from PyQt4 import QtCore, QtGui; print('PyQt4 OK', QtCore.PYQT_VERSION_STR, QtCore.QT_VERSION_STR)"
C:\Python34\python.exe -m PyInstaller --version
```

Build:

```powershell
cd C:\AudioConverter_XP
powershell -ExecutionPolicy Bypass -File .\FULL_BUILD_OLDWIN_v0136c_PRESTABLE_UNIFIED_INSTALLER.ps1
```
