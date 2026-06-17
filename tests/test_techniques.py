import pytest

from pyeclab.api.kbio_types import BANDWIDTH, E_RANGE, I_RANGE
from pyeclab.techniques.ca import ChronoAmperometry
from pyeclab.techniques.calim import ChronoAmperometryWithLimits
from pyeclab.techniques.cp import ChronoPotentiometry
from pyeclab.techniques.cplim import ChronoPotentiometryWithLimits
from pyeclab.techniques.loop import Loop
from pyeclab.techniques.ocv import OpenCircuitVoltage


class FakeApi:
    """
    Stands in for BiologicDevice in make_technique(): only needs is_VMP3 and a
    DefineParameter that mimics BL_Define<Type>Parameter without a loaded DLL or
    a live device connection.
    """

    def __init__(self, is_vmp3: bool):
        self.is_VMP3 = is_vmp3
        self.calls = 0

    def DefineParameter(self, label, value, index, parm):
        self.calls += 1


def _ca():
    return ChronoAmperometry(
        voltage=0.5, duration=60, vs_init=False, nb_steps=0,
        record_dt=1, record_dI=0.1, repeat=0,
        i_range=I_RANGE.I_RANGE_10mA, e_range=E_RANGE.E_RANGE_5V, bandwidth=BANDWIDTH.BW_4,
    )


def _cp():
    return ChronoPotentiometry(
        current=0.001, duration=60, vs_init=False, nb_steps=0,
        record_dt=1, record_dE=0.1, repeat=0,
        i_range=I_RANGE.I_RANGE_10mA, e_range=E_RANGE.E_RANGE_5V, bandwidth=BANDWIDTH.BW_4,
    )


def _ocv():
    return OpenCircuitVoltage(duration=60, record_dt=1, e_range=E_RANGE.E_RANGE_5V, bandwidth=BANDWIDTH.BW_4)


def _calim():
    return ChronoAmperometryWithLimits(
        voltage=0.5, duration=60, vs_init=False, nb_steps=0,
        record_dt=1, record_dI=0.1, repeat=0,
        i_range=I_RANGE.I_RANGE_10mA, e_range=E_RANGE.E_RANGE_5V,
        limit_variable=0, limit_value=1.0, bandwidth=BANDWIDTH.BW_4,
    )


def _cplim():
    return ChronoPotentiometryWithLimits(
        current=0.001, duration=60, vs_init=False, nb_steps=0,
        record_dt=1, record_dE=0.1, repeat=0,
        i_range=I_RANGE.I_RANGE_10mA, e_range=E_RANGE.E_RANGE_5V,
        limit_variable=0, limit_value=1.0, bandwidth=BANDWIDTH.BW_4,
    )


def _loop():
    return Loop(repeat_N=1, loop_start=0)


TECHNIQUE_CASES = [
    (_ca, "ca.ecc", "ca4.ecc"),
    (_cp, "cp.ecc", "cp4.ecc"),
    (_ocv, "ocv.ecc", "ocv4.ecc"),
    (_calim, "calimit.ecc", "calimit4.ecc"),
    (_cplim, "cplimit.ecc", "cplimit4.ecc"),
    (_loop, "loop.ecc", "loop4.ecc"),
]


@pytest.mark.parametrize("make_technique, vmp3_file, vmp300_file", TECHNIQUE_CASES)
def test_constructs_with_no_device_argument(make_technique, vmp3_file, vmp300_file):
    technique = make_technique()
    assert technique.ecc_file is None
    assert technique.ecc_params is None


@pytest.mark.parametrize("make_technique, vmp3_file, vmp300_file", TECHNIQUE_CASES)
def test_choose_ecc_file_needs_only_a_bool(make_technique, vmp3_file, vmp300_file):
    technique = make_technique()
    assert technique.choose_ecc_file(is_vmp3=True) == vmp3_file
    assert technique.choose_ecc_file(is_vmp3=False) == vmp300_file


@pytest.mark.parametrize("make_technique, vmp3_file, vmp300_file", TECHNIQUE_CASES)
def test_make_technique_works_with_a_fake_api_no_real_device(make_technique, vmp3_file, vmp300_file):
    technique = make_technique()
    fake_api = FakeApi(is_vmp3=True)

    technique.make_technique(fake_api)

    assert technique.ecc_file == vmp3_file
    assert technique.ecc_params is not None
    assert technique.ecc_params.len > 0
    assert fake_api.calls == technique.ecc_params.len
