from datetime import datetime
import sqlite3
from pathlib import Path
from collections.abc import Sequence

from attrs import define

from pyeclab.channel.writers.abstractwriter import AbstractWriter


@define
class SqlWriter(AbstractWriter):
    """"""

    db: Path | str
    experiment_name: str

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

    def write_metadata(self, data: dict[str, str | int | float | datetime]):
        raise NotImplementedError()

    def instantiate(self, structure: Sequence[str]) -> None:
        """Create DB/Table and create connection."""
        self.conn = sqlite3.connect(self.db)
        cur = self.conn.cursor()
        stmt = "CREATE TABLE IF NOT EXISTS ?(id INTEGER PRIMARY KEY AUTOINCREMENT, time REAL, current REAL, voltage REAL, technique_num INTEGER, loop_num INTEGER, user_cycle INTEGER, user_state TEXT)"
        cur.execute(stmt, self.experiment_name)
        self.conn.commit()

    def close(self) -> None:
        """Close the DB connection"""
        self.conn.close()
