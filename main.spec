# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo,
    FixedFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarFileInfo,
    VarStruct,
)

block_cipher = None

PROJECT_ROOT = Path.cwd()
APP_NAME = "Metryki Downloader"

hiddenimports = collect_submodules("metrykidownloader")

datas = []
for filename in (
    "icon.ico",
    "icon.png",
    "logo.png",
    "splash.png",
    "Metryki Downloader.png",
    "banner.png",
    "banner.jpg",
    "banner.jpeg",
    "header.png",
):
    path = PROJECT_ROOT / filename
    if path.exists():
        datas.append((str(path), "."))

icon_file = None
for candidate in ("icon.ico", "icon.png", "logo.png"):
    candidate_path = PROJECT_ROOT / candidate
    if candidate_path.exists():
        icon_file = str(candidate_path)
        break

splash_file = None
for candidate in ("splash.png",):
    candidate_path = PROJECT_ROOT / candidate
    if candidate_path.exists():
        splash_file = str(candidate_path)
        break

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(1, 6, 0, 0),
        prodvers=(1, 6, 0, 0),
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    "040904B0",
                    [
                        StringStruct("CompanyName", "Sebastian (Testatost)"),
                        StringStruct("FileDescription", "Metryki Downloader"),
                        StringStruct("FileVersion", "1.6.0"),
                        StringStruct("InternalName", "Metryki Downloader"),
                        StringStruct("OriginalFilename", "Metryki Downloader.exe"),
                        StringStruct("ProductName", "Metryki Downloader"),
                        StringStruct("ProductVersion", "1.6.0"),
                        StringStruct("Comments", "Written by Sebastian (Testatost)"),
                    ],
                )
            ]
        ),
        VarFileInfo([VarStruct("Translation", [1033, 1200])]),
    ],
)

a = Analysis(
    ["main.py"],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe_kwargs = dict(
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    version=version_info,
)

if splash_file:
    exe_kwargs["splash"] = splash_file

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    **exe_kwargs,
)