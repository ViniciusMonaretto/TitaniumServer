#!/usr/bin/env python3
"""
Teste para verificar o fluxo de memória após as correções
"""

import psutil
import time
import json
import websocket
import sys
from datetime import datetime, timedelta


def find_titanium_process():
    """Encontra o processo Python do TitaniumServer"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python' and proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'main.py' in cmdline or 'server' in cmdline:
                    return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def get_memory_usage(pid):
    """Obtém uso de memória do processo"""
    try:
        process = psutil.Process(pid)
        return process.memory_info().rss / 1024 / 1024  # MB
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0


def test_memory_flow():
    """Testa o fluxo de memória após as correções"""
    print("🧪 Teste de Fluxo de Memória - Correções Implementadas")
    print("=" * 60)

    # Encontra processo
    pid = find_titanium_process()
    if not pid:
        print("❌ Processo TitaniumServer não encontrado!")
        return

    print(f"✅ Processo encontrado: PID {pid}")

    # Mede baseline
    baseline = get_memory_usage(pid)
    print(f"📊 Memória inicial: {baseline:.1f}MB")

    # Conecta WebSocket
    try:
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:8888/websocket")
        print("✅ Conectado ao WebSocket")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return

    # Envia 3 requisições para testar
    for i in range(3):
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
                "requestId": f"test_flow_{i}_{int(time.time())}",
                "beginDate": start_time.isoformat() + "Z",
                "endDate": end_time.isoformat() + "Z"
            }
        }

        # Mede memória antes
        memory_before = get_memory_usage(pid)

        # Envia requisição
        ws.send(json.dumps(request))
        print(f"📤 Enviada requisição #{i+1}")

        # Aguarda resposta
        try:
            response = ws.recv()
            data = json.loads(response)

            if data.get("status") == "statusInfo":
                message = data.get("message", {})

                # Verifica se os dados estão presentes
                if "info" in message:
                    info_data = message["info"]
                    total_points = sum(len(sensor_data) for sensor_data in info_data.values(
                    ) if isinstance(sensor_data, list))

                    # Mede memória após resposta
                    memory_after = get_memory_usage(pid)
                    delta = memory_after - memory_before

                    print(f"📊 Resposta #{i+1}: {total_points} pontos, "
                          f"Memória: {memory_before:.1f}MB → {memory_after:.1f}MB (Δ{delta:+.1f}MB)")

                    if delta > 2.0:
                        print("⚠️  AVISO: Aumento significativo de memória")
                    elif delta < 0:
                        print("✅ BOM: Memória foi liberada")
                    else:
                        print("✅ OK: Uso de memória controlado")
                else:
                    print(
                        f"❌ ERRO: Campo 'info' não encontrado na resposta #{i+1}")
            else:
                print(
                    f"❌ ERRO: Status inesperado na resposta #{i+1}: {data.get('status')}")

        except Exception as e:
            print(f"❌ Erro na resposta #{i+1}: {e}")

        time.sleep(2)  # Aguarda entre requisições

    # Medição final
    final_memory = get_memory_usage(pid)
    total_increase = final_memory - baseline

    print("\n" + "="*60)
    print("📈 RESULTADO DO TESTE DE FLUXO")
    print("="*60)
    print(f"📊 Memória inicial: {baseline:.1f}MB")
    print(f"📊 Memória final: {final_memory:.1f}MB")
    print(f"📊 Aumento total: {total_increase:.1f}MB")
    print(f"📊 Aumento por requisição: {total_increase/3:.1f}MB")

    # Avaliação
    if total_increase > 10:  # Mais de 10MB total
        print("🚨 PROBLEMA: Ainda há vazamento de memória!")
    elif total_increase > 5:  # Mais de 5MB total
        print("⚠️  AVISO: Pequeno vazamento de memória")
    else:
        print("✅ SUCESSO: Fluxo de memória está funcionando corretamente!")

    # Fecha conexão
    ws.close()
    print("🔌 Desconectado do WebSocket")

    print("\n💡 Explicação das correções implementadas:")
    print("   1. Cópia dos dados em send_message_to_ui()")
    print("   2. Limpeza de memória em safe_write_message()")
    print("   3. Garbage collection após envio")
    print("   4. Liberação de referências após write_message()")


if __name__ == "__main__":
    test_memory_flow()

