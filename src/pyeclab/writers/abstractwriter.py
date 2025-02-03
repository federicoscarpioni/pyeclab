from abc import ABC, abstractmethod


class AbstractWriter(ABC):
    @abstractmethod
    def write(self, data) -> None: ...

    @abstractmethod
    def instantiate(self, structure: list[str]) -> None: ...

    @abstractmethod
    def close(self) -> None: ...
