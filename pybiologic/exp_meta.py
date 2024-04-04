'''
This module contains material for helping saving experiment metadata
'''

from dataclasses import dataclass

@dataclass
class SavingMetadata():
    deis_directory : str
    project_name : str
    cell_name : str
    experiment_name : str