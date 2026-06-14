$ErrorActionPreference = "Stop"

Write-Host "Advanced Audio Converter OldWin - 0.13.6c pre-stable Unified Installer"
Set-Location "C:\AudioConverter_XP"

$python = "C:\Python34\python.exe"
$iscc = "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
if (!(Test-Path $iscc)) {
    $iscc = "C:\Program Files\Inno Setup 5\ISCC.exe"
}

$required = @(
    $python,
    $iscc,
    ".\audio_converter_pyqt4_oldwin_v0136ca_prestable.py",
    ".\prepare_setup_payload_oldwin_v0136ca_prestable.bat",
    ".\build_oldwin_pyqt4_v0136ca_prestable_unified_onedir.bat",
    ".\Advanced_Audio_Converter_OldWin_Inno5_v0136ca_prestable_unified_setup_data.iss",
    ".\INSTALL_MINIMUM_REQUIREMENTS_OLDWIN.txt",
    ".\icon.ico",
    ".\LICENSE_MIT_Advanced_Audio_Converter_OldWin.txt",
    ".\THIRD_PARTY_NOTICES_OLDWIN.txt",
    ".\ffmpeg\ffmpeg.exe",
    ".\ffmpeg\ffprobe.exe"
)

foreach ($p in $required) {
    if (!(Test-Path $p)) {
        throw "Missing required file: $p"
    }
}

cmd /c ".\build_oldwin_pyqt4_v0136ca_prestable_unified_onedir.bat"
if ($LASTEXITCODE -ne 0) { throw "Runtime build failed." }

if (!(Test-Path ".\dist\Advanced_Audio_Converter_OldWin\INSTALL_MINIMUM_REQUIREMENTS.txt")) {
    throw "Minimum requirements file missing from dist."
}
if (!(Test-Path ".\dist\Advanced_Audio_Converter_OldWin\licenses\INSTALL_LICENSE_ACCEPTANCE.txt")) {
    throw "License acceptance file missing from dist."
}

Remove-Item ".\installer_output_oldwin_unified" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item ".\release_setup_data_bundle_oldwin" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force ".\release_setup_data_bundle_oldwin" | Out-Null

& $iscc ".\Advanced_Audio_Converter_OldWin_Inno5_v0136ca_prestable_unified_setup_data.iss"
if ($LASTEXITCODE -ne 0) { throw "Inno Setup build failed." }

Copy-Item ".\installer_output_oldwin_unified\setup.exe" ".\release_setup_data_bundle_oldwin\setup.exe" -Force
Copy-Item ".\installer_output_oldwin_unified\setup-1.bin" ".\release_setup_data_bundle_oldwin\setup-1.bin" -Force

@"
Advanced Audio Converter OldWin 0.13.6c pre-stable unified installer

Keep setup.exe and setup-1.bin together.
Do not rename setup-1.bin.
Run setup.exe.

Target:
  Windows XP SP3 x86
  Windows 7/8/10 32-bit
  Windows 7/8/10/11 64-bit via WOW64

Minimum RAM:
  384 MB absolute minimum
  512 MB recommended minimum
"@ | Set-Content ".\release_setup_data_bundle_oldwin\README_INSTALL.txt" -Encoding Default

Write-Host "DONE:"
Write-Host "C:\AudioConverter_XP\release_setup_data_bundle_oldwin"
Get-ChildItem ".\release_setup_data_bundle_oldwin"
