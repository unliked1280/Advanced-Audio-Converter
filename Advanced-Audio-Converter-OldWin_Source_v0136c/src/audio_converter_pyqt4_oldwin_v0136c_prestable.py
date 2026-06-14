# -*- coding: utf-8 -*-
"""
Advanced Audio Converter OldWin Legacy PyQt4 Edition
Version: 0.13.6c pre-stable OldWin Legacy PyQt4
Author: unliked1280
License: MIT

Windows XP SP3 x86 friendly port.
Runtime target: Python 3.4.x x86 + PyQt4 4.11.4 + Qt 4.8.7 + PyInstaller 3.4 + FFmpeg 3.0 win32 static.

This build keeps the audio conversion core but uses old Qt4/PyQt4 widgets instead of wxPython/PySide6.
"""
from __future__ import unicode_literals

import csv
import ctypes
import json
import locale
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from datetime import datetime

try:
    from PyQt4 import QtCore, QtGui
except Exception as exc:
    raise SystemExit("PyQt4 is required for XP PyQt4 build: %s" % exc)

try:
    import winsound
except Exception:
    winsound = None

try:
    import winreg
except Exception:
    winreg = None

APP_NAME = "Advanced Audio Converter OldWin"
APP_DISPLAY_NAME = "Advanced Audio Converter OldWin Edition"
APP_VERSION = "0.13.6c pre-stable OldWin Legacy PyQt4"
AUTHOR = "unliked1280"
LICENSE_NAME = "MIT License"
MIT_LICENSE_TEXT = """MIT License

Copyright (c) 2026 unliked1280

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
THIRD_PARTY_NOTICES_TEXT = """Third-party license notices

Advanced Audio Converter OldWin is released under the MIT License. The binary package also contains or is built with third-party components. Their licenses remain separate from the application license.

1. PyQt4 4.11.4 / Riverbank Computing
   License: GNU GPL v3 for the free edition, or a commercial Riverbank license.
   This XP build uses the GPL PyQt4 installer. Therefore, redistributed binaries should be treated as GPL-compatible/open-source distribution unless a commercial PyQt license is used.

2. Qt 4.8.7 / Qt Project / The Qt Company
   License family: LGPL/GPL/commercial depending on the exact Qt package and modules.
   This application uses Qt4 through PyQt4. Keep Qt DLL notices and license texts with redistributed binaries.

3. FFmpeg 3.0 win32 static
   License: FFmpeg is LGPL by default, but the bundled build used for XP was configured with --enable-gpl and --enable-version3. Treat the bundled ffmpeg.exe/ffprobe.exe as GPLv3-covered binaries and provide corresponding source/offers where required.

4. Python 3.4.x
   License: Python Software Foundation License.
   Python is used as the runtime for development/building and may be included by PyInstaller in frozen binaries.

5. PyInstaller 3.4
   License: GPL with the PyInstaller bootloader exception.
   PyInstaller is used only to build the frozen executable/onedir package.

6. 7-Zip, if used manually during packaging
   License: LGPL with unRAR restriction for some parts, depending on distributed files. 7-Zip is not bundled by this application package unless you add it yourself.

No warranty is provided. This notice is informational and is not legal advice. For final public releases, ship this notice together with the full license files of all redistributed components.
"""
CONFIG_FILE = "config_xp_pyqt4.json"
RECOVERY_FILE = "recovery_xp_pyqt4.json"

CREATE_NO_WINDOW = 0
if sys.platform == "win32":
    try:
        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
    except Exception:
        CREATE_NO_WINDOW = 0x08000000

AUDIO_EXTENSIONS = set([
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".opus",
    ".aiff", ".alac", ".webm", ".mp4", ".mkv", ".ape", ".mpc",
    ".tta", ".wv", ".amr", ".ac3", ".dts", ".3gp", ".caf", ".ra", ".rm", ".mka"
])

OUTPUT_FORMATS = {
    "mp3": {"extension": ".mp3", "codec": "libmp3lame"},
    "wav": {"extension": ".wav", "codec": "pcm_s16le"},
    "flac": {"extension": ".flac", "codec": "flac"},
    "ogg": {"extension": ".ogg", "codec": "libvorbis"},
    "opus": {"extension": ".opus", "codec": "libopus"},
    "aac": {"extension": ".m4a", "codec": "aac"},
}

OUTPUT_FORMAT_ITEMS = ["mp3", "wav", "flac", "ogg", "opus", "aac"]
QUALITY_PRESETS = ["128k", "192k", "256k", "320k", "Lossless / Best"]
SAMPLE_RATES = ["Original", "22050 Hz", "44100 Hz", "48000 Hz"]
CHANNELS = ["Original", "Stereo", "Mono"]
CONFLICT_MODES = ["Rename", "Skip", "Overwrite"]
THREAD_ITEMS = ["1", "2", "3", "4"]

PRESETS = [
    "Custom", "Legacy MP3 192k", "High Quality MP3", "Archive FLAC",
    "Lossless WAV", "Podcast / Voice", "Audiobook", "Car Audio", "Low Size MP3", "Web AAC",
    "OGG Vorbis", "OPUS Voice"
]

COLUMNS = [
    ("File", 300),
    ("Format", 58),
    ("Codec", 70),
    ("Bitrate", 70),
    ("Sample Rate / Bit Depth", 122),
    ("Channels", 62),
    ("Duration", 68),
    ("Size", 74),
    ("Progress", 96),
]

COLUMN_KEYS = [
    "col_file", "col_format", "col_codec", "col_bitrate", "col_sample",
    "col_channels", "col_duration", "col_size", "col_percent"
]


LANGUAGES = ["en", "ru", "de", "uk"]
LANGUAGE_NAMES = {"en": "English", "ru": "Русский", "de": "Deutsch", "uk": "Українська"}

LOC = {'en': {'about': 'About',
        'license': 'Licenses',
        'mit_license': 'MIT License',
        'third_party_licenses': 'Third-party licenses',
        'settings': 'Settings',
        'input_files_folders': 'Input files / folders',
        'add_files': 'Add Files',
        'add_folder': 'Add Folder',
        'remove_selected': 'Remove Selected',
        'clear_list': 'Clear List',
        'analyze': 'Analyze',
        'preview_open': 'Preview / Open',
        'conversion_settings': 'Conversion settings',
        'preset': 'Preset:',
        'output_format': 'Output format:',
        'quality': 'Quality:',
        'quality_lossless_best': 'Lossless / Best',
        'ffmpeg_threads': 'FFmpeg threads:',
        'sample_rate': 'Sample rate:',
        'channels': 'Channels:',
        'if_target_exists': 'If target exists:',
        'keep_metadata': 'Keep metadata',
        'preserve_structure': 'Preserve folder structure',
        'open_output_when_done': 'Open output when done',
        'sounds': 'Sounds',
        'choose_output_folder': 'Choose Output Folder',
        'use_auto_output': 'Use Auto Output',
        'test_run': 'Test Run',
        'convert': 'Convert',
        'stop': 'STOP',
        'open_output_folder': 'Open Output Folder',
        'save_log': 'Save Log TXT',
        'export_csv': 'Export CSV Report',
        'show_errors': 'Show Errors',
        'statistics': 'Statistics',
        'ready': 'Ready',
        'output_folder_auto': 'Output folder: Auto',
        'output_folder_path': 'Output folder: {path}',
        'stats_initial': 'Total: 0 | Converted: 0 | Skipped: 0 | Failed: 0 | Elapsed: 00:00:00',
        'current_file_empty': 'Current file: -',
        'current_file_done': 'Current file: done',
        'analysis_running': 'Analysis running...',
        'analysis_finished': 'Analysis finished.',
        'settings_general': 'General',
        'settings_interface': 'Interface',
        'settings_ffmpeg': 'FFmpeg / FFprobe',
        'settings_safety': 'Safety',
        'settings_system': 'System',
        'language': 'Language:',
        'auto_analyze_on_add': 'Auto-analyze files after adding',
        'auto_scale_current_screen': 'Auto-scale to current screen',
        'dark_theme': 'Simple dark theme',
        'compact_ui': 'Compact interface',
        'ui_scale': 'Interface scale:',
        'custom_ffmpeg_path': 'Custom ffmpeg.exe path:',
        'custom_ffprobe_path': 'Custom ffprobe.exe path:',
        'browse': 'Browse',
        'use_bundled': 'Use bundled FFmpeg/FFprobe',
        'active_ffmpeg': 'Active FFmpeg:',
        'active_ffprobe': 'Active FFprobe:',
        'confirm_stop': 'Confirm before STOP',
        'confirm_external_open': 'Confirm before opening external paths',
        'safe_output_checks': 'Strict output folder safety checks',
        'warn_huge_batch': 'Warn before huge batch',
        'huge_batch_limit': 'Huge batch limit:',
        'warn_long_paths': 'Warn about classic Windows path limit',
        'auto_scale_note': 'Auto-scale reads the current screen resolution and adjusts text, controls and spacing automatically. Manual scale is available only when auto-scale is disabled.',
        'path_limit_helper_button': 'Open Windows 260-character path limit helper...',
        'path_limit_helper_title': 'Windows long path limit helper',
        'path_limit_helper_text': 'This helper can enable LongPathsEnabled in Windows 10/11 registry. It does not work on Windows XP/Vista/7/8 and it does not guarantee that every old component supports long paths. Administrator rights and restart are required.',
        'path_limit_status_enabled': 'Current status: LongPathsEnabled = 1.',
        'path_limit_status_disabled': 'Current status: LongPathsEnabled is not enabled.',
        'path_limit_status_unsupported': 'Current status: not supported on this Windows version.',
        'path_limit_run': 'Apply registry change',
        'path_limit_copy': 'Copy command',
        'path_limit_copied': 'Command copied to clipboard.',
        'path_limit_started': 'Registry command started. Confirm UAC/Admin prompt if shown, then restart Windows.',
        'path_limit_failed': 'Failed to start registry command: {error}',
        'path_limit_unsupported': 'This registry method is supported only on Windows 10/11 or Windows Server 2016+.',
        'ok': 'OK',
        'cancel': 'Cancel',
        'error': 'Error',
        'warning': 'Warning',
        'process_safety': 'Process safety',
        'no_files': 'No files or folders selected.',
        'no_analyze': 'No files to analyze.',
        'ffprobe_missing': 'ffprobe.exe not found.',
        'ffmpeg_missing': 'ffmpeg.exe or ffprobe.exe not found.',
        'custom_ffmpeg_invalid': 'Custom ffmpeg.exe path is invalid.',
        'custom_ffprobe_invalid': 'Custom ffprobe.exe path is invalid.',
        'no_audio_found': 'No supported audio files found.',
        'selected_missing': 'Selected files do not exist.',
        'no_write_access': 'No write access to output folder:\n{error}',
        'risky_output': 'Output folder looks risky: {path}',
        'overwrite_warning': 'Overwrite mode is enabled. Existing target files may be replaced.',
        'huge_batch_warning': 'Huge batch: {count} audio files selected.',
        'long_paths_warning': 'Some output paths may be too long for classic Windows handling.',
        'warnings_continue': 'Warnings:\n\n{warnings}\n\nContinue?',
        'conversion_running': 'Conversion is already running.',
        'analysis_busy': 'Analysis is already running.',
        'stop_question': 'Stop current conversion? Current partial file may be deleted.',
        'stopping': 'Stopping...',
        'stopped_failed': 'Conversion stopped or failed.',
        'conversion_finished': 'Conversion finished.',
        'output_unavailable': 'Output folder is not available yet.',
        'saved': 'Saved',
        'log_saved': 'Log saved:\n{path}',
        'save_log_failed': 'Failed to save log:\n{error}',
        'no_errors_saved': 'No error details saved.',
        'error_details': 'Error Details',
        'close': 'Close',
        'export': 'Export',
        'no_files_to_export': 'No files to export.',
        'csv_saved': 'CSV report saved:\n{path}',
        'export_error': 'Export error',
        'added_files': 'Added files: {count}',
        'auto_analysis_log': 'Auto-analysis started.',
        'data_folder': 'Data folder',
        'config_file': 'Config file',
        'appdata_note': 'OldWin config path: %APPDATA%\\AdvancedAudioConverter_OldWin',
        'app_info': 'Application info',
        'version_label': 'Version',
        'author_label': 'Author',
        'ui_scale_info': 'UI scale',
        'file_list_height_info': 'File list height',
        'log_height_info': 'Log height',
        'ffmpeg_thread_setting_info': 'FFmpeg thread setting',
        'system_hardware_section': 'Operating system / hardware',
        'legacy_config_migration': 'Legacy config migration',
        'safety_note': 'Safety checks are designed for old Windows: writable output folder, dangerous path warning, huge batch warning and classic path length '
                       'warning.',
        'apply_restart_note': 'Most settings apply immediately. Auto-scale is the default UI scaling mode. If Qt behaves oddly on XP, restart the app.',
        'settings_performance': 'Performance',
        'list_height': 'File list height:',
        'log_height': 'Log height:',
        'compact_locks_scale': 'Interface scale is locked while compact interface is enabled.',
        'cpu_threads_detected': 'Detected CPU threads: {count}',
        'threads_locked_single': 'Only one CPU thread is detected. FFmpeg is limited to 1 thread.',
        'threads_available_note': 'Available FFmpeg threads: 1..{limit}. Values above detected CPU threads are disabled.',
        'oldwin_runtime_note': 'OldWin compatibility build: 32-bit runtime for XP/Win7-11.',
        'col_file': 'File',
        'col_format': 'Format',
        'col_codec': 'Codec',
        'col_bitrate': 'Bitrate',
        'col_sample': 'Sample Rate / Bit Depth',
        'col_channels': 'Channels',
        'col_duration': 'Duration',
        'col_size': 'Size',
        'col_percent': 'Progress',
        'stats_runtime': 'Total: {total} | Converted: {converted} | Skipped: {skipped} | Failed: {failed} | Elapsed: {elapsed}',
        'exit_running': 'Conversion is running. Stop and exit?'},
 'ru': {'about': 'О программе',
        'license': 'Лицензии',
        'mit_license': 'MIT License',
        'third_party_licenses': 'Лицензии компонентов',
        'settings': 'Настройки',
        'input_files_folders': 'Входные файлы / папки',
        'add_files': 'Добавить файлы',
        'add_folder': 'Добавить папку',
        'remove_selected': 'Удалить выбранное',
        'clear_list': 'Очистить список',
        'analyze': 'Анализ',
        'preview_open': 'Просмотр / открыть',
        'conversion_settings': 'Настройки конвертации',
        'preset': 'Пресет:',
        'output_format': 'Формат:',
        'quality': 'Качество:',
        'quality_lossless_best': 'Без потерь / лучшее',
        'ffmpeg_threads': 'Потоки FFmpeg:',
        'sample_rate': 'Частота:',
        'channels': 'Каналы:',
        'if_target_exists': 'Если файл есть:',
        'keep_metadata': 'Сохранять метаданные',
        'preserve_structure': 'Сохранять структуру папок',
        'open_output_when_done': 'Открыть папку после завершения',
        'sounds': 'Звуки',
        'choose_output_folder': 'Выбрать папку вывода',
        'use_auto_output': 'Авто-папка',
        'test_run': 'Пробный запуск',
        'convert': 'Конвертировать',
        'stop': 'СТОП',
        'open_output_folder': 'Открыть папку вывода',
        'save_log': 'Сохранить лог TXT',
        'export_csv': 'Экспорт CSV',
        'show_errors': 'Ошибки',
        'statistics': 'Статистика',
        'ready': 'Готово',
        'output_folder_auto': 'Папка вывода: Авто',
        'output_folder_path': 'Папка вывода: {path}',
        'stats_initial': 'Всего: 0 | Готово: 0 | Пропущено: 0 | Ошибок: 0 | Время: 00:00:00',
        'current_file_empty': 'Текущий файл: -',
        'current_file_done': 'Текущий файл: готово',
        'analysis_running': 'Идёт анализ...',
        'analysis_finished': 'Анализ завершён.',
        'settings_general': 'Общие',
        'settings_interface': 'Интерфейс',
        'settings_ffmpeg': 'FFmpeg / FFprobe',
        'settings_safety': 'Безопасность',
        'settings_system': 'Система',
        'language': 'Язык:',
        'auto_analyze_on_add': 'Автоанализ после добавления',
        'auto_scale_current_screen': 'Автомасштаб под текущий экран',
        'dark_theme': 'Простая тёмная тема',
        'compact_ui': 'Компактный интерфейс',
        'ui_scale': 'Масштаб интерфейса:',
        'custom_ffmpeg_path': 'Свой путь к ffmpeg.exe:',
        'custom_ffprobe_path': 'Свой путь к ffprobe.exe:',
        'browse': 'Обзор',
        'use_bundled': 'Использовать встроенный FFmpeg/FFprobe',
        'active_ffmpeg': 'Активный FFmpeg:',
        'active_ffprobe': 'Активный FFprobe:',
        'confirm_stop': 'Подтверждать STOP',
        'confirm_external_open': 'Подтверждать открытие внешних путей',
        'safe_output_checks': 'Строгая проверка папки вывода',
        'warn_huge_batch': 'Предупреждать о большой пачке',
        'huge_batch_limit': 'Лимит большой пачки:',
        'warn_long_paths': 'Предупреждать о лимите путей Windows',
        'auto_scale_note': 'Автомасштаб читает текущее разрешение экрана и подстраивает текст, элементы и отступы. Ручной масштаб доступен только когда автомасштаб выключен.',
        'path_limit_helper_button': 'Открыть помощник снятия лимита пути Windows 260 символов...',
        'path_limit_helper_title': 'Помощник длинных путей Windows',
        'path_limit_helper_text': 'Этот помощник может включить LongPathsEnabled в реестре Windows 10/11. На Windows XP/Vista/7/8 это не работает и не гарантирует, что старые компоненты поддержат длинные пути. Нужны права администратора и перезагрузка.',
        'path_limit_status_enabled': 'Текущий статус: LongPathsEnabled = 1.',
        'path_limit_status_disabled': 'Текущий статус: LongPathsEnabled не включён.',
        'path_limit_status_unsupported': 'Текущий статус: не поддерживается этой версией Windows.',
        'path_limit_run': 'Применить изменение реестра',
        'path_limit_copy': 'Скопировать команду',
        'path_limit_copied': 'Команда скопирована в буфер обмена.',
        'path_limit_started': 'Команда реестра запущена. Подтверди UAC/Admin-запрос, если он появится, затем перезагрузи Windows.',
        'path_limit_failed': 'Не удалось запустить команду реестра: {error}',
        'path_limit_unsupported': 'Этот способ через реестр поддерживается только на Windows 10/11 или Windows Server 2016+.',
        'ok': 'OK',
        'cancel': 'Отмена',
        'error': 'Ошибка',
        'warning': 'Предупреждение',
        'process_safety': 'Безопасность процесса',
        'no_files': 'Файлы или папки не выбраны.',
        'no_analyze': 'Нет файлов для анализа.',
        'ffprobe_missing': 'ffprobe.exe не найден.',
        'ffmpeg_missing': 'ffmpeg.exe или ffprobe.exe не найден.',
        'custom_ffmpeg_invalid': 'Свой путь к ffmpeg.exe неверный.',
        'custom_ffprobe_invalid': 'Свой путь к ffprobe.exe неверный.',
        'no_audio_found': 'Поддерживаемые аудиофайлы не найдены.',
        'selected_missing': 'Выбранные файлы больше не существуют.',
        'no_write_access': 'Нет доступа на запись в папку вывода:\n{error}',
        'risky_output': 'Папка вывода выглядит рискованно: {path}',
        'overwrite_warning': 'Включена перезапись. Целевые файлы могут быть заменены.',
        'huge_batch_warning': 'Большая пачка: выбрано {count} аудиофайлов.',
        'long_paths_warning': 'Некоторые пути могут быть слишком длинными для классической Windows.',
        'warnings_continue': 'Предупреждения:\n\n{warnings}\n\nПродолжить?',
        'conversion_running': 'Конвертация уже идёт.',
        'analysis_busy': 'Анализ уже идёт.',
        'stop_question': 'Остановить конвертацию? Частичный файл может быть удалён.',
        'stopping': 'Остановка...',
        'stopped_failed': 'Конвертация остановлена или завершилась ошибкой.',
        'conversion_finished': 'Конвертация завершена.',
        'output_unavailable': 'Папка вывода пока недоступна.',
        'saved': 'Сохранено',
        'log_saved': 'Лог сохранён:\n{path}',
        'save_log_failed': 'Не удалось сохранить лог:\n{error}',
        'no_errors_saved': 'Детали ошибок не сохранены.',
        'error_details': 'Детали ошибок',
        'close': 'Закрыть',
        'export': 'Экспорт',
        'no_files_to_export': 'Нет файлов для экспорта.',
        'csv_saved': 'CSV-отчёт сохранён:\n{path}',
        'export_error': 'Ошибка экспорта',
        'added_files': 'Добавлено файлов: {count}',
        'auto_analysis_log': 'Автоанализ запущен.',
        'data_folder': 'Папка данных',
        'config_file': 'Файл настроек',
        'appdata_note': 'Путь настроек OldWin: %APPDATA%\\AdvancedAudioConverter_OldWin',
        'app_info': 'Информация о приложении',
        'version_label': 'Версия',
        'author_label': 'Автор',
        'ui_scale_info': 'Масштаб интерфейса',
        'file_list_height_info': 'Высота списка файлов',
        'log_height_info': 'Высота лога',
        'ffmpeg_thread_setting_info': 'Настройка потоков FFmpeg',
        'system_hardware_section': 'Операционная система / железо',
        'legacy_config_migration': 'Миграция старых настроек',
        'safety_note': 'Защита рассчитана на старую Windows: проверка записи, предупреждение о рискованных папках, больших пачках и длинных путях.',
        'apply_restart_note': 'Большинство настроек применяются сразу. Автомасштаб — основной режим масштаба интерфейса. Если Qt на XP чудит — перезапусти программу.',
        'settings_performance': 'Производительность',
        'list_height': 'Высота списка файлов:',
        'log_height': 'Высота лога:',
        'compact_locks_scale': 'Масштаб интерфейса заблокирован, пока включён компактный интерфейс.',
        'cpu_threads_detected': 'Обнаружено потоков CPU: {count}',
        'threads_locked_single': 'Обнаружен только 1 поток CPU. FFmpeg ограничен 1 потоком.',
        'threads_available_note': 'Доступные потоки FFmpeg: 1..{limit}. Значения выше числа потоков CPU отключены.',
        'oldwin_runtime_note': 'OldWin-совместимая сборка: 32-битный runtime для XP/Win7-11.',
        'col_file': 'Файл',
        'col_format': 'Формат',
        'col_codec': 'Кодек',
        'col_bitrate': 'Битрейт',
        'col_sample': 'Частота / битность',
        'col_channels': 'Каналы',
        'col_duration': 'Длительность',
        'col_size': 'Размер',
        'col_percent': 'Прогресс',
        'stats_runtime': 'Всего: {total} | Готово: {converted} | Пропущено: {skipped} | Ошибок: {failed} | Время: {elapsed}',
        'exit_running': 'Конвертация идёт. Остановить и выйти?'},
 'de': {'about': 'Über',
        'license': 'Lizenzen',
        'mit_license': 'MIT-Lizenz',
        'third_party_licenses': 'Dritthersteller-Lizenzen',
        'settings': 'Einstellungen',
        'input_files_folders': 'Eingabedateien / Ordner',
        'add_files': 'Dateien hinzufügen',
        'add_folder': 'Ordner hinzufügen',
        'remove_selected': 'Auswahl entfernen',
        'clear_list': 'Liste leeren',
        'analyze': 'Analysieren',
        'preview_open': 'Vorschau / Öffnen',
        'conversion_settings': 'Konvertierungseinstellungen',
        'preset': 'Profil:',
        'output_format': 'Ausgabeformat:',
        'quality': 'Qualität:',
        'quality_lossless_best': 'Verlustfrei / Beste',
        'ffmpeg_threads': 'FFmpeg-Threads:',
        'sample_rate': 'Abtastrate:',
        'channels': 'Kanäle:',
        'if_target_exists': 'Wenn Ziel existiert:',
        'keep_metadata': 'Metadaten behalten',
        'preserve_structure': 'Ordnerstruktur behalten',
        'open_output_when_done': 'Ausgabeordner danach öffnen',
        'sounds': 'Töne',
        'choose_output_folder': 'Ausgabeordner wählen',
        'use_auto_output': 'Automatische Ausgabe',
        'test_run': 'Testlauf',
        'convert': 'Konvertieren',
        'stop': 'STOP',
        'open_output_folder': 'Ausgabeordner öffnen',
        'save_log': 'Log als TXT speichern',
        'export_csv': 'CSV-Bericht exportieren',
        'show_errors': 'Fehler anzeigen',
        'statistics': 'Statistik',
        'ready': 'Bereit',
        'output_folder_auto': 'Ausgabeordner: Automatisch',
        'output_folder_path': 'Ausgabeordner: {path}',
        'stats_initial': 'Gesamt: 0 | Fertig: 0 | Übersprungen: 0 | Fehlgeschlagen: 0 | Zeit: 00:00:00',
        'current_file_empty': 'Aktuelle Datei: -',
        'current_file_done': 'Aktuelle Datei: fertig',
        'analysis_running': 'Analyse läuft...',
        'analysis_finished': 'Analyse abgeschlossen.',
        'settings_general': 'Allgemein',
        'settings_interface': 'Oberfläche',
        'settings_ffmpeg': 'FFmpeg / FFprobe',
        'settings_safety': 'Sicherheit',
        'settings_system': 'System',
        'settings_performance': 'Leistung',
        'language': 'Sprache:',
        'auto_analyze_on_add': 'Dateien nach dem Hinzufügen automatisch analysieren',
        'auto_scale_current_screen': 'Automatisch an aktuellen Bildschirm skalieren',
        'dark_theme': 'Einfaches dunkles Thema',
        'compact_ui': 'Kompakte Oberfläche',
        'ui_scale': 'Oberflächenskalierung:',
        'list_height': 'Höhe der Dateiliste:',
        'log_height': 'Höhe des Logs:',
        'compact_locks_scale': 'Die Skalierung ist gesperrt, solange die kompakte Oberfläche aktiviert ist.',
        'custom_ffmpeg_path': 'Eigener Pfad zu ffmpeg.exe:',
        'custom_ffprobe_path': 'Eigener Pfad zu ffprobe.exe:',
        'browse': 'Durchsuchen',
        'use_bundled': 'Gebündeltes FFmpeg/FFprobe verwenden',
        'active_ffmpeg': 'Aktives FFmpeg:',
        'active_ffprobe': 'Aktives FFprobe:',
        'confirm_stop': 'STOP bestätigen',
        'confirm_external_open': 'Öffnen externer Pfade bestätigen',
        'safe_output_checks': 'Strenge Prüfung des Ausgabeordners',
        'warn_huge_batch': 'Vor großen Stapeln warnen',
        'huge_batch_limit': 'Grenze für großen Stapel:',
        'warn_long_paths': 'Vor klassischer Windows-Pfadlänge warnen',
        'auto_scale_note': 'Die automatische Skalierung liest die aktuelle Bildschirmauflösung und passt Text, Bedienelemente und Abstände an. Manuelle Skalierung ist nur verfügbar, wenn Auto-scale deaktiviert ist.',
        'path_limit_helper_button': 'Windows-260-Zeichen-Pfadlimit-Helfer öffnen...',
        'path_limit_helper_title': 'Windows-Helfer für lange Pfade',
        'path_limit_helper_text': 'Dieser Helfer kann LongPathsEnabled in der Windows-10/11-Registry aktivieren. Unter Windows XP/Vista/7/8 funktioniert das nicht und garantiert nicht, dass alte Komponenten lange Pfade unterstützen. Administratorrechte und Neustart sind erforderlich.',
        'path_limit_status_enabled': 'Aktueller Status: LongPathsEnabled = 1.',
        'path_limit_status_disabled': 'Aktueller Status: LongPathsEnabled ist nicht aktiviert.',
        'path_limit_status_unsupported': 'Aktueller Status: von dieser Windows-Version nicht unterstützt.',
        'path_limit_run': 'Registry-Änderung anwenden',
        'path_limit_copy': 'Befehl kopieren',
        'path_limit_copied': 'Befehl in die Zwischenablage kopiert.',
        'path_limit_started': 'Registry-Befehl gestartet. UAC/Admin-Abfrage bestätigen, falls angezeigt, dann Windows neu starten.',
        'path_limit_failed': 'Registry-Befehl konnte nicht gestartet werden: {error}',
        'path_limit_unsupported': 'Diese Registry-Methode wird nur unter Windows 10/11 oder Windows Server 2016+ unterstützt.',
        'ok': 'OK',
        'cancel': 'Abbrechen',
        'error': 'Fehler',
        'warning': 'Warnung',
        'process_safety': 'Prozesssicherheit',
        'no_files': 'Keine Dateien oder Ordner ausgewählt.',
        'no_analyze': 'Keine Dateien zum Analysieren.',
        'ffprobe_missing': 'ffprobe.exe nicht gefunden.',
        'ffmpeg_missing': 'ffmpeg.exe oder ffprobe.exe nicht gefunden.',
        'custom_ffmpeg_invalid': 'Eigener Pfad zu ffmpeg.exe ist ungültig.',
        'custom_ffprobe_invalid': 'Eigener Pfad zu ffprobe.exe ist ungültig.',
        'no_audio_found': 'Keine unterstützten Audiodateien gefunden.',
        'selected_missing': 'Ausgewählte Dateien existieren nicht mehr.',
        'no_write_access': 'Kein Schreibzugriff auf den Ausgabeordner:\n{error}',
        'risky_output': 'Ausgabeordner wirkt riskant: {path}',
        'overwrite_warning': 'Überschreiben ist aktiviert. Zieldateien können ersetzt werden.',
        'huge_batch_warning': 'Großer Stapel: {count} Audiodateien ausgewählt.',
        'long_paths_warning': 'Einige Ausgabepfade könnten für klassisches Windows zu lang sein.',
        'warnings_continue': 'Warnungen:\n\n{warnings}\n\nFortfahren?',
        'conversion_running': 'Konvertierung läuft bereits.',
        'analysis_busy': 'Analyse läuft bereits.',
        'stop_question': 'Konvertierung stoppen? Eine Teildatei kann gelöscht werden.',
        'stopping': 'Stoppe...',
        'stopped_failed': 'Konvertierung gestoppt oder fehlgeschlagen.',
        'conversion_finished': 'Konvertierung abgeschlossen.',
        'output_unavailable': 'Ausgabeordner ist noch nicht verfügbar.',
        'saved': 'Gespeichert',
        'log_saved': 'Log gespeichert:\n{path}',
        'save_log_failed': 'Log konnte nicht gespeichert werden:\n{error}',
        'no_errors_saved': 'Keine Fehlerdetails gespeichert.',
        'error_details': 'Fehlerdetails',
        'close': 'Schließen',
        'export': 'Exportieren',
        'no_files_to_export': 'Keine Dateien zum Exportieren.',
        'csv_saved': 'CSV-Bericht gespeichert:\n{path}',
        'export_error': 'Exportfehler',
        'added_files': 'Dateien hinzugefügt: {count}',
        'auto_analysis_log': 'Auto-Analyse gestartet.',
        'data_folder': 'Datenordner',
        'config_file': 'Konfigurationsdatei',
        'appdata_note': 'OldWin-Konfigurationspfad: %APPDATA%\\AdvancedAudioConverter_OldWin',
        'app_info': 'Anwendungsinfo',
        'version_label': 'Version',
        'author_label': 'Autor',
        'ui_scale_info': 'UI-Skalierung',
        'file_list_height_info': 'Dateilistenhöhe',
        'log_height_info': 'Loghöhe',
        'ffmpeg_thread_setting_info': 'FFmpeg-Thread-Einstellung',
        'system_hardware_section': 'Betriebssystem / Hardware',
        'legacy_config_migration': 'Migration alter Einstellungen',
        'safety_note': 'Sicherheitsprüfungen für alte Windows-Versionen: Schreibtest, Warnung bei riskanten Ordnern, großen Stapeln und langen Pfaden.',
        'apply_restart_note': 'Die meisten Einstellungen gelten sofort. Skalierung ist nur verfügbar, wenn die kompakte Oberfläche deaktiviert ist. Wenn Qt '
                              'unter XP seltsam reagiert, App neu starten.',
        'cpu_threads_detected': 'Erkannte CPU-Threads: {count}',
        'threads_locked_single': 'Nur ein CPU-Thread wurde erkannt. FFmpeg ist auf 1 Thread begrenzt.',
        'threads_available_note': 'Verfügbare FFmpeg-Threads: 1..{limit}. Werte über den erkannten CPU-Threads sind deaktiviert.',
        'oldwin_runtime_note': 'OldWin-Kompatibilitätsbuild: 32-Bit-Runtime für XP/Win7-11.',
        'col_file': 'Datei',
        'col_format': 'Format',
        'col_codec': 'Codec',
        'col_bitrate': 'Bitrate',
        'col_sample': 'Abtastrate / Bittiefe',
        'col_channels': 'Kanäle',
        'col_duration': 'Dauer',
        'col_size': 'Größe',
        'col_percent': 'Progress',
        'stats_runtime': 'Gesamt: {total} | Fertig: {converted} | Übersprungen: {skipped} | Fehlgeschlagen: {failed} | Zeit: {elapsed}',
        'exit_running': 'Konvertierung läuft. Stoppen und beenden?'},
 'uk': {'about': 'Про програму',
        'license': 'Ліцензії',
        'mit_license': 'MIT License',
        'third_party_licenses': 'Ліцензії компонентів',
        'settings': 'Налаштування',
        'input_files_folders': 'Вхідні файли / папки',
        'add_files': 'Додати файли',
        'add_folder': 'Додати папку',
        'remove_selected': 'Видалити вибране',
        'clear_list': 'Очистити список',
        'analyze': 'Аналіз',
        'preview_open': 'Перегляд / відкрити',
        'conversion_settings': 'Налаштування конвертації',
        'preset': 'Пресет:',
        'output_format': 'Формат виводу:',
        'quality': 'Якість:',
        'quality_lossless_best': 'Без втрат / найкраще',
        'ffmpeg_threads': 'Потоки FFmpeg:',
        'sample_rate': 'Частота:',
        'channels': 'Канали:',
        'if_target_exists': 'Якщо файл існує:',
        'keep_metadata': 'Зберігати метадані',
        'preserve_structure': 'Зберігати структуру папок',
        'open_output_when_done': 'Відкрити папку після завершення',
        'sounds': 'Звуки',
        'choose_output_folder': 'Вибрати папку виводу',
        'use_auto_output': 'Автоматична папка',
        'test_run': 'Тестовий запуск',
        'convert': 'Конвертувати',
        'stop': 'СТОП',
        'open_output_folder': 'Відкрити папку виводу',
        'save_log': 'Зберегти лог TXT',
        'export_csv': 'Експорт CSV',
        'show_errors': 'Помилки',
        'statistics': 'Статистика',
        'ready': 'Готово',
        'output_folder_auto': 'Папка виводу: Авто',
        'output_folder_path': 'Папка виводу: {path}',
        'stats_initial': 'Усього: 0 | Готово: 0 | Пропущено: 0 | Помилок: 0 | Час: 00:00:00',
        'current_file_empty': 'Поточний файл: -',
        'current_file_done': 'Поточний файл: готово',
        'analysis_running': 'Триває аналіз...',
        'analysis_finished': 'Аналіз завершено.',
        'settings_general': 'Загальні',
        'settings_interface': 'Інтерфейс',
        'settings_ffmpeg': 'FFmpeg / FFprobe',
        'settings_safety': 'Безпека',
        'settings_system': 'Система',
        'settings_performance': 'Продуктивність',
        'language': 'Мова:',
        'auto_analyze_on_add': 'Автоаналіз після додавання',
        'auto_scale_current_screen': 'Автомасштаб під поточний екран',
        'dark_theme': 'Проста темна тема',
        'compact_ui': 'Компактний інтерфейс',
        'ui_scale': 'Масштаб інтерфейсу:',
        'list_height': 'Висота списку файлів:',
        'log_height': 'Висота логу:',
        'compact_locks_scale': 'Масштаб інтерфейсу заблокований, поки увімкнений компактний інтерфейс.',
        'custom_ffmpeg_path': 'Свій шлях до ffmpeg.exe:',
        'custom_ffprobe_path': 'Свій шлях до ffprobe.exe:',
        'browse': 'Огляд',
        'use_bundled': 'Використовувати вбудований FFmpeg/FFprobe',
        'active_ffmpeg': 'Активний FFmpeg:',
        'active_ffprobe': 'Активний FFprobe:',
        'confirm_stop': 'Підтверджувати STOP',
        'confirm_external_open': 'Підтверджувати відкриття зовнішніх шляхів',
        'safe_output_checks': 'Сувора перевірка папки виводу',
        'warn_huge_batch': 'Попереджати про велику пачку',
        'huge_batch_limit': 'Ліміт великої пачки:',
        'warn_long_paths': 'Попереджати про ліміт шляхів Windows',
        'auto_scale_note': 'Автомасштаб читає поточну роздільну здатність екрана і підлаштовує текст, елементи та відступи. Ручне масштабування доступне лише коли автомасштаб вимкнено.',
        'path_limit_helper_button': 'Відкрити помічник зняття ліміту шляху Windows 260 символів...',
        'path_limit_helper_title': 'Помічник довгих шляхів Windows',
        'path_limit_helper_text': 'Цей помічник може увімкнути LongPathsEnabled у реєстрі Windows 10/11. На Windows XP/Vista/7/8 це не працює і не гарантує, що старі компоненти підтримають довгі шляхи. Потрібні права адміністратора та перезавантаження.',
        'path_limit_status_enabled': 'Поточний статус: LongPathsEnabled = 1.',
        'path_limit_status_disabled': 'Поточний статус: LongPathsEnabled не увімкнено.',
        'path_limit_status_unsupported': 'Поточний статус: не підтримується цією версією Windows.',
        'path_limit_run': 'Застосувати зміну реєстру',
        'path_limit_copy': 'Скопіювати команду',
        'path_limit_copied': 'Команду скопійовано в буфер обміну.',
        'path_limit_started': 'Команду реєстру запущено. Підтвердь UAC/Admin-запит, якщо він з’явиться, потім перезавантаж Windows.',
        'path_limit_failed': 'Не вдалося запустити команду реєстру: {error}',
        'path_limit_unsupported': 'Цей спосіб через реєстр підтримується лише на Windows 10/11 або Windows Server 2016+.',
        'ok': 'OK',
        'cancel': 'Скасувати',
        'error': 'Помилка',
        'warning': 'Попередження',
        'process_safety': 'Безпека процесу',
        'no_files': 'Файли або папки не вибрані.',
        'no_analyze': 'Немає файлів для аналізу.',
        'ffprobe_missing': 'ffprobe.exe не знайдено.',
        'ffmpeg_missing': 'ffmpeg.exe або ffprobe.exe не знайдено.',
        'custom_ffmpeg_invalid': 'Свій шлях до ffmpeg.exe неправильний.',
        'custom_ffprobe_invalid': 'Свій шлях до ffprobe.exe неправильний.',
        'no_audio_found': 'Підтримувані аудіофайли не знайдені.',
        'selected_missing': 'Вибрані файли більше не існують.',
        'no_write_access': 'Немає доступу на запис до папки виводу:\n{error}',
        'risky_output': 'Папка виводу виглядає ризиковано: {path}',
        'overwrite_warning': 'Увімкнено перезапис. Цільові файли можуть бути замінені.',
        'huge_batch_warning': 'Велика пачка: вибрано {count} аудіофайлів.',
        'long_paths_warning': 'Деякі шляхи можуть бути занадто довгими для класичної Windows.',
        'warnings_continue': 'Попередження:\n\n{warnings}\n\nПродовжити?',
        'conversion_running': 'Конвертація вже триває.',
        'analysis_busy': 'Аналіз уже триває.',
        'stop_question': 'Зупинити конвертацію? Частковий файл може бути видалений.',
        'stopping': 'Зупинка...',
        'stopped_failed': 'Конвертацію зупинено або завершено з помилкою.',
        'conversion_finished': 'Конвертацію завершено.',
        'output_unavailable': 'Папка виводу поки недоступна.',
        'saved': 'Збережено',
        'log_saved': 'Лог збережено:\n{path}',
        'save_log_failed': 'Не вдалося зберегти лог:\n{error}',
        'no_errors_saved': 'Деталі помилок не збережені.',
        'error_details': 'Деталі помилок',
        'close': 'Закрити',
        'export': 'Експорт',
        'no_files_to_export': 'Немає файлів для експорту.',
        'csv_saved': 'CSV-звіт збережено:\n{path}',
        'export_error': 'Помилка експорту',
        'added_files': 'Додано файлів: {count}',
        'auto_analysis_log': 'Автоаналіз запущено.',
        'data_folder': 'Папка даних',
        'config_file': 'Файл налаштувань',
        'appdata_note': 'Шлях налаштувань OldWin: %APPDATA%\\AdvancedAudioConverter_OldWin',
        'app_info': 'Інформація про програму',
        'version_label': 'Версія',
        'author_label': 'Автор',
        'ui_scale_info': 'Масштаб інтерфейсу',
        'file_list_height_info': 'Висота списку файлів',
        'log_height_info': 'Висота логу',
        'ffmpeg_thread_setting_info': 'Налаштування потоків FFmpeg',
        'system_hardware_section': 'Операційна система / залізо',
        'legacy_config_migration': 'Міграція старих налаштувань',
        'safety_note': 'Захист розрахований на стару Windows: перевірка запису, попередження про ризиковані папки, великі пачки і довгі шляхи.',
        'apply_restart_note': 'Більшість налаштувань застосовуються одразу. Автомасштаб — основний режим масштабу інтерфейсу. Якщо Qt на XP поводиться дивно — перезапусти програму.',
        'cpu_threads_detected': 'Виявлено потоків CPU: {count}',
        'threads_locked_single': 'Виявлено лише 1 потік CPU. FFmpeg обмежено 1 потоком.',
        'threads_available_note': 'Доступні потоки FFmpeg: 1..{limit}. Значення вище кількості потоків CPU вимкнені.',
        'oldwin_runtime_note': 'OldWin-сумісна збірка: 32-бітний runtime для XP/Win7-11.',
        'col_file': 'Файл',
        'col_format': 'Формат',
        'col_codec': 'Кодек',
        'col_bitrate': 'Бітрейт',
        'col_sample': 'Частота / бітність',
        'col_channels': 'Канали',
        'col_duration': 'Тривалість',
        'col_size': 'Розмір',
        'col_percent': 'Прогрес',
        'stats_runtime': 'Усього: {total} | Готово: {converted} | Пропущено: {skipped} | Помилок: {failed} | Час: {elapsed}',
        'exit_running': 'Конвертація триває. Зупинити і вийти?'}}


EXTRA_LOC_0135 = {
    "en": {
        "follow_windows_theme": "Follow Windows theme",
        "use_windows_accent_color": "Use Windows accent color",
        "dark_theme": "Dark theme (manual)",
        "theme_status": "Detected theme: {theme} | Accent: {accent}",
        "theme_dark": "dark",
        "theme_light": "light",
        "theme_manual_note": "When Windows theme following is enabled, manual dark theme is disabled and the app reads the current Windows theme. On XP/Vista/7 it falls back to the saved manual choice.",
        "threads_popup_note": "Values above detected CPU threads stay visible but disabled.",
        "disabled_threads_are_light": "Disabled thread values are shown with a light background.",
        "system_theme_section": "Windows theme / accent",
    },
    "ru": {
        "follow_windows_theme": "Следовать теме Windows",
        "use_windows_accent_color": "Использовать цвет акцента Windows",
        "dark_theme": "Тёмная тема (ручной режим)",
        "theme_status": "Определённая тема: {theme} | Акцент: {accent}",
        "theme_dark": "тёмная",
        "theme_light": "светлая",
        "theme_manual_note": "Если включено следование теме Windows, ручная тёмная тема отключается, а программа читает текущую тему Windows. На XP/Vista/7 используется сохранённый ручной выбор.",
        "threads_popup_note": "Значения выше числа потоков CPU остаются видимыми, но отключёнными.",
        "disabled_threads_are_light": "Отключённые значения потоков показаны светлым фоном.",
        "system_theme_section": "Тема Windows / акцент",
    },
    "de": {
        "follow_windows_theme": "Windows-Design übernehmen",
        "use_windows_accent_color": "Windows-Akzentfarbe verwenden",
        "dark_theme": "Dunkles Design (manuell)",
        "theme_status": "Erkanntes Design: {theme} | Akzent: {accent}",
        "theme_dark": "dunkel",
        "theme_light": "hell",
        "theme_manual_note": "Wenn Windows-Design übernehmen aktiv ist, wird das manuelle dunkle Design gesperrt und die App liest das aktuelle Windows-Design. Unter XP/Vista/7 wird die gespeicherte manuelle Auswahl verwendet.",
        "threads_popup_note": "Werte über den erkannten CPU-Threads bleiben sichtbar, sind aber deaktiviert.",
        "disabled_threads_are_light": "Deaktivierte Thread-Werte werden mit hellem Hintergrund angezeigt.",
        "system_theme_section": "Windows-Design / Akzent",
    },
    "uk": {
        "follow_windows_theme": "Дотримуватися теми Windows",
        "use_windows_accent_color": "Використовувати колір акценту Windows",
        "dark_theme": "Темна тема (ручний режим)",
        "theme_status": "Визначена тема: {theme} | Акцент: {accent}",
        "theme_dark": "темна",
        "theme_light": "світла",
        "theme_manual_note": "Якщо увімкнено дотримання теми Windows, ручна темна тема блокується, а програма читає поточну тему Windows. На XP/Vista/7 використовується збережений ручний вибір.",
        "threads_popup_note": "Значення вище кількості потоків CPU залишаються видимими, але вимкненими.",
        "disabled_threads_are_light": "Вимкнені значення потоків показані світлим фоном.",
        "system_theme_section": "Тема Windows / акцент",
    },
}
for _lang, _data in EXTRA_LOC_0135.items():
    try:
        LOC.setdefault(_lang, {}).update(_data)
    except Exception:
        pass

def translate(language, key, **kwargs):
    table = LOC.get(language) or LOC.get("en", {})
    value = table.get(key, LOC.get("en", {}).get(key, key))
    try:
        return value.format(**kwargs)
    except Exception:
        return value


def clamp_color_channel(v):
    try:
        v = int(v)
    except Exception:
        v = 0
    if v < 0:
        return 0
    if v > 255:
        return 255
    return v


def rgb_to_hex(r, g, b):
    return "#%02x%02x%02x" % (clamp_color_channel(r), clamp_color_channel(g), clamp_color_channel(b))


def colorref_to_hex(value, default="#3a6ea5"):
    """Convert Windows COLORREF 0x00BBGGRR to #RRGGBB."""
    try:
        value = int(value)
        r = value & 0xff
        g = (value >> 8) & 0xff
        b = (value >> 16) & 0xff
        return rgb_to_hex(r, g, b)
    except Exception:
        return default


