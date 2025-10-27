# Pacote Debian - Titanium Server

Este diretório contém os arquivos necessários para criar um pacote `.deb` do Titanium Server, que replica o comportamento do script `install_service.sh`.

## Estrutura do Pacote

```
debian-package/
├── DEBIAN/
│   ├── control          # Metadados do pacote
│   ├── preinst          # Script executado antes da instalação
│   ├── postinst         # Script executado após a instalação
│   ├── prerm            # Script executado antes da remoção
│   └── postrm           # Script executado após a remoção
├── opt/titanium-server/ # Diretório de instalação do servidor
├── var/log/titanium-server/ # Diretório de logs
└── etc/systemd/system/  # Arquivo de serviço systemd
```

## Como Construir o Pacote

1. **Certifique-se de que o executável foi construído:**
   ```bash
   ./build.sh
   ```

2. **Construa o pacote .deb:**
   ```bash
   ./build_deb.sh
   ```

3. **O pacote será criado como:** `titanium-server_1.0.0_amd64.deb`

## Como Instalar o Pacote

```bash
sudo dpkg -i titanium-server_1.0.0_amd64.deb
```

## Comportamento do Pacote

O pacote `.deb` replica exatamente o comportamento do `install_service.sh`:

### Durante a Instalação:
- **preinst**: Cria usuário `titanium` e diretórios necessários
- **postinst**: Configura permissões, habilita serviço systemd

### Durante a Remoção:
- **prerm**: Para e desabilita o serviço
- **postrm**: Remove arquivo de serviço e recarrega systemd

### Arquivos Instalados:
- `/opt/titanium-server/titanium_server` - Executável principal
- `/opt/titanium-server/webApp/` - Interface web
- `/opt/titanium-server/docker-compose.yml` - Configuração Docker para MongoDB e Mosquitto
- `/opt/titanium-server/data/` - Dados e configurações
- `/opt/titanium-server/logs/` - Logs do aplicativo
- `/var/log/titanium-server/` - Logs do sistema
- `/etc/systemd/system/titanium-server.service` - Configuração do serviço

## Comandos Úteis

Após a instalação:

```bash
# Gerenciar o serviço
sudo systemctl start titanium-server
sudo systemctl stop titanium-server
sudo systemctl restart titanium-server
sudo systemctl status titanium-server

# Ver logs
sudo journalctl -u titanium-server -f

# Desabilitar inicialização automática
sudo systemctl disable titanium-server
```

## Usando Docker Compose

O pacote inclui um arquivo `docker-compose.yml` para executar os serviços de dependência (MongoDB e Mosquitto MQTT):

```bash
# Navegar para o diretório de instalação
cd /opt/titanium-server

# Iniciar os serviços Docker
sudo docker-compose up -d

# Verificar status dos containers
sudo docker-compose ps

# Parar os serviços
sudo docker-compose down

# Ver logs dos serviços
sudo docker-compose logs -f
```

## Verificação do Pacote

```bash
# Ver conteúdo do pacote
dpkg -c titanium-server_1.0.0_amd64.deb

# Ver informações do pacote
dpkg -I titanium-server_1.0.0_amd64.deb

# Verificar instalação
dpkg -l titanium-server
```

## Remoção Completa

Para remover completamente todos os dados:

```bash
# Desinstalar o pacote
sudo dpkg -r titanium-server

# Remover dados restantes (opcional)
sudo rm -rf /opt/titanium-server
sudo rm -rf /var/log/titanium-server
sudo userdel titanium
```
