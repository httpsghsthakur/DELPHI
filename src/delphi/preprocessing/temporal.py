from datetime import datetime

class TemporalLeakageError(Exception):
    pass

class TemporalLeakageGuard:
    @staticmethod
    def ensure_no_leakage(training_information_time: datetime, prediction_time: datetime):
        """
        Ensures that information used for training is strictly before or at prediction time.
        Raises TemporalLeakageError if leakage is detected.
        """
        if training_information_time > prediction_time:
            raise TemporalLeakageError(
                f"Leakage detected: Information from {training_information_time} "
                f"was used to predict an event at {prediction_time}."
            )

class TemporalSplitter:
    def __init__(self, train_end: datetime, validation_end: datetime, test_end: datetime):
        if not (train_end < validation_end < test_end):
            raise ValueError("Split dates must be strictly increasing: train_end < validation_end < test_end")
            
        self.train_end = train_end
        self.validation_end = validation_end
        self.test_end = test_end

    def get_split(self, date: datetime) -> str:
        if date <= self.train_end:
            return "train"
        elif date <= self.validation_end:
            return "validation"
        elif date <= self.test_end:
            return "test"
        else:
            return "out_of_bounds"
