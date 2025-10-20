# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Adiciona o diretório do projeto ao path
# No contexto do PyInstaller, usamos o diretório atual de trabalho
project_root = os.path.abspath('..')
server_root = os.path.abspath('../server')
sys.path.insert(0, project_root)
sys.path.insert(0, server_root)

block_cipher = None

a = Analysis(
    ['../server/main.py'],
    pathex=[project_root, server_root],
    binaries=[],
    datas=[
        # Inclui arquivos de configuração em múltiplos locais
        ('../server/config/ui_config.json', 'services/config_handler/../../config'),
        ('../server/config/ui_config.json', 'config'),
        ('../server/config/ui_config.json', '.'),
        # Inclui arquivos web completos
        ('../server/webApp/browser', 'webApp/browser'),
        ('../server/webApp/prerendered-routes.json', 'webApp'),
        ('../server/webApp/3rdpartylicenses.txt', 'webApp'),
    ],
    hiddenimports=[
        # Apenas as dependências externas que o PyInstaller pode não detectar automaticamente
        'tornado',
        'paho.mqtt',
        'pytz',
        'pymongo',
        'motor',
        'openpyxl',
        'psutil',
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='titanium_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
