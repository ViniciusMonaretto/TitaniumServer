# Build e Instalação do Titanium Server

Este diretório contém todos os arquivos necessários para criar um executável do Titanium Server e instalá-lo como um serviço systemd no Linux.

## Arquivos Incluídos

- `titanium_server.spec` - Arquivo de configuração do PyInstaller
- `build.sh` - Script para criar o executável
- `clean.sh` - Script para limpar arquivos de build
- `titanium-server.service` - Arquivo de configuração do serviço systemd
- `install_service.sh` - Script para instalar o serviço
- `uninstall_service.sh` - Script para remover o serviço
- `check_prerequisites.sh` - Script para verificar pré-requisitos do sistema
- `install_complete.sh` - Script de instalação completa para sistemas novos
- `quick_fix.sh` - Script para correção rápida de problemas
- `fix_readonly.sh` - Script para corrigir problemas de sistema somente leitura
- `README.md` - Este arquivo com instruções
- `INSTALL_GUIDE.md` - Guia detalhado de instalação

## Pré-requisitos

### Sistema Operacional
- Linux (Ubuntu, Debian, CentOS, RHEL, etc.)
- Python 3.6 ou superior
- pip3

### Dependências Python
O script de build criará automaticamente um ambiente virtual e instalará todas as dependências necessárias. Não é necessário instalar dependências globalmente.

## Processo de Build e Instalação

### 🚀 **Instalação Rápida (Sistema Novo)**

Para instalar em um sistema Linux completamente novo:

```bash
cd Build/
./install_complete.sh
```

Este script faz tudo automaticamente:
- ✅ Verifica pré-requisitos
- ✅ Instala dependências do sistema
- ✅ Executa build
- ✅ Instala serviço
- ✅ Verifica funcionamento

### 📋 **Instalação Manual (Passo a Passo)**

#### 1. Verificar Pré-requisitos

```bash
cd Build/
./check_prerequisites.sh
```

#### 2. Criar o Executável

```bash
./build.sh
```

Este script irá:
- Criar um ambiente virtual Python (se não existir)
- Instalar PyInstaller e dependências no ambiente virtual
- Instalar dependências do projeto no ambiente virtual
- Limpar builds anteriores
- Criar o executável usando PyInstaller
- Gerar o arquivo `dist/titanium_server`

#### 3. Instalar como Serviço

Após o build bem-sucedido, instale o serviço:

```bash
sudo ./install_service.sh
```

Este script irá:
- Criar usuário e grupo `titanium` do sistema
- Criar estrutura de diretórios em `/opt/titanium-server/`
- Copiar o executável e arquivos necessários
- Copiar arquivos da interface web para `/opt/titanium-server/webApp/`
- Configurar permissões adequadas
- Instalar e habilitar o serviço systemd

#### 4. Gerenciar o Serviço

#### Iniciar o Serviço
```bash
sudo systemctl start titanium-server
```

#### Parar o Serviço
```bash
sudo systemctl stop titanium-server
```

#### Verificar Status
```bash
sudo systemctl status titanium-server
```

#### Ver Logs em Tempo Real
```bash
sudo journalctl -u titanium-server -f
```

#### Reiniciar o Serviço
```bash
sudo systemctl restart titanium-server
```

#### Habilitar/Desabilitar Inicialização Automática
```bash
# Habilitar
sudo systemctl enable titanium-server

# Desabilitar
sudo systemctl disable titanium-server
```

#### 5. Desinstalar o Serviço

Para remover completamente o serviço:

```bash
sudo ./uninstall_service.sh
```

## Estrutura de Diretórios

### Durante o Build
```
Build/
├── venv/                    # Ambiente virtual Python
├── dist/                    # Executável gerado
├── build/                   # Arquivos temporários do PyInstaller
└── *.spec                   # Configuração do PyInstaller
```

