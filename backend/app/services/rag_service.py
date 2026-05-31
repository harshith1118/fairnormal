import chromadb
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class RAGService:
    _client = None
    _collection = None

    @classmethod
    def get_collection(cls):
        if cls._collection is None:
            try:
                # Initialize ChromaDB persistent client
                cls._client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
                cls._collection = cls._client.get_or_create_collection(
                    name="bible_verses",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("ChromaDB persistent collection loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading ChromaDB client: {e}. Reverting to EphemeralClient.")
                cls._client = chromadb.EphemeralClient()
                cls._collection = cls._client.get_or_create_collection(name="bible_verses")
        return cls._collection

    @classmethod
    def ingest_verses(cls, verses: List[Dict[str, Any]]):
        collection = cls.get_collection()
        
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for idx, v in enumerate(verses):
            # Create a unique ID e.g., "John_3_16"
            ref_id = f"{v['book'].replace(' ', '_')}_{v['chapter']}_{v['verse']}"
            
            # Combine details for embedding
            text_to_embed = f"{v['book']} {v['chapter']}:{v['verse']} - {v['text']}"
            
            # Generate Gemini Embedding
            emb = GeminiService.generate_embeddings(text_to_embed)
            
            ids.append(ref_id)
            embeddings.append(emb)
            metadatas.append({
                "book": v["book"],
                "chapter": int(v["chapter"]),
                "verse": int(v["verse"]),
                "denomination": v.get("denomination", "universal") # universal, protestant, catholic, orthodox
            })
            documents.append(v["text"])
            
        if ids:
            # Batch upsert into Chroma
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            logger.info(f"Successfully ingested {len(ids)} verses into ChromaDB.")

    @classmethod
    def query_scriptures(cls, query: str, denomination: str = "Protestant", top_k: int = 4) -> List[Dict[str, Any]]:
        collection = cls.get_collection()
        query_emb = GeminiService.generate_embeddings(query)
        
        # Denomination-aware metadata filtering
        # Protestant: can access only 'universal'
        # Catholic: can access 'universal' and 'catholic'
        # Orthodox: can access 'universal', 'catholic', and 'orthodox'
        allowed_scopes = ["universal"]
        
        denom_lower = denomination.lower()
        if denom_lower == "protestant":
            allowed_scopes.append("protestant")
        elif denom_lower == "catholic":
            allowed_scopes.extend(["protestant", "catholic"])
        elif denom_lower == "orthodox":
            allowed_scopes.extend(["protestant", "catholic", "orthodox"])
            
        # ChromaDB dictionary metadata filter
        where_clause = {"denomination": {"$in": allowed_scopes}}
        
        try:
            results = collection.query(
                query_embeddings=[query_emb],
                n_results=top_k,
                where=where_clause
            )
            
            retrieved = []
            if results and results["documents"] and results["documents"][0]:
                docs = results["documents"][0]
                metas = results["metadatas"][0]
                distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
                
                for doc, meta, dist in zip(docs, metas, distances):
                    ref = f"{meta['book']} {meta['chapter']}:{meta['verse']}"
                    retrieved.append({
                        "reference": ref,
                        "text": doc,
                        "score": 1.0 - dist, # Cosine similarity conversion
                        "book": meta["book"],
                        "chapter": meta["chapter"],
                        "verse": meta["verse"],
                        "denomination": meta["denomination"]
                    })
            return retrieved
        except Exception as e:
            logger.error(f"Chroma RAG query failed: {e}")
            return []
