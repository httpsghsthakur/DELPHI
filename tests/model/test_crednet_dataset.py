import pytest
from delphi.models.crednet.dataset import CredNetDataset, create_source_disjoint_split
from delphi.datasets.schemas import CredibilityFeatures

def test_source_disjoint_split():
    features = []
    labels = []
    
    for i in range(100):
        source = f"S_{i % 5}" # 5 unique sources
        feat = CredibilityFeatures(
            source_id=source,
            dataset_version="1.0"
        )
        features.append(feat)
        labels.append(1.0 if i%2 == 0 else 0.0)
        
    train_ds, val_ds = create_source_disjoint_split(features, labels, train_ratio=0.6)
    
    # Train gets 60% of sources, so 3 sources
    train_sources = set(f.source_id for f in train_ds.features)
    val_sources = set(f.source_id for f in val_ds.features)
    
    assert len(train_sources) == 3
    assert len(val_sources) == 2
    
    # Must be totally disjoint
    assert len(train_sources.intersection(val_sources)) == 0
    
def test_dataset_format():
    feat = CredibilityFeatures(source_id="S", dataset_version="1.0")
    ds = CredNetDataset([feat], [1.0])
    
    vec, lab, meta = ds[0]
    assert vec.shape == (12,)
    assert lab.shape == (1,)
    assert meta["source_id"] == "S"
