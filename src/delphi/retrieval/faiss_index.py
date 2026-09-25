import faiss
import numpy as np
import os
import json
import pandas as pd
from typing import List, Dict, Any, Tuple
from .schemas import HistoricalEventDocument
from .similarity import normalize_embeddings

class FaissHistoricalIndex:
    def __init__(self, dimension: int = 256):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.metadata = {} # faiss_id -> dict
        
    def add_events(self, events: List[HistoricalEventDocument]):
        if not events:
            return
            
        embeddings = np.array([e.event_embedding for e in events], dtype=np.float32)
        
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {embeddings.shape[1]}")
            
        normalized = normalize_embeddings(embeddings)
        
        start_id = self.index.ntotal
        self.index.add(normalized)
        
        for i, event in enumerate(events):
            faiss_id = start_id + i
            self.metadata[faiss_id] = event.model_dump()
            
    def search(self, query_embedding: List[float], top_k: int = 100) -> List[Tuple[float, HistoricalEventDocument]]:
        if self.index.ntotal == 0:
            return []
            
        query = np.array([query_embedding], dtype=np.float32)
        if query.shape[1] != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {query.shape[1]}")
            
        normalized = normalize_embeddings(query)
        
        k = min(top_k, self.index.ntotal)
        similarities, indices = self.index.search(normalized, k)
        
        results = []
        for sim, idx in zip(similarities[0], indices[0]):
            if idx == -1:
                continue
            event_dict = self.metadata[idx]
            results.append((float(sim), HistoricalEventDocument(**event_dict)))
            
        return results

    def save(self, path: str, manifest: dict):
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        
        # Save metadata as parquet
        if self.metadata:
            df = pd.DataFrame.from_dict(self.metadata, orient='index')
            
            # Serialize lists and dicts to JSON strings to avoid PyArrow schema errors
            for col in df.columns:
                if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
                    df[col] = df[col].apply(json.dumps)
                    
            df.index.name = 'faiss_id'
            df.to_parquet(os.path.join(path, "metadata.parquet"))
            
        with open(os.path.join(path, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)

    def load(self, path: str):
        self.index = faiss.read_index(os.path.join(path, "index.faiss"))
        if self.index.d != self.dimension:
            raise ValueError(f"Loaded index has dimension {self.index.d}, expected {self.dimension}")
            
        meta_path = os.path.join(path, "metadata.parquet")
        if os.path.exists(meta_path):
            df = pd.read_parquet(meta_path)
            
            # Deserialize JSON strings back to lists and dicts
            for col in df.columns:
                if df[col].dtype == 'object' or df[col].dtype == 'string':
                    df[col] = df[col].apply(lambda x: json.loads(x) if isinstance(x, str) and (x.startswith('{') or x.startswith('[')) else x)
            
            self.metadata = df.to_dict(orient='index')
            
        with open(os.path.join(path, "manifest.json"), "r") as f:
            self.manifest = json.load(f)
