import json
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel
import hashlib

class DatasetManifest(BaseModel):
    dataset_name: str
    dataset_version: str
    source: str
    created_at: str
    records: int
    schema_version: str
    preprocessing_version: str
    checksum: str
    date_min: Optional[str] = None
    date_max: Optional[str] = None
    license_notes: Optional[str] = None
    source_files: List[str]

def generate_manifest(
    dataset_name: str,
    dataset_version: str,
    source: str,
    records: int,
    schema_version: str,
    preprocessing_version: str,
    checksum: str,
    date_min: Optional[str] = None,
    date_max: Optional[str] = None,
    license_notes: Optional[str] = None,
    source_files: List[str] = None
) -> DatasetManifest:
    if source_files is None:
        source_files = []
    
    return DatasetManifest(
        dataset_name=dataset_name,
        dataset_version=dataset_version,
        source=source,
        created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        records=records,
        schema_version=schema_version,
        preprocessing_version=preprocessing_version,
        checksum=checksum,
        date_min=date_min,
        date_max=date_max,
        license_notes=license_notes,
        source_files=source_files
    )

def generate_checksum(file_path: str) -> str:
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()
