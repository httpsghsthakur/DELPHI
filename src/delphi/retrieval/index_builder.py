from typing import List, Dict, Any
from datetime import datetime
from .faiss_index import FaissHistoricalIndex
from .schemas import HistoricalEventDocument

class HistoricalIndexBuilder:
    def __init__(self, dimension: int = 256):
        self.dimension = dimension
        
    def build(self, events: List[HistoricalEventDocument], output_dir: str, config: dict):
        index = FaissHistoricalIndex(dimension=self.dimension)
        
        # In a real implementation we would batch this.
        # Here we just add all. 
        index.add_events(events)
        
        # Validate integrity
        if index.index.ntotal != len(events):
             raise ValueError("Mismatch between number of vectors and number of events")
             
        if len(index.metadata) != len(events):
             raise ValueError("Mismatch between metadata records and number of events")
             
        manifest = {
            "index_version": config.get("index_version", "1.0"),
            "eventembed_version": config.get("eventembed_version", "unknown"),
            "tokenizer_version": config.get("tokenizer_version", "unknown"),
            "dataset_version": config.get("dataset_version", "unknown"),
            "embedding_dimension": self.dimension,
            "similarity_metric": "InnerProduct",
            "normalization_method": "L2",
            "creation_timestamp": datetime.now().isoformat(),
            "record_count": len(events),
            "environment": config.get("environment", "development")
        }
        
        index.save(output_dir, manifest)
        return manifest
