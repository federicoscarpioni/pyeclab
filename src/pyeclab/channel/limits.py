from dataclasses import dataclass


@dataclass(frozen=False)
class Condition:
    '''
    Quantity should have the format of Channel.current_values for example: "Ewe",
    "Ece", "I" or "ElapsedTime". Operator instead can only be ">" or "<".
    Note that using the hardware limits of EC-Lab SDK Ece is not implemented.
    '''
    technique_index: int
    quantity: str
    operator: str
    threshold: float


class SoftwareLimitChecker:
    """
    Tracks a list of Condition objects and checks whether any of them is met
    for the currently measured values. Used as a workaround since the
    EC-Lab SDK hardware limits do not support all measured quantities (e.g. Ece).
    """

    def __init__(self, conditions: list[Condition] | None = None):
        self.conditions = conditions if conditions is not None else []

    def add(self, condition: Condition):
        self.conditions.append(condition)

    def check(self, current_values, data_info) -> bool:
        """
        Check if a certain condition (< or > of a treshold value) is met for a
        value of the sampled data over a certain number of points.
        """
        for condition in self.conditions:
            if data_info.TechniqueIndex == condition.technique_index:
                quantity_value = getattr(current_values, condition.quantity)
                if condition.operator == ">" and quantity_value >= condition.threshold:
                    return True
                elif condition.operator == "<" and quantity_value <= condition.threshold:
                    return True
        return False
