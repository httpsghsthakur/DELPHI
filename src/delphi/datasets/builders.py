from abc import ABC, abstractmethod

class BaseDatasetBuilder(ABC):
    @abstractmethod
    def build(self, input_parquet: str, output_dir: str):
        pass

class EventEmbedDatasetBuilder(BaseDatasetBuilder):
    def build(self, input_parquet: str, output_dir: str):
        raise NotImplementedError("EventEmbedDatasetBuilder not implemented")

class EventNetDatasetBuilder(BaseDatasetBuilder):
    def build(self, input_parquet: str, output_dir: str):
        raise NotImplementedError("EventNetDatasetBuilder not implemented")

class CausalSeqDatasetBuilder(BaseDatasetBuilder):
    def build(self, input_parquet: str, output_dir: str):
        raise NotImplementedError("CausalSeqDatasetBuilder not implemented")

class CredNetDatasetBuilder(BaseDatasetBuilder):
    def build(self, input_parquet: str, output_dir: str):
        raise NotImplementedError("CredNetDatasetBuilder not implemented")
