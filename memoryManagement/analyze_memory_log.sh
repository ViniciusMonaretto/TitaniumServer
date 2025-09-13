#!/bin/bash

# Script para analisar logs de memória gerados pelo monitor_memory.sh
# Uso: ./analyze_memory_log.sh <arquivo_log>

LOG_FILE=${1:-"memory_monitor_*.log"}

if [ ! -f "$LOG_FILE" ] && [ ! -f $(ls $LOG_FILE 2>/dev/null | head -1) ]; then
    echo "❌ Arquivo de log não encontrado: $LOG_FILE"
    echo "💡 Use: ./analyze_memory_log.sh <arquivo_log>"
    exit 1
fi

# Se for um padrão, pega o primeiro arquivo
if [ ! -f "$LOG_FILE" ]; then
    LOG_FILE=$(ls $LOG_FILE 2>/dev/null | head -1)
fi

echo "📊 Analisando log: $LOG_FILE"
echo ""

# Remove cabeçalho e processa dados
DATA=$(tail -n +2 "$LOG_FILE" | grep -v "Processo não encontrado")

if [ -z "$DATA" ]; then
    echo "❌ Nenhum dado válido encontrado no log"
    exit 1
fi

# Função para calcular estatísticas
calculate_stats() {
    local column=$1
    local name=$2
    
    echo "📈 $name:"
    
    # Primeiro valor
    FIRST=$(echo "$DATA" | head -1 | cut -d',' -f$column)
    echo "   Inicial: $FIRST"
    
    # Último valor
    LAST=$(echo "$DATA" | tail -1 | cut -d',' -f$column)
    echo "   Final: $LAST"
    
    # Diferença
    if [[ "$FIRST" =~ ^[0-9]+$ ]] && [[ "$LAST" =~ ^[0-9]+$ ]]; then
        DIFF=$((LAST - FIRST))
        echo "   Diferença: $DIFF"
        
        # Taxa de crescimento (assumindo intervalo de 5 segundos)
        TOTAL_LINES=$(echo "$DATA" | wc -l)
        TIME_MINUTES=$((TOTAL_LINES * 5 / 60))
        if [ $TIME_MINUTES -gt 0 ]; then
            RATE=$((DIFF / TIME_MINUTES))
            echo "   Taxa: $RATE MB/minuto"
            
            # Avaliação
            if [ $RATE -gt 10 ]; then
                echo "   🚨 POSSÍVEL MEMORY LEAK!"
            elif [ $RATE -gt 1 ]; then
                echo "   ⚠️  Crescimento moderado"
            else
                echo "   ✅ Crescimento normal"
            fi
        fi
    fi
    echo ""
}

# Estatísticas por PID
echo "🔍 Análise por Processo:"
echo ""

PIDS=$(echo "$DATA" | cut -d',' -f2 | sort -u)

for PID in $PIDS; do
    PID_DATA=$(echo "$DATA" | grep ",$PID,")
    if [ -n "$PID_DATA" ]; then
        echo "🆔 Processo $PID:"
        calculate_stats 3 "Memória (MB)" <<< "$PID_DATA"
    fi
done

# Estatísticas gerais
echo "📊 Estatísticas Gerais:"
echo ""

# Tempo total
FIRST_TIME=$(echo "$DATA" | head -1 | cut -d',' -f1)
LAST_TIME=$(echo "$DATA" | tail -1 | cut -d',' -f1)
echo "⏱️  Período: $FIRST_TIME → $LAST_TIME"

# Número de medições
TOTAL_MEASUREMENTS=$(echo "$DATA" | wc -l)
echo "📏 Total de medições: $TOTAL_MEASUREMENTS"

# Memória média
AVG_MEMORY=$(echo "$DATA" | cut -d',' -f3 | awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print 0}')
echo "📊 Memória média: $(printf "%.1f" $AVG_MEMORY) MB"

# Pico de memória
PEAK_MEMORY=$(echo "$DATA" | cut -d',' -f3 | sort -n | tail -1)
echo "📈 Pico de memória: $PEAK_MEMORY MB"

echo ""
echo "✅ Análise concluída!"
echo "💡 Para visualização gráfica, use: gnuplot ou importe o CSV em Excel/LibreOffice"
