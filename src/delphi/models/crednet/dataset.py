import torch
from torch.utils.data import Dataset
from typing import List, Dict, Any
from delphi.datasets.schemas import CredibilityFeatures

class CredNetDataset(Dataset):
    def __init__(self, features_list: List[CredibilityFeatures], labels: List[float]):
        """
        features_list: List of the 12-dimensional CredibilityFeatures.
        labels: 1.0 for credible, 0.0 for not credible.
        """
        assert len(features_list) == len(labels), "Features and labels must match in length"
        self.features = features_list
        self.labels = labels
        
    def __len__(self):
        return len(self.features)
        
    def __getitem__(self, idx):
        feat = self.features[idx]
        
        # Strictly preserve the 12 order
        vector = torch.tensor([
            feat.author_identifiable,
            feat.article_length_normalized,
            feat.citation_density,
            feat.title_sensationalism,
            feat.historical_source_reliability,
            feat.corroboration_count_normalized,
            feat.correction_history_signal,
            feat.publication_consistency,
            feat.primary_source_presence,
            feat.attribution_completeness,
            feat.author_history_availability,
            feat.source_longevity_normalized
        ], dtype=torch.float32)
        
        label = torch.tensor([self.labels[idx]], dtype=torch.float32)
        
        # Meta dictionary
        meta = {
            "source_id": feat.source_id,
            "article_id": feat.article_id,
            "timestamp": feat.timestamp
        }
        
        return vector, label, meta
        
def create_source_disjoint_split(
    features: List[CredibilityFeatures], 
    labels: List[float], 
    train_ratio: float = 0.8
):
    """
    Splits the dataset such that sources in train do not appear in test/val.
    """
    source_to_idx = {}
    for i, f in enumerate(features):
        if f.source_id not in source_to_idx:
            source_to_idx[f.source_id] = []
        source_to_idx[f.source_id].append(i)
        
    sources = list(source_to_idx.keys())
    # Deterministic sort for reproducibility
    sources.sort()
    
    train_sources = set(sources[:int(len(sources) * train_ratio)])
    
    train_feats, train_labels = [], []
    val_feats, val_labels = [], []
    
    for i, f in enumerate(features):
        if f.source_id in train_sources:
            train_feats.append(f)
            train_labels.append(labels[i])
        else:
            val_feats.append(f)
            val_labels.append(labels[i])
            
    return CredNetDataset(train_feats, train_labels), CredNetDataset(val_feats, val_labels)

def create_temporal_split(
    features: List[CredibilityFeatures], 
    labels: List[float], 
    val_ratio: float = 0.1,
    test_ratio: float = 0.1
):
    """
    Splits the dataset sequentially strictly by timestamp.
    Guarantees train_time < validation_time < test_time.
    """
    assert len(features) == len(labels), "Length mismatch"
    
    # Sort strictly by timestamp
    paired = sorted(zip(features, labels), key=lambda x: x[0].timestamp)
    
    total = len(paired)
    train_end = int(total * (1.0 - val_ratio - test_ratio))
    val_end = int(total * (1.0 - test_ratio))
    
    train_data = paired[:train_end]
    val_data = paired[train_end:val_end]
    test_data = paired[val_end:]
    
    # Verify temporal non-overlap via strict assertions
    if train_data and val_data:
        assert train_data[-1][0].timestamp <= val_data[0][0].timestamp, "Temporal leak between Train and Val"
    if val_data and test_data:
        assert val_data[-1][0].timestamp <= test_data[0][0].timestamp, "Temporal leak between Val and Test"
        
    return (
        CredNetDataset([f for f, l in train_data], [l for f, l in train_data]),
        CredNetDataset([f for f, l in val_data], [l for f, l in val_data]),
        CredNetDataset([f for f, l in test_data], [l for f, l in test_data])
    )
