#!/bin/bash

# Script para corrigir problema de sistema de arquivos somente leitura

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo -e "${BLUE}[FIX]${NC} $1"
}

echo "=========================================="
echo "  Correção de Sistema Somente Leitura"
echo "=========================================="

# Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then
    print_error "Este script deve ser executado como root (use sudo)"
    exit 1
fi

print_header "1. Parando serviço..."
systemctl stop titanium-server || true

print_header "2. Verificando montagem do sistema de arquivos..."
mount | grep " / " | head -1

print_header "3. Atualizando arquivo de serviço..."
cp titanium-server.service /etc/systemd/system/
systemctl daemon-reload

print_header "4. Corrigindo permissões..."
chown -R titanium:titanium /opt/titanium-server/
chmod 755 /opt/titanium-server/
chmod 755 /opt/titanium-server/logs
chmod 755 /opt/titanium-server/data
chmod 755 /opt/titanium-server/config
chmod 755 /opt/titanium-server/webApp
chmod +x /opt/titanium-server/titanium_server

# Remove arquivo de log se existir
if [ -f "/opt/titanium-server/app.log" ]; then
    rm -f /opt/titanium-server/app.log
    print_status "Arquivo app.log removido"
fi

print_header "5. Testando escrita no diretório..."
sudo -u titanium touch /opt/titanium-server/test_write.log
if [ -f "/opt/titanium-server/test_write.log" ]; then
    print_status "✓ Escrita funcionando"
    rm -f /opt/titanium-server/test_write.log
else
    print_error "✗ Escrita não funcionando"
fi

print_header "6. Iniciando serviço..."
systemctl start titanium-server
sleep 3

print_header "7. Verificando status..."
systemctl status titanium-server --no-pager

print_header "8. Verificando logs..."
echo "Últimas 5 linhas dos logs:"
journalctl -u titanium-server -n 5 --no-pager

print_status "Correção concluída!"
echo ""
echo "=========================================="
echo "  Correção concluída!"
echo "=========================================="
