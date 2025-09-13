# 🔍 Memory Management Tools

Esta pasta contém todas as ferramentas para monitoramento e detecção de memory leaks no TitaniumServer.

## 📁 Arquivos Disponíveis

### **Scripts de Monitoramento:**
- `monitor_memory.sh` - Monitora processos Python específicos
- `system_memory_monitor.sh` - Monitora memória geral do sistema
- `htop_memory_monitor.sh` - Interface visual com htop
- `watch_memory.sh` - Monitoramento contínuo com watch
- `valgrind_memory_check.sh` - Análise profunda com valgrind

### **Scripts de Análise:**
- `analyze_memory_log.sh` - Analisa logs gerados pelos monitores

### **Documentação:**
- `MEMORY_MONITORING_GUIDE.md` - Guia completo de uso
- `README.md` - Este arquivo

## 🚀 Uso Rápido

### **Monitoramento Básico:**
```bash
# 1. Execute seu programa
python3 ../server/main.py

# 2. Em outro terminal, monitore
./monitor_memory.sh python 5

# 3. Analise os resultados
./analyze_memory_log.sh memory_monitor_*.log
```

### **Monitoramento Visual:**
```bash
./htop_memory_monitor.sh
```

### **Monitoramento do Sistema:**
```bash
./system_memory_monitor.sh 10
```

## 📊 Logs Gerados

Os scripts geram logs na pasta atual:
- `memory_monitor_*.log` - Logs de processo específico
- `system_memory_*.log` - Logs do sistema
- `valgrind_output.log` - Análise profunda (se usar valgrind)

## 🎯 Interpretação Rápida

### **Sinais de Memory Leak:**
- Taxa de crescimento > 1 MB/minuto
- Crescimento contínuo da memória
- Processos que não liberam memória

### **Valores Normais:**
- Taxa < 0.1 MB/minuto
- Memória estável após operações
- Liberação de memória após picos

## 📖 Documentação Completa

Para instruções detalhadas, consulte:
- `MEMORY_MONITORING_GUIDE.md` - Guia completo
- Comentários nos scripts para detalhes técnicos

---

**Dica**: Execute os testes durante desenvolvimento para detectar memory leaks precocemente!
