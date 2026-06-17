import struct
from types import SimpleNamespace

from pytest import fixture

from pyeclab.channel.acquisition import DataAcquisition
from pyeclab.channel.config import ChannelConfig

OCV_TECHNIQUE_ID = 100


def _encode_float(value: float) -> int:
    """Pack a float the same way the real ADC buffer stores it (raw IEEE754 bits)."""
    return struct.unpack("I", struct.pack("f", value))[0]


class FakeBioDevice:
    """
    Stands in for BiologicDevice.GetData/ConvertNumericIntoSingle so DataAcquisition
    can be tested without a real instrument connection.
    """

    device_id = 1

    def __init__(self, technique_id: int, rows: list[list[float]], time_base: float = 1.0):
        # rows: one list of physical values per row, in column order [Ewe, col3, col4]
        # (col0/col1 encode an integer tick count for the timestamp, handled separately)
        self.technique_id = technique_id
        self.rows = rows
        self.time_base = time_base

    def GetData(self, device_id, channel_num):
        current_values = SimpleNamespace(TimeBase=self.time_base)
        data_info = SimpleNamespace(
            NbRows=len(self.rows),
            NbCols=len(self.rows[0]) + 2,
            TechniqueID=self.technique_id,
            StartTime=0.0,
        )
        data_buffer = []
        for tick, row in enumerate(self.rows):
            data_buffer.append(0)  # high 32 bits of the tick count, unused at this scale
            data_buffer.append(tick)  # low 32 bits of the tick count
            data_buffer.extend(_encode_float(value) for value in row)
        return current_values, data_info, data_buffer

    def ConvertNumericIntoSingle(self, raw):
        return struct.unpack("f", struct.pack("I", raw & 0xFFFFFFFF))[0]


@fixture
def ocv_rows():
    # columns: [Ewe, col3, col4] - col3/col4 are interpreted as charge/Ece/unused
    # depending on config, see buffer_converters.py special-casing for TechniqueID == 100.
    return [[1.0, 2.0, 3.0], [1.5, 2.5, 3.5]]


def test_poll_returns_base_columns_with_default_config(ocv_rows):
    bio_device = FakeBioDevice(OCV_TECHNIQUE_ID, ocv_rows)
    acquisition = DataAcquisition(bio_device, channel_num=1, config=ChannelConfig())

    current_values, data_info, converted = acquisition.poll()

    assert data_info.TechniqueID == OCV_TECHNIQUE_ID
    t, Ewe, I = converted
    assert list(t) == [0.0, 1.0]
    assert list(Ewe) == [1.0, 1.5]
    # OCV does not measure current: I is always zero regardless of the buffer content.
    assert list(I) == [0.0, 0.0]


def test_poll_returns_charge_column_when_configured(ocv_rows):
    bio_device = FakeBioDevice(OCV_TECHNIQUE_ID, ocv_rows)
    config = ChannelConfig(record_charge=True)
    acquisition = DataAcquisition(bio_device, channel_num=1, config=config)

    _, _, converted = acquisition.poll()

    t, Ewe, I, q = converted
    assert list(q) == [2.0, 2.5]


def test_poll_returns_ece_column_when_configured(ocv_rows):
    bio_device = FakeBioDevice(OCV_TECHNIQUE_ID, ocv_rows)
    config = ChannelConfig(record_ece=True)
    acquisition = DataAcquisition(bio_device, channel_num=1, config=config)

    _, _, converted = acquisition.poll()

    t, Ewe, I, Ece = converted
    assert list(Ece) == [2.0, 2.5]


def test_poll_returns_charge_and_ece_columns_when_both_configured(ocv_rows):
    bio_device = FakeBioDevice(OCV_TECHNIQUE_ID, ocv_rows)
    config = ChannelConfig(record_charge=True, record_ece=True)
    acquisition = DataAcquisition(bio_device, channel_num=1, config=config)

    _, _, converted = acquisition.poll()

    t, Ewe, I, Ece, q = converted
    assert list(Ece) == [2.0, 2.5]
    assert list(q) == [3.0, 3.5]


def test_poll_passes_through_current_values_and_data_info(ocv_rows):
    bio_device = FakeBioDevice(OCV_TECHNIQUE_ID, ocv_rows, time_base=0.5)
    acquisition = DataAcquisition(bio_device, channel_num=1, config=ChannelConfig())

    current_values, data_info, _ = acquisition.poll()

    assert current_values.TimeBase == 0.5
    assert data_info.NbRows == 2
