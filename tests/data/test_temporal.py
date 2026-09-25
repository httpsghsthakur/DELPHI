import pytest
from datetime import datetime
from delphi.preprocessing.temporal import TemporalLeakageGuard, TemporalLeakageError, TemporalSplitter

def test_leakage_guard_pass():
    training_time = datetime(2020, 1, 1)
    prediction_time = datetime(2020, 1, 10)
    TemporalLeakageGuard.ensure_no_leakage(training_time, prediction_time)

def test_leakage_guard_fail():
    training_time = datetime(2020, 1, 11)
    prediction_time = datetime(2020, 1, 10)
    with pytest.raises(TemporalLeakageError):
        TemporalLeakageGuard.ensure_no_leakage(training_time, prediction_time)

def test_temporal_splitter():
    splitter = TemporalSplitter(
        train_end=datetime(2020, 1, 1),
        validation_end=datetime(2021, 1, 1),
        test_end=datetime(2022, 1, 1)
    )
    
    assert splitter.get_split(datetime(2019, 1, 1)) == "train"
    assert splitter.get_split(datetime(2020, 6, 1)) == "validation"
    assert splitter.get_split(datetime(2021, 6, 1)) == "test"
    assert splitter.get_split(datetime(2022, 6, 1)) == "out_of_bounds"
