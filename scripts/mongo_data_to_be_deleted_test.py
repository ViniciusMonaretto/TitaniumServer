from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import time

# ==== CONFIGURAÇÃO DE CONEXÃO ====
client = MongoClient(
    "mongodb://root:example@localhost:27017/?authSource=admin")
db = client["IoCloud"]
collection = db["SensorData"]

# ==== LIMPAR BASE ====
print("🗑️ Limpando dados existentes...")
collection.delete_many({})
print("✅ Dados existentes removidos.\n")

# ==== CONFIGURAÇÃO DE DADOS BASE ====
base_data = [
    {"SensorFullTopic": f"1C69209DFC08-temperature-{i}", "Value": v}
    for i, v in enumerate([
        -42.78, -25.56, -20.21, -15.67, -1.92, 6.6, 18.14, 24.84, 27.24, 37.56,
        50.55, 60.09, 72.29, 85.1, 91.35, 102.47, 106.62, 124.55, 129.33, 143.88
    ])
]

# ==== CONFIGURAÇÃO DE TEMPO ====
N = 200_000  # Leituras por sensor
base_timestamp = int(time.time())

# Gera dados antigos (para testar TTL)
start_days_ago = 120
end_days_ago = 90
start_timestamp = base_timestamp - start_days_ago * 24 * 60 * 60
end_timestamp = base_timestamp - end_days_ago * 24 * 60 * 60

print("Gerando dados antigos para testar TTL:")
print(f"  ⏱️  Período: {start_days_ago} a {end_days_ago} dias atrás")
print(f"  📆  Início: {datetime.fromtimestamp(start_timestamp)}")
print(f"  📆  Fim:    {datetime.fromtimestamp(end_timestamp)}")
print("  🧹  Todos os dados estarão mais antigos que 60 dias.\n")

# ==== GERAR TIMESTAMPS COMPARTILHADOS ====
print("⏳ Gerando timestamps compartilhados...")
shared_timestamps = sorted([
    random.randint(start_timestamp, end_timestamp) for _ in range(N)
])
print(f"✅ {len(shared_timestamps)} timestamps gerados e ordenados.\n")

# ==== GERAR E INSERIR DADOS ====
batch_size = 5000  # inserir em lotes para não travar
total_inserted = 0

for sensor in base_data:
    topic = sensor["SensorFullTopic"]
    base_value = sensor["Value"]

    print(f"🌡️ Gerando dados para {topic}...")

    docs = []
    for i, ts in enumerate(shared_timestamps):
        # Cria valor com variação de ±10%
        value = base_value * (1 + random.uniform(-0.1, 0.1))
        # O campo Timestamp deve ser um datetime, não int
        ts_dt = datetime.fromtimestamp(ts)

        docs.append({
            "SensorFullTopic": topic,
            "Timestamp": ts_dt,
            "Value": round(value, 2),
        })

        # Inserir em lotes
        if len(docs) >= batch_size:
            collection.insert_many(docs)
            total_inserted += len(docs)
            docs.clear()

    # Inserir o resto
    if docs:
        collection.insert_many(docs)
        total_inserted += len(docs)

    print(f"✅ Inseridos {total_inserted:,} registros até agora.\n")

print("🎉 Inserção concluída com sucesso!")
print(
    f"📦 Total final de documentos: {collection.estimated_document_count():,}")

# ==== INFORMAÇÕES SOBRE TTL ====
print("\n=== INFORMAÇÕES SOBRE TTL ===")
print("📅 Todos os dados são mais antigos que 60 dias.")
print("⏰ O MongoDB TTL deve remover esses dados automaticamente.")
print("🔄 O processo TTL roda a cada 60 segundos em background.")
print("🕐 Aguarde 1–2 minutos e rode:")
print("   db.SensorData.countDocuments({})")
print("✅ O número deve começar a diminuir automaticamente.")
