#!/bin/bash

# Script de Desinstalação do Serviço Titanium Server
# Este script remove o serviço systemd e os arquivos instalados

set -e  # Para o script se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

echo "=========================================="
echo "  Desinstalação do Serviço Titanium Server"
echo "=========================================="

# Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then
    print_error "Este script deve ser executado como root (use sudo)"
    exit 1
fi

print_header "Parando e desabilitando serviço..."
# Para e desabilita o serviço se estiver rodando
if systemctl is-active --quiet titanium-server; then
    systemctl stop titanium-server
    print_status "Serviço parado"
fi

if systemctl is-enabled --quiet titanium-server; then
    systemctl disable titanium-server
    print_status "Serviço desabilitado"
fi

print_header "Removendo arquivos do sistema..."
# Remove arquivo de serviço
if [ -f "/etc/systemd/system/titanium-server.service" ]; then
    rm /etc/systemd/system/titanium-server.service
    systemctl daemon-reload
    print_status "Arquivo de serviço removido"
fi

# Remove diretórios e arquivos
if [ -d "/opt/titanium-server" ]; then
    rm -rf /opt/titanium-server
    print_status "Diretório /opt/titanium-server removido (incluindo arquivos web)"
fi

if [ -d "/var/log/titanium-server" ]; then
    rm -rf /var/log/titanium-server
    print_status "Logs removidos"
fi

print_header "Removendo usuário do sistema..."
# Remove usuário se existir
if id "titanium" &>/dev/null; then
    userdel titanium
    print_status "Usuário 'titanium' removido"
else
    print_warning "Usuário 'titanium' não encontrado"
fi

print_status "Desinstalação concluída com sucesso!"
echo ""
echo "=========================================="
echo "  Desinstalação concluída!"
echo "=========================================="
