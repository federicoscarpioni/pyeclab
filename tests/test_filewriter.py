from datetime import datetime

import numpy as np
import pytest
from pyeclab.channel.writers.filewriter import FileWriter
from pytest import fixture


@fixture
def writer(tmp_path):
    writer = FileWriter(file_dir=tmp_path, experiment_name="Test-Experiment")
    print(tmp_path)
    return writer


@fixture
def writer_append(tmp_path):
    writer = FileWriter(file_dir=tmp_path, experiment_name="Test-Experiment", append=True)
    print(tmp_path)
    return writer


@fixture
def writer_new_file(tmp_path):
    writer = FileWriter(file_dir=tmp_path, experiment_name="Test-Experiment", overwrite=False)
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
    structure = ["Time/s", "Ewe/V", "I/A", "Technique_num", "Loop_num"]
    writer.instantiate(structure)

    file_path = writer.file_dir / writer.experiment_name / "measurement_data.txt"
    with open(file_path) as f:
        line = f.read()

    assert line == "Time/s\tEwe/V\tI/A\tTechnique_num\tLoop_num\n"


def test_file_header_creation_new_file(writer_new_file):
    structure = ["Time/s", "Ewe/V", "I/A", "Technique_num", "Loop_num"]
    writer_new_file.instantiate(structure)

    file_path = writer_new_file.file_dir / writer_new_file.experiment_name / "measurement_data.txt"
    with open(file_path) as f:
        line = f.read()

    assert line == "Time/s\tEwe/V\tI/A\tTechnique_num\tLoop_num\n"


def test_file_header_creation_new_file_fail_on_existing(writer_new_file):
    file_path = writer_new_file.file_dir / writer_new_file.experiment_name / "measurement_data.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        f.write("Something")

    structure = ["Time/s", "Ewe/V", "I/A", "Technique_num", "Loop_num"]
    with pytest.raises(FileExistsError):
        writer_new_file.instantiate(structure)


def test_file_header_creation_append(writer_append):
    structure = ["Time/s", "Ewe/V", "I/A", "Technique_num", "Loop_num"]
    writer_append.instantiate(structure)

    file_path = writer_append.file_dir / writer_append.experiment_name / "measurement_data.txt"
    with open(file_path) as f:
        line = f.read()

    assert line == ""


@fixture
def writer_instantiated(writer):
    structure = ["Time/s", "Ewe/V", "I/A", "Technique_num", "Loop_num"]
    writer.instantiate(structure)
    return writer


def test_file_content_handling_single_line(writer_instantiated):
    data = np.column_stack([0.0, 0.0003009, 0.0, 0, 0])
    writer_instantiated.write(data)

    file_path = writer_instantiated.file_dir / writer_instantiated.experiment_name / "measurement_data.txt"
    with open(file_path) as f:
        lines = f.readlines()

    assert lines[1] == "0.000e+00	3.009e-04	0.000e+00	0.000e+00	0.000e+00\n"


def test_file_content_handling_multi_line(writer_instantiated):
    data = np.column_stack(
        [[0.0, 0.0003009, 0.0, 0, 0], [0.00012, 1.147, 0.0009218, 0, 0], [0.00016, 1.61, 0.001085, 0, 0]]
    ).transpose()
    writer_instantiated.write(data)

    file_path = writer_instantiated.file_dir / writer_instantiated.experiment_name / "measurement_data.txt"
    with open(file_path) as f:
        lines = f.readlines()

    assert lines[1] == "0.000e+00	3.009e-04	0.000e+00	0.000e+00	0.000e+00\n"
