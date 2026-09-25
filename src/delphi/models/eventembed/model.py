from typing import Any

class BaseModel:
    def forward(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def save_checkpoint(self, path: str):
        raise NotImplementedError

    def load_checkpoint(self, path: str):
        raise NotImplementedError

    def predict(self, *args, **kwargs) -> Any:
        raise NotImplementedError

class EventEmbed(BaseModel):
    def forward(self, x):
        raise NotImplementedError("EventEmbed model is not yet implemented")
