#!/bin/bash

# Script de Instalação do Serviço Titanium Server
# Este script instala o executável como um serviço systemd

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
echo "  Instalação do Serviço Titanium Server"
echo "=========================================="

# Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then
    print_error "Este script deve ser executado como root (use sudo)"
    exit 1
fi

# Verifica se o executável existe
if [ ! -f "dist/titanium_server" ]; then
    print_error "Executável não encontrado em dist/titanium_server"
    print_error "Execute primeiro o script build.sh"
    exit 1
fi

# Verifica se o arquivo de serviço existe
if [ ! -f "titanium-server.service" ]; then
    print_error "Arquivo titanium-server.service não encontrado!"
    exit 1
fi

print_header "Criando usuário e grupo do sistema..."
# Cria usuário e grupo se não existirem
if ! id "titanium" &>/dev/null; then
    useradd --system --shell /bin/false --home-dir /opt/titanium-server --create-home titanium
    print_status "Usuário 'titanium' criado"
else
    print_warning "Usuário 'titanium' já existe"
fi

print_header "Criando estrutura de diretórios..."
# Cria diretórios necessários
mkdir -p /opt/titanium-server/{logs,data,config}
mkdir -p /var/log/titanium-server

# Copia o executável
print_header "Copiando executável..."
cp dist/titanium_server /opt/titanium-server/
chmod +x /opt/titanium-server/titanium_server

# Copia arquivos de configuração se existirem
if [ -f "../titanium_server_db.db" ]; then
    cp ../titanium_server_db.db /opt/titanium-server/data/
    print_status "Banco de dados copiado"
fi

# Copia arquivos web para a pasta de instalação
print_header "Copiando arquivos web..."
if [ -d "../server/webApp" ]; then
    cp -r ../server/webApp /opt/titanium-server/
    print_status "Arquivos web copiados"
else
    print_warning "Diretório webApp não encontrado"
fi

# Remove arquivo de log se existir (pode ter sido criado com permissões incorretas)
if [ -f "/opt/titanium-server/app.log" ]; then
    rm -f /opt/titanium-server/app.log
    print_status "Arquivo app.log removido (será recriado com permissões corretas)"
fi

# Define permissões
print_header "Configurando permissões..."
chown -R titanium:titanium /opt/titanium-server
chown -R titanium:titanium /var/log/titanium-server
chmod 755 /opt/titanium-server
chmod 755 /opt/titanium-server/logs
chmod 755 /opt/titanium-server/data
chmod 755 /opt/titanium-server/config
chmod 755 /opt/titanium-server/webApp

# Instala o arquivo de serviço
print_header "Instalando serviço systemd..."
cp titanium-server.service /etc/systemd/system/
systemctl daemon-reload
print_status "Arquivo de serviço atualizado com configurações de segurança relaxadas"

print_header "Configurando serviço..."
# Habilita o serviço para iniciar automaticamente
systemctl enable titanium-server.service

print_status "Instalação concluída com sucesso!"
echo ""
print_status "Comandos úteis:"
echo "  Iniciar serviço:     sudo systemctl start titanium-server"
echo "  Parar serviço:       sudo systemctl stop titanium-server"
echo "  Status do serviço:   sudo systemctl status titanium-server"
echo "  Ver logs:            sudo journalctl -u titanium-server -f"
echo "  Reiniciar serviço:   sudo systemctl restart titanium-server"
echo "  Desabilitar serviço: sudo systemctl disable titanium-server"
echo ""
print_warning "Para iniciar o serviço agora, execute:"
echo "  sudo systemctl start titanium-server"
echo ""
echo "=========================================="
echo "  Instalação concluída!"
echo "=========================================="
