"""
Picker route
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Route:
    """Model representing a picker's route"""

    picker_id: int
    locations: List[Tuple[float, float]]
    cost: float = 0.0
    assigned_orders: List[int] = None
