import os
import json

class ModelRegistry:
    def __init__(self):
        self.tokenizer_version = self._get_version("vocab")
        self.eventembed_version = self._get_version("eventembed")
        self.eventnet_version = self._get_version("eventnet")
        self.crednet_version = self._get_version("crednet")
        self.causalseq_version = self._get_version("causalseq")
        self.retrieval_index_version = self._get_index_version()
        self.calibration_version = self._get_cal_version()
        self.dataset_version = "v1"
        
        self.checkpoint_timestamps = {
            "eventembed": self._get_timestamp("eventembed"),
            "eventnet": self._get_timestamp("eventnet"),
            "crednet": self._get_timestamp("crednet"),
            "causalseq": self._get_timestamp("causalseq")
        }
        self.is_loaded = True
        
    def _get_version(self, name):
        p = f"models/{name}/metadata.json"
        if os.path.exists(p):
            with open(p, "r") as f:
                return json.load(f).get("model_version", "v1.0")
        if name == "vocab" and os.path.exists("models/vocab/vocabulary.json"):
            return "v1.0"
        return ""
        
    def _get_timestamp(self, name):
        p = f"models/{name}/metadata.json"
        if os.path.exists(p):
            with open(p, "r") as f:
                return json.load(f).get("training_information_end_time", "")
        return ""
        
    def _get_index_version(self):
        p = "indexes/historical/manifest.json"
        if os.path.exists(p):
            return "v1.0"
        return ""
        
    def _get_cal_version(self):
        p = "models/calibration/calibration.json"
        if os.path.exists(p):
            return "v1.0"
        return ""
        
    def get_status(self):
        return {
            "tokenizer_version": self.tokenizer_version,
            "eventembed_version": self.eventembed_version,
            "eventnet_version": self.eventnet_version,
            "crednet_version": self.crednet_version,
            "causalseq_version": self.causalseq_version,
            "retrieval_index_version": self.retrieval_index_version,
            "calibration_version": self.calibration_version,
            "checkpoint_timestamps": self.checkpoint_timestamps
        }
