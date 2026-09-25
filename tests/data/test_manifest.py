import pytest
from delphi.datasets.manifest import generate_manifest

def test_generate_manifest():
    manifest = generate_manifest(
        dataset_name="test_dataset",
        dataset_version="1.0.0",
        source="GDELT",
        records=100,
        schema_version="1.0",
        preprocessing_version="1.0",
        checksum="12345abc",
        source_files=["file1.parquet"]
    )
    assert manifest.dataset_name == "test_dataset"
    assert manifest.records == 100
    assert len(manifest.source_files) == 1
