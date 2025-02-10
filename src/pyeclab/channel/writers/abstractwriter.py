from abc import ABC, abstractmethod

from pyeclab.channel.writers.filewriter import FileWriter
from pyeclab.channel.writers.sqlwriter import SqlWriter


class AbstractWriter(ABC):
    @abstractmethod
    def write(self, data) -> None: ...

    @abstractmethod
    def write_metadata(self, data: dict) -> None: ...

    @abstractmethod
    def instantiate(self, structure: list[str]) -> None: ...

    @abstractmethod
    def close(self) -> None: ...


AbstractWriter.register(FileWriter)
AbstractWriter.register(SqlWriter)
