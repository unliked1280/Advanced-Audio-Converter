# Source Availability

This package contains the application source code and build scripts for Advanced Audio Converter OldWin Edition.

## Application source

```text
src/audio_converter_pyqt4_oldwin_v0136c_prestable.py
```

## Build scripts

```text
packaging/FULL_BUILD_OLDWIN_v0136c_PRESTABLE_UNIFIED_INSTALLER.ps1
packaging/FULL_BUILD_OLDWIN_v0136c_PRESTABLE_UNIFIED_INSTALLER.bat
packaging/build_oldwin_pyqt4_v0136c_prestable_unified_onedir.bat
packaging/prepare_setup_payload_oldwin_v0136c_prestable.bat
packaging/Advanced_Audio_Converter_OldWin_Inno5_v0136c_prestable_unified_setup_data.iss
```

## Third-party runtime components

The binary installer may include:

```text
Python 3.4.x runtime
PyQt4 4.11.4
Qt 4.8.7
PyInstaller bootloader
FFmpeg 3.0 win32 static
FFprobe 3.0 win32 static
Inno Setup generated uninstaller
```

See:

```text
THIRD_PARTY_NOTICES_OLDWIN.txt
licenses/THIRD_PARTY_NOTICES_OLDWIN.txt
```

## FFmpeg source note

The tested OldWin package used FFmpeg 3.0 win32 static binaries with GPL-related configuration flags:

```text
--enable-gpl
--enable-version3
```

Treat bundled FFmpeg/FFprobe binaries as GPL-covered unless replaced with a verified LGPL-only build.

For binary releases, provide corresponding FFmpeg source/build information for the exact binary distributed.
