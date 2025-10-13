# 🚀 Guia de Instalação - Titanium Server

## 📋 Instalação em Sistema Linux Novo

### ✅ **Resposta Rápida: SIM, vai funcionar!**

Os scripts `build.sh` e `install_service.sh` foram projetados para funcionar em qualquer sistema Linux novo, mas há alguns pré-requisitos que precisam ser atendidos.

---

## 🔍 **1. Verificação de Pré-requisitos**

**Execute primeiro:**
```bash
cd /caminho/para/TitaniumServer/Build
./check_prerequisites.sh
```

Este script verifica:
- ✅ Python 3.6+ instalado
- ✅ pip3 disponível  
- ✅ systemd disponível
- ✅ Permissões sudo
- ✅ Espaço em disco
- ✅ Conectividade de rede
- ✅ Porta 8888 disponível
- ✅ Arquivos do projeto presentes

---

## 📦 **2. Dependências do Sistema**

### **Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### **CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip
```

### **Fedora:**
```bash
sudo dnf install python3 python3-pip
```

---

## 🛠️ **3. Processo de Instalação**

### **Passo 1: Build do Executável**
```bash
cd /caminho/para/TitaniumServer/Build
./build.sh
```

**O que acontece:**
- ✅ Cria ambiente virtual (`venv`)
- ✅ Instala PyInstaller e dependências
- ✅ Aplica correções de path automaticamente
- ✅ Gera executável em `dist/titanium_server`
- ✅ Restaura arquivos originais

### **Passo 2: Instalação do Serviço**
```bash
sudo ./install_service.sh
```

**O que acontece:**
- ✅ Cria usuário `titanium`
- ✅ Cria diretórios necessários
- ✅ Copia executável para `/opt/titanium-server/`
- ✅ Copia arquivos web para `/opt/titanium-server/webApp/`
- ✅ Configura permissões corretas
- ✅ Instala serviço systemd
- ✅ Habilita inicialização automática
- ✅ Inicia o serviço

---

## 🎯 **4. Verificação da Instalação**

### **Status do Serviço:**
```bash
sudo systemctl status titanium-server
```

### **Logs do Serviço:**
```bash
sudo journalctl -u titanium-server -f
```

### **Teste da Interface Web:**
```bash
curl http://localhost:8888
```

### **Teste de Conectividade:**
```bash
netstat -tuln | grep 8888
```

---

## 🔧 **5. Comandos de Gerenciamento**

### **Iniciar/Parar/Reiniciar:**
```bash
sudo systemctl start titanium-server
sudo systemctl stop titanium-server
sudo systemctl restart titanium-server
```

### **Habilitar/Desabilitar:**
```bash
sudo systemctl enable titanium-server
sudo systemctl disable titanium-server
```

### **Desinstalar:**
```bash
sudo ./uninstall_service.sh
```

---

## 🚨 **6. Solução de Problemas**

### **Problema: "Read-only file system"**
```bash
sudo ./quick_fix.sh
```

### **Problema: Permissões incorretas**
```bash
sudo chown -R titanium:titanium /opt/titanium-server
sudo systemctl restart titanium-server
```

### **Problema: Porta em uso**
```bash
sudo netstat -tulpn | grep 8888
sudo kill -9 <PID>
```

### **Problema: Dependências faltando**
```bash
sudo ./check_dependencies.sh
```

---

## 📁 **7. Estrutura Após Instalação**

```
/opt/titanium-server/
├── titanium_server          # Executável principal
├── app.log                  # Log da aplicação
├── logs/                    # Diretório de logs
├── data/                    # Diretório de dados
├── config/                  # Configurações
└── webApp/                  # Interface web
    └── browser/
        ├── index.html
        ├── assets/
        └── ...
```

---

## 🌐 **8. Acesso à Interface**

Após instalação bem-sucedida:
- **URL:** `http://localhost:8888`
- **URL Externa:** `http://SEU_IP:8888`

---

## ⚡ **9. Instalação Rápida (TL;DR)**

```bash
# 1. Verificar pré-requisitos
./check_prerequisites.sh

# 2. Build
./build.sh

# 3. Instalar
sudo ./install_service.sh

# 4. Verificar
sudo systemctl status titanium-server
curl http://localhost:8888
```

---

## 🎉 **Resultado Esperado**

Após a instalação completa:
- ✅ Serviço rodando automaticamente
- ✅ Interface web acessível
- ✅ Logs funcionando
- ✅ Reinicialização automática
- ✅ Conexão MQTT ativa

**O sistema estará 100% funcional e pronto para uso!** 🚀
