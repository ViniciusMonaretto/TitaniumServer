#!/bin/bash

# Script para monitorar memory leaks sem executar código Python
# Uso: ./monitor_memory.sh <nome_do_processo> [intervalo_segundos]

PROCESS_NAME=${1:-"python"}
INTERVAL=${2:-5}
LOG_FILE="memory_monitor_$(date +%Y%m%d_%H%M%S).log"

echo "🔍 Monitorando memória do processo: $PROCESS_NAME"
echo "⏱️  Intervalo: $INTERVAL segundos"
echo "📝 Log: $LOG_FILE"
echo "🛑 Pressione Ctrl+C para parar"
echo ""

# Cabeçalho do log
echo "Timestamp,Process_ID,Memory_MB,CPU_%,Status" > "$LOG_FILE"

# Função para capturar Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Monitoramento interrompido"
    echo "📊 Log salvo em: $LOG_FILE"
    exit 0
}

trap cleanup SIGINT

# Loop de monitoramento
while true; do
    # Busca processos que correspondem ao nome
    PIDS=$(pgrep -f "$PROCESS_NAME" 2>/dev/null)
    
    if [ -z "$PIDS" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S'),N/A,N/A,N/A,Processo não encontrado"
        echo "$(date '+%Y-%m-%d %H:%M:%S'),N/A,N/A,N/A,Processo não encontrado" >> "$LOG_FILE"
    else
        for PID in $PIDS; do
            # Obtém informações do processo
            if [ -f "/proc/$PID/status" ]; then
                MEMORY_KB=$(grep VmRSS /proc/$PID/status | awk '{print $2}')
                MEMORY_MB=$((MEMORY_KB / 1024))
                CPU=$(ps -p $PID -o %cpu --no-headers 2>/dev/null | tr -d ' ')
                STATUS=$(ps -p $PID -o stat --no-headers 2>/dev/null | tr -d ' ')
                
                TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
                
                echo "$TIMESTAMP,$PID,$MEMORY_MB,$CPU,$STATUS"
                echo "$TIMESTAMP,$PID,$MEMORY_MB,$CPU,$STATUS" >> "$LOG_FILE"
            fi
        done
    fi
    
    sleep $INTERVAL
done
