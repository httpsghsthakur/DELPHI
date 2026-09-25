from delphi.models.eventembed.model import BaseModel

class CausalSeq(BaseModel):
    def forward(self, x):
        raise NotImplementedError("CausalSeq model is not yet implemented")
