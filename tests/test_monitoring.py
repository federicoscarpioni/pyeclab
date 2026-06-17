from types import SimpleNamespace

from pytest import fixture

from pyeclab.channel.monitoring import SequenceMonitor


def _data_info(technique_index: int, technique_id: int, loop: int):
    return SimpleNamespace(TechniqueIndex=technique_index, TechniqueID=technique_id, loop=loop)


@fixture
def monitor():
    return SequenceMonitor()


def test_first_technique_does_not_count_as_a_transition(monitor):
    transitioned = monitor.update(_data_info(technique_index=0, technique_id=100, loop=0))
    assert transitioned is False


def test_trackers_are_initialized_from_the_first_poll(monitor):
    monitor.update(_data_info(technique_index=0, technique_id=100, loop=0))
    assert monitor.current_tech_index == 0
    assert monitor.current_tech_id == 100
    assert monitor.current_loop == 0


def test_repeated_polls_of_the_same_technique_do_not_transition(monitor):
    monitor.update(_data_info(technique_index=0, technique_id=100, loop=0))
    transitioned = monitor.update(_data_info(technique_index=0, technique_id=100, loop=0))
    assert transitioned is False


def test_technique_index_change_is_a_transition(monitor):
    monitor.update(_data_info(technique_index=0, technique_id=100, loop=0))
    transitioned = monitor.update(_data_info(technique_index=1, technique_id=101, loop=0))
    assert transitioned is True
    assert (monitor.current_tech_index, monitor.current_tech_id, monitor.current_loop) == (1, 101, 0)


def test_loop_change_is_a_transition(monitor):
    monitor.update(_data_info(technique_index=1, technique_id=101, loop=0))
    transitioned = monitor.update(_data_info(technique_index=1, technique_id=101, loop=1))
    assert transitioned is True
    assert monitor.current_loop == 1


def test_callback_not_fired_for_the_first_technique():
    events = []
    monitor = SequenceMonitor(on_technique_change=lambda: events.append("fired"))
    monitor.update(_data_info(technique_index=0, technique_id=100, loop=0))
    assert events == []


def test_callback_fired_on_transition():
    events = []
    monitor = SequenceMonitor(on_technique_change=lambda: events.append("fired"))
    monitor.update(_data_info(technique_index=0, technique_id=100, loop=0))
    monitor.update(_data_info(technique_index=1, technique_id=101, loop=0))
    assert events == ["fired"]


def test_callback_sees_outgoing_technique_values_not_incoming():
    """
    Regression test: the original implementation advanced current_tech_id to the
    NEW technique's id one line before checking for a transition, so the callback
    saw current_tech_id already updated while current_tech_index/current_loop still
    held the OLD technique's values - an inconsistent snapshot. All three trackers
    must be consistent (and reflect the outgoing technique) at callback time.
    """
    snapshots = []

    def on_change():
        snapshots.append((monitor.current_tech_index, monitor.current_tech_id, monitor.current_loop))

    monitor = SequenceMonitor(on_technique_change=on_change)
    monitor.update(_data_info(technique_index=0, technique_id=100, loop=0))
    monitor.update(_data_info(technique_index=1, technique_id=101, loop=0))

    assert snapshots == [(0, 100, 0)]
