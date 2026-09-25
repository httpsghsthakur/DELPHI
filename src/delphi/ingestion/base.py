from abc import ABC, abstractmethod

class BaseIngestor(ABC):
    @abstractmethod
    def discover(self):
        raise NotImplementedError

    @abstractmethod
    def ingest(self):
        raise NotImplementedError

    @abstractmethod
    def validate(self):
        raise NotImplementedError

    @abstractmethod
    def normalize(self):
        raise NotImplementedError

    @abstractmethod
    def write(self):
        raise NotImplementedError
