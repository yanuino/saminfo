# packaging/pyinstaller/linux.spec
# Generic PyInstaller spec for Linux
# Entry point: python -m <module>

import os

module_name = os.environ.get("PYINSTALLER_MODULE", "project")
binary_name = os.environ.get("PYINSTALLER_NAME", module_name)

a = Analysis(
    [],
    hiddenimports=[module_name],
    binaries=[],
    datas=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    [],
    [],
    [],
    [],
    name=binary_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
