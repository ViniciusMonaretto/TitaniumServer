#!/bin/bash

# Script para construir o pacote .deb do Titanium Server
# Este script cria um pacote Debian com o mesmo comportamento do install_service.sh

set -e  # Para o script se houver erro

echo "=========================================="
echo "  Build do Pacote Debian - Titanium Server"
echo "=========================================="

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

# Verifica se estamos no diretório correto
if [ ! -f "build.sh" ]; then
    print_error "Script build.sh não encontrado!"
    print_error "Execute este script a partir do diretório Build/"
    exit 1
fi

# Verifica se o executável foi construído
if [ ! -f "dist/titanium_server" ]; then
    print_warning "Executável não encontrado. Executando build..."
    ./build.sh
fi

# Verifica se o arquivo de serviço existe
if [ ! -f "titanium-server.service" ]; then
    print_error "Arquivo titanium-server.service não encontrado!"
    exit 1
fi

print_header "Preparando arquivos para o pacote .deb..."

# Limpa o diretório do pacote
rm -rf debian-package/opt/titanium-server/*
rm -rf debian-package/etc/systemd/system/*

# Garante que os diretórios existam
mkdir -p debian-package/opt/titanium-server/{logs,data,config}
mkdir -p debian-package/etc/systemd/system

# Copia o executável
print_status "Copiando executável..."
cp dist/titanium_server debian-package/opt/titanium-server/
chmod +x debian-package/opt/titanium-server/titanium_server

# Copia arquivos web para a pasta de instalação
print_header "Copiando arquivos web..."
if [ -d "../server/webApp" ]; then
    cp -r ../server/webApp debian-package/opt/titanium-server/
    print_status "Arquivos web copiados"
else
    print_warning "Diretório webApp não encontrado"
fi

# Copia arquivo docker-compose.yml
print_header "Copiando arquivo docker-compose.yml..."
if [ -f "../server/docker-compose.yml" ]; then
    cp ../server/docker-compose.yml debian-package/opt/titanium-server/
    print_status "Arquivo docker-compose.yml copiado"
else
    print_warning "Arquivo docker-compose.yml não encontrado"
fi

# Copia o arquivo de serviço
print_status "Copiando arquivo de serviço..."
cp titanium-server.service debian-package/etc/systemd/system/

# Calcula o tamanho do pacote
print_status "Calculando tamanho do pacote..."
PACKAGE_SIZE=$(du -sk debian-package | cut -f1)

# Remove Installed-Size se já existir e adiciona o novo valor
sed -i '/^Installed-Size:/d' debian-package/DEBIAN/control
echo "Installed-Size: $PACKAGE_SIZE" >> debian-package/DEBIAN/control

print_header "Construindo pacote .deb..."

# Constrói o pacote
dpkg-deb --build debian-package titanium-server_1.0.0_amd64.deb

# Verifica se o pacote foi criado
if [ -f "titanium-server_1.0.0_amd64.deb" ]; then
    print_status "Pacote .deb criado com sucesso!"
    print_status "Arquivo: $(pwd)/titanium-server_1.0.0_amd64.deb"
    
    # Mostra informações do arquivo
    echo ""
    print_status "Informações do pacote:"
    ls -lh titanium-server_1.0.0_amd64.deb
    
    echo ""
    print_status "Para instalar o pacote:"
    echo "  sudo dpkg -i titanium-server_1.0.0_amd64.deb"
    echo ""
    print_status "Para verificar o conteúdo do pacote:"
    echo "  dpkg -c titanium-server_1.0.0_amd64.deb"
    echo ""
    print_status "Para verificar informações do pacote:"
    echo "  dpkg -I titanium-server_1.0.0_amd64.deb"
    
else
    print_error "Falha ao criar o pacote .deb!"
    exit 1
fi

echo ""
echo "=========================================="
echo "  Build do pacote .deb concluído!"
echo "=========================================="
