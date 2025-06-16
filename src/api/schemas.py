"""
Module for defining Pydantic schemas for the optimization API.
"""

from pydantic import BaseModel, Field
from typing import List, Tuple


class OptimizationRequest(BaseModel):
    """Request schema for the warehouse optimization API."""

    num_pickers: int = Field(
        ..., description="Number of pickers available for optimization", gt=0
    )  # Required to be greater than 0
    picker_capacities: List[int] = Field(
        ...,
        description="Maximum number of orders each picker can handle",
        min_length=1,
    )  # Required
    picker_locations: List[Tuple[float, float]] = Field(
        ..., description="Starting coordinates for each picker (x,y positions)"
    )  # Required
    warehouse_name: str = Field(
        ..., description="Identifier for the warehouse configuration"
    )  # Required
