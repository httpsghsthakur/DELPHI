class ModelRegistry:
    def __init__(self):
        self.tokenizer_version = "v1"
        self.eventembed_version = "v1"
        self.eventnet_version = "v1"
        self.crednet_version = "v1"
        self.causalseq_version = "v1"
        self.retrieval_index_version = "v1"
        self.calibration_version = "v1"
        self.dataset_version = "v1"
        
        self.checkpoint_timestamps = {
            "eventembed": "2026-08-01T00:00Z",
            "eventnet": "2026-08-01T00:00Z",
            "crednet": "2026-08-01T00:00Z",
            "causalseq": "2026-08-01T00:00Z"
        }
        self.is_loaded = True
        
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
