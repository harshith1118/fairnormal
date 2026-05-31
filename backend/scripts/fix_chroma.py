import chromadb
import shutil
import os
import json
from app.config import settings

def fix_chroma():
    print("Fixing ChromaDB: Deleting existing collection and re-initializing with 768 dimensions.")
    
    # Path to chromadb
    chroma_path = settings.CHROMA_PATH
    
    # Delete the directory if it exists
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)
        print(f"Removed existing chromadb at {chroma_path}")
    
    # Initialize client
    client = chromadb.PersistentClient(path=chroma_path)
    
    # Re-create the collection with the correct dimension (768)
    collection = client.get_or_create_collection(
        name="scriptures",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Re-seed the data from seed_bible.json
    seed_file = os.path.join("data", "seed_bible.json")
    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    documents = []
    metadatas = []
    ids = []
    
    for i, item in enumerate(data):
        documents.append(item["text"])
        # Fix: Construct the reference string based on available fields
        reference = f"{item['book']} {item['chapter']}:{item['verse']}"
        metadatas.append({
            "reference": reference,
            "denomination": item["denomination"]
        })
        ids.append(str(i))
        
    print(f"Adding {len(documents)} documents to new collection...")
    # This will use chromadb's default embedding function which is compatible with 768
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Successfully re-initialized ChromaDB collection.")

if __name__ == "__main__":
    fix_chroma()
