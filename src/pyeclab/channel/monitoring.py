import logging

logger = logging.getLogger("pyeclab")


class SequenceMonitor:
    """
    Tracks technique/loop transitions in a running sequence and invokes a
    callback when a new technique starts.
    """

    def __init__(self, on_technique_change=None):
        self.on_technique_change = on_technique_change
        self.current_tech_index = 0
        self.current_tech_id = None
        self.current_loop = 0

    def update(self, data_info) -> bool:
        """
        Compare the latest data_info against the last known technique/loop.
        If a transition occurred, fire on_technique_change while the trackers
        still hold the outgoing technique's values, then update current_tech_index
        and current_loop to the new technique/loop. current_tech_id is kept in
        sync with every poll (not just transitions), since unlike index/loop it
        has no meaningful default to start from. Returns True if a transition
        was detected.
        """
        new_tech_index = data_info.TechniqueIndex
        new_loop = data_info.loop
        transitioned = self.current_loop != new_loop or self.current_tech_index != new_tech_index
        if transitioned:
            if self.on_technique_change is not None:
                self.on_technique_change()
            self.current_tech_index = new_tech_index
            self.current_loop = new_loop
            logger.debug(
                f"New technique started: index={self.current_tech_index}, "
                f"id={data_info.TechniqueID}, loop={self.current_loop}"
            )
        self.current_tech_id = data_info.TechniqueID
        return transitioned
