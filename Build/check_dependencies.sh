#!/bin/bash

# Script de Verificação de Dependências
# Verifica se todas as dependências necessárias estão instaladas

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

echo "=========================================="
echo "  Verificação de Dependências"
echo "=========================================="

# Verifica Python
print_header "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python3 encontrado: $PYTHON_VERSION"
    
    # Verifica versão mínima (3.6)
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)" 2>/dev/null; then
        print_status "Versão do Python compatível (>= 3.6)"
    else
        print_error "Versão do Python muito antiga. Necessário >= 3.6"
        exit 1
    fi
else
    print_error "Python3 não encontrado!"
    exit 1
fi

# Verifica pip
print_header "Verificando pip..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    print_status "pip3 encontrado: $PIP_VERSION"
else
    print_error "pip3 não encontrado!"
    exit 1
fi

# Verifica ambiente virtual
print_header "Verificando ambiente virtual..."
if [ -d "venv" ]; then
    print_status "Ambiente virtual encontrado"
    
    # Ativa o venv e verifica PyInstaller
    source venv/bin/activate
    if python -c "import PyInstaller" 2>/dev/null; then
        PYINSTALLER_VERSION=$(python -c "import PyInstaller; print(PyInstaller.__version__)")
        print_status "PyInstaller no venv: $PYINSTALLER_VERSION"
    else
        print_warning "PyInstaller não encontrado no venv. Será instalado durante o build."
    fi
    deactivate
else
    print_warning "Ambiente virtual não encontrado. Será criado durante o build."
fi

# Verifica dependências do projeto
print_header "Verificando dependências do projeto..."
if [ -f "../requirements.txt" ]; then
    print_status "Arquivo requirements.txt encontrado"
    
    # Se o venv existe, usa ele para verificar dependências
    if [ -d "venv" ]; then
        source venv/bin/activate
        print_status "Verificando dependências no ambiente virtual..."
        
        # Verifica cada dependência
        while IFS= read -r line; do
            # Remove comentários e linhas vazias
            line=$(echo "$line" | sed 's/#.*//' | xargs)
            if [ -n "$line" ]; then
                package=$(echo "$line" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1)
                if python -c "import $package" 2>/dev/null; then
                    print_status "✓ $package (venv)"
                else
                    print_warning "✗ $package não encontrado no venv"
                fi
            fi
        done < ../requirements.txt
        deactivate
    else
        print_warning "Ambiente virtual não encontrado. Dependências serão instaladas durante o build."
    fi
else
    print_warning "Arquivo requirements.txt não encontrado"
fi

# Verifica arquivos do projeto
print_header "Verificando arquivos do projeto..."
if [ -f "../server/main.py" ]; then
    print_status "Arquivo main.py encontrado"
else
    print_error "Arquivo ../server/main.py não encontrado!"
    exit 1
fi

# Verifica estrutura de diretórios
print_header "Verificando estrutura de diretórios..."
for dir in "../server" "../apps" "../modules" "../middleware" "../services" "../support"; do
    if [ -d "$dir" ]; then
        print_status "Diretório $dir encontrado"
    else
        print_warning "Diretório $dir não encontrado"
    fi
done

# Verifica permissões
print_header "Verificando permissões..."
if [ -w "." ]; then
    print_status "Permissão de escrita no diretório atual"
else
    print_error "Sem permissão de escrita no diretório atual"
    exit 1
fi

echo ""
print_status "Verificação de dependências concluída!"
echo ""
print_status "Para prosseguir com o build, execute:"
echo "  ./build.sh"
echo ""
echo "=========================================="
