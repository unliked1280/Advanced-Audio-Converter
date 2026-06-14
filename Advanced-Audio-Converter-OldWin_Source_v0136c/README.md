# Advanced Audio Converter OldWin Edition

Advanced Audio Converter OldWin Edition is a legacy-compatible Windows audio converter build.

Current source package:

```text
0.13.6c pre-stable OldWin Legacy PyQt4
```

## Target systems

- Windows XP SP3 x86 minimum
- Windows Vista x86/x64
- Windows 7 x86/x64
- Windows 8 / 8.1 x86/x64
- Windows 10 x86/x64
- Windows 11 x64 through 32-bit runtime compatibility

The runtime is 32-bit x86. On 64-bit Windows it runs through WOW64.

## Tested legacy stack

```text
Python 3.4.4 x86
PyQt4 4.11.4
Qt 4.8.7
PyInstaller 3.4
FFmpeg 3.0 win32 static
Inno Setup 5.6.1
```

## Layout

```text
src/          application source
packaging/    build and installer scripts
docs/         build notes, bugsearch, minimum requirements
assets/       icon/assets
licenses/     project and third-party license notes
third_party/  third-party source availability notes
```

## Build

Expected local build root:

```powershell
C:\AudioConverter_XP
```

Run:

```powershell
cd C:\AudioConverter_XP
powershell -ExecutionPolicy Bypass -File .\FULL_BUILD_OLDWIN_v0136c_PRESTABLE_UNIFIED_INSTALLER.ps1
```

Final output:

```text
release_setup_data_bundle_oldwin/
  setup.exe
  setup-1.bin
  README_INSTALL.txt
```

## License and AI disclosure

The original application source is MIT licensed. The complete binary package may include GPL/LGPL/PSF/other third-party components. See `THIRD_PARTY_NOTICES_OLDWIN.txt` and `SOURCE_AVAILABILITY.md`.

Parts of this project were created, reviewed, or refactored with assistance from AI tools.
