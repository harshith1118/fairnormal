import json
import os
import sys

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db
from app.services.rag_service import RAGService
from app.services.eval_service import EvalService

def main():
    print("Initializing SQLite Database...")
    init_db()
    print("SQLite Database initialized successfully.")

    print("Seeding baseline 80-case evaluations...")
    EvalService.seed_pre_evaluated_results()

    seed_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "seed_bible.json")

    
    if not os.path.exists(seed_file):
        print(f"Error: Seed file not found at {seed_file}")
        return
        
    print(f"Loading seed data from {seed_file}...")
    with open(seed_file, "r", encoding="utf-8") as f:
        verses = json.load(f)
        
    print(f"Ingesting {len(verses)} verses into ChromaDB...")
    RAGService.ingest_verses(verses)
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    main()
