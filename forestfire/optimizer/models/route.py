"""
Picker route model
"""

from typing import List, Tuple
from pydantic import BaseModel, Field


class Route(BaseModel):
    """Model representing a picker's route"""

    picker_id: int = Field(..., description="Unique identifier for the picker")
    locations: List[Tuple[float, float]] = Field(
        ..., description="List of (x,y) coordinates in the route"
    )
    cost: float = Field(
        default=0.0, ge=0.0, description="Total cost/distance of the route"
    )
    assigned_orders: List[int] = Field(
        default_factory=list,
        description="List of order IDs assigned to this route",
    )

    class Config:
        """Model configuration"""

        frozen = True
