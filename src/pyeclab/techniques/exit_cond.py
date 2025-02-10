from enum import Enum

class EXIT_COND(Enum):
    NEXT_STEP = 0
    NEXT_TECHNIQUE = 1
    STOP_EXPERIMENT = 2