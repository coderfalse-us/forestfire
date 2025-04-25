"""Distance calculation service for warehouse routing.

This module provides utilities for calculating distances between points in
the warehouse environment.
"""
from typing import Tuple
import math

class DistanceCalculator:
    """Service for calculating distances between points"""
    @staticmethod
    def euclidean_distance(
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """Calculate Euclidean distance between two points"""
        try:
            x1, y1 = float(point1[0]), float(point1[1])
            x2, y2 = float(point2[0]), float(point2[1])
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        except (TypeError, ValueError) as e:
            raise TypeError(
                f"Invalid point format: {e}. Point1: {point1}, Point2: {point2}"
            ) from e
