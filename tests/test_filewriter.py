from datetime import datetime
from pyeclab.channel.writers.filewriter import FileWriter
from pytest import fixture


@fixture
def writer(tmp_path):
    writer = FileWriter(file_dir=tmp_path, experiment_name="Test-Experiment")
    print(tmp_path)
    return writer


def test_metadata_creation(writer):
    metadata = {
        "dir": "C:/Users/bla/Desktop/",
        "experiment_name": "Experiment",
        "time": datetime(2025, 1, 1, 1, 1, 1),  # change to actual datetime as soon as implemented
        "init_state": 0,
        "value_changed": False,
    }
    writer.write_metadata(metadata)

    file_path = writer.file_dir / writer.experiment_name / "metadata.txt"
    with open(file_path) as f:
        lines = f.readlines()

    results = [
        "dir: C:/Users/bla/Desktop/",
        "experiment_name: Experiment",
        "time: 01.01.2025, 01:01:01",
        "init_state: 0",
        "value_changed: False",
    ]
    for line, result in zip(lines, results):
        assert line == result + "\n"


def test_file_header_creation(writer):
    pass


def test_file_content_handling_single_line(writer):
    pass


def test_file_content_handling_multi_line(writer):
    pass
