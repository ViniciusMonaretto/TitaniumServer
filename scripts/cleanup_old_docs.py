#!/usr/bin/env python3
"""
Script de limpeza automática para documentos antigos
Execute este script periodicamente (ex: via cron job)
"""

from pymongo import MongoClient
import time

def clean_old_documents():
    client = MongoClient("mongodb://root:example@localhost:27017/?authSource=admin")
    db = client["IoCloud"]
    collection = db["SensorData"]
    
    now = time.time()
    ttl_threshold = now - (60 * 24 * 60 * 60)  # 60 dias
    
    old_count = collection.count_documents({"Timestamp": {"$lt": ttl_threshold}})
    if old_count > 0:
        result = collection.delete_many({"Timestamp": {"$lt": ttl_threshold}})
        print(f"Removidos {result.deleted_count:,} documentos antigos")
    else:
        print("Nenhum documento antigo encontrado")

if __name__ == "__main__":
    clean_old_documents()