### Após Instalação do Serviço
```
/opt/titanium-server/
├── titanium_server          # Executável principal
├── webApp/                  # Arquivos da interface web
│   ├── browser/             # Arquivos HTML, CSS, JS
│   ├── prerendered-routes.json
│   └── 3rdpartylicenses.txt
├── logs/                    # Logs do aplicativo
├── data/                    # Dados do aplicativo
│   └── titanium_server_db.db
└── config/                  # Arquivos de configuração

/var/log/titanium-server/    # Logs do sistema
```

## Arquivos Web

Os arquivos da interface web são copiados para `/opt/titanium-server/webApp/` durante a instalação:

- **`browser/`** - Arquivos HTML, CSS, JavaScript da interface Angular
- **`prerendered-routes.json`** - Configuração de rotas pré-renderizadas
- **`3rdpartylicenses.txt`** - Licenças de terceiros

### Acesso à Interface Web

Após a instalação e inicialização do serviço, a interface web estará disponível em:
- **URL**: `http://localhost:8888`
- **WebSocket**: `ws://localhost:8888/websocket`

## Configuração do Serviço

O arquivo `titanium-server.service` está configurado com:

- **Usuário/Grupo**: `titanium` (usuário do sistema sem privilégios)
- **Restart**: Automático em caso de falha
- **Logs**: Integrados ao systemd journal
- **Segurança**: Configurações de sandboxing
- **Recursos**: Limites de arquivos e processos

## Gerenciamento do Ambiente Virtual

### Ativar o Ambiente Virtual Manualmente
```bash
cd Build/
source venv/bin/activate
```

### Desativar o Ambiente Virtual
```bash
deactivate
```

### Reinstalar Dependências
```bash
cd Build/
./clean.sh  # Remove tudo incluindo o venv
./build.sh  # Recriará o venv e instalará dependências
```

### Verificar Dependências Instaladas
```bash
cd Build/
source venv/bin/activate
pip list
deactivate
```

## Solução de Problemas

### 🚨 **Problemas Comuns**

#### Erro "Read-only file system"
```bash
sudo ./quick_fix.sh
```

#### Executável não é criado
- Verifique se o ambiente virtual foi criado corretamente
- Execute `./check_dependencies.sh` para verificar dependências
- Verifique se o arquivo `main.py` existe em `../server/`
- Tente recriar o ambiente virtual executando `./clean.sh` seguido de `./build.sh`

#### Serviço não inicia
- Verifique os logs: `sudo journalctl -u titanium-server -n 50`
- Verifique permissões: `ls -la /opt/titanium-server/`
- Verifique se o executável é válido: `/opt/titanium-server/titanium_server --help`

#### Problemas de Permissão
- Verifique se o usuário `titanium` foi criado: `id titanium`
- Verifique propriedade dos arquivos: `ls -la /opt/titanium-server/`
- Execute: `sudo ./fix_readonly.sh`

#### Porta 8888 em uso
```bash
sudo netstat -tulpn | grep 8888
sudo kill -9 <PID>
```

### 📋 **Scripts de Diagnóstico**

- **`check_prerequisites.sh`** - Verifica pré-requisitos do sistema
- **`quick_fix.sh`** - Correção rápida de problemas comuns
- **`fix_readonly.sh`** - Correção de problemas de sistema somente leitura

### 📊 **Logs**
- Logs do aplicativo: `/opt/titanium-server/logs/`
- Logs do sistema: `sudo journalctl -u titanium-server`
- Logs em tempo real: `sudo journalctl -u titanium-server -f`

## Personalização

### Modificar Configurações do Serviço
Edite o arquivo `titanium-server.service` antes de executar `install_service.sh`:

- Alterar usuário/grupo
- Modificar variáveis de ambiente
- Ajustar configurações de segurança
- Alterar diretórios de trabalho

### Modificar Build do PyInstaller
Edite o arquivo `titanium_server.spec`:

- Adicionar/remover dependências ocultas
- Incluir arquivos adicionais
- Modificar configurações de otimização
- Alterar nome do executável

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs do sistema
2. Consulte a documentação do PyInstaller
3. Verifique a documentação do systemd
4. Entre em contato com a equipe de desenvolvimento
