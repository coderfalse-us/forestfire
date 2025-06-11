"""Utility functions for geometry calculations"""


class WalkwayCalculator:
    """Utility class for walkway calculations"""

    def __init__(self, left_walkway: int, right_walkway: int):
        self.left_walkway = left_walkway
        self.right_walkway = right_walkway

    def get_walkway_position(self, value: int) -> int:
        """Determine walkway position based on value"""
        return self.left_walkway if value % 20 == 0 else self.right_walkway
