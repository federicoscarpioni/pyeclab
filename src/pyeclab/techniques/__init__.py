"""
This module contain functions to create a technique object to be loaded on the
BioLogic potentiost to perform electrochemical experiments.

For each technique a set of parameters are allowed (see OEM User's Guide).

NOTE: the following explanation is not contained in the manual (which uses only
Delphi language as example) but it can be found in the examples provided with
the Python wrapper in the installation folder of EC-lab Developer Package.

A technique object must be prepared in the following way:
- Python type numbers (int or floats) representing the parameters must be
  converted to c-types using the OEM function make_ecc_parm
- All the parameters must be incorporated in one object using the function
  make_ecc_parms (mind the 's')
- For convenience technique file (.ecc) and the parameters object can be converted
  to a namedtuple; this way, the technique file and parameters belong to one
  name space and can be easily accessed with the attribute notation.
The namedtuple istance can be used in the LoadTechnique function of the Python API.
Calling such function multiple times creates a sequence of techniques.

This library supports the following techniques (not all!):
- Open Circuit Voltage
- Chono-Amperometry with Potential Limitation
- Chrono-Potentiometry
- Loop
Note: some techniques like CP and CA allows multiple steps but in the following
functions, only one is abilitated. For most battery-related reasearch that is
enough.

For each technique are provided:
- A dictionary XXX_params for storing all the parameters
- A function convert_XXX_ecc_params to create the parameters object
- A function make_XXX_tech to create the namedtuple

"""

from typing import Literal

from pyeclab.techniques.ca import ChronoAmperometry
from pyeclab.techniques.cplim import ChronoPotentiometryWithLimits
from pyeclab.techniques.loop import Loop
from pyeclab.techniques.ocv import OpenCircuitVoltage

# from pyeclab.techniques.functions import set_duration_to_1s, reset_duration


def _set_bit(value, bit_index):
    return value | (1 << bit_index)


def build_limit(
    type: Literal["voltage", "current"], sign: Literal["greater", "less"], logic: Literal["and", "or"], active=True
):
    """
    Generate the appropriate bitfield to set-up limit in limited techniques according
    to the structure in the manual.
    """
    value = 0b0
    if active:
        value = _set_bit(value, 0)

    if logic == "and":
        value = _set_bit(value, 1)

    if sign == "greater":
        value = _set_bit(value, 2)

    if type == "current":
        value = _set_bit(value, 5)
        value = _set_bit(value, 6)

    return value
