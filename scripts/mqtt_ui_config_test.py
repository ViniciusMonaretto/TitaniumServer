#!/usr/bin/env python3
"""
Simula, via MQTT, todos os gateways descritos em server/config/ui_config.json.

Diferente do mqtt_test.py (que simula um único gateway com uma lista fixa de
sensores), este script deriva o layout de cada gateway do próprio ui_config.json:
o índice de cada sensor no array do report é o "indicator" do painel, e o tipo
vem do campo "topic". Assim o simulador acompanha a configuração sem edição
manual quando painéis são adicionados ou removidos.

Protocolo (conforme modules/titanium_mqtt/translators/io_cloud_api.py):

  servidor  -> iocloud/request/all/command
               {"command": 2, ...}                      pedido de status

  gateway   -> iocloud/response/<device_id>/command
               {"command_index": 2, "command_status": 0,
                "device_id", "ip_address", "uptime",
                "sensors": [{gain, offset, index, state, unit}]}

               A "unit" desta mensagem é o que define o tipo de cada índice no
               servidor, então ela precisa bater com o ui_config.json — é isso
               que este script garante.

  gateway   -> iocloud/response/<device_id>/sensor/report
               {"timestamp": <epoch>, "sensors": [{value, active, unit}]}

               O tipo aqui vem da posição no array, não da unit.

As faixas de valor são propositalmente de ordens de grandeza diferentes
(temperatura ~25 ºC, pressão ~101 kPa) para exercitar os eixos por tipo do
gráfico: num eixo único a pressão achata contra o piso.

Uso:
    python3 scripts/mqtt_ui_config_test.py --list
    python3 scripts/mqtt_ui_config_test.py
    python3 scripts/mqtt_ui_config_test.py --gateways 1C69209DFC08 --interval 5
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime

import paho.mqtt.client as mqtt

DEFAULT_BROKER = "localhost"
DEFAULT_PORT = 1883
DEFAULT_INTERVAL = 10

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG = os.path.join(REPO_ROOT, "server", "config", "ui_config.json")

REQUEST_TOPIC = "iocloud/request/#"

# Tipo de sensor (campo "topic" do ui_config) -> unidade que o tradutor do
# servidor reconhece. Ver IoCloudApiTranslator._get_type_of_sensor.
UNIT_BY_TOPIC = {
    "temperature": "°C",
    "pressure": "kPa",
    "tension": "V",
    "current": "A",
    "power": "W",
    "powerFactor": "%",
}

# Índices sem painel configurado precisam existir no array mesmo assim, porque a
# posição é que define o índice. Vão como temperatura e o servidor simplesmente
# não terá ninguém inscrito neles.
FILLER_TOPIC = "temperature"

# Fator de potência em escala percentual, como o default de PowerReport (86.7).
# O mqtt_test.py usa 0.96; ajuste aqui se o dispositivo real mandar fração.
POWER_FACTOR_BASE = 96.0

# base, passo do random walk, mínimo, máximo
VALUE_PROFILE = {
    "temperature": (22.0, 0.25, 18.0, 32.0),
    "pressure": (101.3, 0.15, 98.0, 105.0),
    "tension": (220.0, 0.50, 210.0, 230.0),
    "current": (2.0, 0.05, 0.50, 4.00),
    "power": (440.0, 5.00, 100.0, 900.0),
    "powerFactor": (POWER_FACTOR_BASE, 0.20, 80.0, 100.0),
}


def load_layouts(config_path):
    """
    Lê o ui_config.json e devolve {gateway: [topic_por_indice, ...]}.

    O array é denso: buracos entre os indicadores configurados viram FILLER_TOPIC,
    já que o servidor identifica o sensor pela posição no array do report.
    """
    with open(config_path, encoding="utf-8") as config_file:
        ui_config = json.load(config_file)

    topic_by_index = {}

    for group_name, panels in ui_config.items():
        for panel in panels:
            gateway = panel["gateway"]
            index = int(panel["indicator"])
            topic = panel["topic"]

            if topic not in UNIT_BY_TOPIC:
                print(f"aviso: tipo '{topic}' do painel '{panel['name']}' "
                      f"({group_name}) não é reconhecido pelo servidor, ignorado")
                continue

            existing = topic_by_index.setdefault(gateway, {}).get(index)
            if existing is not None and existing != topic:
                print(f"aviso: gateway {gateway} índice {index} aparece como "
                      f"'{existing}' e '{topic}'; mantendo '{existing}'")
                continue

            topic_by_index[gateway][index] = topic

    layouts = {}
    for gateway, indexes in topic_by_index.items():
        layouts[gateway] = [indexes.get(i, FILLER_TOPIC)
                            for i in range(max(indexes) + 1)]

    return layouts, topic_by_index


def describe_layouts(layouts, topic_by_index):
    for gateway in sorted(layouts):
        layout = layouts[gateway]
        configured = topic_by_index[gateway]
        fillers = [i for i in range(len(layout)) if i not in configured]

        print(f"\n{gateway} — {len(layout)} sensores no report "
              f"({len(configured)} configurados)")

        runs = []
        for index, topic in enumerate(layout):
            if runs and runs[-1][2] == topic and runs[-1][1] == index - 1:
                runs[-1][1] = index
            else:
                runs.append([index, index, topic])

        for start, end, topic in runs:
            span = f"{start}" if start == end else f"{start}-{end}"
            print(f"    [{span:>7}] {topic} ({UNIT_BY_TOPIC[topic]})")

        if fillers:
            print(f"    sem painel configurado: {fillers} "
                  f"(enviados como {FILLER_TOPIC} apenas para manter o índice)")


def initial_values(layout):
    values = []
    for index, topic in enumerate(layout):
        base, _, minimum, maximum = VALUE_PROFILE[topic]
        # Um leve deslocamento por índice separa as curvas no gráfico
        start = base + (index % 20) * (0.4 if topic == "temperature" else 0.05)
        values.append(min(max(start, minimum), maximum))
    return values


def step_values(layout, values):
    """Random walk limitado, para curvas que parecem leitura de sensor."""
    for index, topic in enumerate(layout):
        _, step, minimum, maximum = VALUE_PROFILE[topic]
        moved = values[index] + random.uniform(-step, step)
        values[index] = round(min(max(moved, minimum), maximum), 2)

    # Potência acompanha tensão x corrente, quando o gateway tem os três
    try:
        tension_index = layout.index("tension")
        current_index = layout.index("current")
        power_index = layout.index("power")
    except ValueError:
        return values

    values[power_index] = round(
        values[tension_index] * values[current_index], 2)
    return values


def command_payload(gateway, layout, uptime):
    """Resposta ao comando 2: é ela que ensina os índices ao servidor."""
    sensors = []
    for index, topic in enumerate(layout):
        sensors.append({
            "gain": 1,
            "offset": 0,
            "index": index,
            "state": 0,
            "unit": UNIT_BY_TOPIC[topic],
        })

    return {
        "command_index": 2,
        "command_status": 0,
        "device_id": gateway,
        "ip_address": f"192.168.3.{79 + (hash(gateway) % 150)}",
        "uptime": uptime,
        "sensors": sensors,
    }


def report_payload(layout, values):
    sensors = []
    for index, topic in enumerate(layout):
        sensors.append({
            "value": values[index],
            "active": True,
            "unit": UNIT_BY_TOPIC[topic],
        })

    return {
        "timestamp": datetime.now().timestamp(),
        "sensors": sensors,
    }


class GatewaySimulator:
    def __init__(self, client, layouts, verbose):
        self._client = client
        self._layouts = layouts
        self._verbose = verbose
        self._values = {gw: initial_values(layout)
                        for gw, layout in layouts.items()}
        self._started_at = time.time()

    def uptime(self):
        return int(time.time() - self._started_at)

    def send_all_status(self):
        for gateway, layout in self._layouts.items():
            topic = f"iocloud/response/{gateway}/command"
            payload = command_payload(gateway, layout, self.uptime())
            self._client.publish(topic, json.dumps(payload))
            print(f"status  -> {topic} ({len(layout)} sensores)")

    def send_all_reports(self):
        for gateway, layout in self._layouts.items():
            values = step_values(layout, self._values[gateway])
            topic = f"iocloud/response/{gateway}/sensor/report"
            payload = report_payload(layout, values)
            self._client.publish(topic, json.dumps(payload))

            if self._verbose:
                print(f"report  -> {topic} {json.dumps(payload)}")
            else:
                preview = ", ".join(
                    f"{layout[i]}[{i}]={values[i]}"
                    for i in (0, len(layout) - 1)
                )
                print(f"report  -> {topic} ({len(values)} valores: {preview})")

    def handle_calibration(self, response_topic, obj):
        """Ecoa a calibração de volta, como o mqtt_test.py faz."""
        params = obj.get("params", {})
        if not all(key in params for key in ("sensor_id", "gain", "offset")):
            print(f"calibração sem campos obrigatórios em {response_topic}")
            return

        gateway = response_topic.split("/")[2]
        layout = self._layouts.get(gateway)
        index = int(params["sensor_id"])

        unit = UNIT_BY_TOPIC[FILLER_TOPIC]
        if layout is not None and 0 <= index < len(layout):
            unit = UNIT_BY_TOPIC[layout[index]]

        obj["command_index"] = 1
        obj["command_status"] = 0
        obj["sensor_id"] = index
        obj["gain"] = params["gain"]
        obj["offset"] = params["offset"]
        obj["unit"] = unit

        self._client.publish(response_topic, json.dumps(obj))
        print(f"calib   -> {response_topic} (sensor {index}, {unit})")


def main():
    parser = argparse.ArgumentParser(
        description="Simula os gateways do ui_config.json via MQTT.")
    parser.add_argument("--config", default=DEFAULT_CONFIG,
                        help="caminho do ui_config.json")
    parser.add_argument("--broker", default=DEFAULT_BROKER)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                        help="segundos entre reports (padrão: 10)")
    parser.add_argument("--gateways", nargs="+", metavar="ID",
                        help="simula apenas estes gateways")
    parser.add_argument("--once", action="store_true",
                        help="envia status + um report e sai")
    parser.add_argument("--list", action="store_true",
                        help="mostra o layout derivado do config e sai")
    parser.add_argument("--verbose", action="store_true",
                        help="imprime o payload completo de cada report")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"config não encontrado: {args.config}")
        return 1

    layouts, topic_by_index = load_layouts(args.config)

    if args.gateways:
        unknown = [gw for gw in args.gateways if gw not in layouts]
        if unknown:
            print(f"gateway(s) fora do config: {', '.join(unknown)}")
            print(f"disponíveis: {', '.join(sorted(layouts))}")
            return 1
        layouts = {gw: layouts[gw] for gw in args.gateways}
        topic_by_index = {gw: topic_by_index[gw] for gw in args.gateways}

    if not layouts:
        print("nenhum gateway encontrado no config")
        return 1

    print(f"config: {args.config}")
    print(f"gateways: {', '.join(sorted(layouts))}")
    describe_layouts(layouts, topic_by_index)

    if args.list:
        return 0

    client = mqtt.Client()
    simulator = GatewaySimulator(client, layouts, args.verbose)

    def on_connect(mqtt_client, userdata, flags, rc):
        if rc != 0:
            print(f"falha na conexão, código {rc}")
            return
        print(f"\nconectado em {args.broker}:{args.port}")
        mqtt_client.subscribe(REQUEST_TOPIC)
        # O servidor só aprende os índices pelo status, então manda de cara
        simulator.send_all_status()

    def on_message(mqtt_client, userdata, msg):
        if not msg.payload:
            print(f"payload vazio em {msg.topic}")
            return

        try:
            obj = json.loads(msg.payload)
        except json.JSONDecodeError as e:
            print(f"JSON inválido em {msg.topic}: {e}")
            return

        response_topic = msg.topic.replace("request/", "response/", 1)

        if obj.get("command") == 2:
            print(f"pedido de status em {msg.topic}")
            simulator.send_all_status()
            return

        if "params" in obj:
            simulator.handle_calibration(response_topic, obj)
            return

        print(f"comando não tratado em {msg.topic}: {msg.payload}")

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(args.broker, args.port)
    except OSError as e:
        print(f"não foi possível conectar em {args.broker}:{args.port}: {e}")
        return 1

    client.loop_start()

    try:
        if args.once:
            time.sleep(1)
            simulator.send_all_reports()
        else:
            while True:
                simulator.send_all_reports()
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nencerrando")
    finally:
        client.loop_stop()
        client.disconnect()

    return 0


if __name__ == "__main__":
    sys.exit(main())
