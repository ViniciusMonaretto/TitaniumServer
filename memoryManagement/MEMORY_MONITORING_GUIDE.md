 # 🔍 Guia de Monitoramento de Memória (Sem Código Python)

Este guia te mostra como monitorar memory leaks no seu programa **sem executar código Python adicional**.

## 🛠️ Ferramentas Disponíveis

### **1. Monitor de Processo** (`monitor_memory.sh`)
Monitora um processo específico em tempo real.

```bash
# Monitora todos os processos Python
./monitor_memory.sh python

# Monitora com intervalo de 10 segundos
./monitor_memory.sh python 10

# Analisa o log gerado
./analyze_memory_log.sh memory_monitor_*.log
```

### **2. Monitor do Sistema** (`system_memory_monitor.sh`)
Monitora a memória geral do sistema e processos Python.

```bash
# Monitora sistema a cada 10 segundos
./system_memory_monitor.sh 10
```

### **3. Htop Interativo** (`htop_memory_monitor.sh`)
Interface visual para monitorar processos.

```bash
# Abre htop configurado para monitoramento de memória
./htop_memory_monitor.sh
```

### **4. Watch Contínuo** (`watch_memory.sh`)
Monitora processos Python com atualização contínua.

```bash
# Atualiza a cada 2 segundos
./watch_memory.sh 2
```

### **5. Valgrind (Análise Profunda)** (`valgrind_memory_check.sh`)
Análise profunda de memory leaks (requer instalação).

```bash
# Analisa o main.py
./valgrind_memory_check.sh server/main.py
```

### **6. Monitor de Threads** (`monitor_threads.sh`)
Monitora threads individuais do sistema.

```bash
# Monitora threads com intervalo de 5s por 60 minutos
./monitor_threads.sh 5 60

# Monitora threads com intervalo de 2s por 30 minutos
./monitor_threads.sh 2 30
```

### **7. Monitor Avançado de Threads** (`advanced_thread_monitor.py`)
Monitor Python com métricas detalhadas e alertas.

```bash
# Monitora por 5 minutos com intervalo de 5s
python3 advanced_thread_monitor.py --interval 5 --duration 300

# Monitora por 10 minutos com intervalo de 2s
python3 advanced_thread_monitor.py -i 2 -d 600
```

### **8. Monitor Visual de Threads** (`visual_thread_monitor.py`)
Interface visual em tempo real para monitorar threads.

```bash
# Monitor visual com atualização a cada 2s
python3 visual_thread_monitor.py

# Monitor visual com atualização a cada 1s
python3 visual_thread_monitor.py --interval 1
```

## 🚀 Como Usar

### **Método 1: Monitoramento Simples**

1. **Terminal 1**: Execute seu programa
   ```bash
   python3 server/main.py
   ```

2. **Terminal 2**: Execute o monitor
   ```bash
   ./monitor_memory.sh python 5
   ```

3. **Analise os resultados**:
   ```bash
   ./analyze_memory_log.sh memory_monitor_*.log
   ```

### **Método 2: Monitoramento Visual**

1. **Terminal 1**: Execute seu programa
   ```bash
   python3 server/main.py
   ```

2. **Terminal 2**: Abra o htop
   ```bash
   ./htop_memory_monitor.sh
   ```

3. **No htop**:
   - Pressione `F6` para ordenar por memória
   - Pressione `F2` para configurar colunas
   - Adicione colunas: VIRT, RES, SHR, %MEM

### **Método 3: Monitoramento Contínuo**

```bash
# Em um terminal
./watch_memory.sh 3
```

## 📊 Interpretando os Resultados

### **Sinais de Memory Leak:**

1. **Crescimento contínuo** da coluna RES (memória física)
2. **Aumento constante** da coluna %MEM
3. **Processos que não liberam** memória após operações
4. **Taxa de crescimento > 1 MB/minuto**

### **Valores de Referência:**

- **< 0.1 MB/minuto**: Normal
- **0.1 - 1 MB/minuto**: Crescimento lento
- **> 1 MB/minuto**: Possível memory leak

## 🔧 Comandos Úteis do Sistema

### **Verificar memória atual:**
```bash
free -h
ps aux --sort=-%mem | head -10
```

### **Monitorar processo específico:**
```bash
# Por PID
ps -p <PID> -o pid,rss,vsz,pmem,comm

# Por nome
ps aux | grep python | grep -v grep
```

### **Usar top/htop:**
```bash
# Ordenar por memória
top -o %MEM

# Filtrar por processo
htop -u $USER
```

## 📈 Análise de Logs

### **Logs gerados:**
- `memory_monitor_*.log`: Logs de processo específico
- `system_memory_*.log`: Logs do sistema
- `valgrind_output.log`: Análise profunda (se usar valgrind)

### **Analisar logs:**
```bash
# Ver resumo
./analyze_memory_log.sh memory_monitor_*.log

# Ver em formato tabela
cat memory_monitor_*.log | column -t -s,

# Filtrar por crescimento
awk -F',' '$3 > 100 {print}' memory_monitor_*.log
```

## 🎯 Cenários de Teste

### **Teste 1: Execução Normal**
```bash
# Terminal 1
python3 server/main.py

# Terminal 2
./monitor_memory.sh python 5
```

### **Teste 2: Stress Test**
```bash
# Terminal 1
python3 server/main.py

# Terminal 2 (em loop)
for i in {1..100}; do
    echo "Iteração $i"
    sleep 10
done

# Terminal 3
./monitor_memory.sh python 10
```

### **Teste 3: Longa Duração**
```bash
# Terminal 1
python3 server/main.py

# Terminal 2 (monitora por 1 hora)
timeout 3600 ./monitor_memory.sh python 30
```

## 🚨 Sinais de Alerta

### **No htop/top:**
- Processo Python com %MEM > 10%
- Crescimento contínuo da coluna RES
- Múltiplos processos Python órfãos

### **Nos logs:**
- Taxa de crescimento > 1 MB/minuto
- Aumento constante no número de objetos
- Picos de memória que não retornam

### **No sistema:**
- Uso de memória > 80%
- Swap sendo usado ativamente
- Sistema lento/responsivo

## 💡 Dicas Importantes

1. **Execute testes longos** (30+ minutos) para detectar leaks lentos
2. **Monitore durante operações** que deveriam liberar memória
3. **Compare baseline** (início) com picos de uso
4. **Use múltiplas ferramentas** para confirmação
5. **Documente padrões** de uso normal vs anômalo

## 🔍 Troubleshooting

### **Problema: Script não executa**
```bash
chmod +x *.sh
```

### **Problema: Valgrind não funciona**
```bash
sudo apt-get install valgrind
```

### **Problema: Htop não abre**
```bash
sudo apt-get install htop
```

---

**Lembre-se**: Memory leaks são mais fáceis de detectar com monitoramento contínuo. Use estas ferramentas regularmente durante desenvolvimento e testes!
