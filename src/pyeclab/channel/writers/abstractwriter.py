from abc import ABC, abstractmethod

import numpy as np


class AbstractWriter(ABC):
    @abstractmethod
    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name

    @abstractmethod
    def write(self, data: np.typing.NDArray) -> None: ...

    @abstractmethod
    def write_metadata(self, data: dict) -> None: ...

    @abstractmethod
    def instantiate(self, structure: list[str]) -> None: ...

    @abstractmethod
    def close(self) -> None: ...
