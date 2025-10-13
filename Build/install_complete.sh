#!/bin/bash

# Script de Instalação Completa para Sistema Linux Novo
# Este script instala todas as dependências e o Titanium Server

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
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo "=========================================="
echo "  Instalação Completa - Titanium Server"
echo "  Sistema Linux Novo"
echo "=========================================="

# Verifica se está sendo executado como root
if [ "$EUID" -eq 0 ]; then
    print_error "Não execute este script como root!"
    print_error "Execute como usuário normal (sudo será solicitado quando necessário)"
    exit 1
fi

# Verifica se está no diretório correto
if [ ! -f "build.sh" ] || [ ! -f "install_service.sh" ]; then
    print_error "Execute este script a partir do diretório Build/"
    print_error "cd /caminho/para/TitaniumServer/Build"
    exit 1
fi

print_header "1. Verificando Pré-requisitos..."
./check_prerequisites.sh

if [ $? -ne 0 ]; then
    print_error "Pré-requisitos não atendidos. Resolva os problemas antes de continuar."
    exit 1
fi

print_header "2. Instalando Dependências do Sistema..."

# Detecta a distribuição
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    print_error "Não foi possível detectar a distribuição Linux"
    exit 1
fi

print_info "Distribuição detectada: $DISTRO"

case $DISTRO in
    ubuntu|debian)
        print_info "Instalando dependências para Ubuntu/Debian..."
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential
        ;;
    centos|rhel|fedora)
        print_info "Instalando dependências para CentOS/RHEL/Fedora..."
        if command -v dnf &> /dev/null; then
            sudo dnf install -y python3 python3-pip python3-devel gcc
        else
            sudo yum install -y python3 python3-pip python3-devel gcc
        fi
        ;;
    *)
        print_warning "Distribuição não reconhecida: $DISTRO"
        print_warning "Certifique-se de que Python 3.6+ e pip3 estão instalados"
        ;;
esac

print_header "3. Verificando Porta 8888..."
if netstat -tuln 2>/dev/null | grep -q ":8888 "; then
    print_warning "Porta 8888 está em uso!"
    print_info "Processos usando a porta:"
    sudo netstat -tulpn | grep ":8888 "
    echo ""
    read -p "Deseja continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Instalação cancelada pelo usuário"
        exit 1
    fi
else
    print_status "Porta 8888 disponível"
fi

print_header "4. Executando Build..."
./build.sh

if [ $? -ne 0 ]; then
    print_error "Build falhou!"
    exit 1
fi

print_header "5. Instalando Serviço..."
sudo ./install_service.sh

if [ $? -ne 0 ]; then
    print_error "Instalação do serviço falhou!"
    exit 1
fi

print_header "6. Verificando Instalação..."

# Aguarda o serviço inicializar
sleep 5

# Verifica status do serviço
if systemctl is-active --quiet titanium-server; then
    print_status "Serviço está rodando!"
else
    print_warning "Serviço não está rodando. Verificando logs..."
    sudo journalctl -u titanium-server --no-pager -n 20
fi

# Testa conectividade
print_info "Testando conectividade..."
if curl -s http://localhost:8888 > /dev/null; then
    print_status "Interface web acessível!"
else
    print_warning "Interface web não acessível. Verificando logs..."
    sudo journalctl -u titanium-server --no-pager -n 10
fi

echo ""
echo "=========================================="
print_status "Instalação Completa Finalizada!"
echo "=========================================="
echo ""
print_info "Comandos úteis:"
echo "  Status do serviço:    sudo systemctl status titanium-server"
echo "  Logs em tempo real:   sudo journalctl -u titanium-server -f"
echo "  Reiniciar serviço:    sudo systemctl restart titanium-server"
echo "  Parar serviço:        sudo systemctl stop titanium-server"
echo "  Desinstalar:          sudo ./uninstall_service.sh"
echo ""
print_info "Acesso à interface:"
echo "  Local:  http://localhost:8888"
echo "  Rede:   http://$(hostname -I | awk '{print $1}'):8888"
echo ""
print_status "Sistema pronto para uso! 🎉"