def dword_color_to_hex(value, default="#3a6ea5"):
    """Best-effort conversion for Windows registry accent DWORDs.

    Modern Windows stores several accent values in slightly different byte
    orders. Prefer a sane visible color; fall back to default if it looks empty.
    """
    try:
        value = int(value) & 0xffffffff
        # DWM AccentColor is commonly ABGR: 0xAABBGGRR.
        r = value & 0xff
        g = (value >> 8) & 0xff
        b = (value >> 16) & 0xff
        if (r + g + b) > 15:
            return rgb_to_hex(r, g, b)
        # Some ColorizationColor values are ARGB: 0xAARRGGBB.
        r = (value >> 16) & 0xff
        g = (value >> 8) & 0xff
        b = value & 0xff
        if (r + g + b) > 15:
            return rgb_to_hex(r, g, b)
    except Exception:
        pass
    return default


def dword_abgr_to_hex(value, default="#3a6ea5"):
    """Windows accent DWORD commonly stored as AABBGGRR."""
    try:
        value = int(value) & 0xffffffff
        r = value & 0xff
        g = (value >> 8) & 0xff
        b = (value >> 16) & 0xff
        if (r + g + b) > 15:
            return rgb_to_hex(r, g, b)
    except Exception:
        pass
    return default


def dword_argb_to_hex(value, default="#3a6ea5"):
    """Windows ColorizationColor commonly stored as AARRGGBB."""
    try:
        value = int(value) & 0xffffffff
        r = (value >> 16) & 0xff
        g = (value >> 8) & 0xff
        b = value & 0xff
        if (r + g + b) > 15:
            return rgb_to_hex(r, g, b)
    except Exception:
        pass
    return default


def read_reg_value(root, path, name, default=None, access_extra=0):
    try:
        if winreg is None:
            return default
        access = winreg.KEY_READ
        try:
            access |= int(access_extra)
        except Exception:
            pass
        key = winreg.OpenKey(root, path, 0, access)
        try:
            value, typ = winreg.QueryValueEx(key, name)
        finally:
            try:
                winreg.CloseKey(key)
            except Exception:
                pass
        return value
    except Exception:
        return default


def read_reg_string(root, path, name, default="", access_extra=0):
    try:
        value = read_reg_value(root, path, name, None, access_extra)
        if value is None:
            return default
        return to_text(value).strip() or default
    except Exception:
        return default


def read_reg_binary(root, path, name, default=None, access_extra=0):
    try:
        value = read_reg_value(root, path, name, None, access_extra)
        if value is None:
            return default
        return value
    except Exception:
        return default


def accent_palette_to_hex(value, default="#3a6ea5"):
    """Extract a visible color from Explorer AccentPalette REG_BINARY.

    AccentPalette stores a sequence of 4-byte colors. The most useful Windows
    accent is usually not the first neutral entry, so choose the first saturated
    visible color after the neutral bytes.
    """
    try:
        data = value
        if isinstance(data, str):
            return default
        data = bytes(bytearray(data))
        best = None
        best_score = -1
        for i in range(0, max(0, len(data) - 3), 4):
            b = data[i]
            g = data[i + 1]
            r = data[i + 2]
            if r < 20 and g < 20 and b < 20:
                continue
            if r > 245 and g > 245 and b > 245:
                continue
            score = max(r, g, b) - min(r, g, b)
            if score > best_score:
                best_score = score
                best = (r, g, b)
        if best is not None and best_score >= 8:
            return rgb_to_hex(best[0], best[1], best[2])
    except Exception:
        pass
    return default


def read_reg_dword(root, path, name, default=None):
    try:
        if winreg is None:
            return default
        key = winreg.OpenKey(root, path)
        try:
            value, typ = winreg.QueryValueEx(key, name)
        finally:
            try:
                winreg.CloseKey(key)
            except Exception:
                pass
        return int(value)
    except Exception:
        return default


