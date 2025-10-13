#!/bin/bash

# Script rápido para corrigir o problema de somente leitura

echo "=========================================="
echo "  Correção Rápida - Sistema Somente Leitura"
echo "=========================================="

echo "1. Parando serviço..."
systemctl stop titanium-server || true

echo "2. Atualizando arquivo de serviço..."
cp titanium-server.service /etc/systemd/system/
systemctl daemon-reload

echo "3. Corrigindo permissões..."
chown -R titanium:titanium /opt/titanium-server/
chmod 755 /opt/titanium-server/
chmod 755 /opt/titanium-server/logs
chmod 755 /opt/titanium-server/data
chmod 755 /opt/titanium-server/config
chmod 755 /opt/titanium-server/webApp
chmod +x /opt/titanium-server/titanium_server

echo "4. Removendo arquivo de log problemático..."
rm -f /opt/titanium-server/app.log

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
echo "  journalctl -u titanium-server -f"
echo ""
echo "Para testar a interface web:"
echo "  curl http://localhost:8888"
