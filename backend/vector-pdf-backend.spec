# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
hidden = ['app.main'] + collect_submodules('fitz') + collect_submodules('docx') + collect_submodules('openpyxl')
datas = collect_data_files('fitz') + collect_data_files('docx') + collect_data_files('openpyxl') + [('../frontend/dist', 'frontend')]
a = Analysis(['run_backend.py'], pathex=['.'], binaries=[], datas=datas, hiddenimports=hidden, hookspath=[], runtime_hooks=[], excludes=['pytest', 'pandas', 'scipy', 'matplotlib', 'IPython', 'tkinter'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='Vector PDF Suite', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False)
