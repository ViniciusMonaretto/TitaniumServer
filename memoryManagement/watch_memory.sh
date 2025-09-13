#!/bin/bash

# Script para monitorar memória usando ps e watch
# Uso: ./watch_memory.sh [intervalo_segundos]

INTERVAL=${1:-2}

echo "👀 Monitor de Memória com ps e watch"
echo "⏱️  Atualizando a cada $INTERVAL segundos"
echo "🛑 Pressione Ctrl+C para parar"
echo ""

# Comando para monitorar processos Python
MONITOR_CMD="ps aux | grep -E '(python|Python)' | grep -v grep | awk '{print \$2, \$4, \$6, \$11}' | column -t"

echo "📊 Monitorando processos Python:"
echo "   PID | %MEM | RSS(KB) | COMMAND"
echo "   ----|------|---------|--------"

# Usa watch para atualizar continuamente
watch -n $INTERVAL "$MONITOR_CMD"
