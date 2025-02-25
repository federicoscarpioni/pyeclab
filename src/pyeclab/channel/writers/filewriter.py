from collections.abc import Iterable, Sequence
from datetime import datetime
from io import TextIOWrapper
from pathlib import Path

import numpy as np
from attrs import define, field

from pyeclab.channel.writers.abstractwriter import AbstractWriter


@define
class FileWriter(AbstractWriter):
    """
    Writer class which writes to a text file.

    Attention on append-mode: When appending, the headers aren't written, as its assumed, that you want to append to an existing file.
    """

    file_dir: Path
    experiment_name: str
    append: bool = False
    overwrite: bool = True

    file: TextIOWrapper | None = field(init=False, default=None)
    data_length: int | None = field(init=False, default=None)

    def write(self, data: np.typing.NDArray):
        """Write to one or multiple rows of data to file."""

        cols = data.shape[1]
        formatter = ["%4.3e"] * (cols - 2) + ["%d"] * 2

        if self.file:
            np.savetxt(self.file, data, fmt=formatter, delimiter="\t")
            self.file.flush()

    def write_metadata(self, data: dict[str, str | int | float | datetime]):
        """Write Metadata to file."""
        file_path = self.file_dir / self.experiment_name / "metadata.txt"
        lines = []
        for k, v in data.items():
            if isinstance(v, datetime):
                v = v.strftime("%d.%m.%Y, %H:%M:%S")
            lines.append(": ".join([k, str(v)]) + "\n")

        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            f.writelines(lines)

    def instantiate(self, structure: Sequence[str]):
        """Create dir"""
        self._create_exp_folder()
        self._create_file(structure)
        self.data_length = len(structure)

    def close(self):
        """Close file"""
        self._close_saving_file()

    def _create_exp_folder(self):
        Path(self.file_dir).mkdir(parents=True, exist_ok=True)

    def _create_file(self, structure: Sequence[str]):
        """Create the file in the specified write mode and add a header line."""
        file_path = self.file_dir / self.experiment_name / "measurement_data.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if self.append:
            self.file = open(file_path, "a")
        elif self.overwrite:
            self.file = open(file_path, "w")
        else:
            self.file = open(file_path, "x")

        if not self.append:
            self.file.write("\t".join(structure) + "\n")
            self.file.flush()

    def _close_saving_file(self):
        """Close file if open."""
        if self.file:
            self.file.close()
