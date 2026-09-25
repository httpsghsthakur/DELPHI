from enum import Enum
from pydantic import BaseModel
from typing import Dict, Optional

class DatasetStatus(str, Enum):
    REGISTERED = "REGISTERED"
    DOWNLOADED = "DOWNLOADED"
    VALIDATED = "VALIDATED"
    NORMALIZED = "NORMALIZED"
    PROCESSED = "PROCESSED"
    SPLIT = "SPLIT"
    READY_FOR_TRAINING = "READY_FOR_TRAINING"

class DatasetMetadata(BaseModel):
    dataset_name: str
    dataset_type: str
    source: str
    version: str
    location: str
    schema_name: str
    date_range: Optional[str] = None
    status: DatasetStatus = DatasetStatus.REGISTERED

class DatasetRegistry:
    def __init__(self):
        self._datasets: Dict[str, DatasetMetadata] = {}

    def register(self, metadata: DatasetMetadata):
        self._datasets[metadata.dataset_name] = metadata

    def get(self, dataset_name: str) -> Optional[DatasetMetadata]:
        return self._datasets.get(dataset_name)

    def update_status(self, dataset_name: str, status: DatasetStatus):
        if dataset_name in self._datasets:
            self._datasets[dataset_name].status = status
        else:
            raise ValueError(f"Dataset {dataset_name} not found in registry.")

    def list_datasets(self) -> Dict[str, DatasetMetadata]:
        return self._datasets
