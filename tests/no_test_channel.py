import pytest

from pyeclab.channel import Channel
from pyeclab.device import BiologicDevice

_instantiate_writers_parameters = [
    (False, False, "Time/s\tEwe/V\tI/A\tTechnique_num\tLoop_num"),
    (True, False, "Time/s\tEwe/V\tI/A\tEce/V\tTechnique_num\tLoop_num\n"),
    (False, True, "Time/s\tEwe/V\tI/A\tQ/C\tTechnique_num\tLoop_num\n"),
    (True, True, "Time/s\tEwe/V\tI/A\tEce/V\tQ/C\tTechnique_num\tLoop_num\n"),
]


@pytest.mark.parametrize("ece,charge,expected", _instantiate_writers_parameters)
def test_instantiate_writer_no(ece: bool, charge: bool, expected: str, channel: Channel):
    channel.is_recording_Ece = ece
    channel.is_charge_recorded = charge
    channel._instantiate_writer()

    # assert on written file to temp directory
    assert ... == expected
