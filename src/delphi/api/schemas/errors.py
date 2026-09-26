from pydantic import BaseModel

class APIError(BaseModel):
    error_code: str
    message: str
    request_id: str
    timestamp: str

class TemporalLeakageError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class CheckpointIncompatibleError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
