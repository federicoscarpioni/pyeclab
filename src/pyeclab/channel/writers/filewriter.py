import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

from attrs import define
import numpy as np

from pyeclab.channel.writers.abstractwriter import AbstractWriter


@define
class FileWriter(AbstractWriter):
    """
    Writer class which writes to a text file.

    Attention on append-mode: When appending, the headers aren't written, as its assumed, that you want to append to an existing file.
    """

    file_dir: Path
    experiment_name: str
    current_cycle: int = 0
    current_state: int = 0
    append: bool = False
    overwrite: bool = True

    def write(self, data: np.typing.NDArray):
        """Write to file"""
        if len(data) != self.data_length:
            raise ValueError("Data of wrong length supplied.")

        if len(data) > 0:
            np.savetxt(self.file, data, fmt="%4.3e", delimiter="\t")
            self.file.flush()

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
        if self.append:
            self.file = open(file_path, "a")
        elif self.overwrite:
            self.file = open(file_path, "w")
        else:
            self.file = open(file_path, "x")

        if not self.append:
            self.file.write("\t".join(structure) + "\n")

    def _close_saving_file(self):
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


@define
class SqlWriter(AbstractWriter):
    """"""

    db: Path
    experiment_name: str
    current_cycle: int = 0
    current_state: int = 0

    def write(self, data):
        """Write to DB"""
        cur = self.conn.cursor()
        insert_data = (
            self.experiment_name,
            data.time,
            data.voltage,
            data.current,
            data.technique_num,
            data.loop_num,
            data.user_cycle,
        )
        cur.execute(
            "INSERT INTO ?(?,?,?,?,?,?)",
            insert_data,
        )

    def instantiate(self) -> None:
        """Create DB/Table and create connection."""
        self.conn = sqlite3.connect(self.db)
        cur = self.conn.cursor()
        stmt = "CREATE TABLE IF NOT EXISTS ?(id INTEGER PRIMARY KEY AUTOINCREMENT, time REAL, current REAL, voltage REAL, technique_num INTEGER, loop_num INTEGER, user_cycle INTEGER, user_state TEXT)"
        cur.execute(stmt, self.experiment_name)
        self.conn.commit()

    def close(self) -> None:
        """Close the DB connection"""
        self.conn.close()
