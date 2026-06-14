Advanced Audio Converter OldWin - 0.13.6c pre-stable polish hotfix

Changes from 0.13.6b:
  - Dark theme manual fallback default is now OFF on clean install.
    Follow Windows theme remains ON by default, so manual dark is only a fallback.
  - System information output is polished:
      GenuineIntel / AuthenticAMD are not printed as ugly vendor prefixes.
      Intel(R) / Core(TM) / CPU strings are cleaned.
      Micro-Star International Co., Ltd. is shortened to MSI.
      RAM summary is shorter and cleaner.

Example polished output:
  Computer: MSI MS-7C89
  CPU: Intel Core i5-10400F @ 2.90 GHz
  CPU cores/threads: 6 cores / 12 threads
  CPU clock: 2.90 GHz current | 2.90 GHz nominal/max | overclock: not detected
  RAM: 16 GB total | Transcend | 2667 MHz
  RAM module 1: 16 GB | Transcend | 2667 MHz

Build:
  cd C:\AudioConverter_XP
  powershell -ExecutionPolicy Bypass -File .\FULL_BUILD_OLDWIN_v0136c_PRESTABLE_UNIFIED_INSTALLER.ps1
