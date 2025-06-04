"""
Module for defining Pydantic schemas for the optimization API.
"""

from pydantic import BaseModel
from typing import List


class OptimizationRequest(BaseModel):
    """Request schema for the optimization API."""

    num_pickers: int
    picker_capacities: List[int]
    picker_locations: List[tuple]
    warehouse_name: str
