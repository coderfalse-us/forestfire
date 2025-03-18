import math

def euclidean_distance(point1, point2):
    """Calculate Euclidean distance between two points"""
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def walkway_from_condition(value, left_walkway, right_walkway):
    """Determine walkway based on row value"""
    return left_walkway if value % 20 == 0 else right_walkway