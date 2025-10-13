from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import time

# Conexão com o MongoDB
client = MongoClient(
    "mongodb://root:example@localhost:27017/?authSource=admin")
db = client["IoCloud"]
collection = db["SensorData"]

# Dados base (podes pegar direto do banco também)
base_data = [
    {"SensorFullTopic": "1C69209DFC08-temperature-0", "Value": -42.78},
    {"SensorFullTopic": "1C69209DFC08-temperature-1", "Value": -25.56},
    {"SensorFullTopic": "1C69209DFC08-temperature-2", "Value": -20.21},
    {"SensorFullTopic": "1C69209DFC08-temperature-3", "Value": -15.67},
    {"SensorFullTopic": "1C69209DFC08-temperature-4", "Value": -1.92},
    {"SensorFullTopic": "1C69209DFC08-temperature-5", "Value": 6.6},
    {"SensorFullTopic": "1C69209DFC08-temperature-6", "Value": 18.14},
    {"SensorFullTopic": "1C69209DFC08-temperature-7", "Value": 24.84},
    {"SensorFullTopic": "1C69209DFC08-temperature-8", "Value": 27.24},
    {"SensorFullTopic": "1C69209DFC08-temperature-9", "Value": 37.56},
    {"SensorFullTopic": "1C69209DFC08-temperature-10", "Value": 50.55},
    {"SensorFullTopic": "1C69209DFC08-temperature-11", "Value": 60.09},
    {"SensorFullTopic": "1C69209DFC08-temperature-12", "Value": 72.29},
    {"SensorFullTopic": "1C69209DFC08-temperature-13", "Value": 85.1},
    {"SensorFullTopic": "1C69209DFC08-temperature-14", "Value": 91.35},
    {"SensorFullTopic": "1C69209DFC08-temperature-15", "Value": 102.47},
    {"SensorFullTopic": "1C69209DFC08-temperature-16", "Value": 106.62},
    {"SensorFullTopic": "1C69209DFC08-temperature-17", "Value": 124.55},
    {"SensorFullTopic": "1C69209DFC08-temperature-18", "Value": 129.33},
    {"SensorFullTopic": "1C69209DFC08-temperature-19", "Value": 143.88},
]

# Quantidade de leituras por sensor
N = 20000
# Intervalo de 7 dias
one_week_seconds = 7 * 24 * 60 * 60
# Data base (hoje)
base_timestamp = int(time.time())

# Gerar array de timestamps compartilhado para todos os sensores
print("Gerando array de timestamps compartilhado...")
shared_timestamps = []
for _ in range(N):
    # Timestamp aleatório dentro de uma semana
    ts = base_timestamp - random.randint(0, one_week_seconds)
    shared_timestamps.append(ts)

# Ordenar timestamps para ter uma sequência temporal lógica
shared_timestamps.sort()

print(f"Array de {len(shared_timestamps)} timestamps gerado e ordenado.")

# Geração e inserção dos dados
for sensor in base_data:
    topic = sensor["SensorFullTopic"]
    base_value = sensor["Value"]

    print(f"Gerando dados para {topic}...")

    docs = []
    for i, ts in enumerate(shared_timestamps):
        # Valor com pequena variação (+/- 10%)
        value = base_value * (1 + random.uniform(-0.1, 0.1))

        docs.append({
            "SensorFullTopic": topic,
            "Timestamp": ts,
            "Value": round(value, 2)
        })

    # Inserção em lote (melhor performance)
    collection.insert_many(docs)

print("✅ Inserção concluída com sucesso!")
