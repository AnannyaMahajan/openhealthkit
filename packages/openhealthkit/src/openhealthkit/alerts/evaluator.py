import operator
from typing import Any


class ConditionEvaluator:
    """Evaluates rule conditions against observation values."""

    OPERATORS = {
        ">": operator.gt,
        "<": operator.lt,
        "==": operator.eq,
        ">=": operator.ge,
        "<=": operator.le,
        "!=": operator.ne,
    }

    @classmethod
    def evaluate(cls, value: Any, condition_operator: str, threshold: Any) -> bool:
        if value is None:
            return False

        op = condition_operator.strip()

        if op == "in":
            if isinstance(threshold, (list, tuple, set)):
                return value in threshold
            elif isinstance(threshold, str):
                return str(value) in threshold
            return False

        if op in cls.OPERATORS:
            try:
                num_val = float(value)
                num_thresh = float(threshold)
                return cls.OPERATORS[op](num_val, num_thresh)
            except (ValueError, TypeError):
                # Fallback to string comparison
                return cls.OPERATORS[op](str(value), str(threshold))

        return False
