from typing import List, Tuple, Dict
from dataclasses import dataclass
import numpy as np
from ..utils.distance import euclidean_distance, walkway_from_condition
from ..utils.config import (
    NUM_PICKERS, 
    STEP_BETWEEN_ROWS, 
    LEFT_WALKWAY, 
    RIGHT_WALKWAY
)

@dataclass
class PathData:
    """Data class to hold path information"""
    points: List[Tuple[int, int]]
    distance: float
    picker_id: int

class FitnessCalculator:
    def __init__(self, picker_locations: List[Tuple[int, int]], picker_capacities: List[int]):
        self.picker_locations = picker_locations
        self.picker_capacities = picker_capacities
        self.left_walkway = LEFT_WALKWAY
        self.right_walkway = RIGHT_WALKWAY

    def evaluate(self, solution: List[int]) -> float:
        """Evaluate fitness of a solution"""
        total_cost, _, _ = self.calculate_solution_fitness(solution)
        return total_cost

    def calculate_solution_fitness(
        self, 
        solution: List[int]
    ) -> Tuple[float, List[PathData], Dict[int, List[Tuple[int, int]]]]:
        """Calculate fitness score and generate optimized paths"""
        # Create assignments for each picker
        assignments = [[] for _ in range(len(self.picker_locations))]
        for item_idx, picker_id in enumerate(solution):
            assignments[picker_id].append(item_idx)

        # Sort paths for optimal routing
        sorted_paths = self._sort_picker_paths(assignments)
        
        # Generate actual walkway paths
        optimized_paths = self._generate_walkway_paths(sorted_paths)
        
        # Calculate total distance
        total_cost = sum(path.distance for path in optimized_paths)
        
        return total_cost, optimized_paths, assignments

    def _sort_picker_paths(self, assignments: List[List[int]]) -> List[List[Tuple[int, int]]]:
        """Sort items for each picker to minimize travel distance"""
        sorted_paths = []
        
        for picker_id, assigned_items in enumerate(assignments):
            if not assigned_items:
                continue
                
            picker_location = self.picker_locations[picker_id]
            points = [picker_location]  # Start at picker location
            
            # Sort points by nearest neighbor
            while assigned_items:
                current = points[-1]
                nearest_idx = min(
                    range(len(assigned_items)),
                    key=lambda i: euclidean_distance(current, assigned_items[i])
                )
                points.append(assigned_items.pop(nearest_idx))
                
            points.append(picker_location)  # Return to start
            sorted_paths.append(points)
            
        return sorted_paths

    def _generate_walkway_paths(self, sorted_paths: List[List[Tuple[int, int]]]) -> List[PathData]:
        """Generate paths considering warehouse walkways"""
        optimized_paths = []
        
        for picker_id, path in enumerate(sorted_paths):
            walkway_points = []
            total_distance = 0
            
            for i in range(len(path) - 1):
                current = path[i]
                next_point = path[i + 1]
                
                # Add walkway points and calculate distances
                walkway_entry = (
                    walkway_from_condition(current[1], self.left_walkway, self.right_walkway),
                    current[1]
                )
                walkway_exit = (
                    walkway_from_condition(next_point[1], self.left_walkway, self.right_walkway),
                    next_point[1]
                )
                
                segment_distance = (
                    euclidean_distance(current, walkway_entry) +
                    euclidean_distance(walkway_entry, walkway_exit) +
                    euclidean_distance(walkway_exit, next_point)
                )
                
                walkway_points.extend([current, walkway_entry, walkway_exit, next_point])
                total_distance += segment_distance
                
            optimized_paths.append(PathData(
                points=walkway_points,
                distance=total_distance,
                picker_id=picker_id
            ))
            
        return optimized_paths