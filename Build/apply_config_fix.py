#!/usr/bin/env python3
"""
Script para aplicar correção de caminho de configuração automaticamente durante o build
"""
import os
import sys


def apply_config_fix():
    """Aplica a correção no arquivo config_handler.py"""

    original_file = "../server/services/config_handler/config_handler.py"
    backup_file = "../server/services/config_handler/config_handler.py.backup"

    # Verifica se já foi aplicada a correção
    if os.path.exists(backup_file):
        print("Correção já aplicada anteriormente")
        return

    # Faz backup do arquivo original
    if os.path.exists(original_file):
        os.rename(original_file, backup_file)
        print(f"Backup criado: {backup_file}")

    # Lê o arquivo original
    with open(backup_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Substitui a função read_default_config
    old_function = '''    def read_default_config(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        json_directory = os.path.join(
            script_directory, "..", "..", "config", "ui_config.json"
        )
        with open(json_directory, "r", encoding="utf-8") as json_file:'''

    new_function = '''    def read_default_config(self):
        # Função para obter caminho correto tanto em desenvolvimento quanto no executável
        def get_resource_path(relative_path):
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        
        # Tenta múltiplos caminhos possíveis
        possible_paths = [
            "config/ui_config.json",
            "services/config_handler/../../config/ui_config.json",
            "ui_config.json"
        ]
        
        json_directory = None
        for path in possible_paths:
            full_path = get_resource_path(path)
            if os.path.exists(full_path):
                json_directory = full_path
                break
        
        if json_directory is None:
            self._logger.error("Arquivo ui_config.json não encontrado em nenhum dos caminhos possíveis")
            return
            
        with open(json_directory, "r", encoding="utf-8") as json_file:'''

    # Substitui o conteúdo
    new_content = content.replace(old_function, new_function)

    # Adiciona import sys se não existir
    if "import sys" not in new_content:
        new_content = new_content.replace(
            "import json", "import json\nimport sys")

    # Escreve o arquivo modificado
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Correção aplicada: {original_file}")


def restore_original():
    """Restaura o arquivo original"""
    original_file = "../server/services/config_handler/config_handler.py"
    backup_file = "../server/services/config_handler/config_handler.py.backup"

    if os.path.exists(backup_file):
        os.rename(backup_file, original_file)
        print(f"Arquivo original restaurado: {original_file}")
    else:
        print("Arquivo de backup não encontrado")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_original()
    else:
        apply_config_fix()
