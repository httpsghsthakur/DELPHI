import pytest
import os
import tempfile
from delphi.retrieval import HistoricalIndexBuilder, FaissHistoricalIndex, HistoricalEventDocument

def test_index_integrity():
    dim = 256
    builder = HistoricalIndexBuilder(dimension=dim)
    
    events = [
        HistoricalEventDocument(
            event_id="E1",
            event_date="2021-01-01",
            event_type="TRADE",
            event_embedding=[0.1] * dim
        ),
        HistoricalEventDocument(
            event_id="E2",
            event_date="2021-02-01",
            event_type="CONFLICT",
            event_embedding=[0.2] * dim
        )
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"environment": "development"}
        manifest = builder.build(events, tmpdir, config)
        
        # Test saved files exist
        assert os.path.exists(os.path.join(tmpdir, "index.faiss"))
        assert os.path.exists(os.path.join(tmpdir, "metadata.parquet"))
        assert os.path.exists(os.path.join(tmpdir, "manifest.json"))
        
        # Reload and test integrity
        idx = FaissHistoricalIndex(dimension=dim)
        idx.load(tmpdir)
        
        assert idx.index.ntotal == 2
        assert len(idx.metadata) == 2
        
        # Mismatch vector dimensions should fail at search time or build time
        with pytest.raises(ValueError):
            idx.search([0.1] * 128)
            
        del idx
        import gc
        gc.collect()
