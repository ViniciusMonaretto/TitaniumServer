#!/bin/bash

# Script para usar htop de forma automatizada para monitorar memory leaks
# Uso: ./htop_memory_monitor.sh

echo "🔍 Monitor de Memória com htop"
echo ""
echo "📋 Instruções:"
echo "1. Execute seu programa Python em outro terminal"
echo "2. Pressione 'F6' no htop para ordenar por memória"
echo "3. Pressione 'F2' para configurar colunas"
echo "4. Adicione colunas: VIRT, RES, SHR, %MEM"
echo "5. Observe o crescimento de memória ao longo do tempo"
echo ""
echo "🎯 O que procurar:"
echo "   - Crescimento contínuo da coluna RES (memória física)"
echo "   - Aumento constante da coluna %MEM"
echo "   - Processos que não liberam memória após operações"
echo ""
echo "⌨️  Atalhos úteis:"
echo "   F6 - Ordenar por coluna"
echo "   F2 - Configurar colunas"
echo "   F5 - Alternar visualização de árvore"
echo "   u - Filtrar por usuário"
echo "   / - Buscar processo"
echo "   q - Sair"
echo ""
echo "🚀 Iniciando htop..."
echo ""

# Inicia htop com configurações otimizadas para monitoramento de memória
htop -d 2 -s PERCENT_MEM
