# Hook personalizado para detectar automaticamente todos os módulos do Titanium Server
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

# Detecta automaticamente todos os submódulos dos pacotes principais
hiddenimports = []

# Adiciona todos os submódulos dos pacotes principais
packages = [
    'apps',
    'modules',
    'middleware',
    'services',
    'dataModules',
    'support'
]

for package in packages:
    try:
        hiddenimports.extend(collect_submodules(package))
    except:
        pass

# Adiciona módulos específicos que podem ser importados dinamicamente
additional_modules = [
    'tornado.web',
    'tornado.websocket',
    'tornado.ioloop',
    'tornado.options',
    'paho.mqtt.client',
    'pymongo.mongo_client',
    'motor.motor_asyncio',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'psutil.process',
    'psutil.system',
]

hiddenimports.extend(additional_modules)

# Remove duplicatas
hiddenimports = list(set(hiddenimports))

print(f"Detectados {len(hiddenimports)} módulos automaticamente")
