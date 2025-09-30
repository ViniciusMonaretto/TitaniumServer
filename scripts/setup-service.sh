#!/bin/bash

# Configurações
USER_NAME="venax"
SCRIPT_PATH="/home/venax/ioCloud/TitaniumServer/scripts/run.sh"
SERVICE_NAME="titanium-server"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

# 🔒 Verifica se o script existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Erro: O script $SCRIPT_PATH não existe."
    exit 1
fi

# 🛠️ Cria o serviço systemd apontando para o seu script
echo "🛠️ Criando serviço systemd: $SERVICE_NAME"
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Start Titanium Server on boot
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$(dirname "$SCRIPT_PATH")
ExecStart=$SCRIPT_PATH
Restart=on-failure
Environment=DOCKER_BUILDKIT=1

[Install]
WantedBy=multi-user.target
EOF

# 🔄 Atualiza e habilita o serviço
echo "🔄 Atualizando systemd..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "✅ Habilitando $SERVICE_NAME para iniciar no boot..."
sudo systemctl enable "$SERVICE_NAME"

# ▶️ Inicia o serviço agora
echo "🚀 Iniciando serviço agora..."
sudo systemctl start "$SERVICE_NAME"

# 📋 Mostra o status
echo "📋 Status do serviço:"
sudo systemctl status "$SERVICE_NAME" --no-pager
