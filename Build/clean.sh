#!/bin/bash

# Script de Limpeza do Ambiente de Build
# Remove todos os arquivos gerados durante o build

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
    echo -e "${BLUE}[CLEAN]${NC} $1"
}

echo "=========================================="
echo "  Limpeza do Ambiente de Build"
echo "=========================================="

# Verifica se estamos no diretório correto
if [ ! -f "titanium_server.spec" ]; then
    print_error "Arquivo titanium_server.spec não encontrado!"
    print_error "Execute este script a partir do diretório Build/"
    exit 1
fi

print_header "Removendo arquivos de build..."
if [ -d "dist" ]; then
    rm -rf dist/
    print_status "Diretório dist/ removido"
fi

if [ -d "build" ]; then
    rm -rf build/
    print_status "Diretório build/ removido"
fi

if [ -d "__pycache__" ]; then
    rm -rf __pycache__/
    print_status "Cache Python removido"
fi

print_header "Removendo ambiente virtual..."
if [ -d "venv" ]; then
    rm -rf venv/
    print_status "Ambiente virtual removido"
else
    print_warning "Ambiente virtual não encontrado"
fi

print_header "Removendo arquivos temporários..."
# Remove arquivos .pyc
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

print_status "Limpeza concluída com sucesso!"
echo ""
print_status "Para recriar o ambiente de build, execute:"
echo "  ./build.sh"
echo ""
echo "=========================================="
echo "  Limpeza concluída!"
echo "=========================================="
