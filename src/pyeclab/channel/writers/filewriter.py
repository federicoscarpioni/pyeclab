from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from attrs import define, field


@define
class FileWriter:
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
        """Write to file"""

        if self.file:
            np.savetxt(self.file, data, fmt="%4.3e", delimiter="\t")
            self.file.flush()

    def write_metadata(self, data: dict[str, str | int | float | datetime]):
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
        if self.file:
            self.file.close()

    def _save_exp_metadata(self):
        # Note: I am not using the 'with' constructor here because I assume I
        # might want to update the metada if some event happen. In that case,
        # the closing function should be move in the stop() method.
        self.metadata_file = open(self.saving_path + "/experiment_metadata.txt", "w")
        # File title
        self.metadata_file.write("PYECLAB METADATA FILE\n")
        # Information of the starting time
        self.starting_time = datetime.now()
        self.metadata_file.write(f"Date : {self.starting_time.strftime('%Y-%m-%d')}\n")
        self.metadata_file.write(f"Starting time : {self.starting_time.strftime('%H:%M:%S')}\n")
        # Information of the saving file name
        self.metadata_file.write(f"Experiment name : {self.experiment_name}\n")
        self.metadata_file.write(f"Saving file path : {self.saving_path}\n")
        # !!! Print all the information of the techniques in the sequence
        # ! Add information on the device, channel number, cell name and user comments
        # ! Add the list of condition checked by the software
        self.metadata_file.close()
