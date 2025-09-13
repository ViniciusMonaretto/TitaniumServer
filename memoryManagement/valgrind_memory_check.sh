#!/bin/bash

# Script para usar valgrind para detectar memory leaks
# Uso: ./valgrind_memory_check.sh <script_python>

SCRIPT=${1:-"server/main.py"}

echo "🔍 Verificando se valgrind está disponível..."

if ! command -v valgrind &> /dev/null; then
    echo "❌ valgrind não está instalado"
    echo "💡 Para instalar:"
    echo "   sudo apt-get install valgrind"
    echo "   ou"
    echo "   sudo yum install valgrind"
    exit 1
fi

echo "✅ valgrind encontrado"
echo ""

# Verifica se o script Python existe
if [ ! -f "$SCRIPT" ]; then
    echo "❌ Script não encontrado: $SCRIPT"
    echo "💡 Use: ./valgrind_memory_check.sh <caminho_do_script>"
    exit 1
fi

echo "🚀 Executando valgrind no script: $SCRIPT"
echo "⏱️  Isso pode demorar um pouco..."
echo ""

# Executa valgrind com configurações otimizadas para Python
valgrind \
    --tool=memcheck \
    --leak-check=full \
    --show-leak-kinds=all \
    --track-origins=yes \
    --verbose \
    --log-file=valgrind_output.log \
    python3 "$SCRIPT"

echo ""
echo "✅ Análise concluída!"
echo "📊 Relatório salvo em: valgrind_output.log"
echo ""
echo "🔍 Para analisar o relatório:"
echo "   cat valgrind_output.log | grep -E '(LEAK|ERROR|definitely lost|indirectly lost)'"
echo ""
echo "📈 Para resumo:"
echo "   cat valgrind_output.log | grep -A5 -B5 'LEAK SUMMARY'"
