#!/bin/bash

# Monitor de memória usando ferramentas nativas do sistema
# Uso: ./system_memory_monitor.sh [intervalo_segundos]

INTERVAL=${1:-10}
LOG_FILE="system_memory_$(date +%Y%m%d_%H%M%S).log"

echo "🖥️  Monitorando memória do sistema"
echo "⏱️  Intervalo: $INTERVAL segundos"
echo "📝 Log: $LOG_FILE"
echo "🛑 Pressione Ctrl+C para parar"
echo ""

# Cabeçalho do log
echo "Timestamp,Total_MB,Used_MB,Free_MB,Available_MB,Python_Processes,Python_Memory_MB" > "$LOG_FILE"

# Função para capturar Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Monitoramento interrompido"
    echo "📊 Log salvo em: $LOG_FILE"
    echo ""
    echo "📈 Para analisar o log:"
    echo "   cat $LOG_FILE | column -t -s,"
    exit 0
}

trap cleanup SIGINT

# Loop de monitoramento
while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Informações gerais de memória
    MEMORY_INFO=$(free -m | grep "Mem:")
    TOTAL=$(echo $MEMORY_INFO | awk '{print $2}')
    USED=$(echo $MEMORY_INFO | awk '{print $3}')
    FREE=$(echo $MEMORY_INFO | awk '{print $4}')
    AVAILABLE=$(echo $MEMORY_INFO | awk '{print $7}')
    
    # Processos Python
    PYTHON_PROCESSES=$(pgrep -f python | wc -l)
    PYTHON_MEMORY=$(ps -eo pid,rss,comm | grep python | awk '{sum+=$2} END {print sum/1024}')
    
    # Se não há processos Python, define como 0
    if [ -z "$PYTHON_MEMORY" ]; then
        PYTHON_MEMORY=0
    fi
    
    # Exibe informações
    printf "%-19s | Total: %4d MB | Used: %4d MB | Free: %4d MB | Python: %2d procs (%4.0f MB)\n" \
           "$TIMESTAMP" "$TOTAL" "$USED" "$FREE" "$PYTHON_PROCESSES" "$PYTHON_MEMORY"
    
    # Salva no log
    echo "$TIMESTAMP,$TOTAL,$USED,$FREE,$AVAILABLE,$PYTHON_PROCESSES,$PYTHON_MEMORY" >> "$LOG_FILE"
    
    sleep $INTERVAL
done
