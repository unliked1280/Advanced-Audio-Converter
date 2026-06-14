# Third-Party Licenses

Advanced Audio Converter uses third-party software components.  
Each third-party component remains the property of its original authors and is distributed under its own license terms.

This file is intended as a notice for users and contributors. It is not a full legal analysis.

## FFmpeg / FFprobe

Component: FFmpeg and FFprobe  
Website: https://ffmpeg.org/  
License: LGPL-2.1-or-later or GPL-2.0-or-later, depending on the specific build configuration

FFmpeg and FFprobe are used for audio decoding, encoding, probing, and conversion.

Advanced Audio Converter calls FFmpeg and FFprobe as external executable tools. FFmpeg and FFprobe are separate third-party programs and are not owned by this project.

The exact FFmpeg license depends on how the bundled or user-provided FFmpeg binary was built. FFmpeg is generally licensed under LGPL-2.1-or-later, but builds that include GPL components are covered by GPL-2.0-or-later.

## Python

Component: Python  
Version used in OldWin builds: Python 3.4.x  
Website: https://www.python.org/  
License: Python Software Foundation License

Python is used as the runtime environment for packaged builds of the application.

## Qt

Component: Qt  
Version used in OldWin builds: Qt 4.8.x  
Website: https://www.qt.io/  
License: LGPL and/or commercial license, depending on distribution terms

Qt is used as the graphical user interface toolkit foundation.

## PyQt

Component: PyQt4  
Version used in OldWin builds: PyQt 4.11.x  
Website: https://riverbankcomputing.com/software/pyqt/  
License: GPL or commercial license

PyQt4 provides Python bindings for Qt and is used by the OldWin legacy GUI build.

## Notes

This project may support using user-provided FFmpeg and FFprobe binaries instead of bundled ones.

Third-party components are not re-licensed by Advanced Audio Converter. Their original license terms continue to apply.

For exact license texts and additional details, refer to the official websites and license files of the respective projects.
