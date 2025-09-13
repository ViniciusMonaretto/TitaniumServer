#!/bin/bash

# Script para monitorar threads individuais do sistema TitaniumServer
# Uso: ./monitor_threads.sh [intervalo_em_segundos] [duração_em_minutos]

INTERVAL=${1:-5}
DURATION=${2:-60}
LOG_FILE="threads_monitor_$(date +%Y%m%d_%H%M%S).log"
PYTHON_PROCESS="python"

echo "🧵 Monitorando threads individuais do TitaniumServer"
echo "📊 Intervalo: ${INTERVAL}s"
echo "⏱️  Duração: ${DURATION}min"
echo "📝 Log: ${LOG_FILE}"
echo "⏰ Iniciado em: $(date)"
echo ""

# Cabeçalho do log
echo "timestamp,pid,thread_id,thread_name,status,cpu_percent,memory_mb,iterations,errors" > "$LOG_FILE"

# Função para obter informações detalhadas das threads
get_thread_info() {
    local pid=$1
    if [ -z "$pid" ] || ! kill -0 "$pid" 2>/dev/null; then
        return 1
    fi
    
    # Obtém informações das threads usando ps
    ps -T -p "$pid" -o tid,comm,stat,pcpu,pmem --no-headers | while read -r tid comm stat pcpu pmem; do
        # Filtra threads relevantes
        if [[ "$comm" == *"python"* ]] || [[ "$comm" == *"Titanium"* ]]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S'),$pid,$tid,$comm,$stat,$pcpu,$pmem,0,0"
        fi
    done
}

# Função para detectar threads problemáticas
detect_problematic_threads() {
    local current_log="$1"
    local threshold_cpu=50.0
    local threshold_memory=100.0
    
    echo "🔍 Analisando threads problemáticas..."
    
    # Threads com alto uso de CPU
    high_cpu=$(awk -F',' -v threshold="$threshold_cpu" '$6 > threshold {print $4 " (CPU: " $6 "%)"}' "$current_log" | tail -5)
    if [ -n "$high_cpu" ]; then
        echo "⚠️  Threads com alto uso de CPU:"
        echo "$high_cpu"
    fi
    
    # Threads com alto uso de memória
    high_memory=$(awk -F',' -v threshold="$threshold_memory" '$7 > threshold {print $4 " (Mem: " $7 "MB)"}' "$current_log" | tail -5)
    if [ -n "$high_memory" ]; then
        echo "⚠️  Threads com alto uso de memória:"
        echo "$high_memory"
    fi
    
    # Threads mortas
    dead_threads=$(awk -F',' '$5 ~ /Z/ {print $4}' "$current_log" | tail -5)
    if [ -n "$dead_threads" ]; then
        echo "💀 Threads mortas detectadas:"
        echo "$dead_threads"
    fi
}

# Encontra o processo Python principal
find_python_process() {
    ps aux | grep -E "(python.*main\.py|python.*server)" | grep -v grep | head -1 | awk '{print $2}'
}

echo "🔍 Procurando processo Python..."
PYTHON_PID=$(find_python_process)

if [ -z "$PYTHON_PID" ]; then
    echo "❌ Processo Python não encontrado!"
    echo "💡 Certifique-se de que o servidor está rodando com: python3 server/main.py"
    exit 1
fi

echo "✅ Processo Python encontrado: PID $PYTHON_PID"
echo ""

# Contador de tempo
start_time=$(date +%s)
end_time=$((start_time + DURATION * 60))

# Loop de monitoramento
while [ $(date +%s) -lt $end_time ]; do
    # Obtém informações das threads
    THREAD_INFO=$(get_thread_info "$PYTHON_PID")
    
    if [ -n "$THREAD_INFO" ]; then
        echo "$THREAD_INFO" >> "$LOG_FILE"
        
        # Exibe status atual
        thread_count=$(echo "$THREAD_INFO" | wc -l)
        current_time=$(date '+%H:%M:%S')
        printf "\r🧵 Threads ativas: %d | Última atualização: %s" "$thread_count" "$current_time"
    else
        echo "❌ Processo Python não encontrado ou terminou!"
        break
    fi
    
    sleep "$INTERVAL"
done

echo ""
echo ""
echo "📈 Resumo do monitoramento:"
echo "   - Log salvo em: $LOG_FILE"
echo "   - Duração: ${DURATION} minutos"
echo "   - Intervalo: ${INTERVAL} segundos"

# Análise do log
if [ -f "$LOG_FILE" ] && [ -s "$LOG_FILE" ]; then
    echo ""
    echo "📊 Análise das threads:"
    
    # Contagem de threads únicas
    unique_threads=$(tail -n +2 "$LOG_FILE" | cut -d',' -f4 | sort -u | wc -l)
    echo "   - Threads únicas detectadas: $unique_threads"
    
    # Threads mais ativas
    echo "   - Threads mais ativas:"
    tail -n +2 "$LOG_FILE" | cut -d',' -f4 | sort | uniq -c | sort -nr | head -5 | while read -r count thread; do
        echo "     $thread: $count ocorrências"
    done
    
    # Detecta threads problemáticas
    detect_problematic_threads "$LOG_FILE"
    
    # Estatísticas de CPU e memória
    echo ""
    echo "📊 Estatísticas de recursos:"
    avg_cpu=$(tail -n +2 "$LOG_FILE" | awk -F',' '{sum+=$6; count++} END {if(count>0) print sum/count; else print 0}')
    avg_memory=$(tail -n +2 "$LOG_FILE" | awk -F',' '{sum+=$7; count++} END {if(count>0) print sum/count; else print 0}')
    echo "   - CPU médio: ${avg_cpu}%"
    echo "   - Memória média: ${avg_memory}MB"
fi

echo ""
echo "💡 Para análise detalhada:"
echo "   cat $LOG_FILE | column -t -s,"
echo "   awk -F',' 'NR>1 {print \$4, \$6, \$7}' $LOG_FILE | sort -k2 -nr | head -10"
