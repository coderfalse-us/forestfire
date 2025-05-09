"""Route optimization service for warehouse picker routing.

This module provides functionality for calculating optimal routes for pickers
in a warehouse environment, implementing serpentine routing logic and
optimizing for distance traveled.
"""

from typing import List, Tuple, Dict
from ..models.route import Route
from ..utils.geometry import WalkwayCalculator
from .distance import DistanceCalculator
from forestfire.utils.config import NUM_PICKERS


class RouteOptimizer:
    """Service for optimizing picker routes"""

    def __init__(
        self,
        left_walkway: int = 15,
        right_walkway: int = 105,
        step_between_rows: int = 10,
    ):
        self.left_walkway = left_walkway
        self.right_walkway = right_walkway
        self.step_between_rows = step_between_rows
        self.distance_calculator = DistanceCalculator()
        self.walkway_calculator = WalkwayCalculator(left_walkway, right_walkway)

    def calculate_shortest_route(
        self,
        picker_locations: List[Tuple[float, float]],
        emptypop_position: List[int],
        orders_assign: List[List[Tuple[float, float]]],
        picktasks: List[str],
        stage_results: Dict[str, List[Tuple[float, float]]],
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

        final_result = self._get_staging_points(
            order_indices, picktasks, stage_results
        )
        sorted_data = self._sort_locations(assignments)
        r_flag = [0] * NUM_PICKERS

        for p in range(NUM_PICKERS):
            if not sorted_data[p]:
                continue
            sorted_data[p] = self._handle_entry_logic(
                picker_locations[p], sorted_data[p], p, r_flag
            )
        optimized_routes = self._handle_serpentine_logic(
            sorted_data, r_flag, final_result
        )
        # Calculate total cost
        total_cost = 0
        routes = []
        for idx, route in enumerate(optimized_routes):
            cost = self._calculate_route_cost(route)
            total_cost += cost
            routes.append(
                Route(
                    picker_id=idx,
                    locations=route,
                    cost=cost,
                    assigned_orders=order_indices[idx],
                )
            )
        return total_cost, routes, assignments

    def _get_staging_points(
        self,
        order_indices: List[List[int]],
        picktasks: List[str],
        stage_result: Dict[str, List[Tuple[float, float]]],
    ) -> List[Tuple[float, float]]:
        """Get staging locations for the route"""
        final_result = []
        for i in range(NUM_PICKERS):
            indices = order_indices[i]
            picktasks = list(picktasks)
            taskids = [picktasks[i] for i in indices]
            for taskid in taskids:
                final_result.extend(stage_result.get(taskid[0], []))
            return final_result

    def _sort_locations(
        self, assignments: List[List[Tuple[float, float]]]
    ) -> List[List[Tuple[float, float]]]:
        """Sort locations by aisle and position"""
        sorted_data = [[] for _ in range(NUM_PICKERS)]
        # Group locations by aisle for each picker
        for i in range(NUM_PICKERS):
            aisles = {}
            locations = assignments[i]
            for loc in locations:
                aisle = loc[1] // 10
                if aisle not in aisles:
                    aisles[aisle] = []
                aisles[aisle].append(loc)

            # Sort within each aisle and maintain picker-specific grouping
            for aisle in sorted(aisles.keys()):
                if aisle % 2 == 0:  # Even aisles
                    sorted_aisle = sorted(aisles[aisle], key=lambda x: x[0])
                else:  # Odd aisles
                    sorted_aisle = sorted(
                        aisles[aisle], key=lambda x: x[0], reverse=True
                    )
                sorted_data[i].extend(sorted_aisle)

        return sorted_data

    def _calculate_route_cost(self, path: List[Tuple[float, float]]) -> float:
        """Calculate total distance of route"""
        if not path:
            return 0.0
        total_distance = 0.0
        try:
            for i in range(len(path) - 1):
                # Convert both points to proper format
                try:
                    point1 = self._ensure_point_tuple(path[i])
                    point2 = self._ensure_point_tuple(path[i + 1])
                except (TypeError, ValueError) as e:
                    raise TypeError(f"Invalid point at index {i}: {e}") from e
                # Calculate distance
                distance = self.distance_calculator.euclidean_distance(
                    point1, point2
                )
                total_distance += distance
        except Exception as e:
            raise TypeError(f"Error calculating route cost: {e}") from e
        return total_distance

    def _ensure_point_tuple(self, point) -> Tuple[float, float]:
        """
        Ensure a point is in the correct tuple format

        Args:
            point: Point to convert

        Returns:
            Tuple[float, float]: Point as (x, y) tuple
        """
        if isinstance(point, (list, tuple)):
            if len(point) != 2:
                raise ValueError(
                    f"Point must have exactly 2 coordinates, got {point}"
                )
            return (float(point[0]), float(point[1]))
        raise TypeError(
            f"Point must be tuple or list, got {type(point)}: {point}"
        )

    def _handle_entry_logic(
        self,
        picker_location: Tuple[float, float],
        sorted_data: List[Tuple[float, float]],
        p: int,
        r_flag: List[int],
    ) -> List[Tuple[float, float]]:
        """
        Handle entry logic for picker routing based on picker location and
        sorted data.

        This function determines the best entry point for a picker's route.

        Args:
            picker_location: Current picker's location
            sorted_data: Sorted locations for the picker
            p: Picker index
            r_flag: Route direction flags

        Returns:
            Updated route with entry points
        """
        if not sorted_data:
            return sorted_data
        route = sorted_data.copy()
        # Calculate distances to determine entry point
        dist1_walkway = self.walkway_calculator.get_walkway_position(
            route[0][1]
        )
        dist2_walkway = self.walkway_calculator.get_walkway_position(
            route[-1][1]
        )
        point1 = (
            tuple(picker_location)
            if not isinstance(picker_location, tuple)
            else picker_location
        )
        point2 = tuple((dist1_walkway, route[0][1]))
        point3 = tuple((dist2_walkway, route[-1][1]))

        dist1 = self.distance_calculator.euclidean_distance(point1, point2)
        dist2 = self.distance_calculator.euclidean_distance(point1, point3)

        # Logic for left side of warehouse
        if picker_location[0] < 50:
            if dist1 < dist2:
                route.insert(0, picker_location)
                if route[1][1] % 20 == 0:
                    route.insert(1, (self.left_walkway, route[1][1]))
                else:
                    route.insert(
                        1,
                        (
                            self.left_walkway,
                            route[1][1] - self.step_between_rows,
                        ),
                    )
            else:
                route = route[::-1]
                r_flag[p] = 1
                route.insert(0, picker_location)
                if route[1][1] % 20 == 0:
                    route.insert(1, (self.left_walkway, route[1][1]))
                else:
                    route.insert(
                        1,
                        (
                            self.left_walkway,
                            route[1][1] + self.step_between_rows,
                        ),
                    )
        # Logic for right side of warehouse
        else:
            if dist1 < dist2:
                if route[0][1] % 20 != 0:
                    route.insert(0, picker_location)
                    route.insert(1, (self.right_walkway, route[1][1]))
                else:
                    route.insert(0, picker_location)
                    route.insert(
                        1,
                        (
                            self.right_walkway,
                            route[1][1] - self.step_between_rows,
                        ),
                    )
            else:
                route = route[::-1]
                r_flag[p] = 1
                if route[-1][1] % 20 != 0:
                    route.insert(0, picker_location)
                    route.insert(1, (self.right_walkway, route[1][1]))
                else:
                    route.insert(0, picker_location)
                    route.insert(
                        1,
                        (
                            self.right_walkway,
                            route[1][1] + self.step_between_rows,
                        ),
                    )
        return route

    def _handle_serpentine_logic(
        self,
        sorted_data: List[List[Tuple[float, float]]],
        r_flag: List[int],
        final_result: List[Tuple[float, float]],
    ) -> List[List[Tuple[float, float]]]:
        """
        Implements serpentine routing logic for warehouse paths

        Args:
            sorted_data: List of sorted locations for each picker
            r_flag: Route direction flags for each picker
            final_result: Staging locations to append at end

        Returns:
            List of optimized routes with serpentine paths
        """
        processed_routes = []

        for j, route in enumerate(sorted_data):
            if not route:
                processed_routes.append([])
                continue
            current_route = list(route).copy()
            i = 1
            while i < len(current_route) - 1:
                # Check if moving to different y-coordinate
                if current_route[i][1] != current_route[i + 1][1]:
                    i = self._handle_aisle_transition(
                        current_route, i, r_flag[j]
                    )
                else:
                    i += 1
            # Append staging locations
            current_route.extend(final_result)
            processed_routes.append(current_route)

        return processed_routes

    def _handle_aisle_transition(
        self, route: List[Tuple[float, float]], index: int, r_flag: int
    ) -> int:
        """
        Handle transitions between aisles in serpentine routing

        Args:
            route: Current route being processed
            index: Current position in route
            r_flag: Route direction flag

        Returns:
            Updated index position after handling transition
        """
        current_pos = route[index]
        next_pos = route[index + 1]
        # Current position on main aisle
        if current_pos[1] % 20 == 0:
            if next_pos[1] % 20 != 0:
                # Add right walkway points
                route.insert(index + 1, (self.right_walkway, current_pos[1]))
                route.insert(
                    index + 2, (self.right_walkway, route[index + 2][1])
                )
                return index + 2
            else:
                # Both positions on main aisle
                step = (
                    -self.step_between_rows
                    if r_flag
                    else self.step_between_rows
                )
                route.insert(index + 1, (self.right_walkway, current_pos[1]))
                route.insert(
                    index + 2, (self.right_walkway, route[index + 1][1] + step)
                )
                route.insert(
                    index + 3, (self.left_walkway, route[index + 2][1])
                )
                route.insert(
                    index + 4, (self.left_walkway, route[index + 4][1])
                )
                return index + 4
        # Current position on regular aisle
        else:
            if next_pos[1] % 20 == 0:
                # Add left walkway points
                route.insert(index + 1, (self.left_walkway, current_pos[1]))
                route.insert(
                    index + 2, (self.left_walkway, route[index + 2][1])
                )
                return index + 2
            else:
                # Neither position on main aisle
                step = (
                    -self.step_between_rows
                    if r_flag
                    else self.step_between_rows
                )
                route.insert(index + 1, (self.left_walkway, current_pos[1]))
                route.insert(
                    index + 2, (self.left_walkway, route[index + 1][1] + step)
                )
                route.insert(
                    index + 3, (self.right_walkway, route[index + 2][1])
                )
                route.insert(
                    index + 4, (self.right_walkway, route[index + 4][1])
                )
                return index + 4
