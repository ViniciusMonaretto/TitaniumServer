#!/bin/bash

# Script de Verificação de Pré-requisitos para Instalação em Sistema Linux Novo

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

echo "=========================================="
echo "  Verificação de Pré-requisitos"
echo "  Sistema Linux Novo"
echo "=========================================="

ERRORS=0

print_header "1. Verificando Sistema Operacional..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    print_status "Sistema: $NAME $VERSION"
else
    print_warning "Não foi possível identificar o sistema operacional"
fi

print_header "2. Verificando Python3..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python3 encontrado: $PYTHON_VERSION"
    
    # Verifica versão mínima (3.6)
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)" 2>/dev/null; then
        print_status "Versão do Python compatível (>= 3.6)"
    else
        print_error "Versão do Python muito antiga. Necessário >= 3.6"
        ((ERRORS++))
    fi
else
    print_error "Python3 não encontrado!"
    print_error "Instale com: sudo apt install python3 python3-pip python3-venv"
    ((ERRORS++))
fi

print_header "3. Verificando pip3..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    print_status "pip3 encontrado: $PIP_VERSION"
else
    print_error "pip3 não encontrado!"
    print_error "Instale com: sudo apt install python3-pip"
    ((ERRORS++))
fi

print_header "4. Verificando systemd..."
if command -v systemctl &> /dev/null; then
    print_status "systemd encontrado"
else
    print_error "systemd não encontrado!"
    print_error "Este script requer systemd (Ubuntu 15.04+, Debian 8+, CentOS 7+)"
    ((ERRORS++))
fi

print_header "5. Verificando permissões de sudo..."
if sudo -n true 2>/dev/null; then
    print_status "sudo configurado e funcionando"
else
    print_warning "sudo pode requerer senha durante a instalação"
fi

print_header "6. Verificando espaço em disco..."
AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
if [ "$AVAILABLE_SPACE" -gt 1048576 ]; then  # 1GB em KB
    print_status "Espaço em disco suficiente (>1GB disponível)"
else
    print_warning "Pouco espaço em disco disponível"
fi

print_header "7. Verificando conectividade de rede..."
if ping -c 1 google.com &> /dev/null; then
    print_status "Conectividade de rede OK"
else
    print_warning "Sem conectividade de rede (pode afetar instalação de dependências)"
fi

print_header "8. Verificando porta 8888..."
if netstat -tuln 2>/dev/null | grep -q ":8888 "; then
    print_warning "Porta 8888 já está em uso"
    print_warning "Você pode precisar parar outros serviços ou alterar a porta"
else
    print_status "Porta 8888 disponível"
fi

print_header "9. Verificando arquivos do projeto..."
if [ -f "../server/main.py" ]; then
    print_status "Arquivo main.py encontrado"
else
    print_error "Arquivo main.py não encontrado!"
    print_error "Execute este script a partir do diretório Build/"
    ((ERRORS++))
fi

if [ -f "../requirements.txt" ]; then
    print_status "Arquivo requirements.txt encontrado"
else
    print_error "Arquivo requirements.txt não encontrado!"
    ((ERRORS++))
fi

if [ -d "../server/webApp" ]; then
    print_status "Diretório webApp encontrado"
else
    print_error "Diretório webApp não encontrado!"
    ((ERRORS++))
fi

echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    print_status "Todos os pré-requisitos estão OK!"
    echo ""
    print_status "Você pode prosseguir com a instalação:"
    echo "  1. ./build.sh"
    echo "  2. sudo ./install_service.sh"
    echo ""
    print_status "Sistema pronto para instalação! 🎉"
else
    print_error "Encontrados $ERRORS problemas que precisam ser resolvidos"
    echo ""
    print_error "Resolva os problemas acima antes de prosseguir"
    echo ""
    print_status "Comandos úteis para instalação de dependências:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "  Fedora:        sudo dnf install python3 python3-pip"
fi
echo "=========================================="