def windows_accent_color(default="#3a6ea5"):
    """Read current Windows accent/highlight color.

    0.13.6: use the correct byte order per registry value and try
    Explorer's AccentPalette before falling back to COLOR_HIGHLIGHT.
    """
    try:
        if winreg is not None:
            hkcu = winreg.HKEY_CURRENT_USER
            vbin = read_reg_binary(hkcu, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent", "AccentPalette", None)
            if vbin is not None:
                color = accent_palette_to_hex(vbin, "")
                if color:
                    return color
            for reg_path, value_name, mode in [
                (r"Software\Microsoft\Windows\DWM", "AccentColor", "abgr"),
                (r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent", "AccentColorMenu", "abgr"),
                (r"Software\Microsoft\Windows\DWM", "ColorizationColor", "argb"),
            ]:
                v = read_reg_dword(hkcu, reg_path, value_name, None)
                if v is not None:
                    if mode == "argb":
                        color = dword_argb_to_hex(v, "")
                    else:
                        color = dword_abgr_to_hex(v, "")
                    if color:
                        return color
    except Exception:
        pass
    try:
        if sys.platform == "win32":
            colorref = ctypes.windll.user32.GetSysColor(13)  # COLOR_HIGHLIGHT
            color = colorref_to_hex(colorref, default)
            if color:
                return color
    except Exception:
        pass
    return default

def windows_prefers_dark(default=True):
    """Return modern Windows app theme preference when available.

    AppsUseLightTheme=0 means dark. Missing value means old Windows or classic
    theme; keep the user's manual dark_theme value as fallback.
    """
    try:
        if sys.platform == "win32" and winreg is not None:
            hkcu = winreg.HKEY_CURRENT_USER
            v = read_reg_dword(hkcu, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", None)
            if v is not None:
                return int(v) == 0
    except Exception:
        pass
    return bool(default)


def effective_theme_is_dark(config):
    try:
        cfg = config or {}
        manual = bool(cfg.get("dark_theme", False))
        if bool(cfg.get("follow_windows_theme", True)):
            return windows_prefers_dark(manual)
        return manual
    except Exception:
        return True


def effective_accent_color(config):
    try:
        cfg = config or {}
        if bool(cfg.get("use_windows_accent", True)):
            return windows_accent_color(to_text(cfg.get("accent_color", "#3a6ea5")) or "#3a6ea5")
        value = to_text(cfg.get("accent_color", "#3a6ea5")).strip()
        if re.match(r"^#[0-9a-fA-F]{6}$", value):
            return value
    except Exception:
        pass
    return "#3a6ea5"


def apply_combo_view_theme(combo, dark=True, accent="#3a6ea5"):
    try:
        if hasattr(combo, "set_oldwin_theme"):
            combo.set_oldwin_theme(dark, accent)
    except Exception:
        pass
    """Force popup colors for old Qt4 combo boxes.

    PyQt4/Qt4 sometimes ignores the global stylesheet for QComboBox popups,
    especially disabled model items. This is why the FFmpeg threads popup could
    look empty in dark mode. Apply a direct view stylesheet and palette.
    """
    try:
        view = combo.view()
        if view is None:
            return
        if dark:
            bg = "#1f1f1f"
            fg = "#eeeeee"
            disabled_bg = "#eeeeee"
            disabled_fg = "#555555"
            border = "#555555"
        else:
            bg = "#ffffff"
            fg = "#111111"
            disabled_bg = "#eeeeee"
            disabled_fg = "#999999"
            border = "#a0a0a0"
        view.setStyleSheet("""
QListView {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; outline: 0px; }}
QListView::item {{ min-height: 18px; padding: 2px 4px; background-color: {bg}; color: {fg}; }}
QListView::item:selected {{ background-color: {accent}; color: #ffffff; }}
QListView::item:disabled {{ background-color: {disabled_bg}; color: {disabled_fg}; }}
QListView::item:selected:disabled {{ background-color: {disabled_bg}; color: {disabled_fg}; }}
""".format(bg=bg, fg=fg, border=border, accent=accent, disabled_bg=disabled_bg, disabled_fg=disabled_fg))
        pal = view.palette()
        pal.setColor(QtGui.QPalette.Base, QtGui.QColor(bg))
        pal.setColor(QtGui.QPalette.Text, QtGui.QColor(fg))
        pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor(accent))
        pal.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#ffffff"))
        pal.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(disabled_fg))
        pal.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base, QtGui.QColor(disabled_bg))
        pal.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Window, QtGui.QColor(disabled_bg))
        view.setPalette(pal)
    except Exception:
        pass


def dark_stylesheet(accent="#5a87b8"):
    return """
QMainWindow, QWidget, QDialog {{ background-color: #2b2b2b; color: #e6e6e6; }}
QGroupBox {{ border: 1px solid #555555; margin-top: 8px; padding-top: 8px; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px 0 4px; color: #f0f0f0; }}
QLabel {{ color: #e6e6e6; }}
QLineEdit, QTextEdit, QTreeWidget, QComboBox, QSpinBox {{ background-color: #1f1f1f; color: #eeeeee; border: 1px solid #555555; selection-background-color: {accent}; }}
QComboBox {{ padding: 1px 18px 1px 4px; selection-background-color: {accent}; }}
QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: top right; border-left: 1px solid #555555; width: 20px; background-color: #2b2b2b; }}
/* 0.13.6a: arrow is painted by ThemedComboBox, not by fragile Qt4 CSS triangles. */
QComboBox QAbstractItemView {{ background-color: #1f1f1f; color: #eeeeee; border: 1px solid #555555; selection-background-color: {accent}; selection-color: #ffffff; padding: 0px; outline: 0px; }}
QComboBox QAbstractItemView::item {{ min-height: 18px; padding: 2px 4px; background-color: #1f1f1f; color: #eeeeee; }}
QComboBox QAbstractItemView::item:selected {{ background-color: {accent}; color: #ffffff; }}
QComboBox QAbstractItemView::item:disabled {{ background-color: #eeeeee; color: #555555; }}
QTreeWidget {{ alternate-background-color: #1f1f1f; show-decoration-selected: 1; }}
QTreeWidget::item {{ background-color: #1f1f1f; color: #eeeeee; border: 0px; padding: 2px; }}
QTreeWidget::item:alternate {{ background-color: #1f1f1f; color: #eeeeee; }}
QTreeWidget::item:hover {{ background-color: #2a2a2a; color: #ffffff; }}
QTreeWidget::item:selected {{ background-color: {accent}; color: #ffffff; }}
QTreeView::item {{ background-color: #1f1f1f; color: #eeeeee; }}
QTreeView::item:alternate {{ background-color: #1f1f1f; color: #eeeeee; }}
QTreeView::item:selected {{ background-color: {accent}; color: #ffffff; }}
QHeaderView::section {{ background-color: #3a3a3a; color: #eeeeee; border: 1px solid #555555; padding: 3px; }}
QPushButton {{ background-color: #3a3a3a; color: #eeeeee; border: 1px solid #666666; padding: 3px 6px; }}
QPushButton:hover {{ background-color: #4a4a4a; border-color: {accent}; }}
QPushButton:disabled {{ background-color: #303030; color: #777777; }}
QCheckBox {{ color: #eeeeee; }}
QMenu {{ background-color: #1f1f1f; color: #eeeeee; border: 1px solid #555555; }}
QMenu::item {{ background-color: transparent; padding: 3px 24px 3px 18px; }}
QMenu::item:selected {{ background-color: {accent}; color: #ffffff; }}
QMenu::indicator {{ width: 12px; height: 12px; }}
QProgressBar {{ border: 1px solid #555555; background-color: #1f1f1f; color: #eeeeee; text-align: center; }}
QProgressBar::chunk {{ background-color: {accent}; }}
QStatusBar {{ background-color: #252525; color: #dddddd; }}
""".format(accent=accent)


def light_stylesheet(accent="#3a6ea5"):
    return """
QMainWindow, QWidget, QDialog {{ background-color: #f0f0f0; color: #111111; }}
QGroupBox {{ border: 1px solid #a0a0a0; margin-top: 8px; padding-top: 8px; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px 0 4px; color: #111111; }}
QLabel {{ color: #111111; }}
QLineEdit, QTextEdit, QTreeWidget, QComboBox, QSpinBox {{ background-color: #ffffff; color: #111111; border: 1px solid #a0a0a0; selection-background-color: {accent}; selection-color: #ffffff; }}
QComboBox {{ padding: 1px 18px 1px 4px; selection-background-color: {accent}; }}
QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: top right; border-left: 1px solid #a0a0a0; width: 20px; background-color: #e6e6e6; }}
/* 0.13.6a: arrow is painted by ThemedComboBox, not by fragile Qt4 CSS triangles. */
QComboBox QAbstractItemView {{ background-color: #ffffff; color: #111111; border: 1px solid #a0a0a0; selection-background-color: {accent}; selection-color: #ffffff; padding: 0px; outline: 0px; }}
QComboBox QAbstractItemView::item {{ min-height: 18px; padding: 2px 4px; background-color: #ffffff; color: #111111; }}
QComboBox QAbstractItemView::item:selected {{ background-color: {accent}; color: #ffffff; }}
QComboBox QAbstractItemView::item:disabled {{ background-color: #eeeeee; color: #999999; }}
QTreeWidget {{ alternate-background-color: #f7f7f7; show-decoration-selected: 1; }}
QTreeWidget::item {{ background-color: #ffffff; color: #111111; border: 0px; padding: 2px; }}
QTreeWidget::item:alternate {{ background-color: #f7f7f7; color: #111111; }}
QTreeWidget::item:hover {{ background-color: #e8f0ff; color: #111111; }}
QTreeWidget::item:selected {{ background-color: {accent}; color: #ffffff; }}
QTreeView::item:selected {{ background-color: {accent}; color: #ffffff; }}
QHeaderView::section {{ background-color: #e6e6e6; color: #111111; border: 1px solid #a0a0a0; padding: 3px; }}
QPushButton {{ background-color: #e6e6e6; color: #111111; border: 1px solid #a0a0a0; padding: 3px 6px; }}
QPushButton:hover {{ background-color: #f2f6ff; border-color: {accent}; }}
QPushButton:disabled {{ background-color: #dddddd; color: #999999; }}
QProgressBar {{ border: 1px solid #a0a0a0; background-color: #ffffff; color: #111111; text-align: center; }}
QProgressBar::chunk {{ background-color: {accent}; }}
QStatusBar {{ background-color: #e6e6e6; color: #111111; }}
""".format(accent=accent)

def to_text(value):
    try:
        if value is None:
            return ""
        return str(value)
    except Exception:
        try:
            return unicode(value)  # noqa: F821  # Python 2 fallback if somebody experiments.
        except Exception:
            return ""


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(*parts):
    rel = os.path.join(*parts)
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        p = os.path.join(sys._MEIPASS, rel)
        if os.path.exists(p):
            return p
    return os.path.join(app_dir(), rel)


def ensure_dir(path):
    if path and not os.path.isdir(path):
        os.makedirs(path)


def xp_appdata_base():
    appdata = os.environ.get("APPDATA")
    if appdata:
        return appdata
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        return os.path.join(userprofile, "Application Data")
    return app_dir()


def config_dir():
    portable_flag = os.path.join(app_dir(), "portable_oldwin_pyqt4.flag")
    if os.path.exists(portable_flag):
        return app_dir()
    return os.path.join(xp_appdata_base(), "AdvancedAudioConverter_OldWin")


def legacy_config_dirs():
    return [
        os.path.join(xp_appdata_base(), "AdvancedAudioConverter_OldWin_PyQt4"),
        os.path.join(xp_appdata_base(), "AdvancedAudioConverter_XP"),
        os.path.join(xp_appdata_base(), "AdvancedAudioConverter_XP_PyQt4"),
    ]


def legacy_config_dir():
    dirs = legacy_config_dirs()
    return dirs[0] if dirs else os.path.join(xp_appdata_base(), "AdvancedAudioConverter_OldWin_PyQt4")


DATA_DIR = config_dir()
try:
    ensure_dir(DATA_DIR)
except Exception:
    DATA_DIR = app_dir()

CONFIG_PATH = os.path.join(DATA_DIR, CONFIG_FILE)
RECOVERY_PATH = os.path.join(DATA_DIR, RECOVERY_FILE)
LOG_DIR = os.path.join(DATA_DIR, "logs")
try:
    ensure_dir(LOG_DIR)
except Exception:
    pass

# OldWin migration: previous prerelease builds could store config under XP names.
# Keep user settings if present.
try:
    if not os.path.exists(CONFIG_PATH):
        for old_dir in legacy_config_dirs():
            old_config = os.path.join(old_dir, CONFIG_FILE)
            if os.path.exists(old_config):
                ensure_dir(DATA_DIR)
                shutil.copy2(old_config, CONFIG_PATH)
                break
except Exception:
    pass


def bundled_ffmpeg_path():
    p = resource_path("ffmpeg", "ffmpeg.exe")
    if os.path.exists(p):
        return p
    p = resource_path("ffmpeg.exe")
    if os.path.exists(p):
        return p
    return os.path.join(app_dir(), "ffmpeg", "ffmpeg.exe")


def bundled_ffprobe_path():
    p = resource_path("ffmpeg", "ffprobe.exe")
    if os.path.exists(p):
        return p
    p = resource_path("ffprobe.exe")
    if os.path.exists(p):
        return p
    return os.path.join(app_dir(), "ffmpeg", "ffprobe.exe")


def norm_path(path):
    try:
        return os.path.abspath(to_text(path))
    except Exception:
        return to_text(path)


def norm_key(path):
    return norm_path(path).lower()


def open_path(path):
    try:
        if sys.platform == "win32":
            os.startfile(path)
            return True
        subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False


def format_bytes(num):
    try:
        num = float(num)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if num < 1024:
                return "%.1f %s" % (num, unit)
            num /= 1024.0
        return "%.1f PB" % num
    except Exception:
        return "-"


def format_duration(seconds):
    try:
        seconds = int(float(seconds))
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h:
            return "%02d:%02d:%02d" % (h, m, s)
        return "%02d:%02d" % (m, s)
    except Exception:
        return "-"


def collect_files(paths):
    result = []
    for item in paths:
        if not item:
            continue
        item = norm_path(item)
        if os.path.isfile(item):
            result.append(item)
        elif os.path.isdir(item):
            for root, dirs, files in os.walk(item):
                for name in files:
                    result.append(os.path.join(root, name))
    unique = []
    seen = set()
    for p in result:
        k = norm_key(p)
        if k not in seen:
            seen.add(k)
            unique.append(p)
    return unique


def audio_only(paths):
    return [p for p in collect_files(paths) if os.path.splitext(p)[1].lower() in AUDIO_EXTENSIONS]



