from typing import List, Tuple, Dict
from ..models.route import Route
from ..utils.geometry import WalkwayCalculator
from .distance import DistanceCalculator
from forestfire.utils.config import *

class RouteOptimizer:
    """Service for optimizing picker routes"""
    
    def __init__(self, left_walkway: int = 15, right_walkway: int = 105):
        self.left_walkway = left_walkway
        self.right_walkway = right_walkway
        self.distance_calculator = DistanceCalculator()
        self.walkway_calculator = WalkwayCalculator(left_walkway, right_walkway)

    def calculate_shortest_route(
        self,
        picker_locations: List[Tuple[float, float]],
        emptypop_position: List[int],
        orders_assign: List[List[Tuple[float, float]]],
        picktasks: List[str],
        stage_results: Dict[str, List[Tuple[float, float]]]
    ) -> Tuple[float, List[Route], List[List[Tuple[float, float]]]]:
        """
        Calculate shortest routes for all pickers
        """
        order_indices = [[] for _ in range(len(picker_locations))]
        assignments = [[] for _ in range(len(picker_locations))]
        
        # Map orders to pickers
        for index, picker_index in enumerate(emptypop_position):
            assignments[picker_index].extend(orders_assign[index])
            order_indices[picker_index].append(index)

        final_result=self._get_staging_points(order_indices, picktasks, stage_results)
        sorted_data=self._sort_locations(assignments)
        r_flag=[0]*NUM_PICKERS

        for p in range(NUM_PICKERS):
            if not sorted_data[p]:
                continue
            





    def _get_staging_points(
        self,
        order_indices: List[List[int]],
        picktasks: List[str],
        stage_result: Dict[str, List[Tuple[float, float]]]
    ) -> List[Tuple[float, float]]:
        """Get staging locations for the route"""
        final_result = []
        
        for i in range(NUM_PICKERS):
            indices = order_indices[i]
            picktasks=list(picktasks)
            taskids = [picktasks[i] for i in indices]
    
            for taskid in taskids:
                final_result.extend(stage_result.get(taskid[0], []))
            return final_result
        
    def _sort_locations(self, assignments: List[List[Tuple[float, float]]]) -> List[Tuple[float, float]]:
        """Sort locations by aisle and position"""
        sorted_data = [[] for _ in range(NUM_PICKERS)]
        # Group locations by aisle
        for i in range(NUM_PICKERS):
            aisles = {}
            locations=assignments[i]
            for loc in locations:
                aisle = loc[1] // 10
                if aisle not in aisles:
                    aisles[aisle] = []
                aisles[aisle].append(loc)

            # Sort within each aisle

            for aisle in sorted(aisles.keys()):
                if aisle % 2 == 0:  # Even aisles
                    sorted_aisle = sorted(aisles[aisle], key=lambda x: x[0])
                else:  # Odd aisles
                    sorted_aisle = sorted(aisles[aisle], key=lambda x: x[0], reverse=True)
                sorted_data.extend(sorted_aisle)

        return sorted_data
    
    def _get_walkway_points(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float]
    ) -> List[Tuple[float, float]]:
        """Calculate intermediate walkway points between locations"""
        dist1_walkway = self.walkway_calculator.get_walkway_position(sorted_data[p][0][1], left_walkway, right_walkway)
        dist2_walkway = self.walkway_calculator.get_walkway_position(sorted_data[p][-1][1], left_walkway, right_walkway)

        dist1 = e_d(picker_locations[p], (dist1_walkway, sorted_data[p][0][1]))
        dist2 = e_d(picker_locations[p], (dist2_walkway, sorted_data[p][-1][1]))


    def _calculate_route_cost(self, path: List[Tuple[float, float]]) -> float:
        """Calculate total distance of route"""
        total_distance = 0
        for i in range(len(path) - 1):
            distance = self.distance_calculator.euclidean_distance(path[i], path[i + 1])
            total_distance += distance
        return total_distance

 


        