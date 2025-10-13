#!/bin/bash

# Script para correção manual dos problemas do serviço
# Execute com: sudo ./manual_fix.sh

echo "=========================================="
echo "  Correção Manual do Serviço"
echo "=========================================="

echo "1. Parando processos..."
pkill -f titanium_server || true
systemctl stop titanium-server || true

echo "2. Corrigindo permissões..."
chown -R titanium:titanium /opt/titanium-server/
chmod 755 /opt/titanium-server/
chmod 755 /opt/titanium-server/logs
chmod 755 /opt/titanium-server/data
chmod 755 /opt/titanium-server/config
chmod 755 /opt/titanium-server/webApp
chmod +x /opt/titanium-server/titanium_server

echo "3. Removendo arquivo de log problemático..."
rm -f /opt/titanium-server/app.log

echo "4. Recarregando systemd..."
systemctl daemon-reload

echo "5. Iniciando serviço..."
systemctl start titanium-server

echo "6. Aguardando 3 segundos..."
sleep 3

echo "7. Status do serviço:"
systemctl status titanium-server --no-pager

echo ""
echo "=========================================="
echo "  Correção concluída!"
echo "=========================================="
echo ""
echo "Para verificar logs em tempo real:"
echo "  sudo journalctl -u titanium-server -f"
echo ""
echo "Para verificar se a interface web está funcionando:"
echo "  curl http://localhost:8888"
