#!/bin/bash

# Script de Build para Titanium Server
# Este script cria um executável do programa Python usando PyInstaller

set -e  # Para o script se houver erro

echo "=========================================="
echo "  Build do Titanium Server"
echo "=========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica se estamos no diretório correto
if [ ! -f "titanium_server.spec" ]; then
    print_error "Arquivo titanium_server.spec não encontrado!"
    print_error "Execute este script a partir do diretório Build/"
    exit 1
fi

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    print_error "Python3 não está instalado!"
    exit 1
fi

# Cria e ativa ambiente virtual se não existir
if [ ! -d "venv" ]; then
    print_status "Criando ambiente virtual..."
    python3 -m venv venv
fi

print_status "Ativando ambiente virtual..."
source venv/bin/activate

# Verifica se o PyInstaller está instalado no venv
if ! python -c "import PyInstaller" 2>/dev/null; then
    print_warning "PyInstaller não está instalado no venv. Instalando..."
    pip install --upgrade pip
    pip install -r requirements-build.txt
fi

# Instala dependências do projeto no venv
print_status "Instalando dependências do projeto..."
if [ -f "../requirements.txt" ]; then
    pip install -r ../requirements.txt
else
    print_warning "Arquivo requirements.txt não encontrado"
fi

# Aplica correções
print_status "Aplicando correção de configuração..."
python3 apply_config_fix.py

print_status "Aplicando correção de templates..."
python3 fix_template_path.py

# Limpa builds anteriores (mas mantém o venv)
print_status "Limpando builds anteriores..."
rm -rf dist/ build/ __pycache__/

# Cria diretório de saída
mkdir -p dist

# Executa o PyInstaller usando o Python do venv
print_status "Executando PyInstaller..."
python -m PyInstaller titanium_server.spec

# Verifica se o executável foi criado
if [ -f "dist/titanium_server" ]; then
    print_status "Build concluído com sucesso!"
    print_status "Executável criado em: $(pwd)/dist/titanium_server"
    
    # Torna o executável executável
    chmod +x dist/titanium_server
    
    # Mostra informações do arquivo
    echo ""
    print_status "Informações do executável:"
    ls -lh dist/titanium_server
    
    echo ""
    print_status "Para testar o executável:"
    echo "  ./dist/titanium_server"
    
    echo ""
    print_status "Para instalar como serviço:"
    echo "  sudo ./install_service.sh"
    
else
    print_error "Falha ao criar o executável!"
    exit 1
fi

# Restaura arquivos originais
print_status "Restaurando arquivos originais..."
python3 apply_config_fix.py restore
python3 fix_template_path.py restore

# Desativa o ambiente virtual
deactivate

echo ""
echo "=========================================="
echo "  Build concluído!"
echo "=========================================="
