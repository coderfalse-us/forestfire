"""
Module for defining Pydantic schemas for the optimization API.
"""

from pydantic import BaseModel
from typing import List


class OptimizationRequest(BaseModel):
    num_pickers: int
    picker_capacities: List[int]
    picker_locations: List[tuple]
    warehouse_name: str


# class OptimizationResponse(BaseModel):
#     solution: List[int]
#     fitness_score: float
#     routes: Optional[List[Dict[str, Any]]] = None
