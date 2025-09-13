#!/usr/bin/env python3
"""
Teste para verificar se a cópia de dados está funcionando corretamente
"""

import json
import websocket
import time
from datetime import datetime, timedelta


def test_data_copy():
    """Testa se os dados estão sendo enviados corretamente após a correção"""
    print("🧪 Teste de Cópia de Dados - graphRequest")
    print("=" * 50)

    # Conecta WebSocket
    try:
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:8888/websocket")
        print("✅ Conectado ao WebSocket")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return

    # Cria requisição
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)

    request = {
        "commandName": "getStatusHistory",
        "payload": {
            "sensorInfos": [{
                "gateway": "gateway1",
                "topic": "temperature",
                "indicator": "sensor1"
            }],
            "requestId": f"test_copy_{int(time.time())}",
            "beginDate": start_time.isoformat() + "Z",
            "endDate": end_time.isoformat() + "Z"
        }
    }

    # Envia requisição
    ws.send(json.dumps(request))
    print("📤 Requisição enviada")

    # Aguarda resposta
    try:
        response = ws.recv()
        data = json.loads(response)

        print(f"📊 Status da resposta: {data.get('status')}")

        if data.get("status") == "statusInfo":
            message = data.get("message", {})

            # Verifica se os dados estão presentes
            if "info" in message:
                info_data = message["info"]
                print(f"✅ Dados recebidos: {len(info_data)} sensores")

                # Conta pontos de dados
                total_points = 0
                for sensor_name, sensor_data in info_data.items():
                    if isinstance(sensor_data, list):
                        total_points += len(sensor_data)
                        print(f"  📊 {sensor_name}: {len(sensor_data)} pontos")

                print(f"📈 Total de pontos: {total_points}")

                if total_points > 0:
                    print("✅ SUCESSO: Dados foram enviados corretamente!")
                else:
                    print("⚠️  AVISO: Nenhum ponto de dados encontrado")
            else:
                print("❌ ERRO: Campo 'info' não encontrado na resposta")
                print(f"📋 Estrutura da resposta: {list(message.keys())}")
        else:
            print(f"❌ ERRO: Status inesperado: {data.get('status')}")
            print(f"📋 Resposta completa: {data}")

    except Exception as e:
        print(f"❌ Erro ao receber resposta: {e}")

    # Fecha conexão
    ws.close()
    print("🔌 Desconectado do WebSocket")


if __name__ == "__main__":
    test_data_copy()