class ThemedComboBox(QtGui.QComboBox):
    """QComboBox with a stable painted down-arrow for Qt4/XP-era stylesheets.

    Qt4 stylesheet triangles are unreliable on XP/Vista/Win10 combinations:
    they may show as missing arrows, broken geometry, or white drop-down zones
    in dark theme. This subclass lets Qt draw the normal combo first, then
    paints a clean arrow on top of the drop-down area.
    """
    def __init__(self, *args):
        QtGui.QComboBox.__init__(self, *args)
        self._oldwin_dark = True
        self._oldwin_accent = "#3a6ea5"

    def set_oldwin_theme(self, dark=True, accent="#3a6ea5"):
        try:
            self._oldwin_dark = bool(dark)
            self._oldwin_accent = to_text(accent or "#3a6ea5")
            self.update()
        except Exception:
            pass

    def paintEvent(self, event):
        QtGui.QComboBox.paintEvent(self, event)
        try:
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

            rect = self.rect()
            h = max(18, rect.height())
            drop_w = max(18, min(24, int(h * 0.85)))
            drop_rect = QtCore.QRect(rect.right() - drop_w + 1, rect.top() + 1, drop_w - 2, rect.height() - 2)

            dark = bool(getattr(self, "_oldwin_dark", True))
            enabled = self.isEnabled()

            if dark:
                bg = QtGui.QColor("#2b2b2b") if enabled else QtGui.QColor("#303030")
                border = QtGui.QColor("#555555")
                arrow = QtGui.QColor("#eeeeee") if enabled else QtGui.QColor("#777777")
            else:
                bg = QtGui.QColor("#e6e6e6") if enabled else QtGui.QColor("#eeeeee")
                border = QtGui.QColor("#a0a0a0")
                arrow = QtGui.QColor("#111111") if enabled else QtGui.QColor("#999999")

            painter.fillRect(drop_rect, bg)
            painter.setPen(border)
            painter.drawLine(drop_rect.left(), drop_rect.top(), drop_rect.left(), drop_rect.bottom())

            cx = drop_rect.center().x()
            cy = drop_rect.center().y() + 1
            aw = max(4, min(6, int(h / 5)))
            ah = max(3, min(5, int(h / 6)))
            poly = QtGui.QPolygon()
            poly.append(QtCore.QPoint(cx - aw, cy - ah // 2))
            poly.append(QtCore.QPoint(cx + aw, cy - ah // 2))
            poly.append(QtCore.QPoint(cx, cy + ah))
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(arrow))
            painter.drawPolygon(poly)
            painter.end()
        except Exception:
            pass



def read_process_output(cmd):
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
        out, err = proc.communicate()
        try:
            out = out.decode("utf-8", "ignore")
        except Exception:
            out = to_text(out)
        try:
            err = err.decode("utf-8", "ignore")
        except Exception:
            err = to_text(err)
        return proc.returncode, out, err
    except Exception as exc:
        return 1, "", to_text(exc)


def run_ffprobe_json(path, ffprobe):
    cmd = [ffprobe, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path]
    rc, out, err = read_process_output(cmd)
    if rc == 0 and out.strip():
        try:
            return json.loads(out)
        except Exception:
            return {}
    return {}


def get_audio_stream(probe):
    try:
        for s in probe.get("streams", []):
            if s.get("codec_type") == "audio":
                return s
    except Exception:
        pass
    return {}


def get_duration(probe):
    try:
        audio = get_audio_stream(probe)
        fmt = probe.get("format", {})
        value = audio.get("duration") or fmt.get("duration")
        return float(value) if value else None
    except Exception:
        return None


def detect_bit_depth(audio):
    for key in ("bits_per_raw_sample", "bits_per_sample"):
        value = audio.get(key)
        try:
            if value and str(value) != "N/A" and int(value) > 0:
                return "%d bit" % int(value)
        except Exception:
            pass
    sample_fmt = str(audio.get("sample_fmt", "")).lower()
    mapping = {
        "u8": "8 bit",
        "s16": "16 bit",
        "s16p": "16 bit",
        "s32": "32 bit",
        "s32p": "32 bit",
        "flt": "32 bit float",
        "fltp": "32 bit float",
        "dbl": "64 bit float",
        "dblp": "64 bit float",
    }
    if sample_fmt in mapping:
        return mapping[sample_fmt]
    if "s24" in sample_fmt:
        return "24 bit"
    return "-"


def analyze_file(path, ffprobe):
    info = {
        "format": os.path.splitext(path)[1].lower().replace(".", "").upper() or "-",
        "codec": "-",
        "bitrate": "-",
        "sample": "-",
        "channels": "-",
        "duration": "-",
        "size": "-",
        "status": "Not analyzed",
        "duration_sec": None,
        "size_bytes": 0,
    }
    try:
        size = os.path.getsize(path)
        info["size_bytes"] = size
        info["size"] = format_bytes(size)
    except Exception:
        size = 0
    probe = run_ffprobe_json(path, ffprobe)
    if not probe:
        info["status"] = "Probe failed"
        return info
    fmt = probe.get("format", {})
    audio = get_audio_stream(probe)
    if fmt.get("format_name"):
        info["format"] = str(fmt.get("format_name", "-")).split(",")[0].upper()
    if audio.get("codec_name"):
        info["codec"] = str(audio.get("codec_name", "-")).upper()
    bitrate = audio.get("bit_rate") or fmt.get("bit_rate")
    duration = audio.get("duration") or fmt.get("duration")
    if bitrate:
        try:
            info["bitrate"] = "%d kbps" % (int(float(bitrate)) // 1000)
        except Exception:
            info["bitrate"] = str(bitrate)
    elif duration and size:
        try:
            info["bitrate"] = "%d kbps*" % int((size * 8) / float(duration) / 1000)
        except Exception:
            pass
    sr = audio.get("sample_rate")
    depth = detect_bit_depth(audio)
    if sr and depth != "-":
        info["sample"] = "%s Hz / %s" % (sr, depth)
    elif sr:
        info["sample"] = "%s Hz" % sr
    if audio.get("channels"):
        info["channels"] = str(audio.get("channels"))
    if duration:
        info["duration"] = format_duration(duration)
        try:
            info["duration_sec"] = float(duration)
        except Exception:
            pass
    info["status"] = "OK"
    return info


def get_album_art_stream_index(probe):
    try:
        for stream in probe.get("streams", []):
            if stream.get("codec_type") != "video":
                continue
            disposition = stream.get("disposition") or {}
            try:
                if int(disposition.get("attached_pic", 0) or 0) == 1:
                    return stream.get("index")
            except Exception:
                pass
    except Exception:
        pass
    return None


def normalize_sample_rate(fmt, sr):
    if not sr or sr == "Original":
        return sr
    value = sr.replace(" Hz", "")
    if fmt == "mp3" and value not in set(["8000", "11025", "12000", "16000", "22050", "24000", "32000", "44100", "48000"]):
        return "48000 Hz"
    return sr


def shape_args(fmt, sr, channels):
    args = []
    sr = normalize_sample_rate(fmt, sr)
    if sr and sr != "Original":
        args.extend(["-ar", sr.replace(" Hz", "")])
    if channels == "Stereo":
        args.extend(["-ac", "2"])
    elif channels == "Mono":
        args.extend(["-ac", "1"])
    return args


def codec_extra_args(fmt, quality, sr, channels):
    quality = quality_value_from_display(quality)
    q = "lossless" if quality == "Lossless / Best" else quality
    args = shape_args(fmt, sr, channels)
    if fmt == "wav":
        return args
    if fmt == "flac":
        return ["-compression_level", "8" if q == "lossless" else "5"] + args
    if fmt == "opus":
        return ["-b:a", "256k" if q == "lossless" else q] + args
    if fmt == "aac":
        return ["-b:a", "320k" if q == "lossless" else q] + args + ["-movflags", "+faststart"]
    if fmt == "ogg":
        if q == "lossless":
            return ["-q:a", "10"] + args
        return ["-b:a", q] + args
    if fmt == "mp3":
        return ["-b:a", "320k" if q == "lossless" else q] + args
    return args


def detect_system_language():
    try:
        lang = locale.getdefaultlocale()[0] or ""
    except Exception:
        lang = ""
    lang = lang.lower()
    if lang.startswith("de"):
        return "de"
    if lang.startswith("uk") or lang.startswith("ua"):
        return "uk"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def system_cpu_count():
    try:
        import multiprocessing
        count = multiprocessing.cpu_count()
        if count and int(count) > 0:
            return int(count)
    except Exception:
        pass
    try:
        count = int(os.environ.get("NUMBER_OF_PROCESSORS", "1"))
        if count > 0:
            return count
    except Exception:
        pass
    return 1


def ffmpeg_thread_limit():
    """OldWin safe thread cap: 1..4, never above detected logical CPU threads."""
    try:
        return max(1, min(4, int(system_cpu_count())))
    except Exception:
        return 1


def ffmpeg_thread_items_for_cpu():
    """Return all visible FFmpeg thread menu values.

    0.13.5 policy:
      - show 1, 2, 3, 4 everywhere;
      - user may select every value up to detected CPU thread limit;
      - values above the limit are disabled and highlighted in the popup.
    """
    return ["1", "2", "3", "4"]


def normalize_ffmpeg_threads(value):
    try:
        value = int(to_text(value).strip())
    except Exception:
        value = ffmpeg_thread_limit()
    limit = ffmpeg_thread_limit()
    if value < 1:
        value = 1
    if value > 4:
        value = 4
    if value > limit:
        value = limit
    return str(value)


def hidden_startupinfo():
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return si
    except Exception:
        return None


def decode_windows_command_bytes(data):
    """Decode output from old Windows command-line tools.

    WMIC often writes UTF-16LE, while some localized systems use OEM code pages.
    Decoding with ANSI/mbcs first produced mojibake like:
        Њ ©Єа®б®дв Windows 10 Pro
    0.13.6a detects UTF-16 and then tries OEM pages before ANSI.
    """
    try:
        if not data:
            return ""
        if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
            try:
                return data.decode("utf-16", "replace")
            except Exception:
                pass
        sample = data[:200]
        try:
            if b"\x00" in sample:
                return data.decode("utf-16le", "replace")
        except Exception:
            pass
        encodings = []
        for enc in ["utf-8-sig", "cp866", "cp850", "mbcs", locale.getpreferredencoding(False), "cp1251", "latin1"]:
            if enc and enc not in encodings:
                encodings.append(enc)
        best_text = None
        best_score = -999999
        bad_chars = set(list(u"ЊЌЋЏџЄє©®њќћџ"))
        for enc in encodings:
            try:
                text = data.decode(enc, "replace")
            except Exception:
                continue
            score = 0
            score += text.count("=") * 5
            score += text.lower().count("windows") * 20
            score += text.lower().count("microsoft") * 10
            score -= text.count("\ufffd") * 100
            score -= text.count("\x00") * 100
            score -= sum(1 for ch in text if ch in bad_chars) * 10
            if score > best_score:
                best_score = score
                best_text = text
        if best_text is not None:
            return best_text
    except Exception:
        pass
    try:
        return to_text(data)
    except Exception:
        return ""


def command_output_text(args, timeout_sec=4):
    try:
        si = hidden_startupinfo()
        kwargs = {"stderr": subprocess.STDOUT}
        if si is not None:
            kwargs["startupinfo"] = si
        # Python 3.4 has no subprocess timeout parameter. WMIC calls here are
        # small and local; if WMIC is broken, the exception fallback is used.
        data = subprocess.check_output(args, **kwargs)
        return decode_windows_command_bytes(data)
    except Exception:
        return ""


def parse_wmic_value_blocks(text, expected_fields=None):
    """Parse `wmic ... /value` output robustly.

    WMIC often prints blank lines between individual properties, not only
    between objects. Older parser split on every blank line, so OS/CPU/RAM
    became incomplete: e.g. one RAM stick could appear as four fake modules.
    0.13.6 ignores blank lines and starts a new object when a key repeats.
    """
    blocks = []
    current = {}
    expected = set(expected_fields or [])
    for raw in to_text(text).splitlines():
        line = raw.strip()
        if not line:
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        if k in current and current:
            blocks.append(current)
            current = {}
        current[k] = v
        if expected and len([x for x in expected if x in current]) >= len(expected):
            # Keep reading; next repeated key will start next block. Do not split
            # immediately because WMIC may omit some expected fields.
            pass
    if current:
        blocks.append(current)
    return blocks

def wmic_value_blocks(alias, fields):
    try:
        args = ["wmic", alias, "get", ",".join(fields), "/value"]
        return parse_wmic_value_blocks(command_output_text(args), fields)
    except Exception:
        return []


def first_nonempty(mapping, keys, default="Unknown"):
    for key in keys:
        try:
            val = to_text(mapping.get(key, "")).strip()
            if val:
                return val
        except Exception:
            pass
    return default


def format_bytes_gb(value):
    try:
        n = float(value)
        if n <= 0:
            raise ValueError()
        gb = n / (1024.0 ** 3)
        if gb >= 10:
            return "%.0f GB" % gb
        return "%.1f GB" % gb
    except Exception:
        return "Unknown"


def format_mhz(value):
    try:
        n = int(float(to_text(value).strip()))
        if n <= 0:
            raise ValueError()
        if n >= 1000:
            return "%d MHz (%.2f GHz)" % (n, n / 1000.0)
        return "%d MHz" % n
    except Exception:
        return "Unknown"


def unique_nonempty(values):
    out = []
    seen = set()
    for value in values:
        text = to_text(value).strip()
        if not text:
            continue
        key = text.lower()
        if key not in seen:
            seen.add(key)
            out.append(text)
    return out




def registry_windows_info():
    out = {}
    try:
        if sys.platform != "win32" or winreg is None:
            return out
        hklm = winreg.HKEY_LOCAL_MACHINE
        path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        accesses = [0]
        try:
            accesses.append(winreg.KEY_WOW64_64KEY)
        except Exception:
            pass
        for acc in accesses:
            for key, reg_name in [
                ("ProductName", "ProductName"),
                ("EditionID", "EditionID"),
                ("DisplayVersion", "DisplayVersion"),
                ("ReleaseId", "ReleaseId"),
                ("CurrentVersion", "CurrentVersion"),
                ("CurrentBuildNumber", "CurrentBuildNumber"),
                ("BuildLabEx", "BuildLabEx"),
                ("CSDVersion", "CSDVersion"),
                ("CurrentMajorVersionNumber", "CurrentMajorVersionNumber"),
                ("CurrentMinorVersionNumber", "CurrentMinorVersionNumber"),
                ("UBR", "UBR"),
            ]:
                if not out.get(key):
                    value = read_reg_string(hklm, path, reg_name, "", acc)
                    if value:
                        out[key] = value
    except Exception:
        pass
    return out


def registry_cpu_info():
    out = {}
    try:
        if sys.platform != "win32" or winreg is None:
            return out
        hklm = winreg.HKEY_LOCAL_MACHINE
        base = r"HARDWARE\DESCRIPTION\System\CentralProcessor"
        logical_count = 0
        try:
            key = winreg.OpenKey(hklm, base)
            try:
                while True:
                    try:
                        winreg.EnumKey(key, logical_count)
                        logical_count += 1
                    except Exception:
                        break
            finally:
                try:
                    winreg.CloseKey(key)
                except Exception:
                    pass
        except Exception:
            pass
        path0 = base + r"\0"
        name = read_reg_string(hklm, path0, "ProcessorNameString", "")
        vendor = read_reg_string(hklm, path0, "VendorIdentifier", "")
        mhz = read_reg_value(hklm, path0, "~MHz", "")
        if name:
            out["Name"] = name
        if vendor:
            out["Manufacturer"] = vendor
        if mhz not in (None, ""):
            out["CurrentClockSpeed"] = to_text(mhz)
        if logical_count:
            out["NumberOfLogicalProcessors"] = to_text(logical_count)
    except Exception:
        pass
    return out


def merge_missing(base_map, fallback_map):
    try:
        for k, v in (fallback_map or {}).items():
            if not to_text(base_map.get(k, "")).strip() and to_text(v).strip():
                base_map[k] = v
    except Exception:
        pass
    return base_map

def collect_system_info():
    info = {}
    try:
        os_blocks = wmic_value_blocks("os", ["Caption", "Version", "BuildNumber", "OSArchitecture", "CSDVersion", "ServicePackMajorVersion", "ServicePackMinorVersion"])
        info["os"] = os_blocks[0] if os_blocks else {}
    except Exception:
        info["os"] = {}
    try:
        reg_os = registry_windows_info()
        if reg_os:
            mapped = {}
            if reg_os.get("ProductName"):
                # Prefer registry ProductName over WMIC Caption to avoid localized
                # WMIC mojibake on Russian/legacy code pages.
                mapped["Caption"] = reg_os.get("ProductName")
            major = to_text(reg_os.get("CurrentMajorVersionNumber", "")).strip()
            minor = to_text(reg_os.get("CurrentMinorVersionNumber", "")).strip()
            build_no = to_text(reg_os.get("CurrentBuildNumber", "")).strip()
            if major and minor and build_no:
                mapped["Version"] = "%s.%s.%s" % (major, minor, build_no)
            elif reg_os.get("CurrentVersion"):
                mapped["Version"] = reg_os.get("CurrentVersion")
            if reg_os.get("CurrentBuildNumber"):
                mapped["BuildNumber"] = reg_os.get("CurrentBuildNumber")
            if reg_os.get("CSDVersion"):
                mapped["CSDVersion"] = reg_os.get("CSDVersion")
            mapped["EditionID"] = reg_os.get("EditionID", "")
            mapped["DisplayVersion"] = reg_os.get("DisplayVersion", "") or reg_os.get("ReleaseId", "")
            base_os = info.get("os", {}) or {}
            base_os = merge_missing(base_os, mapped)
            # Force these registry fields after merge; they are less likely to
            # be mojibake than WMIC on localized Windows.
            for force_key in ["Caption", "Version", "BuildNumber", "EditionID", "DisplayVersion"]:
                if to_text(mapped.get(force_key, "")).strip():
                    base_os[force_key] = mapped[force_key]
            info["os"] = base_os
    except Exception:
        pass
    try:
        cs_blocks = wmic_value_blocks("computersystem", ["Manufacturer", "Model", "TotalPhysicalMemory"])
        info["computer"] = cs_blocks[0] if cs_blocks else {}
    except Exception:
        info["computer"] = {}
    try:
        cpu_blocks = wmic_value_blocks("cpu", ["Manufacturer", "Name", "NumberOfCores", "NumberOfLogicalProcessors", "MaxClockSpeed", "CurrentClockSpeed"])
        info["cpu"] = cpu_blocks[0] if cpu_blocks else {}
    except Exception:
        info["cpu"] = {}
    try:
        info["cpu"] = merge_missing(info.get("cpu", {}) or {}, registry_cpu_info())
    except Exception:
        pass
    try:
        mem_blocks = wmic_value_blocks("memorychip", ["Manufacturer", "Capacity", "Speed", "ConfiguredClockSpeed"])
        info["memory"] = mem_blocks or []
    except Exception:
        info["memory"] = []
    return info



def clean_os_caption(caption):
    text = to_text(caption).strip()
    if not text:
        return "Windows"
    try:
        idx = text.lower().find("windows")
        if idx > 0:
            prefix = text[:idx].strip()
            # Correct English "Microsoft Windows" is fine, but mojibake/localized
            # vendor prefixes from WMIC are not useful. Keep the actual Windows
            # product name from the first "Windows" token.
            if "microsoft" not in prefix.lower():
                text = text[idx:].strip()
    except Exception:
        pass
    # Remove common mojibake vendor fragments if they still survived.
    try:
        text = re.sub(u"^[ЊЌЋЏџЄє©®њќћџ\\s]+", "", text).strip()
    except Exception:
        pass
    return text or "Windows"


def should_show_edition(caption, edition):
    edition = to_text(edition).strip()
    if not edition or edition == "Unknown":
        return False
    low = to_text(caption).lower()
    edlow = edition.lower()
    if edlow in low:
        return False
    known = [" home", " pro", " professional", " enterprise", " education", " ultimate", " starter", " server"]
    if any(k in low for k in known):
        # Caption already contains a human-readable edition. Avoid contradictory
        # output like "Windows 10 Pro | edition Enterprise".
        return False
    return True




def clean_pc_vendor(vendor):
    text = to_text(vendor).strip()
    low = text.lower()
    if "micro-star" in low or low in ("msi", "micro star"):
        return "MSI"
    if "gigabyte" in low:
        return "Gigabyte"
    if "asustek" in low or low == "asus":
        return "ASUS"
    if "hewlett-packard" in low or low == "hp":
        return "HP"
    if "lenovo" in low:
        return "Lenovo"
    if "dell" in low:
        return "Dell"
    if "acer" in low:
        return "Acer"
    return text or "Unknown"


def clean_pc_model(model):
    text = to_text(model).strip()
    if not text:
        return "Unknown"
    bad = ["System Product Name", "To Be Filled By O.E.M.", "To Be Filled By OEM", "Default string", "Unknown"]
    for b in bad:
        if text.lower() == b.lower():
            return "Unknown"
    return text


def clean_cpu_vendor(vendor, cpu_name=""):
    text = to_text(vendor).strip()
    name = to_text(cpu_name)
    low = text.lower()
    if low in ("genuineintel", "intel64 family", "intel"):
        return ""
    if low in ("authenticamd", "amd"):
        return ""
    # If the CPU name already starts with Intel/AMD, vendor is redundant.
    nlow = name.lower().strip()
    if nlow.startswith("intel") or nlow.startswith("amd"):
        return ""
    return text


def clean_cpu_name(name):
    text = to_text(name).strip()
    if not text:
        return "Unknown"
    text = text.replace("(R)", "").replace("(TM)", "").replace("(tm)", "").replace("(r)", "")
    text = text.replace(" CPU ", " ")
    text = text.replace("Processor", "")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"@\s*([0-9]+(?:\.[0-9]+)?)\s*GHz", r"@ \1 GHz", text, flags=re.I)
    text = text.replace("  ", " ").strip()
    return text or "Unknown"


def compact_frequency_text(value):
    text = format_mhz(value)
    text = to_text(text)
    m = re.search(r"\(([^()]+GHz)\)", text, re.I)
    if m:
        return m.group(1).replace("GHz", "GHz").replace(" ", " ")
    return text


def format_cpu_line(vendor, name):
    vendor = clean_cpu_vendor(vendor, name)
    name = clean_cpu_name(name)
    if vendor and vendor.lower() not in name.lower():
        return "%s %s" % (vendor, name)
    return name


def format_pc_line(vendor, model):
    vendor = clean_pc_vendor(vendor)
    model = clean_pc_model(model)
    if model == "Unknown":
        return vendor
    if vendor == "Unknown":
        return model
    if model.lower().startswith(vendor.lower()):
        return model
    return "%s %s" % (vendor, model)


def nice_unknown_list(values):
    clean = unique_nonempty(values)
    clean = [to_text(x).strip() for x in clean if to_text(x).strip() and to_text(x).strip().lower() != "unknown"]
    return clean or ["Unknown"]



def system_info_lines():
    data = collect_system_info()
    lines = []
    os_info = data.get("os", {}) or {}
    comp = data.get("computer", {}) or {}
    cpu = data.get("cpu", {}) or {}
    mem = data.get("memory", []) or []

    caption = clean_os_caption(first_nonempty(os_info, ["Caption"], "Windows"))
    edition = first_nonempty(os_info, ["EditionID"], "")
    display_version = first_nonempty(os_info, ["DisplayVersion"], "")
    version = first_nonempty(os_info, ["Version"], "Unknown")
    build = first_nonempty(os_info, ["BuildNumber"], "Unknown")
    arch = first_nonempty(os_info, ["OSArchitecture"], "Unknown")
    sp = first_nonempty(os_info, ["CSDVersion"], "")
    if arch == "Unknown":
        try:
            arch = "64-bit" if "64" in os.environ.get("PROCESSOR_ARCHITECTURE", "") or os.environ.get("PROCESSOR_ARCHITEW6432") else "32-bit"
        except Exception:
            pass
    os_tail = []
    if should_show_edition(caption, edition):
        os_tail.append("edition %s" % edition)
    if display_version:
        os_tail.append("release %s" % display_version)
    os_tail.append("version %s" % version)
    os_tail.append("build %s" % build)
    os_tail.append(arch)
    if sp:
        lines.append("OS: %s %s | %s" % (caption, sp, " | ".join(os_tail)))
    else:
        lines.append("OS: %s | %s" % (caption, " | ".join(os_tail)))

    pc_vendor = first_nonempty(comp, ["Manufacturer"], "Unknown")
    pc_model = first_nonempty(comp, ["Model"], "Unknown")
    lines.append("Computer: %s" % format_pc_line(pc_vendor, pc_model))

    cpu_vendor = first_nonempty(cpu, ["Manufacturer"], "Unknown")
    cpu_name = first_nonempty(cpu, ["Name"], "Unknown")
    if cpu_vendor == "Unknown":
        env_id = os.environ.get("PROCESSOR_IDENTIFIER", "")
        if "GenuineIntel" in env_id:
            cpu_vendor = "GenuineIntel"
        elif "AuthenticAMD" in env_id:
            cpu_vendor = "AuthenticAMD"
    if cpu_name == "Unknown":
        env_id = os.environ.get("PROCESSOR_IDENTIFIER", "")
        if env_id:
            cpu_name = env_id
    cores = first_nonempty(cpu, ["NumberOfCores"], "Unknown")
    logical = first_nonempty(cpu, ["NumberOfLogicalProcessors"], str(system_cpu_count()))
    max_clock = first_nonempty(cpu, ["MaxClockSpeed"], "")
    cur_clock = first_nonempty(cpu, ["CurrentClockSpeed"], "")
    if not cur_clock:
        cur_clock = max_clock
    overclock = "not detected"
    try:
        max_mhz = int(float(max_clock))
        cur_mhz = int(float(cur_clock))
        if max_mhz > 0 and cur_mhz > int(max_mhz * 1.05):
            overclock = "possible / current clock above nominal"
    except Exception:
        overclock = "unknown"
    lines.append("CPU: %s" % format_cpu_line(cpu_vendor, cpu_name))
    lines.append("CPU cores/threads: %s cores / %s threads" % (cores, logical))
    lines.append("CPU clock: %s current | %s nominal/max | overclock: %s" % (compact_frequency_text(cur_clock), compact_frequency_text(max_clock), overclock))

    total_ram = first_nonempty(comp, ["TotalPhysicalMemory"], "")
    module_total = 0
    clean_mem = []
    for block in mem:
        if not isinstance(block, dict):
            continue
        if not any([to_text(block.get("Capacity", "")).strip(), to_text(block.get("Manufacturer", "")).strip(), to_text(block.get("Speed", "")).strip(), to_text(block.get("ConfiguredClockSpeed", "")).strip()]):
            continue
        clean_mem.append(block)
        try:
            module_total += int(float(first_nonempty(block, ["Capacity"], "0")))
        except Exception:
            pass
    ram_total_text = format_bytes_gb(total_ram or module_total)
    manufacturers = nice_unknown_list([m.get("Manufacturer", "") for m in clean_mem])
    speeds = nice_unknown_list([m.get("ConfiguredClockSpeed", "") or m.get("Speed", "") for m in clean_mem])
    speed_text = ", ".join([("%s MHz" % x) if to_text(x).isdigit() else to_text(x) for x in speeds])
    lines.append("RAM: %s total | %s | %s" % (ram_total_text, ", ".join(manufacturers), speed_text))
    if clean_mem:
        for i, block in enumerate(clean_mem, 1):
            mfr = first_nonempty(block, ["Manufacturer"], "Unknown")
            cap = format_bytes_gb(first_nonempty(block, ["Capacity"], ""))
            spd = first_nonempty(block, ["ConfiguredClockSpeed", "Speed"], "Unknown")
            if to_text(spd).isdigit():
                spd = "%s MHz" % spd
            lines.append("RAM module %d: %s | %s | %s" % (i, cap, mfr, spd))
    return lines

def bounded_int(value, default_value, minimum, maximum):
    try:
        value = int(value)
    except Exception:
        value = int(default_value)
    if value < minimum:
        value = minimum
    if value > maximum:
        value = maximum
    return value

def default_config():
    return {
        "output_format": "mp3",
        "quality": "192k",
        "preset": "Custom",
        "sample_rate": "44100 Hz",
        "channels": "Stereo",
        "conflict": "Rename",
        "keep_metadata": True,
        "preserve_structure": False,
        "open_output_when_done": False,
        "custom_output_folder": "",
        "ffmpeg_threads": "1",
        "language": detect_system_language(),
        "auto_analyze_on_add": True,
        "dark_theme": False,
        "follow_windows_theme": True,
        "use_windows_accent": True,
        "accent_color": windows_accent_color(),
        "ui_scale": 80,
        "list_height": 220,
        "log_height": 90,
        "sound_enabled": True,
        "custom_ffmpeg_path": "",
        "custom_ffprobe_path": "",
        "confirm_stop": True,
        "confirm_external_open": False,
        "safe_output_checks": True,
        "warn_huge_batch": True,
        "huge_batch_limit": 250,
        "path_length_warning": True,
    }


def load_config():
    cfg = default_config()
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                cfg.update(data)
    except Exception:
        pass
    try:
        if "compact_ui" in cfg:
            del cfg["compact_ui"]
    except Exception:
        pass
    cfg["follow_windows_theme"] = bool(cfg.get("follow_windows_theme", True))
    cfg["use_windows_accent"] = bool(cfg.get("use_windows_accent", True))
    cfg["dark_theme"] = bool(cfg.get("dark_theme", False))
    if not to_text(cfg.get("accent_color", "")).strip():
        cfg["accent_color"] = windows_accent_color()
    cfg["list_height"] = bounded_int(cfg.get("list_height", 220), 220, 100, 420)
    cfg["log_height"] = bounded_int(cfg.get("log_height", 90), 90, 60, 260)
    cfg["ffmpeg_threads"] = normalize_ffmpeg_threads(cfg.get("ffmpeg_threads", "1"))
    cfg["quality"] = quality_value_from_display(cfg.get("quality", "192k"))
    return cfg


def save_config(cfg):
    try:
        ensure_dir(os.path.dirname(CONFIG_PATH))
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


def get_effective_ffmpeg_path(settings=None):
    settings = settings or {}
    custom = to_text(settings.get("custom_ffmpeg_path", "")).strip().strip('"')
    if custom and os.path.isfile(custom):
        return custom
    return bundled_ffmpeg_path()


def get_effective_ffprobe_path(settings=None):
    settings = settings or {}
    custom = to_text(settings.get("custom_ffprobe_path", "")).strip().strip('"')
    if custom and os.path.isfile(custom):
        return custom
    return bundled_ffprobe_path()


def is_dangerous_output_folder(path):
    try:
        p = os.path.abspath(path).rstrip("\\/").lower()
        dangerous = []
        system_drive = os.environ.get("SystemDrive", "C:")
        windir = os.environ.get("WINDIR", os.path.join(system_drive, "Windows"))
        dangerous.append(os.path.abspath(system_drive + "\\").rstrip("\\/").lower())
        dangerous.append(os.path.abspath(windir).rstrip("\\/").lower())
        pf = os.environ.get("ProgramFiles")
        if pf:
            dangerous.append(os.path.abspath(pf).rstrip("\\/").lower())
        pf86 = os.environ.get("ProgramFiles(x86)")
        if pf86:
            dangerous.append(os.path.abspath(pf86).rstrip("\\/").lower())
        return p in dangerous
    except Exception:
        return False


def get_output_base_for_paths(input_paths, custom_output_folder):
    custom = to_text(custom_output_folder).strip()
    if custom:
        return custom
    if not input_paths:
        return None
    first = norm_path(input_paths[0])
    if os.path.isfile(first):
        return os.path.dirname(first)
    return first


def estimate_long_path_warning(files, base, fmt):
    try:
        ext = OUTPUT_FORMATS.get(fmt, OUTPUT_FORMATS["mp3"])["extension"]
        for src in files:
            name = os.path.splitext(os.path.basename(src))[0] + ext
            candidate = os.path.join(base, "Converted_%s_TIMESTAMP" % fmt.upper(), name)
            if len(candidate) > 240:
                return True
    except Exception:
        pass
    return False


def list_index(items, value, default_index=0):
    try:
        return items.index(value)
    except Exception:
        return default_index


def qstring_to_text(value):
    try:
        return str(value)
    except Exception:
        return to_text(value)


def variant_to_text(value):
    try:
        if hasattr(value, "toString"):
            return qstring_to_text(value.toString())
    except Exception:
        pass
    return qstring_to_text(value)


def quality_display(value, language=None):
    raw = qstring_to_text(value).strip()
    normalized = quality_value_from_display(raw)
    lang = language or detect_system_language()
    if normalized == "Lossless / Best":
        return translate(lang, "quality_lossless_best")
    m = re.match(r"^(\d+)\s*k$", normalized, re.I)
    if m:
        if lang in ("ru", "uk"):
            return "%s кбит/с" % m.group(1)
        return "%s kbps" % m.group(1)
    return raw


def quality_value_from_display(value):
    text = qstring_to_text(value).strip()
    low = text.lower()
    if low in ("lossless / best", "lossless", "best", "без потерь / лучшее", "без потерь", "без втрат / найкраще", "без втрат", "verlustfrei / beste", "verlustfrei"):
        return "Lossless / Best"
    m = re.search(r"(\d+)\s*(?:kbit/s|kbps|кбит/с|кбіт/с|k)\b", low, re.I)
    if m:
        return "%sk" % m.group(1)
    if re.match(r"^\d+$", low):
        return "%sk" % low
    if text in QUALITY_PRESETS:
        return text
    return text


class AnalyzeThread(QtCore.QThread):
    rowAnalyzed = QtCore.pyqtSignal(str, object)
    progressChanged = QtCore.pyqtSignal(int)
    logMessage = QtCore.pyqtSignal(str)
    finishedOk = QtCore.pyqtSignal()

    def __init__(self, files, ffprobe, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.files = list(files)
        self.ffprobe = ffprobe

    def run(self):
        total = len(self.files)
        if total <= 0:
            self.finishedOk.emit()
            return
        for i, path in enumerate(self.files, 1):
            try:
                info = analyze_file(path, self.ffprobe)
                self.rowAnalyzed.emit(path, info)
                self.progressChanged.emit(int(round((float(i) / float(total)) * 100.0)))
            except Exception as exc:
                self.logMessage.emit("Analysis error for %s: %s" % (os.path.basename(path), exc))
        self.progressChanged.emit(100)
        self.finishedOk.emit()


class ConvertThread(QtCore.QThread):
    logMessage = QtCore.pyqtSignal(str)
    errorDetail = QtCore.pyqtSignal(str, str)
    currentFile = QtCore.pyqtSignal(str)
    currentFilePath = QtCore.pyqtSignal(str)
    fileProgress = QtCore.pyqtSignal(int)
    fileProgressPath = QtCore.pyqtSignal(str, int)
    overallProgress = QtCore.pyqtSignal(int)
    statsChanged = QtCore.pyqtSignal(int, int, int, int, str)
    outputFolderReady = QtCore.pyqtSignal(str)
    sizeReportReady = QtCore.pyqtSignal(object)
    finishedOk = QtCore.pyqtSignal(bool)

    def __init__(self, input_paths, settings, dry_run=False, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.input_paths = list(input_paths)
        self.settings = dict(settings)
        self.dry_run = bool(dry_run)
        self.stop_requested = False
        self.process = None
        self.ffmpeg = get_effective_ffmpeg_path(self.settings)
        self.ffprobe = get_effective_ffprobe_path(self.settings)

    def stop(self):
        self.stop_requested = True
        try:
            if self.process is not None and self.process.poll() is None:
                self.process.terminate()
                time.sleep(0.2)
                if self.process.poll() is None:
                    self.process.kill()
        except Exception:
            pass

    def make_output_folder(self):
        custom = self.settings.get("custom_output_folder", "").strip()
        if custom:
            base = custom
        else:
            first = self.input_paths[0]
            base = os.path.dirname(first) if os.path.isfile(first) else first
        name = "Converted_%s_%s" % (self.settings.get("output_format", "mp3").upper(), datetime.now().strftime("%Y%m%d_%H%M%S"))
        out = os.path.join(base, name)
        ensure_dir(out)
        return out

    def relative_parent(self, path):
        if not self.settings.get("preserve_structure"):
            return ""
        ap = norm_path(path)
        for source in self.input_paths:
            src = norm_path(source)
            if os.path.isdir(src):
                try:
                    rel = os.path.relpath(os.path.dirname(ap), src)
                    if rel == "." or rel.startswith(".."):
                        continue
                    return rel
                except Exception:
                    pass
        return ""

    def build_command(self, src, dst, probe):
        fmt = self.settings.get("output_format", "mp3")
        quality = self.settings.get("quality", "192k")
        cfg = OUTPUT_FORMATS[fmt]

        metadata_args = ["-map_metadata", "0"] if self.settings.get("keep_metadata") else ["-map_metadata", "-1"]
        map_args = ["-map", "0:a:0", "-sn", "-dn"]
        video_args = ["-vn"]

        filter_args = []

        thread_args = []
        threads = normalize_ffmpeg_threads(self.settings.get("ffmpeg_threads", "1"))
        if threads:
            thread_args = ["-threads", threads]

        cmd = [self.ffmpeg, "-y", "-i", src]
        cmd += map_args
        cmd += metadata_args
        cmd += filter_args
        cmd += ["-codec:a", cfg["codec"]]
        cmd += thread_args
        cmd += codec_extra_args(fmt, quality, self.settings.get("sample_rate", "44100 Hz"), self.settings.get("channels", "Stereo"))
        cmd += video_args
        cmd += ["-progress", "pipe:1", "-nostats", dst]
        return cmd

    def convert_one(self, src, out_dir, index, total):
        fmt = self.settings.get("output_format", "mp3")
        ext = OUTPUT_FORMATS[fmt]["extension"]
        if os.path.splitext(src)[1].lower() == ext:
            self.currentFilePath.emit(src)
            self.fileProgressPath.emit(src, 100)
            self.logMessage.emit("%s skipped: already %s" % (os.path.basename(src), fmt))
            return "skipped", 0

        rel = self.relative_parent(src)
        final_dir = os.path.join(out_dir, rel) if rel else out_dir
        ensure_dir(final_dir)
        base = os.path.splitext(os.path.basename(src))[0]
        dst = os.path.join(final_dir, base + ext)

        if os.path.exists(dst):
            mode = self.settings.get("conflict", "Rename")
            if mode == "Skip":
                self.currentFilePath.emit(src)
                self.fileProgressPath.emit(src, 100)
                self.logMessage.emit("%s skipped: target exists" % os.path.basename(src))
                return "skipped", 0
            if mode != "Overwrite":
                n = 1
                while os.path.exists(dst):
                    dst = os.path.join(final_dir, "%s_%d%s" % (base, n, ext))
                    n += 1

        probe = run_ffprobe_json(src, self.ffprobe)
        duration = get_duration(probe)
        self.currentFile.emit("[%d/%d] %s" % (index, total, os.path.basename(src)))
        self.currentFilePath.emit(src)
        self.fileProgress.emit(0)
        self.fileProgressPath.emit(src, 0)
        self.logMessage.emit("[%d/%d] converting: %s -> %s" % (index, total, os.path.basename(src), os.path.basename(dst)))

        if self.dry_run:
            self.logMessage.emit("[DRY RUN] %s" % os.path.basename(src))
            return "converted", 0

        cmd = self.build_command(src, dst, probe)
        err_path = None
        rc = 1
        try:
            fd, err_path = tempfile.mkstemp(suffix=".ffmpeg.log")
            os.close(fd)
            err_file = open(err_path, "w", encoding="utf-8", errors="ignore")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=err_file,
                universal_newlines=True,
                creationflags=CREATE_NO_WINDOW,
            )
            last = 0.0
            if self.process.stdout:
                for line in self.process.stdout:
                    if self.stop_requested:
                        try:
                            self.process.terminate()
                        except Exception:
                            pass
                        break
                    line = line.strip()
                    if duration and line.startswith("out_time_ms="):
                        try:
                            cur = int(line.split("=", 1)[1]) / 1000000.0
                            if cur > last:
                                pct = int(min(100.0, (cur / duration) * 100.0))
                                self.fileProgress.emit(pct)
                                self.fileProgressPath.emit(src, pct)
                                last = cur
                        except Exception:
                            pass
            self.process.wait()
            rc = self.process.returncode
            err_file.close()
        except Exception as exc:
            self.errorDetail.emit(os.path.basename(src), traceback.format_exc())
            self.logMessage.emit("%s failed: %s" % (os.path.basename(src), exc))
            return "failed", 0
        finally:
            self.process = None

        if self.stop_requested:
            try:
                if os.path.exists(dst):
                    os.remove(dst)
            except Exception:
                pass
            return "failed", 0

        stderr_text = ""
        if err_path and os.path.exists(err_path):
            try:
                with open(err_path, "r", encoding="utf-8", errors="ignore") as f:
                    stderr_text = f.read()
                os.remove(err_path)
            except Exception:
                pass

        if rc == 0 and os.path.exists(dst):
            self.fileProgress.emit(100)
            self.fileProgressPath.emit(src, 100)
            self.logMessage.emit("%s converted" % os.path.basename(src))
            try:
                return "converted", os.path.getsize(dst)
            except Exception:
                return "converted", 0

        self.fileProgressPath.emit(src, 0)
        self.errorDetail.emit(os.path.basename(src), stderr_text or "No FFmpeg stderr captured.")
        self.logMessage.emit("%s failed" % os.path.basename(src))
        return "failed", 0

    def run(self):
        try:
            self._run()
        except Exception:
            self.logMessage.emit("Worker crash:\n" + traceback.format_exc())
            self.finishedOk.emit(False)

    def _run(self):
        if not os.path.exists(self.ffmpeg) or not os.path.exists(self.ffprobe):
            self.logMessage.emit("ERROR: ffmpeg.exe or ffprobe.exe not found.")
            self.finishedOk.emit(False)
            return

        files = audio_only(self.input_paths)
        if not files:
            self.logMessage.emit("ERROR: no supported audio files found.")
            self.finishedOk.emit(False)
            return

        out_dir = self.make_output_folder()
        self.outputFolderReady.emit(out_dir)
        self.logMessage.emit("%s %s" % (APP_NAME, APP_VERSION))
        self.logMessage.emit("FFmpeg: %s" % self.ffmpeg)
        self.logMessage.emit("FFprobe: %s" % self.ffprobe)
        self.logMessage.emit("Output: %s" % out_dir)
        self.logMessage.emit("FFmpeg threads: %s" % normalize_ffmpeg_threads(self.settings.get("ffmpeg_threads", "1")))
        if self.dry_run:
            self.logMessage.emit("DRY RUN MODE: no files will be converted.")

        total = len(files)
        before = 0
        for p in files:
            try:
                before += os.path.getsize(p)
            except Exception:
                pass

        converted = skipped = failed = 0
        after = 0
        start = time.time()
        for i, src in enumerate(files, 1):
            if self.stop_requested:
                break
            result, out_size = self.convert_one(src, out_dir, i, total)
            if result == "converted":
                converted += 1
                after += out_size
            elif result == "skipped":
                skipped += 1
            else:
                failed += 1
            pct = int((float(i) / float(total)) * 100.0)
            elapsed = int(time.time() - start)
            elapsed_text = "%02d:%02d:%02d" % (elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60)
            self.overallProgress.emit(pct)
            self.statsChanged.emit(total, converted, skipped, failed, elapsed_text)

        success = not self.stop_requested
        saved = max(0, before - after)
        self.sizeReportReady.emit({"before": before, "after": after, "saved": saved, "files": total})
        self.finishedOk.emit(success)



class RowProgressDelegate(QtGui.QStyledItemDelegate):
    """Paints one continuous row-wide progress background.

    0.12.2: the fill no longer restarts in every column. The delegate computes
    the whole visible row width, then paints only the intersecting part for the
    current cell, so the progress bar starts at the far left and passes through
    all columns as one strip.
    """
    PROGRESS_ROLE = QtCore.Qt.UserRole + 42

    def __init__(self, tree, app=None):
        QtGui.QStyledItemDelegate.__init__(self, tree)
        self.tree = tree
        self.app = app

    def _index_progress(self, index):
        try:
            item = self.tree.topLevelItem(int(index.row()))
            if item is None:
                return 0
            data = item.data(0, self.PROGRESS_ROLE)
            if hasattr(data, "toInt"):
                value, ok = data.toInt()
                return int(value) if ok else 0
            return int(data)
        except Exception:
            return 0

    def _row_span(self, index, fallback_rect):
        try:
            row = int(index.row())
            left = None
            right = None
            columns = self.tree.columnCount()
            for col in range(columns):
                try:
                    if self.tree.isColumnHidden(col):
                        continue
                except Exception:
                    pass
                try:
                    r = self.tree.visualRect(index.sibling(row, col))
                except Exception:
                    r = QtCore.QRect()
                try:
                    if not r.isValid() or r.width() <= 0:
                        continue
                except Exception:
                    continue
                if left is None or r.left() < left:
                    left = r.left()
                rr = r.right() + 1
                if right is None or rr > right:
                    right = rr
            if left is None or right is None or right <= left:
                left = 0
                right = self.tree.viewport().width()
            if right <= left:
                left = fallback_rect.left()
                right = fallback_rect.right() + 1
            return int(left), int(right)
        except Exception:
            return int(fallback_rect.left()), int(fallback_rect.right() + 1)

    def paint(self, painter, option, index):
        try:
            progress = self._index_progress(index)
            if progress < 0:
                progress = 0
            if progress > 100:
                progress = 100
            painter.save()
            rect = option.rect
            selected = bool(option.state & QtGui.QStyle.State_Selected)
            hovered = bool(option.state & QtGui.QStyle.State_MouseOver)
            dark = False
            accent = "#3a6ea5"
            try:
                dark = effective_theme_is_dark(self.app.config_data)
                accent = effective_accent_color(self.app.config_data)
            except Exception:
                dark = True

            if selected:
                painter.fillRect(rect, QtGui.QColor(accent))
            else:
                base = QtGui.QColor(31, 31, 31) if dark else QtGui.QColor(255, 255, 255)
                alt = QtGui.QColor(35, 35, 35) if dark else QtGui.QColor(245, 245, 245)
                try:
                    row = int(index.row())
                except Exception:
                    row = 0
                painter.fillRect(rect, alt if (row % 2) else base)
                if hovered:
                    painter.fillRect(rect, QtGui.QColor(42, 42, 42) if dark else QtGui.QColor(230, 240, 255))

            if progress > 0:
                row_left, row_right = self._row_span(index, rect)
                row_width = max(1, row_right - row_left)
                fill_right = row_left + int(float(row_width) * float(progress) / 100.0)
                cell_left = rect.left()
                cell_right = rect.right() + 1
                if fill_right > cell_left:
                    fill_rect = QtCore.QRect(rect)
                    fill_rect.setLeft(max(cell_left, row_left))
                    fill_rect.setRight(min(cell_right, fill_right) - 1)
                    if fill_rect.width() > 0:
                        color = QtGui.QColor(accent)
                        if not selected:
                            if dark:
                                color = color.darker(130)
                            else:
                                color = color.lighter(150)
                        painter.fillRect(fill_rect, color)

            text = index.data(QtCore.Qt.DisplayRole)
            if hasattr(text, "toString"):
                text = text.toString()
            text = to_text(text)
            align_data = index.data(QtCore.Qt.TextAlignmentRole)
            alignment = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft
            try:
                if hasattr(align_data, "toInt"):
                    v, ok = align_data.toInt()
                    if ok:
                        alignment = int(v)
                elif align_data:
                    alignment = int(align_data)
            except Exception:
                pass
            text_rect = rect.adjusted(4, 0, -4, 0)
            if selected:
                painter.setPen(QtGui.QColor("#ffffff"))
            else:
                painter.setPen(QtGui.QColor(238, 238, 238) if dark else QtGui.QColor(25, 25, 25))
            painter.drawText(text_rect, alignment, text)
            painter.restore()
        except Exception:
            QtGui.QStyledItemDelegate.paint(self, painter, option, index)


class FieldResizeGrip(QtGui.QLabel):
    """Centered XP-friendly three-bar grip for resizing list/log fields with the mouse."""
    def __init__(self, app, kind, parent=None):
        QtGui.QLabel.__init__(self, parent)
        self.app = app
        self.kind = kind
        self._dragging = False
        self._start_y = 0
        self._start_sizes = None
        self.setFixedSize(74, 12)
        self.setCursor(QtCore.Qt.SizeVerCursor)
        self.setToolTip("Drag the three bars up/down to resize this field")
        self.setAlignment(QtCore.Qt.AlignCenter)

    def paintEvent(self, event):
        try:
            painter = QtGui.QPainter(self)
            color = QtGui.QColor(135, 135, 135)
            painter.setPen(QtGui.QPen(color, 1))
            cx = int(self.width() / 2)
            y0 = int(self.height() / 2) - 3
            half = 14
            # Centered three-bar grip, easier to hit than a corner triangle on 800x600.
            painter.drawLine(cx - half, y0, cx + half, y0)
            painter.drawLine(cx - half, y0 + 3, cx + half, y0 + 3)
            painter.drawLine(cx - half, y0 + 6, cx + half, y0 + 6)
            painter.end()
        except Exception:
            QtGui.QLabel.paintEvent(self, event)

    def mousePressEvent(self, event):
        try:
            if event.button() == QtCore.Qt.LeftButton:
                self._dragging = True
                self._start_y = int(event.globalY())
                self._start_sizes = list(self.app.get_splitter_sizes())
                event.accept()
                return
        except Exception:
            pass
        QtGui.QLabel.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        try:
            if self._dragging:
                delta = int(event.globalY()) - int(self._start_y)
                self.app.resize_field_by_drag(self.kind, self._start_sizes, delta)
                event.accept()
                return
        except Exception:
            pass
        QtGui.QLabel.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        try:
            if self._dragging:
                self._dragging = False
                self.app.save_state()
                event.accept()
                return
        except Exception:
            pass
        QtGui.QLabel.mouseReleaseEvent(self, event)


class SettingsDialog(QtGui.QDialog):
    def __init__(self, app):
        QtGui.QDialog.__init__(self, app)
        self.app = app
        self.setWindowTitle(app.t("settings"))
        self.resize(640, 480)
        self.build_ui()
        self.load_values()

    def safe_splitter_sizes(self, sizes=None):
        try:
            total = int(self.main_splitter.height() or self.height() or 520)
        except Exception:
            total = 520
        if total < 360:
            total = 360
        min_input = self.scaled_value(105, 82)
        min_controls = self.hard_min_controls_height()
        min_log = self.scaled_value(85, 68)
        min_total = min_input + min_controls + min_log
        if total < min_total:
            min_input = 78
            min_controls = self.hard_min_controls_height()
            min_log = 58
            min_total = min_input + min_controls + min_log
        if sizes is None:
            cfg_sizes = self.config_data.get("splitter_sizes", [])
            if isinstance(cfg_sizes, (list, tuple)) and len(cfg_sizes) == 3:
                try:
                    sizes = [int(cfg_sizes[0]), int(cfg_sizes[1]), int(cfg_sizes[2])]
                except Exception:
                    sizes = None
        if not sizes:
            list_h = bounded_int(self.config_data.get("list_height", 220), 220, 82, 460)
            log_h = bounded_int(self.config_data.get("log_height", 90), 90, 58, 280)
            controls_h = max(min_controls, total - list_h - log_h)
            sizes = [list_h, controls_h, log_h]
        try:
            sizes = [max(1, int(x)) for x in sizes[:3]]
        except Exception:
            sizes = [220, self.hard_min_controls_height(), 110]
        sizes[0] = max(min_input, sizes[0])
        sizes[1] = max(min_controls, sizes[1])
        sizes[2] = max(min_log, sizes[2])
        # 0.13: stricter panel limits. Conversion settings should not become
        # the main screen area. The log can only expand up to 45 percent of
        # the available splitter area; extra space goes back to the file list.
        try:
            max_controls = max(min_controls, int(total * 0.32))
            if total <= 600:
                max_controls = max(min_controls, int(total * 0.34))
            if sizes[1] > max_controls:
                extra = sizes[1] - max_controls
                sizes[1] = max_controls
                give_list = int(extra * 0.70)
                sizes[0] += give_list
                sizes[2] += extra - give_list

            max_log = max(min_log, int(total * 0.45))
            if sizes[2] > max_log:
                extra = sizes[2] - max_log
                sizes[2] = max_log
                sizes[0] += extra
        except Exception:
            pass
        s = sum(sizes)
        if s > total and s > 0:
            extra = s - total
            # Shrink input/log first, keep controls visible.
            for idx, mn in [(0, min_input), (2, min_log), (1, min_controls)]:
                can = max(0, sizes[idx] - mn)
                take = min(can, extra)
                sizes[idx] -= take
                extra -= take
                if extra <= 0:
                    break
        return sizes

    def apply_splitter_sizes(self):
        try:
            if not hasattr(self, "main_splitter"):
                return
            sizes = self.safe_splitter_sizes()
            self.main_splitter.setSizes(sizes)
        except Exception:
            pass

    def get_splitter_sizes(self):
        try:
            sizes = [int(x) for x in self.main_splitter.sizes()]
            if len(sizes) == 3 and sum(sizes) > 0:
                return self.safe_splitter_sizes(sizes)
        except Exception:
            pass
        return self.safe_splitter_sizes()

    def on_splitter_moved(self, pos, index):
        try:
            sizes = self.get_splitter_sizes()
            self.config_data["splitter_sizes"] = sizes
            self.config_data["list_height"] = bounded_int(sizes[0], 220, 82, 460)
            self.config_data["log_height"] = bounded_int(sizes[2], 90, 58, 280)
        except Exception:
            pass

    def t(self, key, **kwargs):
        return self.app.t(key, **kwargs)

    def build_ui(self):
        root = QtGui.QVBoxLayout(self)
        self.tabs = QtGui.QTabWidget()
        root.addWidget(self.tabs, 1)
        self.general_tab = QtGui.QWidget()
        general = QtGui.QVBoxLayout(self.general_tab)
        row = QtGui.QHBoxLayout()
        row.addWidget(QtGui.QLabel(self.t("language")))
        self.language_combo = ThemedComboBox()
        for code in LANGUAGES:
            self.language_combo.addItem("%s - %s" % (code, LANGUAGE_NAMES.get(code, code)), code)
        row.addWidget(self.language_combo, 1)
        general.addLayout(row)
        self.auto_analyze_check = QtGui.QCheckBox(self.t("auto_analyze_on_add"))
        self.open_done_check = QtGui.QCheckBox(self.t("open_output_when_done"))
        self.sound_check = QtGui.QCheckBox(self.t("sounds"))
        general.addWidget(self.auto_analyze_check)
        general.addWidget(self.open_done_check)
        general.addWidget(self.sound_check)
        general.addStretch(1)
        self.tabs.addTab(self.general_tab, self.t("settings_general"))
        self.interface_tab = QtGui.QWidget()
        interface = QtGui.QVBoxLayout(self.interface_tab)
        self.follow_windows_theme_check = QtGui.QCheckBox(self.t("follow_windows_theme"))
        interface.addWidget(self.follow_windows_theme_check)
        self.windows_accent_check = QtGui.QCheckBox(self.t("use_windows_accent_color"))
        interface.addWidget(self.windows_accent_check)
        self.dark_check = QtGui.QCheckBox(self.t("dark_theme"))
        interface.addWidget(self.dark_check)
        self.theme_status_label = QtGui.QLabel("")
        self.theme_status_label.setWordWrap(True)
        interface.addWidget(self.theme_status_label)
        self.theme_note_label = QtGui.QLabel(self.t("theme_manual_note"))
        self.theme_note_label.setWordWrap(True)
        interface.addWidget(self.theme_note_label)
        self.auto_scale_check = QtGui.QCheckBox(self.t("auto_scale_current_screen"))
        interface.addWidget(self.auto_scale_check)
        scale_row = QtGui.QHBoxLayout()
        self.ui_scale_label = QtGui.QLabel(self.t("ui_scale"))
        scale_row.addWidget(self.ui_scale_label)
        self.ui_scale_spin = QtGui.QSpinBox()
        self.ui_scale_spin.setRange(65, 125)
        self.ui_scale_spin.setSingleStep(5)
        self.ui_scale_spin.setSuffix("%")
        scale_row.addWidget(self.ui_scale_spin)
        scale_row.addStretch(1)
        interface.addLayout(scale_row)
        self.auto_scale_note = QtGui.QLabel(self.t("auto_scale_note"))
        self.auto_scale_note.setWordWrap(True)
        interface.addWidget(self.auto_scale_note)
        list_row = QtGui.QHBoxLayout()
        list_row.addWidget(QtGui.QLabel(self.t("list_height")))
        self.list_height_spin = QtGui.QSpinBox()
        self.list_height_spin.setRange(100, 420)
        self.list_height_spin.setSingleStep(10)
        self.list_height_spin.setSuffix(" px")
        list_row.addWidget(self.list_height_spin)
        list_row.addStretch(1)
        interface.addLayout(list_row)
        log_row = QtGui.QHBoxLayout()
        log_row.addWidget(QtGui.QLabel(self.t("log_height")))
        self.log_height_spin = QtGui.QSpinBox()
        self.log_height_spin.setRange(60, 260)
        self.log_height_spin.setSingleStep(10)
        self.log_height_spin.setSuffix(" px")
        log_row.addWidget(self.log_height_spin)
        log_row.addStretch(1)
        interface.addLayout(log_row)
        restart = QtGui.QLabel(self.t("apply_restart_note"))
        restart.setWordWrap(True)
        interface.addWidget(restart)
        interface.addStretch(1)
        self.tabs.addTab(self.interface_tab, self.t("settings_interface"))
        self.ffmpeg_tab = QtGui.QWidget()
        ff = QtGui.QGridLayout(self.ffmpeg_tab)
        self.ffmpeg_edit = QtGui.QLineEdit()
        self.ffprobe_edit = QtGui.QLineEdit()
        self.ffmpeg_browse = QtGui.QPushButton(self.t("browse"))
        self.ffprobe_browse = QtGui.QPushButton(self.t("browse"))
        self.use_bundled_button = QtGui.QPushButton(self.t("use_bundled"))
        ff.addWidget(QtGui.QLabel(self.t("custom_ffmpeg_path")), 0, 0)
        ff.addWidget(self.ffmpeg_edit, 0, 1)
        ff.addWidget(self.ffmpeg_browse, 0, 2)
        ff.addWidget(QtGui.QLabel(self.t("custom_ffprobe_path")), 1, 0)
        ff.addWidget(self.ffprobe_edit, 1, 1)
        ff.addWidget(self.ffprobe_browse, 1, 2)
        ff.addWidget(self.use_bundled_button, 2, 1, 1, 2)
        self.active_paths_label = QtGui.QLabel("")
        self.active_paths_label.setWordWrap(True)
        ff.addWidget(self.active_paths_label, 3, 0, 1, 3)
        ff.setRowStretch(4, 1)
        self.tabs.addTab(self.ffmpeg_tab, self.t("settings_ffmpeg"))
        self.performance_tab = QtGui.QWidget()
        performance = QtGui.QVBoxLayout(self.performance_tab)
        threads_row = QtGui.QHBoxLayout()
        self.performance_threads_label = QtGui.QLabel(self.t("ffmpeg_threads"))
        self.performance_threads_combo = ThemedComboBox()
        self.performance_threads_combo.addItems(THREAD_ITEMS)
        threads_row.addWidget(self.performance_threads_label)
        threads_row.addWidget(self.performance_threads_combo)
        threads_row.addStretch(1)
        performance.addLayout(threads_row)
        self.cpu_threads_label = QtGui.QLabel("")
        self.cpu_threads_label.setWordWrap(True)
        performance.addWidget(self.cpu_threads_label)
        self.threads_locked_label = QtGui.QLabel(self.t("threads_popup_note"))
        self.threads_locked_label.setWordWrap(True)
        performance.addWidget(self.threads_locked_label)
        self.disabled_threads_label = QtGui.QLabel(self.t("disabled_threads_are_light"))
        self.disabled_threads_label.setWordWrap(True)
        performance.addWidget(self.disabled_threads_label)
        perf_note = QtGui.QLabel(self.t("oldwin_runtime_note"))
        perf_note.setWordWrap(True)
        performance.addWidget(perf_note)
        performance.addStretch(1)
        self.tabs.addTab(self.performance_tab, self.t("settings_performance"))
        self.safety_tab = QtGui.QWidget()
        safety = QtGui.QVBoxLayout(self.safety_tab)
        self.confirm_stop_check = QtGui.QCheckBox(self.t("confirm_stop"))
        self.confirm_external_check = QtGui.QCheckBox(self.t("confirm_external_open"))
        self.safe_output_check = QtGui.QCheckBox(self.t("safe_output_checks"))
        self.warn_huge_check = QtGui.QCheckBox(self.t("warn_huge_batch"))
        self.path_warn_check = QtGui.QCheckBox(self.t("warn_long_paths"))
        for ctrl in [self.confirm_stop_check, self.confirm_external_check, self.safe_output_check, self.warn_huge_check, self.path_warn_check]:
            safety.addWidget(ctrl)
        limit_row = QtGui.QHBoxLayout()
        limit_row.addWidget(QtGui.QLabel(self.t("huge_batch_limit")))
        self.huge_limit_spin = QtGui.QSpinBox()
        self.huge_limit_spin.setRange(10, 5000)
        self.huge_limit_spin.setSingleStep(10)
        limit_row.addWidget(self.huge_limit_spin)
        limit_row.addStretch(1)
        safety.addLayout(limit_row)
        note = QtGui.QLabel(self.t("safety_note"))
        note.setWordWrap(True)
        safety.addWidget(note)
        self.path_limit_button = QtGui.QPushButton(self.t("path_limit_helper_button"))
        safety.addWidget(self.path_limit_button)
        safety.addStretch(1)
        self.tabs.addTab(self.safety_tab, self.t("settings_safety"))
        self.system_tab = QtGui.QWidget()
        system_layout = QtGui.QVBoxLayout(self.system_tab)
        self.system_text = QtGui.QTextEdit()
        self.system_text.setReadOnly(True)
        system_layout.addWidget(self.system_text, 1)
        self.tabs.addTab(self.system_tab, self.t("settings_system"))
        buttons = QtGui.QHBoxLayout()
        buttons.addStretch(1)
        self.ok_button = QtGui.QPushButton(self.t("ok"))
        self.cancel_button = QtGui.QPushButton(self.t("cancel"))
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)
        root.addLayout(buttons)
        self.ffmpeg_browse.clicked.connect(lambda: self.browse_exe(self.ffmpeg_edit))
        self.ffprobe_browse.clicked.connect(lambda: self.browse_exe(self.ffprobe_edit))
        self.use_bundled_button.clicked.connect(self.use_bundled)
        self.path_limit_button.clicked.connect(self.app.show_path_limit_helper)
        self.follow_windows_theme_check.toggled.connect(self.refresh_interface_locks)
        self.windows_accent_check.toggled.connect(self.refresh_interface_locks)
        self.dark_check.toggled.connect(self.refresh_interface_locks)
        self.auto_scale_check.toggled.connect(self.refresh_interface_locks)
        self.performance_threads_combo.currentIndexChanged.connect(self.enforce_thread_limit)
        self.ok_button.clicked.connect(self.on_ok)
        self.cancel_button.clicked.connect(self.reject)

    def browse_exe(self, edit):
        path = QtGui.QFileDialog.getOpenFileName(self, self.t("browse"), app_dir(), "EXE files (*.exe);;All files (*.*)")
        path = qstring_to_text(path)
        if path:
            edit.setText(path)
            self.refresh_active_paths()

    def use_bundled(self):
        self.ffmpeg_edit.setText("")
        self.ffprobe_edit.setText("")
        self.refresh_active_paths()

    def refresh_interface_locks(self):
        auto_scale = bool(self.auto_scale_check.isChecked())
        self.ui_scale_spin.setEnabled(not auto_scale)
        self.auto_scale_note.setVisible(auto_scale)
        follow = bool(getattr(self, "follow_windows_theme_check", None) and self.follow_windows_theme_check.isChecked())
        use_accent = bool(getattr(self, "windows_accent_check", None) and self.windows_accent_check.isChecked())
        self.dark_check.setEnabled(not follow)
        try:
            temp_cfg = dict(self.app.config_data)
            temp_cfg["follow_windows_theme"] = follow
            temp_cfg["use_windows_accent"] = use_accent
            temp_cfg["dark_theme"] = bool(self.dark_check.isChecked())
            temp_cfg["accent_color"] = effective_accent_color(temp_cfg)
            dark_now = effective_theme_is_dark(temp_cfg)
            accent = effective_accent_color(temp_cfg)
            theme_word = self.t("theme_dark") if dark_now else self.t("theme_light")
            self.theme_status_label.setText(self.t("theme_status", theme=theme_word, accent=accent))
            self.theme_note_label.setVisible(follow)
        except Exception:
            pass
        count = system_cpu_count()
        limit = ffmpeg_thread_limit()
        self.cpu_threads_label.setText(self.t("cpu_threads_detected", count=count) + " | OldWin FFmpeg limit: %s" % limit)
        try:
            current = normalize_ffmpeg_threads(qstring_to_text(self.performance_threads_combo.currentText()))
        except Exception:
            current = normalize_ffmpeg_threads(self.app.config_data.get("ffmpeg_threads", "1"))
        items = ffmpeg_thread_items_for_cpu()
        try:
            self.performance_threads_combo.blockSignals(True)
            self.performance_threads_combo.clear()
            self.performance_threads_combo.addItems(items)
            desired = normalize_ffmpeg_threads(current)
            self.performance_threads_combo.setCurrentIndex(list_index(items, desired, int(limit) - 1))
            model = self.performance_threads_combo.model()
            dark_popup = dark_now
            accent_popup = accent
            for i, value in enumerate(items):
                try:
                    item = model.item(i)
                    enabled = int(value) <= int(limit)
                    item.setEnabled(enabled)
                    if not enabled:
                        item.setBackground(QtGui.QBrush(QtGui.QColor(238, 238, 238)))
                        item.setForeground(QtGui.QBrush(QtGui.QColor(80, 80, 80)))
                    else:
                        if dark_popup:
                            item.setBackground(QtGui.QBrush(QtGui.QColor(31, 31, 31)))
                            item.setForeground(QtGui.QBrush(QtGui.QColor(238, 238, 238)))
                        else:
                            item.setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
                            item.setForeground(QtGui.QBrush(QtGui.QColor(17, 17, 17)))
                except Exception:
                    pass
            apply_combo_view_theme(self.performance_threads_combo, dark_popup, accent_popup)
        finally:
            try:
                self.performance_threads_combo.blockSignals(False)
            except Exception:
                pass
        self.performance_threads_combo.setEnabled(True)
        self.threads_locked_label.setText(self.t("threads_available_note", limit=limit) + "\n" + self.t("threads_popup_note"))
        self.threads_locked_label.setVisible(True)
        try:
            self.disabled_threads_label.setVisible(True)
        except Exception:
            pass

    def enforce_thread_limit(self):
        try:
            value = int(qstring_to_text(self.performance_threads_combo.currentText()))
            limit = int(ffmpeg_thread_limit())
            if value > limit:
                self.performance_threads_combo.blockSignals(True)
                self.performance_threads_combo.setCurrentIndex(list_index(THREAD_ITEMS, str(limit), max(0, limit - 1)))
                self.performance_threads_combo.blockSignals(False)
        except Exception:
            try:
                self.performance_threads_combo.blockSignals(False)
            except Exception:
                pass

    def load_values(self):
        cfg = self.app.config_data
        lang = cfg.get("language", detect_system_language())
        if lang not in LANGUAGES:
            lang = "en"
        self.language_combo.setCurrentIndex(list_index(LANGUAGES, lang, 0))
        self.auto_analyze_check.setChecked(bool(cfg.get("auto_analyze_on_add", True)))
        self.open_done_check.setChecked(bool(self.app.open_done_check.isChecked()))
        self.sound_check.setChecked(bool(self.app.sound_check.isChecked()))
        self.follow_windows_theme_check.setChecked(bool(cfg.get("follow_windows_theme", True)))
        self.windows_accent_check.setChecked(bool(cfg.get("use_windows_accent", True)))
        self.dark_check.setChecked(bool(cfg.get("dark_theme", False)))
        self.auto_scale_check.setChecked(bool(cfg.get("auto_ui_scale", True)))
        try:
            self.ui_scale_spin.setValue(int(cfg.get("ui_scale", 80)))
        except Exception:
            self.ui_scale_spin.setValue(80)
        self.list_height_spin.setValue(bounded_int(cfg.get("list_height", 220), 220, 82, 460))
        self.log_height_spin.setValue(bounded_int(cfg.get("log_height", 90), 90, 58, 280))
        self.app.config_data["ffmpeg_threads"] = normalize_ffmpeg_threads(cfg.get("ffmpeg_threads", "1"))
        self.ffmpeg_edit.setText(to_text(cfg.get("custom_ffmpeg_path", "")))
        self.ffprobe_edit.setText(to_text(cfg.get("custom_ffprobe_path", "")))
        self.confirm_stop_check.setChecked(bool(cfg.get("confirm_stop", True)))
        self.confirm_external_check.setChecked(bool(cfg.get("confirm_external_open", False)))
        self.safe_output_check.setChecked(bool(cfg.get("safe_output_checks", True)))
        self.warn_huge_check.setChecked(bool(cfg.get("warn_huge_batch", True)))
        self.path_warn_check.setChecked(bool(cfg.get("path_length_warning", True)))
        try:
            self.huge_limit_spin.setValue(int(cfg.get("huge_batch_limit", 250)))
        except Exception:
            self.huge_limit_spin.setValue(250)
        self.refresh_active_paths()
        self.refresh_interface_locks()
        self.refresh_system_text()

    def refresh_active_paths(self):
        settings = {"custom_ffmpeg_path": qstring_to_text(self.ffmpeg_edit.text()), "custom_ffprobe_path": qstring_to_text(self.ffprobe_edit.text())}
        self.active_paths_label.setText("%s\n%s\n\n%s\n%s" % (self.t("active_ffmpeg"), get_effective_ffmpeg_path(settings), self.t("active_ffprobe"), get_effective_ffprobe_path(settings)))

    def refresh_system_text(self):
        settings = self.app.current_settings()
        lines = []
        lines.append("%s: %s" % (self.t("app_info"), APP_NAME))
        lines.append("%s: %s" % (self.t("version_label"), APP_VERSION))
        lines.append("%s: %s" % (self.t("author_label"), AUTHOR))
        lines.append("Python: %s" % sys.version.replace("\n", " "))
        lines.append("Qt: %s" % QtCore.QT_VERSION_STR)
        lines.append("PyQt: %s" % QtCore.PYQT_VERSION_STR)
        lines.append("%s: %s%%" % (self.t("ui_scale_info"), int(self.app.config_data.get("ui_scale", 80) or 80)))
        lines.append("%s: %s px" % (self.t("file_list_height_info"), bounded_int(self.app.config_data.get("list_height", 220), 220, 82, 460)))
        lines.append("%s: %s px" % (self.t("log_height_info"), bounded_int(self.app.config_data.get("log_height", 90), 90, 58, 280)))
        lines.append("%s: %s" % (self.t("ffmpeg_thread_setting_info"), normalize_ffmpeg_threads(self.app.config_data.get("ffmpeg_threads", "1"))))
        lines.append("")
        lines.append("--- %s ---" % self.t("system_hardware_section"))
        lines.extend(system_info_lines())
        lines.append("")
        lines.append("--- %s ---" % self.t("system_theme_section"))
        lines.append(self.t("theme_status", theme=(self.t("theme_dark") if effective_theme_is_dark(self.app.config_data) else self.t("theme_light")), accent=effective_accent_color(self.app.config_data)))
        lines.append("%s: %s" % (self.t("follow_windows_theme"), bool(self.app.config_data.get("follow_windows_theme", True))))
        lines.append("%s: %s" % (self.t("use_windows_accent_color"), bool(self.app.config_data.get("use_windows_accent", True))))
        lines.append("")
        lines.append("%s: %s" % (self.t("data_folder"), DATA_DIR))
        lines.append("%s: %s" % (self.t("config_file"), CONFIG_PATH))
        lines.append(self.t("appdata_note"))
        lines.append("%s: %s" % (self.t("legacy_config_migration"), "; ".join(legacy_config_dirs())))
        lines.append("%s %s" % (self.t("active_ffmpeg"), get_effective_ffmpeg_path(settings)))
        lines.append("%s %s" % (self.t("active_ffprobe"), get_effective_ffprobe_path(settings)))
        self.system_text.setPlainText("\n".join(lines))

    def on_ok(self):
        cfg = self.app.config_data
        lang_data = self.language_combo.itemData(self.language_combo.currentIndex())
        if hasattr(lang_data, "toString"):
            lang = qstring_to_text(lang_data.toString())
        else:
            lang = qstring_to_text(lang_data)
        cfg["language"] = lang if lang in LANGUAGES else "en"
        cfg["auto_analyze_on_add"] = bool(self.auto_analyze_check.isChecked())
        cfg["follow_windows_theme"] = bool(self.follow_windows_theme_check.isChecked())
        cfg["use_windows_accent"] = bool(self.windows_accent_check.isChecked())
        cfg["dark_theme"] = bool(self.dark_check.isChecked())
        cfg["accent_color"] = effective_accent_color(cfg)
        try:
            if "compact_ui" in cfg:
                del cfg["compact_ui"]
        except Exception:
            pass
        cfg["auto_ui_scale"] = bool(self.auto_scale_check.isChecked())
        if cfg["auto_ui_scale"]:
            cfg["ui_scale"] = self.app.calculate_auto_ui_scale()
        else:
            cfg["ui_scale"] = int(self.ui_scale_spin.value())
        cfg["list_height"] = bounded_int(self.list_height_spin.value(), 220, 82, 460)
        cfg["log_height"] = bounded_int(self.log_height_spin.value(), 90, 58, 280)
        try:
            sizes = self.app.get_splitter_sizes()
            sizes[0] = cfg["list_height"]
            sizes[2] = cfg["log_height"]
            cfg["splitter_sizes"] = self.app.safe_splitter_sizes(sizes)
        except Exception:
            pass
        cfg["ffmpeg_threads"] = normalize_ffmpeg_threads(qstring_to_text(self.performance_threads_combo.currentText()))
        cfg["sound_enabled"] = bool(self.sound_check.isChecked())
        cfg["custom_ffmpeg_path"] = qstring_to_text(self.ffmpeg_edit.text()).strip()
        cfg["custom_ffprobe_path"] = qstring_to_text(self.ffprobe_edit.text()).strip()
        cfg["confirm_stop"] = bool(self.confirm_stop_check.isChecked())
        cfg["confirm_external_open"] = bool(self.confirm_external_check.isChecked())
        cfg["safe_output_checks"] = bool(self.safe_output_check.isChecked())
        cfg["warn_huge_batch"] = bool(self.warn_huge_check.isChecked())
        cfg["huge_batch_limit"] = int(self.huge_limit_spin.value())
        cfg["path_length_warning"] = bool(self.path_warn_check.isChecked())
        self.app.open_done_check.setChecked(bool(self.open_done_check.isChecked()))
        self.app.sound_check.setChecked(bool(self.sound_check.isChecked()))
        self.app.apply_language()
        self.app.apply_theme()
        self.app.apply_ui_scale()
        self.app.update_output_label()
        self.app.save_state()
        self.accept()


class AudioConverterPyQt4(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("%s %s" % (APP_DISPLAY_NAME, APP_VERSION))
        try:
            icon_path = resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.setWindowIcon(QtGui.QIcon(icon_path))
        except Exception:
            pass
        self.config_data = load_config()
        self.current_progress_path = ""
        self.configure_auto_scale()
        self.resize(self.scaled_value(900, 700), self.scaled_value(600, 470))
        self.setMinimumSize(self.scaled_value(760, 680), self.scaled_value(480, 430))
        self.input_paths = []
        self.analysis_cache = {}
        self.error_details = {}
        self.output_folder_path = ""
        self.size_report = {}
        self.worker = None
        self.analyzer = None
        self.start_time = None
        self.runtime_total = 0
        self.runtime_converted = 0
        self.runtime_skipped = 0
        self.runtime_failed = 0
        self.runtime_last_elapsed = "00:00:00"
        self.runtime_timer = QtCore.QTimer(self)
        self.runtime_timer.setInterval(1000)
        self.runtime_timer.timeout.connect(self.update_elapsed_tick)

        self.build_ui()
        self.load_state_to_controls()
        self.apply_language()
        self.apply_theme()
        self.apply_ui_scale()
        self.update_output_label()
        self.update_button_states()
        QtCore.QTimer.singleShot(250, self.check_recovery)
        QtCore.QTimer.singleShot(600, self.add_system_info_to_log)

    def build_ui(self):
        central = QtGui.QWidget(self)
        self.setCentralWidget(central)
        root = QtGui.QVBoxLayout(central)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(3)

        top = QtGui.QHBoxLayout()
        self.title_label = QtGui.QLabel(APP_DISPLAY_NAME)
        font = self.title_label.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 1)
        self.title_label.setFont(font)
        top.addWidget(self.title_label, 1)
        self.settings_button = QtGui.QPushButton("Settings")
        self.license_button = QtGui.QPushButton("License")
        self.about_button = QtGui.QPushButton("About")
        top.addWidget(self.settings_button)
        top.addWidget(self.license_button)
        top.addWidget(self.about_button)
        root.addLayout(top)

        self.main_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(6)
        root.addWidget(self.main_splitter, 1)

        input_box = QtGui.QGroupBox("Input files / folders")
        self.input_box = input_box
        input_layout = QtGui.QVBoxLayout(input_box)
        buttons = QtGui.QGridLayout()
        buttons.setSpacing(3)
        self.add_files_button = QtGui.QPushButton("Add Files")
        self.add_folder_button = QtGui.QPushButton("Add Folder")
        self.remove_button = QtGui.QPushButton("Remove Selected")
        self.clear_button = QtGui.QPushButton("Clear List")
        self.analyze_button = QtGui.QPushButton("Analyze")
        self.preview_button = QtGui.QPushButton("Preview / Open")
        input_buttons = [self.add_files_button, self.add_folder_button, self.remove_button, self.clear_button, self.analyze_button, self.preview_button]
        for i, btn in enumerate(input_buttons):
            buttons.addWidget(btn, i // 3, i % 3)
        input_layout.addLayout(buttons)

        self.table = QtGui.QTreeWidget()
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHeaderLabels([self.t(k) for k in COLUMN_KEYS])
        for i, c in enumerate(COLUMNS):
            self.table.setColumnWidth(i, c[1])
        self.table.setAlternatingRowColors(False)
        self.table.setRootIsDecorated(False)
        self.table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        try:
            self.table.setItemDelegate(RowProgressDelegate(self.table, self))
        except Exception:
            pass
        input_layout.addWidget(self.table, 1)
        list_grip_row = QtGui.QHBoxLayout()
        list_grip_row.setContentsMargins(0, 0, 0, 0)
        list_grip_row.setSpacing(0)
        list_grip_row.addStretch(1)
        self.list_resize_grip = FieldResizeGrip(self, "list", input_box)
        list_grip_row.addWidget(self.list_resize_grip)
        list_grip_row.addStretch(1)
        input_layout.addLayout(list_grip_row)
        self.input_box.setMinimumHeight(self.scaled_value(120, 95))
        self.main_splitter.addWidget(input_box)

        self.controls_panel = QtGui.QWidget()
        controls_root = QtGui.QVBoxLayout(self.controls_panel)
        controls_root.setContentsMargins(0, 0, 0, 0)
        controls_root.setSpacing(3)

        self.overall_progress = QtGui.QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setTextVisible(True)
        self.overall_progress.setFormat("%p%")
        controls_root.addWidget(self.overall_progress)

        settings_box = QtGui.QGroupBox("Conversion settings")
        self.settings_box = settings_box
        settings_layout = QtGui.QGridLayout(settings_box)
        settings_layout.setContentsMargins(5, 5, 5, 5)

        self.preset_combo = ThemedComboBox()
        self.preset_combo.addItems(PRESETS)
        self.format_combo = ThemedComboBox()
        self.format_combo.addItems(OUTPUT_FORMAT_ITEMS)
        self.quality_combo = ThemedComboBox()
        self.refresh_quality_combo_items("192k")
        self.sample_combo = ThemedComboBox()
        self.sample_combo.addItems(SAMPLE_RATES)
        self.channels_combo = ThemedComboBox()
        self.channels_combo.addItems(CHANNELS)
        self.conflict_combo = ThemedComboBox()
        self.conflict_combo.addItems(CONFLICT_MODES)
        self.main_combos = [self.preset_combo, self.format_combo, self.quality_combo, self.sample_combo, self.channels_combo, self.conflict_combo]
        try:
            self.apply_fixed_widget_metrics()
        except Exception:
            pass

        self.preset_label = QtGui.QLabel("Preset:")
        self.format_label = QtGui.QLabel("Output format:")
        self.quality_label = QtGui.QLabel("Quality:")
        self.sample_label = QtGui.QLabel("Sample rate:")
        self.channels_label = QtGui.QLabel("Channels:")
        self.conflict_label = QtGui.QLabel("If target exists:")
        settings_layout.setHorizontalSpacing(4)
        settings_layout.setVerticalSpacing(3)
        settings_layout.addWidget(self.preset_label, 0, 0)
        settings_layout.addWidget(self.preset_combo, 0, 1)
        settings_layout.addWidget(self.format_label, 0, 2)
        settings_layout.addWidget(self.format_combo, 0, 3)

        settings_layout.addWidget(self.quality_label, 1, 0)
        settings_layout.addWidget(self.quality_combo, 1, 1)
        settings_layout.addWidget(self.sample_label, 1, 2)
        settings_layout.addWidget(self.sample_combo, 1, 3)

        settings_layout.addWidget(self.channels_label, 2, 0)
        settings_layout.addWidget(self.channels_combo, 2, 1)
        settings_layout.addWidget(self.conflict_label, 2, 2)
        settings_layout.addWidget(self.conflict_combo, 2, 3)

        self.meta_check = QtGui.QCheckBox("Keep metadata")
        self.structure_check = QtGui.QCheckBox("Preserve folder structure")
        self.open_done_check = QtGui.QCheckBox("Open output when done")
        self.sound_check = QtGui.QCheckBox("Sounds")
        check_row = QtGui.QGridLayout()
        check_row.setSpacing(3)
        check_items = [self.meta_check, self.structure_check, self.open_done_check, self.sound_check]
        for i, ctrl in enumerate(check_items):
            check_row.addWidget(ctrl, i // 3, i % 3)
        settings_layout.addLayout(check_row, 4, 0, 1, 4)
        controls_root.addWidget(settings_box)

        output_row = QtGui.QHBoxLayout()
        self.output_label = QtGui.QLabel("")
        self.choose_output_button = QtGui.QPushButton("Choose Output Folder")
        self.clear_output_button = QtGui.QPushButton("Use Auto Output")
        output_row.addWidget(self.output_label, 1)
        output_row.addWidget(self.choose_output_button)
        output_row.addWidget(self.clear_output_button)
        controls_root.addLayout(output_row)

        actions = QtGui.QGridLayout()
        actions.setSpacing(3)
        self.test_button = QtGui.QPushButton("Test Run")
        self.convert_button = QtGui.QPushButton("Convert")
        self.stop_button = QtGui.QPushButton("STOP")
        self.open_output_button = QtGui.QPushButton("Open Output Folder")
        self.save_log_button = QtGui.QPushButton("Save Log TXT")
        self.export_button = QtGui.QPushButton("Export CSV Report")
        self.errors_button = QtGui.QPushButton("Show Errors")
        action_buttons = [self.test_button, self.convert_button, self.stop_button, self.open_output_button, self.save_log_button, self.export_button, self.errors_button]
        self.action_buttons = action_buttons
        try:
            for btn in action_buttons + input_buttons + [self.settings_button, self.license_button, self.about_button, self.choose_output_button, self.clear_output_button]:
                self.apply_fixed_button_metrics(btn)
        except Exception:
            pass
        for i, btn in enumerate(action_buttons):
            actions.addWidget(btn, i // 4, i % 4)
        controls_root.addLayout(actions)
        self.controls_panel.setMinimumHeight(self.hard_min_controls_height())
        self.main_splitter.addWidget(self.controls_panel)

        stats_box = QtGui.QGroupBox("Statistics")
        self.stats_box = stats_box
        stats_layout = QtGui.QVBoxLayout(stats_box)
        self.stats_label = QtGui.QLabel("Total: 0 | Converted: 0 | Skipped: 0 | Failed: 0 | Elapsed: 00:00:00")
        self.current_label = QtGui.QLabel("Current file: -")
        self.log_box = QtGui.QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(80)
        stats_layout.addWidget(self.stats_label)
        stats_layout.addWidget(self.current_label)
        log_grip_row = QtGui.QHBoxLayout()
        log_grip_row.setContentsMargins(0, 0, 0, 0)
        log_grip_row.setSpacing(0)
        log_grip_row.addStretch(1)
        self.log_resize_grip = FieldResizeGrip(self, "log", stats_box)
        log_grip_row.addWidget(self.log_resize_grip)
        log_grip_row.addStretch(1)
        stats_layout.addLayout(log_grip_row)
        stats_layout.addWidget(self.log_box, 1)
        self.stats_box.setMinimumHeight(self.scaled_value(110, 90))
        self.main_splitter.addWidget(stats_box)

        self.statusBar().showMessage("Ready")

        self.settings_button.clicked.connect(self.show_settings)
        self.license_button.clicked.connect(self.show_license)
        self.about_button.clicked.connect(self.show_about)
        self.add_files_button.clicked.connect(self.choose_files)
        self.add_folder_button.clicked.connect(self.choose_folder)
        self.remove_button.clicked.connect(self.remove_selected)
        self.clear_button.clicked.connect(self.clear_list)
        self.analyze_button.clicked.connect(self.analyze_files)
        self.preview_button.clicked.connect(self.preview_selected)
        self.choose_output_button.clicked.connect(self.choose_output)
        self.clear_output_button.clicked.connect(self.clear_output)
        self.test_button.clicked.connect(lambda: self.start_conversion(True))
        self.convert_button.clicked.connect(lambda: self.start_conversion(False))
        self.stop_button.clicked.connect(self.stop_conversion)
        self.open_output_button.clicked.connect(self.open_output)
        self.save_log_button.clicked.connect(self.save_log)
        self.export_button.clicked.connect(self.export_csv)
        self.errors_button.clicked.connect(self.show_errors)
        self.preset_combo.currentIndexChanged[str].connect(self.apply_preset)
        self.table.itemDoubleClicked.connect(self.open_item)
        try:
            self.main_splitter.splitterMoved.connect(self.on_splitter_moved)
        except Exception:
            pass
        QtCore.QTimer.singleShot(0, self.apply_splitter_sizes)


    def screen_size(self):
        try:
            desktop = QtGui.QApplication.desktop()
            geom = desktop.availableGeometry(self)
            w, h = int(geom.width()), int(geom.height())
            if w <= 0 or h <= 0:
                return 1024, 768
            return w, h
        except Exception:
            return 1024, 768

    def calculate_auto_ui_scale(self):
        try:
            w, h = self.screen_size()
            # OldWin baseline is 1024x768. Formula balances width, height and
            # screen area so 800x600 remains usable while modern screens do not
            # become comically huge. Buttons use the same effective scale later.
            fw = float(w) / 1024.0
            fh = float(h) / 768.0
            fmin = min(fw, fh)
            fmax = max(fw, fh)
            farea = (float(w * h) / float(1024 * 768)) ** 0.5
            mixed = (0.55 * fmin) + (0.30 * farea) + (0.15 * min(fmax, 1.60))
            scale = int(82.0 * mixed)
            if w <= 800 or h <= 600:
                scale = min(scale, 70)
            elif w <= 1024 or h <= 768:
                scale = min(max(scale, 76), 86)
            elif w >= 1600 and h >= 900:
                scale = max(scale, 96)
            if scale < 68:
                scale = 68
            if scale > 118:
                scale = 118
            return int(scale)
        except Exception:
            return 80

    def configure_auto_scale(self):
        try:
            w, h = self.screen_size()
            self.config_data["screen_width"] = int(w)
            self.config_data["screen_height"] = int(h)
            if "auto_ui_scale" not in self.config_data:
                self.config_data["auto_ui_scale"] = True
            if bool(self.config_data.get("auto_ui_scale", True)):
                self.config_data["ui_scale"] = self.calculate_auto_ui_scale()
        except Exception:
            if "ui_scale" not in self.config_data:
                self.config_data["ui_scale"] = 80

    def effective_ui_scale(self):
        try:
            if bool(self.config_data.get("auto_ui_scale", True)):
                scale = int(self.config_data.get("ui_scale", self.calculate_auto_ui_scale()) or 80)
            else:
                scale = int(self.config_data.get("ui_scale", 80) or 80)
        except Exception:
            scale = 80
        if scale < 68:
            scale = 68
        if scale > 118:
            scale = 118
        return int(scale)

    def fixed_margin(self):
        # Hard-fixed visual padding, derived from scale but clamped to a tiny set
        # of values to avoid random theme-dependent layout drift on XP/Vista.
        try:
            scale = self.effective_ui_scale()
            if scale <= 72:
                return 2
            if scale <= 90:
                return 3
            return 4
        except Exception:
            return 3

    def fixed_spacing(self):
        try:
            scale = self.effective_ui_scale()
            if scale <= 72:
                return 2
            if scale <= 90:
                return 3
            return 4
        except Exception:
            return 3

    def fixed_control_height(self):
        try:
            scale = self.effective_ui_scale()
            h = int(22 * scale / 100)
            if h < 18:
                h = 18
            if h > 28:
                h = 28
            return h
        except Exception:
            return 21

    def fixed_combo_width(self, wide=False):
        try:
            scale = self.effective_ui_scale()
            base = 150 if wide else 112
            width = int(base * scale / 100)
            if wide:
                return max(116, min(width, 178))
            return max(86, min(width, 142))
        except Exception:
            return 112

    def apply_fixed_combo_metrics(self, combo, wide=False):
        try:
            h = self.fixed_control_height()
            w = self.fixed_combo_width(wide)
            combo.setFixedHeight(h)
            combo.setMinimumWidth(w)
            combo.setMaximumWidth(w + 18)
            combo.setMaxVisibleItems(8)
            combo.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
            combo.setMinimumContentsLength(8 if not wide else 12)
            view = combo.view()
            if view is not None:
                view.setMinimumWidth(w + 18)
                try:
                    view.setUniformItemSizes(True)
                except Exception:
                    pass
                try:
                    apply_combo_view_theme(combo, effective_theme_is_dark(self.config_data), effective_accent_color(self.config_data))
                except Exception:
                    pass
        except Exception:
            pass

    def apply_fixed_button_metrics(self, button):
        try:
            h = self.fixed_control_height() + 2
            button.setMinimumHeight(h)
            button.setMaximumHeight(h + 4)
            button.setMinimumWidth(max(68, self.fixed_combo_width(False) - 8))
        except Exception:
            pass

    def apply_fixed_widget_metrics(self):
        try:
            if hasattr(self, "main_combos"):
                for combo in self.main_combos:
                    self.apply_fixed_combo_metrics(combo, combo is self.preset_combo)
            if hasattr(self, "action_buttons"):
                for btn in self.action_buttons:
                    self.apply_fixed_button_metrics(btn)
            for btn_name in ["settings_button", "license_button", "about_button", "choose_output_button", "clear_output_button", "add_files_button", "add_folder_button", "remove_button", "clear_button", "analyze_button", "preview_button"]:
                if hasattr(self, btn_name):
                    self.apply_fixed_button_metrics(getattr(self, btn_name))
        except Exception:
            pass

    def hard_min_controls_height(self):
        try:
            app = QtGui.QApplication.instance()
            font = app.font() if app else self.font()
            fm = QtGui.QFontMetrics(font)
            row_h = max(self.fixed_control_height() + 2, int(fm.height()) + self.fixed_spacing() + 4)
        except Exception:
            row_h = self.fixed_control_height() + 4
        try:
            progress_h = max(self.fixed_control_height(), self.overall_progress.sizeHint().height())
        except Exception:
            progress_h = self.fixed_control_height()
        # 0.13: smaller, stricter formula. It keeps the conversion controls
        # complete, but avoids letting this panel steal most of the screen.
        minimum = progress_h + (row_h * 3) + (self.fixed_margin() * 4) + self.scaled_value(12, 8)
        try:
            w, h = self.screen_size()
            floor = self.scaled_value(165, 135)
            if h <= 600:
                floor = self.scaled_value(148, 118)
                cap = max(floor, int(h * 0.34))
            elif h <= 768:
                cap = max(floor, int(h * 0.32))
            else:
                cap = max(floor, int(h * 0.30))
            minimum = min(max(floor, minimum), cap)
        except Exception:
            minimum = max(self.scaled_value(165, 135), minimum)
        return int(minimum)

    def scaled_value(self, normal_value, compact_value=None):
        # 0.13: Compact interface mode was removed. Auto-scale to current
        # screen is the only layout scaling mode; compact_value is ignored and
        # kept only for call-site compatibility with older code.
        base = normal_value
        scale = self.effective_ui_scale()
        try:
            return int(base * scale / 100)
        except Exception:
            return int(base)

    def _set_font_recursive(self, widget, font):
        try:
            widget.setFont(font)
        except Exception:
            pass
        try:
            children = widget.findChildren(QtGui.QWidget)
            for child in children:
                try:
                    child.setFont(font)
                except Exception:
                    pass
        except Exception:
            pass

    def apply_ui_scale(self):
        try:
            app = QtGui.QApplication.instance()
            font = app.font()
            try:
                base_size = int(self.config_data.get("_base_font_point_size", 0) or 0)
            except Exception:
                base_size = 0
            if base_size <= 0:
                base_size = font.pointSize()
                if base_size <= 0:
                    base_size = 8
                self.config_data["_base_font_point_size"] = base_size
            self.configure_auto_scale()
            scale = self.effective_ui_scale()
            point = int(base_size * scale / 100)
            if point < 7:
                point = 7
            font.setPointSize(point)
            app.setFont(font)
            self._set_font_recursive(self, font)
            try:
                title_font = QtGui.QFont(font)
                title_font.setBold(True)
                title_font.setPointSize(max(point, 8))
                self.title_label.setFont(title_font)
            except Exception:
                pass
            margin = self.fixed_margin()
            spacing = self.fixed_spacing()
            try:
                self.centralWidget().layout().setContentsMargins(margin, margin, margin, margin)
                self.centralWidget().layout().setSpacing(spacing)
            except Exception:
                pass
            try:
                self.input_box.setMinimumHeight(self.scaled_value(120, 95))
                self.controls_panel.setMinimumHeight(self.hard_min_controls_height())
                self.controls_panel.setMaximumHeight(max(self.hard_min_controls_height(), int(self.height() * 0.78)))
                self.apply_fixed_widget_metrics()
                self.stats_box.setMinimumHeight(self.scaled_value(110, 90))
                self.log_box.setMinimumHeight(self.scaled_value(60, 50))
                self.table.setMinimumHeight(self.scaled_value(80, 65))
            except Exception:
                pass
            for i, c in enumerate(COLUMNS):
                try:
                    self.table.setColumnWidth(i, self.scaled_value(c[1], c[1]))
                except Exception:
                    pass
            try:
                self.setMinimumSize(self.scaled_value(760, 680), self.scaled_value(480, 430))
                state = self.windowState()
                maximized = bool(state & QtCore.Qt.WindowMaximized) or self.isMaximized()
                fullscreen = bool(state & QtCore.Qt.WindowFullScreen) or self.isFullScreen()
                if (not maximized) and (not fullscreen):
                    if self.width() > 1000 or self.height() > 720:
                        self.resize(self.scaled_value(900, 700), self.scaled_value(600, 470))
                self.apply_splitter_sizes()
            except Exception:
                pass
        except Exception:
            pass

    def safe_splitter_sizes(self, sizes=None):
        try:
            total = int(self.main_splitter.height() or self.height() or 520)
        except Exception:
            total = 520
        if total < 360:
            total = 360
        min_input = self.scaled_value(105, 82)
        min_controls = self.hard_min_controls_height()
        min_log = self.scaled_value(85, 68)
        min_total = min_input + min_controls + min_log
        if total < min_total:
            min_input = 78
            min_controls = self.hard_min_controls_height()
            min_log = 58
            min_total = min_input + min_controls + min_log
        if sizes is None:
            cfg_sizes = self.config_data.get("splitter_sizes", [])
            if isinstance(cfg_sizes, (list, tuple)) and len(cfg_sizes) == 3:
                try:
                    sizes = [int(cfg_sizes[0]), int(cfg_sizes[1]), int(cfg_sizes[2])]
                except Exception:
                    sizes = None
        if not sizes:
            list_h = bounded_int(self.config_data.get("list_height", 220), 220, 82, 460)
            log_h = bounded_int(self.config_data.get("log_height", 90), 90, 58, 280)
            controls_h = max(min_controls, total - list_h - log_h)
            sizes = [list_h, controls_h, log_h]
        try:
            sizes = [max(1, int(x)) for x in sizes[:3]]
        except Exception:
            sizes = [220, self.hard_min_controls_height(), 110]
        sizes[0] = max(min_input, sizes[0])
        sizes[1] = max(min_controls, sizes[1])
        sizes[2] = max(min_log, sizes[2])
        # 0.13: stricter panel limits. Conversion settings should not become
        # the main screen area. The log can only expand up to 45 percent of
        # the available splitter area; extra space goes back to the file list.
        try:
            max_controls = max(min_controls, int(total * 0.32))
            if total <= 600:
                max_controls = max(min_controls, int(total * 0.34))
            if sizes[1] > max_controls:
                extra = sizes[1] - max_controls
                sizes[1] = max_controls
                give_list = int(extra * 0.70)
                sizes[0] += give_list
                sizes[2] += extra - give_list

            max_log = max(min_log, int(total * 0.45))
            if sizes[2] > max_log:
                extra = sizes[2] - max_log
                sizes[2] = max_log
                sizes[0] += extra
        except Exception:
            pass
        s = sum(sizes)
        if s > total and s > 0:
            extra = s - total
            # Shrink input/log first, keep controls visible.
            for idx, mn in [(0, min_input), (2, min_log), (1, min_controls)]:
                can = max(0, sizes[idx] - mn)
                take = min(can, extra)
                sizes[idx] -= take
                extra -= take
                if extra <= 0:
                    break
        return sizes

    def apply_splitter_sizes(self):
        try:
            if not hasattr(self, "main_splitter"):
                return
            sizes = self.safe_splitter_sizes()
            self.main_splitter.setSizes(sizes)
        except Exception:
            pass

    def get_splitter_sizes(self):
        try:
            sizes = [int(x) for x in self.main_splitter.sizes()]
            if len(sizes) == 3 and sum(sizes) > 0:
                return self.safe_splitter_sizes(sizes)
        except Exception:
            pass
        return self.safe_splitter_sizes()

    def on_splitter_moved(self, pos, index):
        try:
            sizes = self.get_splitter_sizes()
            self.config_data["splitter_sizes"] = sizes
            self.config_data["list_height"] = bounded_int(sizes[0], 220, 82, 460)
            self.config_data["log_height"] = bounded_int(sizes[2], 90, 58, 280)
        except Exception:
            pass

    def resize_field_by_drag(self, kind, start_sizes, delta):
        try:
            if not hasattr(self, "main_splitter"):
                return
            try:
                sizes = [int(x) for x in list(start_sizes)[:3]]
            except Exception:
                sizes = self.get_splitter_sizes()
            if len(sizes) != 3:
                sizes = self.get_splitter_sizes()
            delta = int(delta)
            if kind == "list":
                # 0.13.1: resizing the file list takes/gives space only
                # from/to the log panel. Conversion settings stays untouched.
                sizes[0] = sizes[0] + delta
                sizes[2] = sizes[2] - delta
            elif kind == "log":
                # 0.13: grip is above the log and inverted. Pull up
                # (negative delta) expands the log upward. Do not touch
                # Conversion settings; take/give space from the file list.
                sizes[2] = sizes[2] - delta
                sizes[0] = sizes[0] + delta
            else:
                return
            sizes = self.safe_splitter_sizes(sizes)
            self.main_splitter.setSizes(sizes)
            self.config_data["splitter_sizes"] = sizes
            self.config_data["list_height"] = bounded_int(sizes[0], 220, 82, 460)
            self.config_data["log_height"] = bounded_int(sizes[2], 90, 58, 280)
        except Exception:
            pass

    def t(self, key, **kwargs):
        return translate(self.config_data.get("language", detect_system_language()), key, **kwargs)

    def apply_view_palette(self, dark, accent):
        """Force view/viewport colors so empty list area is not white in dark mode."""
        try:
            if dark:
                base = QtGui.QColor(31, 31, 31)
                alt = QtGui.QColor(35, 35, 35)
                text = QtGui.QColor(238, 238, 238)
            else:
                base = QtGui.QColor(255, 255, 255)
                alt = QtGui.QColor(245, 245, 245)
                text = QtGui.QColor(17, 17, 17)
            for view in [getattr(self, "table", None), getattr(self, "log_box", None)]:
                if view is None:
                    continue
                pal = view.palette()
                pal.setColor(QtGui.QPalette.Base, base)
                pal.setColor(QtGui.QPalette.AlternateBase, alt)
                pal.setColor(QtGui.QPalette.Window, base)
                pal.setColor(QtGui.QPalette.Text, text)
                pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor(accent))
                pal.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#ffffff"))
                view.setPalette(pal)
                try:
                    vp = view.viewport()
                    vp.setAutoFillBackground(True)
                    vp.setPalette(pal)
                except Exception:
                    pass
        except Exception:
            pass

    def apply_theme(self):
        try:
            app = QtGui.QApplication.instance()
            if app is None:
                return
            accent = effective_accent_color(self.config_data)
            dark = effective_theme_is_dark(self.config_data)
            if dark:
                app.setStyleSheet(dark_stylesheet(accent))
            else:
                app.setStyleSheet(light_stylesheet(accent))
            self.apply_view_palette(dark, accent)
            try:
                if hasattr(self, "main_combos"):
                    for combo in self.main_combos:
                        apply_combo_view_theme(combo, dark, accent)
            except Exception:
                pass
        except Exception:
            pass

    def refresh_quality_combo_items(self, selected_value=None):
        try:
            if not hasattr(self, "quality_combo"):
                return
            current = selected_value
            if current is None:
                current = self.current_quality_value()
            current = quality_value_from_display(current)
            lang = self.config_data.get("language", detect_system_language()) if hasattr(self, "config_data") else detect_system_language()
            self.quality_combo.blockSignals(True)
            self.quality_combo.clear()
            for value in QUALITY_PRESETS:
                self.quality_combo.addItem(quality_display(value, lang), value)
            self.set_quality_combo_value(current)
        except Exception:
            try:
                self.quality_combo.clear()
                self.quality_combo.addItems(QUALITY_PRESETS)
            except Exception:
                pass
        finally:
            try:
                self.quality_combo.blockSignals(False)
            except Exception:
                pass

    def set_quality_combo_value(self, value):
        value = quality_value_from_display(value)
        try:
            for i in range(self.quality_combo.count()):
                data = variant_to_text(self.quality_combo.itemData(i))
                text = quality_value_from_display(self.quality_combo.itemText(i))
                if data == value or text == value:
                    self.quality_combo.setCurrentIndex(i)
                    return
            self.quality_combo.setCurrentIndex(list_index(QUALITY_PRESETS, value, 1))
        except Exception:
            pass

    def current_quality_value(self):
        try:
            idx = self.quality_combo.currentIndex()
            data = variant_to_text(self.quality_combo.itemData(idx))
            if data and data not in ("None", "NULL"):
                return quality_value_from_display(data)
        except Exception:
            pass
        try:
            return quality_value_from_display(self.quality_combo.currentText())
        except Exception:
            return "192k"

    def apply_language(self):
        self.update_window_title()
        self.title_label.setText(APP_DISPLAY_NAME)
        self.settings_button.setText(self.t("settings"))
        self.license_button.setText(self.t("license"))
        self.about_button.setText(self.t("about"))
        self.input_box.setTitle(self.t("input_files_folders"))
        self.add_files_button.setText(self.t("add_files"))
        self.add_folder_button.setText(self.t("add_folder"))
        self.remove_button.setText(self.t("remove_selected"))
        self.clear_button.setText(self.t("clear_list"))
        self.analyze_button.setText(self.t("analyze"))
        self.preview_button.setText(self.t("preview_open"))
        self.settings_box.setTitle(self.t("conversion_settings"))
        self.preset_label.setText(self.t("preset"))
        self.format_label.setText(self.t("output_format"))
        self.quality_label.setText(self.t("quality"))
        self.refresh_quality_combo_items()
        self.sample_label.setText(self.t("sample_rate"))
        self.channels_label.setText(self.t("channels"))
        self.conflict_label.setText(self.t("if_target_exists"))
        self.meta_check.setText(self.t("keep_metadata"))
        self.structure_check.setText(self.t("preserve_structure"))
        self.open_done_check.setText(self.t("open_output_when_done"))
        self.sound_check.setText(self.t("sounds"))
        self.choose_output_button.setText(self.t("choose_output_folder"))
        self.clear_output_button.setText(self.t("use_auto_output"))
        self.test_button.setText(self.t("test_run"))
        self.convert_button.setText(self.t("convert"))
        self.stop_button.setText(self.t("stop"))
        self.open_output_button.setText(self.t("open_output_folder"))
        self.save_log_button.setText(self.t("save_log"))
        self.export_button.setText(self.t("export_csv"))
        self.errors_button.setText(self.t("show_errors"))
        self.stats_box.setTitle(self.t("statistics"))
        try:
            self.table.setHeaderLabels([self.t(k) for k in COLUMN_KEYS])
        except Exception:
            pass
        if not self.start_time:
            self.stats_label.setText(self.t("stats_initial"))
        self.statusBar().showMessage(self.t("ready"))
        self.update_output_label()

    def show_settings(self):
        was_maximized = False
        was_fullscreen = False
        try:
            state = self.windowState()
            was_maximized = bool(state & QtCore.Qt.WindowMaximized) or self.isMaximized()
            was_fullscreen = bool(state & QtCore.Qt.WindowFullScreen) or self.isFullScreen()
        except Exception:
            pass
        dlg = SettingsDialog(self)
        result = dlg.exec_()
        if result == QtGui.QDialog.Accepted:
            try:
                if was_fullscreen:
                    self.showFullScreen()
                elif was_maximized:
                    self.showMaximized()
            except Exception:
                pass

    def load_state_to_controls(self):
        cfg = self.config_data
        self.preset_combo.setCurrentIndex(list_index(PRESETS, cfg.get("preset", "Custom")))
        self.format_combo.setCurrentIndex(list_index(OUTPUT_FORMAT_ITEMS, cfg.get("output_format", "mp3")))
        self.set_quality_combo_value(cfg.get("quality", "192k"))
        self.sample_combo.setCurrentIndex(list_index(SAMPLE_RATES, cfg.get("sample_rate", "44100 Hz"), 2))
        self.channels_combo.setCurrentIndex(list_index(CHANNELS, cfg.get("channels", "Stereo"), 1))
        self.conflict_combo.setCurrentIndex(list_index(CONFLICT_MODES, cfg.get("conflict", "Rename")))
        self.meta_check.setChecked(bool(cfg.get("keep_metadata", True)))
        self.structure_check.setChecked(bool(cfg.get("preserve_structure", False)))
        self.open_done_check.setChecked(bool(cfg.get("open_output_when_done", False)))
        self.sound_check.setChecked(bool(cfg.get("sound_enabled", True)))
        self.custom_output_folder = cfg.get("custom_output_folder", "")

    def current_settings(self):
        return {
            "preset": qstring_to_text(self.preset_combo.currentText()),
            "output_format": qstring_to_text(self.format_combo.currentText()),
            "quality": self.current_quality_value(),
            "sample_rate": qstring_to_text(self.sample_combo.currentText()),
            "channels": qstring_to_text(self.channels_combo.currentText()),
            "conflict": qstring_to_text(self.conflict_combo.currentText()),
            "ffmpeg_threads": normalize_ffmpeg_threads(self.config_data.get("ffmpeg_threads", "1")),
            "keep_metadata": bool(self.meta_check.isChecked()),
            "preserve_structure": bool(self.structure_check.isChecked()),
            "open_output_when_done": bool(self.open_done_check.isChecked()),
            "custom_output_folder": self.custom_output_folder,
            "language": self.config_data.get("language", detect_system_language()),
            "auto_analyze_on_add": bool(self.config_data.get("auto_analyze_on_add", True)),
            "dark_theme": bool(self.config_data.get("dark_theme", False)),
            "ui_scale": int(self.config_data.get("ui_scale", 80) or 80),
            "auto_ui_scale": bool(self.config_data.get("auto_ui_scale", True)),
            "screen_width": int(self.config_data.get("screen_width", 0) or 0),
            "screen_height": int(self.config_data.get("screen_height", 0) or 0),
            "splitter_sizes": self.get_splitter_sizes(),
            "list_height": bounded_int(self.get_splitter_sizes()[0], 220, 82, 460),
            "log_height": bounded_int(self.get_splitter_sizes()[2], 90, 58, 280),
            "sound_enabled": bool(self.sound_check.isChecked()),
            "custom_ffmpeg_path": self.config_data.get("custom_ffmpeg_path", ""),
            "custom_ffprobe_path": self.config_data.get("custom_ffprobe_path", ""),
            "confirm_stop": bool(self.config_data.get("confirm_stop", True)),
            "confirm_external_open": bool(self.config_data.get("confirm_external_open", False)),
            "safe_output_checks": bool(self.config_data.get("safe_output_checks", True)),
            "warn_huge_batch": bool(self.config_data.get("warn_huge_batch", True)),
            "huge_batch_limit": int(self.config_data.get("huge_batch_limit", 250) or 250),
            "path_length_warning": bool(self.config_data.get("path_length_warning", True)),
        }

    def save_state(self):
        save_config(self.current_settings())

    def resizeEvent(self, event):
        try:
            QtGui.QMainWindow.resizeEvent(self, event)
            if hasattr(self, "main_splitter"):
                QtCore.QTimer.singleShot(0, self.apply_splitter_sizes)
        except Exception:
            pass

    def closeEvent(self, event):
        try:
            self.runtime_timer.stop()
        except Exception:
            pass
        self.save_state()
        if self.worker is not None and self.worker.isRunning():
            answer = QtGui.QMessageBox.question(self, self.t("warning"), self.t("exit_running"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if answer != QtGui.QMessageBox.Yes:
                event.ignore()
                return
            self.worker.stop()
            self.clear_recovery()
        event.accept()

    def update_output_label(self):
        if self.custom_output_folder.strip():
            self.output_label.setText(self.t("output_folder_path", path=self.custom_output_folder.strip()))
        else:
            self.output_label.setText(self.t("output_folder_auto"))

    def choose_output(self):
        path = QtGui.QFileDialog.getExistingDirectory(self, self.t("choose_output_folder"), self.custom_output_folder or app_dir())
        path = qstring_to_text(path)
        if path:
            self.custom_output_folder = path
            self.update_output_label()

    def clear_output(self):
        self.custom_output_folder = ""
        self.update_output_label()

    def choose_files(self):
        filt = "Audio files (*.mp3 *.wav *.flac *.aac *.ogg *.m4a *.wma *.opus *.aiff *.alac *.ape *.mpc *.tta *.wv *.amr *.ac3 *.dts *.mka);;All files (*.*)"
        paths = QtGui.QFileDialog.getOpenFileNames(self, self.t("add_files"), app_dir(), filt)
        self.add_inputs([qstring_to_text(p) for p in paths])

    def choose_folder(self):
        path = QtGui.QFileDialog.getExistingDirectory(self, self.t("add_folder"), app_dir())
        path = qstring_to_text(path)
        if path:
            self.add_inputs([path])

    def add_inputs(self, paths):
        files = audio_only(paths)
        existing = set([norm_key(p) for p in self.input_paths])
        added = []
        for p in files:
            k = norm_key(p)
            if k not in existing:
                self.input_paths.append(norm_path(p))
                existing.add(k)
                added.append(norm_path(p))
        for p in added:
            self.insert_or_update_row(p, None)
        if added:
            try:
                self.overall_progress.setValue(0)
            except Exception:
                pass
            self.add_log(self.t("added_files", count=len(added)))
            if bool(self.config_data.get("auto_analyze_on_add", True)):
                self.add_log(self.t("auto_analysis_log"))
                QtCore.QTimer.singleShot(100, self.analyze_files)
        self.update_button_states()

    def insert_or_update_row(self, path, info):
        key = norm_key(path)
        if info is None:
            values = [path, "-", "-", "-", "-", "-", "-", "-", "0%"]
        else:
            values = [
                path,
                info.get("format", "-"),
                info.get("codec", "-"),
                info.get("bitrate", "-"),
                info.get("sample", "-"),
                info.get("channels", "-"),
                info.get("duration", "-"),
                info.get("size", "-"),
                "0%",
            ]
        item = self.find_item(key)
        if item is None:
            item = QtGui.QTreeWidgetItem()
            item.setData(0, QtCore.Qt.UserRole, key)
            self.table.addTopLevelItem(item)
        for i, value in enumerate(values):
            item.setText(i, to_text(value))
        try:
            item.setTextAlignment(len(COLUMNS) - 1, QtCore.Qt.AlignCenter)
        except Exception:
            pass
        try:
            self.ensure_row_progress_widget(item, 0)
        except Exception:
            pass

    def ensure_row_progress_widget(self, item, value=0):
        """Set row progress without embedding a QProgressBar widget.

        The RowProgressDelegate paints the row background itself. The last
        column remains text-only and shows the percentage.
        """
        try:
            col = len(COLUMNS) - 1
            value = bounded_int(value, 0, 0, 100)
            try:
                old_widget = self.table.itemWidget(item, col)
                if old_widget is not None:
                    self.table.removeItemWidget(item, col)
                    old_widget.deleteLater()
            except Exception:
                pass
            item.setData(0, RowProgressDelegate.PROGRESS_ROLE, int(value))
            item.setText(col, "%d%%" % int(value))
            try:
                item.setTextAlignment(col, QtCore.Qt.AlignCenter)
            except Exception:
                pass
            try:
                self.table.viewport().update()
            except Exception:
                pass
        except Exception:
            try:
                item.setText(len(COLUMNS) - 1, "%d%%" % int(value))
            except Exception:
                pass

    def set_file_progress_for_path(self, path, value):
        try:
            item = self.find_item(norm_key(path))
            if item is not None:
                self.ensure_row_progress_widget(item, value)
        except Exception:
            pass

    def reset_row_progresses(self):
        try:
            for i in range(self.table.topLevelItemCount()):
                item = self.table.topLevelItem(i)
                self.ensure_row_progress_widget(item, 0)
        except Exception:
            pass

    def find_item(self, key):
        for i in range(self.table.topLevelItemCount()):
            item = self.table.topLevelItem(i)
            try:
                data = item.data(0, QtCore.Qt.UserRole)
                if hasattr(data, "toString"):
                    data_text = qstring_to_text(data.toString())
                else:
                    data_text = qstring_to_text(data)
                if data_text == key:
                    return item
            except Exception:
                pass
            try:
                if norm_key(qstring_to_text(item.text(0))) == key:
                    return item
            except Exception:
                pass
        return None

    def selected_paths(self):
        paths = []
        for item in self.table.selectedItems():
            if item.columnCount() > 0:
                p = qstring_to_text(item.text(0))
                if p and p not in paths:
                    paths.append(p)
        return paths

    def remove_selected(self):
        selected = set([norm_key(p) for p in self.selected_paths()])
        if not selected:
            return
        self.input_paths = [p for p in self.input_paths if norm_key(p) not in selected]
        for i in reversed(range(self.table.topLevelItemCount())):
            item = self.table.topLevelItem(i)
            path = qstring_to_text(item.text(0))
            if norm_key(path) in selected:
                self.table.takeTopLevelItem(i)
        self.update_button_states()

    def clear_list(self):
        self.input_paths = []
        self.analysis_cache = {}
        self.table.clear()
        self.update_button_states()

    def open_confirmed(self, path):
        if not path:
            return False
        if bool(self.config_data.get("confirm_external_open", False)):
            answer = QtGui.QMessageBox.question(self, self.t("warning"), "%s\n\n%s" % (self.t("confirm_external_open"), path), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if answer != QtGui.QMessageBox.Yes:
                return False
        return open_path(path)

    def preview_selected(self):
        paths = self.selected_paths()
        if paths:
            self.open_confirmed(paths[0])

    def open_item(self, item, col):
        path = qstring_to_text(item.text(0))
        if path:
            self.open_confirmed(path)

    def analyze_files(self):
        if not self.input_paths:
            QtGui.QMessageBox.information(self, self.t("analyze"), self.t("no_analyze"))
            return
        if self.analyzer is not None and self.analyzer.isRunning():
            return
        ffprobe = get_effective_ffprobe_path(self.current_settings())
        if not os.path.exists(ffprobe):
            QtGui.QMessageBox.critical(self, self.t("error"), self.t("ffprobe_missing"))
            return
        self.analyzer = AnalyzeThread(list(self.input_paths), ffprobe, self)
        self.analyzer.rowAnalyzed.connect(self.on_row_analyzed)
        self.analyzer.progressChanged.connect(self.set_file_progress)
        self.analyzer.logMessage.connect(self.add_log)
        self.analyzer.finishedOk.connect(self.analysis_done)
        self.set_current_file(self.t("analysis_running"))
        self.set_file_progress(0)
        self.set_controls_busy(True, analyzing=True)
        self.analyzer.start()

    def on_row_analyzed(self, path, info):
        self.analysis_cache[norm_key(path)] = info
        self.insert_or_update_row(path, info)

    def analysis_done(self):
        self.set_current_file(self.t("current_file_empty"))
        try:
            self.overall_progress.setValue(100)
        except Exception:
            pass
        self.add_log(self.t("analysis_finished"))
        self.set_controls_busy(False, analyzing=False)
        self.update_button_states()

    def apply_preset(self, preset):
        preset = qstring_to_text(preset)
        if not preset or preset == "Custom":
            return
        cases = {
            "Legacy MP3 192k": ("mp3", "192k", "44100 Hz", "Stereo", True, False),
            "High Quality MP3": ("mp3", "320k", "44100 Hz", "Stereo", True, False),
            "Archive FLAC": ("flac", "Lossless / Best", "Original", "Original", True, False),
            "Lossless WAV": ("wav", "Lossless / Best", "Original", "Original", False, False),
            "Podcast / Voice": ("mp3", "128k", "44100 Hz", "Mono", True, False),
            "Audiobook": ("mp3", "128k", "44100 Hz", "Mono", True, False),
            "Car Audio": ("mp3", "256k", "44100 Hz", "Stereo", True, False),
            "Low Size MP3": ("mp3", "128k", "44100 Hz", "Stereo", False, False),
            "Web AAC": ("aac", "192k", "44100 Hz", "Stereo", True, False),
            "OGG Vorbis": ("ogg", "192k", "44100 Hz", "Stereo", True, False),
            "OPUS Voice": ("opus", "128k", "48000 Hz", "Mono", False, False),
        }
        if preset in cases:
            fmt, quality, sr, ch, meta, preserve = cases[preset]
            self.format_combo.setCurrentIndex(list_index(OUTPUT_FORMAT_ITEMS, fmt))
            self.set_quality_combo_value(quality)
            self.sample_combo.setCurrentIndex(list_index(SAMPLE_RATES, sr))
            self.channels_combo.setCurrentIndex(list_index(CHANNELS, ch))
            self.meta_check.setChecked(meta)
            self.structure_check.setChecked(preserve)

    def preflight_check(self, dry_run=False):
        settings = self.current_settings()
        problems = []
        warnings = []
        if not self.input_paths:
            QtGui.QMessageBox.critical(self, self.t("error"), self.t("no_files"))
            return False
        ffmpeg = get_effective_ffmpeg_path(settings)
        ffprobe = get_effective_ffprobe_path(settings)
        if settings.get("custom_ffmpeg_path") and not os.path.isfile(settings.get("custom_ffmpeg_path")):
            problems.append(self.t("custom_ffmpeg_invalid"))
        if settings.get("custom_ffprobe_path") and not os.path.isfile(settings.get("custom_ffprobe_path")):
            problems.append(self.t("custom_ffprobe_invalid"))
        if not os.path.exists(ffmpeg) or not os.path.exists(ffprobe):
            problems.append(self.t("ffmpeg_missing"))
        existing = [p for p in self.input_paths if os.path.exists(p)]
        if not existing:
            problems.append(self.t("selected_missing"))
        files = audio_only(existing)
        if existing and not files:
            problems.append(self.t("no_audio_found"))
        base = get_output_base_for_paths(self.input_paths, self.custom_output_folder)
        if base:
            try:
                ensure_dir(base)
                test = os.path.join(base, ".aac_write_test_%d.tmp" % int(time.time()))
                with open(test, "w", encoding="utf-8") as f:
                    f.write("test")
                os.remove(test)
            except Exception as exc:
                problems.append(self.t("no_write_access", error=exc))
            if settings.get("safe_output_checks") and is_dangerous_output_folder(base):
                warnings.append(self.t("risky_output", path=base))
            if settings.get("path_length_warning") and estimate_long_path_warning(files, base, settings.get("output_format", "mp3")):
                warnings.append(self.t("long_paths_warning"))
        if settings.get("conflict") == "Overwrite":
            warnings.append(self.t("overwrite_warning"))
        try:
            huge_limit = int(settings.get("huge_batch_limit", 250) or 250)
        except Exception:
            huge_limit = 250
        if settings.get("warn_huge_batch") and len(files) >= huge_limit:
            warnings.append(self.t("huge_batch_warning", count=len(files)))
        if problems:
            QtGui.QMessageBox.critical(self, self.t("error"), "\n".join(problems))
            return False
        if warnings and not dry_run:
            answer = QtGui.QMessageBox.question(self, self.t("warning"), self.t("warnings_continue", warnings="\n".join(["- " + w for w in warnings])), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if answer != QtGui.QMessageBox.Yes:
                return False
        if dry_run and warnings:
            self.add_log(self.t("warning"))
            for warning in warnings:
                self.add_log("- " + warning)
        return True

    def start_conversion(self, dry_run=False):
        if self.worker is not None and self.worker.isRunning():
            QtGui.QMessageBox.warning(self, self.t("process_safety"), self.t("conversion_running"))
            return
        if self.analyzer is not None and self.analyzer.isRunning():
            QtGui.QMessageBox.warning(self, self.t("process_safety"), self.t("analysis_busy"))
            return
        if not self.preflight_check(dry_run):
            return
        self.save_state()
        self.clear_log()
        self.add_system_info_to_log()
        self.error_details = {}
        self.size_report = {}
        self.reset_row_progresses()
        self.overall_progress.setValue(0)
        self.output_folder_path = ""
        self.runtime_total = len(audio_only(self.input_paths))
        self.runtime_converted = 0
        self.runtime_skipped = 0
        self.runtime_failed = 0
        self.runtime_last_elapsed = "00:00:00"
        self.start_time = time.time()
        self.update_elapsed_tick()
        self.runtime_timer.start()
        self.write_recovery(dry_run)
        settings = self.current_settings()
        self.worker = ConvertThread(list(self.input_paths), settings, dry_run=dry_run, parent=self)
        self.worker.logMessage.connect(self.add_log)
        self.worker.errorDetail.connect(self.add_error)
        self.worker.currentFile.connect(self.set_current_file)
        self.worker.currentFilePath.connect(self.set_current_file_path)
        self.worker.fileProgress.connect(self.set_file_progress)
        self.worker.fileProgressPath.connect(self.set_file_progress_for_path)
        self.worker.overallProgress.connect(self.set_overall_progress)
        self.worker.statsChanged.connect(self.update_stats)
        self.worker.outputFolderReady.connect(self.set_output_folder)
        self.worker.sizeReportReady.connect(self.set_size_report)
        self.worker.finishedOk.connect(self.conversion_finished)
        self.set_controls_busy(True, analyzing=False)
        self.worker.start()

    def stop_conversion(self):
        if self.worker is None or not self.worker.isRunning():
            return
        answer = QtGui.QMessageBox.Yes
        if bool(self.config_data.get("confirm_stop", True)):
            answer = QtGui.QMessageBox.question(self, self.t("stop"), self.t("stop_question"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.Yes:
            self.worker.stop()
            self.add_log(self.t("stopping"))

    def conversion_finished(self, success):
        self.update_elapsed_tick()
        try:
            self.runtime_timer.stop()
        except Exception:
            pass
        self.clear_recovery()
        self.set_controls_busy(False, analyzing=False)
        self.set_current_file(self.t("current_file_done"))
        self.update_button_states()
        if success:
            self.add_log(self.t("conversion_finished"))
            if self.sound_check.isChecked():
                self.play_done_sound()
            self.show_done_report()
            if self.open_done_check.isChecked() and self.output_folder_path:
                self.open_confirmed(self.output_folder_path)
        else:
            QtGui.QMessageBox.warning(self, self.t("warning"), self.t("stopped_failed"))
        self.start_time = None
        self.update_window_title()

    def set_controls_busy(self, busy, analyzing=False):
        controls = [
            self.add_files_button, self.add_folder_button, self.remove_button, self.clear_button,
            self.analyze_button, self.preview_button, self.choose_output_button, self.clear_output_button,
            self.preset_combo, self.format_combo, self.quality_combo, self.sample_combo, self.channels_combo,
            self.conflict_combo, self.meta_check, self.structure_check, self.open_done_check,
            self.test_button, self.convert_button,
        ]
        for ctrl in controls:
            ctrl.setEnabled(not busy)
        if analyzing:
            self.analyze_button.setEnabled(False)
        self.stop_button.setEnabled(bool(busy and not analyzing))
        self.update_button_states()

    def update_button_states(self):
        running = self.worker is not None and self.worker.isRunning()
        analyzing = self.analyzer is not None and self.analyzer.isRunning()
        has_files = len(self.input_paths) > 0
        self.convert_button.setEnabled(has_files and not running and not analyzing)
        self.test_button.setEnabled(has_files and not running and not analyzing)
        self.stop_button.setEnabled(running)
        self.open_output_button.setEnabled(bool(self.output_folder_path))
        self.save_log_button.setEnabled(True)
        self.export_button.setEnabled(self.table.topLevelItemCount() > 0)
        self.errors_button.setEnabled(bool(self.error_details))

    def set_current_file(self, text):
        self.current_label.setText(text)
        self.statusBar().showMessage(text)

    def set_current_file_path(self, path):
        self.current_progress_path = to_text(path)

    def set_file_progress(self, value):
        try:
            if self.current_progress_path:
                self.set_file_progress_for_path(self.current_progress_path, int(value))
            elif self.analyzer is not None and self.analyzer.isRunning():
                self.overall_progress.setValue(int(value))
        except Exception:
            pass

    def set_overall_progress(self, value):
        self.overall_progress.setValue(int(value))

    def format_elapsed(self):
        try:
            if not self.start_time:
                return self.runtime_last_elapsed or "00:00:00"
            elapsed = int(time.time() - self.start_time)
            if elapsed < 0:
                elapsed = 0
            return "%02d:%02d:%02d" % (elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60)
        except Exception:
            return self.runtime_last_elapsed or "00:00:00"

    def update_window_title(self):
        try:
            running = self.worker is not None and self.worker.isRunning() and self.start_time is not None
        except Exception:
            running = False
        if running:
            try:
                pct = int(self.overall_progress.value())
            except Exception:
                pct = 0
            self.setWindowTitle("%s %s - %s - %d%%" % (APP_DISPLAY_NAME, APP_VERSION, self.format_elapsed(), pct))
        else:
            self.setWindowTitle("%s %s" % (APP_DISPLAY_NAME, APP_VERSION))

    def update_elapsed_tick(self):
        try:
            running = self.worker is not None and self.worker.isRunning() and self.start_time is not None
        except Exception:
            running = False
        if running:
            elapsed = self.format_elapsed()
            self.runtime_last_elapsed = elapsed
            self.stats_label.setText(self.t("stats_runtime", total=self.runtime_total, converted=self.runtime_converted, skipped=self.runtime_skipped, failed=self.runtime_failed, elapsed=elapsed))
            self.update_window_title()
        else:
            try:
                if self.runtime_timer.isActive():
                    self.runtime_timer.stop()
            except Exception:
                pass
            self.update_window_title()

    def update_stats(self, total, converted, skipped, failed, elapsed):
        self.runtime_total = int(total)
        self.runtime_converted = int(converted)
        self.runtime_skipped = int(skipped)
        self.runtime_failed = int(failed)
        self.runtime_last_elapsed = to_text(elapsed)
        self.stats_label.setText(self.t("stats_runtime", total=total, converted=converted, skipped=skipped, failed=failed, elapsed=elapsed))
        self.update_window_title()

    def set_output_folder(self, path):
        self.output_folder_path = path
        self.update_button_states()

    def set_size_report(self, report):
        self.size_report = report or {}

    def add_log(self, text):
        self.log_box.append(to_text(text))
        sb = self.log_box.verticalScrollBar()
        sb.setValue(sb.maximum())

    def add_system_info_to_log(self):
        try:
            self.add_log("=== System information ===")
            for line in system_info_lines():
                self.add_log(line)
            self.add_log("FFmpeg thread setting: %s / OldWin cap: %s" % (normalize_ffmpeg_threads(self.config_data.get("ffmpeg_threads", "1")), ffmpeg_thread_limit()))
            self.add_log("==========================")
        except Exception as exc:
            try:
                self.add_log("System information unavailable: %s" % exc)
            except Exception:
                pass

    def clear_log(self):
        self.log_box.clear()

    def add_error(self, filename, detail):
        self.error_details[filename] = detail
        self.update_button_states()

    def show_errors(self):
        if not self.error_details:
            QtGui.QMessageBox.information(self, self.t("show_errors"), self.t("no_errors_saved"))
            return
        dlg = QtGui.QDialog(self)
        dlg.setWindowTitle(self.t("error_details"))
        dlg.resize(860, 620)
        layout = QtGui.QVBoxLayout(dlg)
        text = QtGui.QTextEdit()
        text.setReadOnly(True)
        chunks = []
        for name, detail in self.error_details.items():
            chunks.append("===== %s =====\n%s\n" % (name, detail))
        text.setPlainText("\n".join(chunks))
        layout.addWidget(text)
        close = QtGui.QPushButton(self.t("close"))
        close.clicked.connect(dlg.accept)
        layout.addWidget(close, 0, QtCore.Qt.AlignRight)
        dlg.exec_()

    def show_done_report(self):
        r = self.size_report or {}
        message = (
            "Files: %s\n"
            "Before: %s\n"
            "After: %s\n"
            "Saved: %s\n\n"
            "Open output folder?"
        ) % (
            r.get("files", 0),
            format_bytes(r.get("before", 0)),
            format_bytes(r.get("after", 0)),
            format_bytes(r.get("saved", 0)),
        )
        if self.output_folder_path:
            answer = QtGui.QMessageBox.question(self, self.t("conversion_finished"), message, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.Yes:
                self.open_confirmed(self.output_folder_path)
        else:
            QtGui.QMessageBox.information(self, self.t("conversion_finished"), message)

    def open_output(self):
        if self.output_folder_path and os.path.isdir(self.output_folder_path):
            self.open_confirmed(self.output_folder_path)
        else:
            QtGui.QMessageBox.warning(self, self.t("warning"), self.t("output_unavailable"))

    def save_log(self):
        default_dir = self.output_folder_path if self.output_folder_path else LOG_DIR
        try:
            ensure_dir(default_dir)
        except Exception:
            default_dir = app_dir()
        path = QtGui.QFileDialog.getSaveFileName(self, self.t("save_log"), os.path.join(default_dir, "conversion_log_xp_pyqt4.txt"), "Text files (*.txt);;All files (*.*)")
        path = qstring_to_text(path)
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("%s\nVersion: %s\nAuthor: %s\n\n" % (APP_NAME, APP_VERSION, AUTHOR))
                f.write("Settings:\n")
                for k, v in sorted(self.current_settings().items()):
                    f.write("%s: %s\n" % (k, v))
                f.write("\nLog:\n%s\n" % qstring_to_text(self.log_box.toPlainText()))
            QtGui.QMessageBox.information(self, self.t("saved"), self.t("log_saved", path=path))
        except Exception as exc:
            QtGui.QMessageBox.critical(self, self.t("error"), self.t("save_log_failed", error=exc))

    def export_csv(self):
        if self.table.topLevelItemCount() == 0:
            QtGui.QMessageBox.information(self, self.t("export"), self.t("no_files_to_export"))
            return
        path = QtGui.QFileDialog.getSaveFileName(self, self.t("export_csv"), os.path.join(app_dir(), "audio_report_xp_pyqt4.csv"), "CSV files (*.csv);;All files (*.*)")
        path = qstring_to_text(path)
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([c[0] for c in COLUMNS])
                for row in range(self.table.topLevelItemCount()):
                    item = self.table.topLevelItem(row)
                    writer.writerow([qstring_to_text(item.text(col)) for col in range(len(COLUMNS))])
            QtGui.QMessageBox.information(self, self.t("export"), self.t("csv_saved", path=path))
        except Exception as exc:
            QtGui.QMessageBox.critical(self, self.t("export_error"), to_text(exc))

    def write_recovery(self, dry_run=False):
        try:
            payload = {
                "app": APP_NAME,
                "version": APP_VERSION,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "dry_run": bool(dry_run),
                "input_paths": list(self.input_paths),
                "settings": self.current_settings(),
            }
            with open(RECOVERY_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def clear_recovery(self):
        try:
            if os.path.exists(RECOVERY_PATH):
                os.remove(RECOVERY_PATH)
        except Exception:
            pass

    def check_recovery(self):
        try:
            if not os.path.exists(RECOVERY_PATH):
                return
            with open(RECOVERY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            paths = data.get("input_paths") or []
            if not paths:
                self.clear_recovery()
                return
            answer = QtGui.QMessageBox.question(
                self,
                "Crash recovery",
                "An unfinished conversion session was found.\n\nCreated: %s\nFiles: %d\n\nRestore?" % (data.get("created_at", "unknown"), len(paths)),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
            )
            if answer == QtGui.QMessageBox.Yes:
                settings = data.get("settings") or {}
                self.config_data.update(settings)
                self.load_state_to_controls()
                self.add_inputs([p for p in paths if os.path.exists(p)])
                self.add_log("Crash recovery: previous session restored.")
            self.clear_recovery()
        except Exception:
            self.clear_recovery()

    def play_done_sound(self):
        try:
            if winsound is not None:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass


    def long_path_limit_command(self):
        return r'add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f'

    def long_path_status_text(self):
        try:
            if not sys.platform.startswith("win"):
                return self.t("path_limit_status_unsupported")
            ver = sys.getwindowsversion()
            if int(ver.major) < 10:
                return self.t("path_limit_status_unsupported")
            if winreg is None:
                return self.t("path_limit_status_disabled")
            key = None
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\FileSystem", 0, winreg.KEY_READ)
                value, value_type = winreg.QueryValueEx(key, "LongPathsEnabled")
                try:
                    value = int(value)
                except Exception:
                    value = 0
                if value == 1:
                    return self.t("path_limit_status_enabled")
                return self.t("path_limit_status_disabled")
            finally:
                try:
                    if key is not None:
                        winreg.CloseKey(key)
                except Exception:
                    pass
        except Exception:
            return self.t("path_limit_status_disabled")

    def run_long_path_limit_process(self, status_label=None):
        try:
            if not sys.platform.startswith("win") or int(sys.getwindowsversion().major) < 10:
                QtGui.QMessageBox.warning(self, self.t("path_limit_helper_title"), self.t("path_limit_unsupported"))
                return
            params = self.long_path_limit_command()
            try:
                result = ctypes.windll.shell32.ShellExecuteW(None, "runas", "reg.exe", params, None, 1)
                try:
                    code = int(result)
                except Exception:
                    code = 0
                if code <= 32:
                    raise RuntimeError("ShellExecuteW returned %s" % code)
                message = self.t("path_limit_started")
                if status_label is not None:
                    status_label.setText(message)
                QtGui.QMessageBox.information(self, self.t("path_limit_helper_title"), message)
            except Exception as exc:
                QtGui.QMessageBox.critical(self, self.t("error"), self.t("path_limit_failed", error=exc))
        except Exception as exc:
            QtGui.QMessageBox.critical(self, self.t("error"), self.t("path_limit_failed", error=exc))

    def show_path_limit_helper(self):
        dlg = QtGui.QDialog(self)
        dlg.setWindowTitle(self.t("path_limit_helper_title"))
        dlg.resize(640, 360)
        layout = QtGui.QVBoxLayout(dlg)
        text = QtGui.QLabel(self.t("path_limit_helper_text"))
        text.setWordWrap(True)
        layout.addWidget(text)
        status = QtGui.QLabel(self.long_path_status_text())
        status.setWordWrap(True)
        layout.addWidget(status)
        command_edit = QtGui.QLineEdit()
        command_edit.setReadOnly(True)
        command_edit.setText("reg.exe " + self.long_path_limit_command())
        layout.addWidget(command_edit)
        buttons = QtGui.QHBoxLayout()
        copy_button = QtGui.QPushButton(self.t("path_limit_copy"))
        run_button = QtGui.QPushButton(self.t("path_limit_run"))
        close_button = QtGui.QPushButton(self.t("close"))
        buttons.addWidget(copy_button)
        buttons.addWidget(run_button)
        buttons.addStretch(1)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

        def copy_command():
            try:
                cb = QtGui.QApplication.clipboard()
                if cb is not None:
                    cb.setText("reg.exe " + self.long_path_limit_command())
                status.setText(self.t("path_limit_copied"))
            except Exception:
                pass

        copy_button.clicked.connect(copy_command)
        run_button.clicked.connect(lambda: self.run_long_path_limit_process(status))
        close_button.clicked.connect(dlg.accept)
        dlg.exec_()

    def show_license(self):
        dlg = QtGui.QDialog(self)
        dlg.setWindowTitle(self.t("license"))
        dlg.resize(820, 620)
        layout = QtGui.QVBoxLayout(dlg)
        title = QtGui.QLabel("%s - %s" % (APP_NAME, self.t("license")))
        font = title.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 1)
        title.setFont(font)
        layout.addWidget(title)
        tabs = QtGui.QTabWidget()
        mit_text = QtGui.QTextEdit()
        mit_text.setReadOnly(True)
        mit_text.setPlainText(MIT_LICENSE_TEXT)
        tabs.addTab(mit_text, self.t("mit_license"))
        third_text = QtGui.QTextEdit()
        third_text.setReadOnly(True)
        third_text.setPlainText(THIRD_PARTY_NOTICES_TEXT)
        tabs.addTab(third_text, self.t("third_party_licenses"))
        layout.addWidget(tabs, 1)
        close = QtGui.QPushButton(self.t("close"))
        close.clicked.connect(dlg.accept)
        layout.addWidget(close, 0, QtCore.Qt.AlignRight)
        dlg.exec_()

    def show_about(self):
        text = (
            "%s\n"
            "Version: %s\n"
            "Author: %s\n"
            "License: %s\n"
            "License details: use the Licenses button for MIT and third-party notices.\n"
            "Important: PyQt4 GPL and the bundled GPL-enabled FFmpeg build affect redistribution.\n\n"
            "OldWin Legacy PyQt4 Edition.\n\n"
            "Runtime target:\n"
            "- Windows XP SP3 x86\n"
            "- Python 3.4.x x86\n"
            "- PyQt4 4.11.4 / Qt 4.8.7 x86\n"
            "- PyInstaller 3.4\n"
            "- FFmpeg 3.0 win32 static\n\n"
            "FFmpeg: %s\n"
            "FFprobe: %s\n"
            "Data folder: %s\n"
            "Config file: %s\n"
        ) % (APP_NAME, APP_VERSION, AUTHOR, LICENSE_NAME, get_effective_ffmpeg_path(self.current_settings()), get_effective_ffprobe_path(self.current_settings()), DATA_DIR, CONFIG_PATH)
        QtGui.QMessageBox.about(self, self.t("about"), text)


def main():
    app = QtGui.QApplication(sys.argv)
    try:
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QtGui.QIcon(icon_path))
    except Exception:
        pass
    try:
        app.setStyle("Windows")
    except Exception:
        pass
    win = AudioConverterPyQt4()
    # Default start: windowed fullscreen/maximized. This keeps the taskbar and
    # normal window controls while giving the OldWin UI maximum space.
    try:
        win.showMaximized()
    except Exception:
        win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
