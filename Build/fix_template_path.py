#!/usr/bin/env python3
"""
Script para corrigir o caminho dos templates HTML no executável
"""
import os
import sys


def apply_template_fix():
    """Aplica a correção no arquivo visualization_manager.py"""

    original_file = "../server/apps/visualization/visualization_manager.py"
    backup_file = "../server/apps/visualization/visualization_manager.py.backup"

    # Verifica se já foi aplicada a correção
    if os.path.exists(backup_file):
        print("Correção de template já aplicada anteriormente")
        return

    # Faz backup do arquivo original
    if os.path.exists(original_file):
        os.rename(original_file, backup_file)
        print(f"Backup criado: {backup_file}")

    # Lê o arquivo original
    with open(backup_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Substitui a função get
    old_function = '''class Visualization(tornado.web.RequestHandler):
    def get(self, path=None):
        # Serve the main Angular app for all routes
        self.render("../../webApp/browser/index.html")'''

    new_function = '''class Visualization(tornado.web.RequestHandler):
    def get(self, path=None):
        # Função para obter caminho correto tanto em desenvolvimento quanto no executável
        def get_resource_path(relative_path):
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        
        # Tenta múltiplos caminhos possíveis para o template
        possible_paths = [
            "webApp/browser/index.html",
            "apps/visualization/../../webApp/browser/index.html",
            "index.html"
        ]
        
        template_path = None
        for path in possible_paths:
            full_path = get_resource_path(path)
            if os.path.exists(full_path):
                template_path = full_path
                break
        
        if template_path is None:
            self.write("Template não encontrado")
            return
            
        # Serve the main Angular app for all routes
        self.render(template_path)'''

    # Substitui o conteúdo
    new_content = content.replace(old_function, new_function)

    # Adiciona import sys se não existir
    if "import sys" not in new_content:
        new_content = new_content.replace("import os", "import os\nimport sys")

    # Escreve o arquivo modificado
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Correção de template aplicada: {original_file}")


def restore_original():
    """Restaura o arquivo original"""
    original_file = "../server/apps/visualization/visualization_manager.py"
    backup_file = "../server/apps/visualization/visualization_manager.py.backup"

    if os.path.exists(backup_file):
        os.rename(backup_file, original_file)
        print(f"Arquivo original restaurado: {original_file}")
    else:
        print("Arquivo de backup não encontrado")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_original()
    else:
        apply_template_fix()
