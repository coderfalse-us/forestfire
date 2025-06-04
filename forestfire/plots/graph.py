"""Visualization module for warehouse picker routes.

This module provides functionality for visualizing optimized picker routes
and assignments in the warehouse environment.
"""

import os
import logging
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.utils.config import (
    ITEM_LOCATIONS,
)
from ..utils import WarehouseConfigManager
from forestfire.database.services.picklist import PicklistRepository

# Use Agg backend if no display available
if os.environ.get("DISPLAY") is None:
    matplotlib.use("Agg")

logger = logging.getLogger(__name__)


class PathVisualizer:
    """Visualizes optimized picker routes in the warehouse environment.

    This class provides methods to generate and save visualizations of
    picker routes, assignments, and item locations.
    """

    def __init__(self):
        self.picklist_repo = PicklistRepository()
        self.route_optimizer = RouteOptimizer()
        self.output_dir = os.path.join(os.getcwd(), "output", "plots")

        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_plot(self, plot_name=None):
        """Save the current plot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if plot_name is None:
            filename = f"route_visualization_{timestamp}.png"
        else:
            filename = f"{plot_name}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        logger.info("Plot saved to: %s", filepath)
        return filepath

    async def plot_routes(self, final_solution, config: WarehouseConfigManager):
        """Plot optimized routes for each picker"""
        # Map orders to pickers
        num_pickers = config.NUM_PICKERS
        picker_locations = config.PICKER_LOCATIONS
        warehouse_name = config.WAREHOUSE_NAME
        orders = {picker_id: [] for picker_id in range(num_pickers)}
        (
            picktasks,
            orders_assign,
            stage_result,
            _,
        ) = await self.picklist_repo.get_optimized_data(warehouse_name)

        for item_id, picker_id in enumerate(final_solution):
            orders[picker_id].append(item_id)

        print("\nOrders for Each Picker:")
        for picker_id, items in orders.items():
            print(f"Picker {picker_id}: Orders Tasks {items}")

        # Generate optimized routes for plotting
        _, routes, assignments = self.route_optimizer.calculate_shortest_route(
            num_pickers,
            picker_locations,
            final_solution,
            orders_assign,
            picktasks,
            stage_result,
        )

        # Setup plot
        _, axes = plt.subplots(
            nrows=1,
            ncols=len(picker_locations),
            figsize=(30, 6),
            sharex=True,
            sharey=True,
        )

        # Extract item coordinates for plotting
        _, _ = zip(*picker_locations)  # Unpack but not used directly
        item_x, item_y = zip(*ITEM_LOCATIONS)

        # Plot routes for each picker
        for group, ax in enumerate(axes):
            if group >= len(picker_locations):
                continue

            # Plot picker start location
            ax.scatter(
                *picker_locations[group],
                c="blue",
                s=150,
                label="Picker Start",
                marker="o",
            )

            # Plot all item locations
            ax.scatter(item_x, item_y, c="red", s=50, label="Items", marker="*")

            # Plot optimized path
            if group < len(routes):
                route = routes[group]
                points = [picker_locations[group]] + route.locations

                if len(points) > 1:
                    x, y = zip(*points)
                    ax.plot(
                        x,
                        y,
                        label=f"Picker {group + 1} Path",
                        linestyle="-",
                        linewidth=2,
                    )

            # Plot assigned items
            if group < len(assignments):
                assignment_points = assignments[group]
                if assignment_points:
                    assign_x, assign_y = zip(*assignment_points)
                    ax.scatter(
                        assign_x,
                        assign_y,
                        c="green",
                        s=60,
                        label="Assigned Items",
                        marker="o",
                    )

            ax.set_title(f"Picker {group + 1}", fontsize=12)
            ax.set_xlabel("X Coordinate", fontsize=10)
            ax.set_ylabel("Y Coordinate", fontsize=10)
            ax.grid(True)

        filepath = self.save_plot()
        plt.close()
        return filepath


# Create instance for backwards compatibility
path_visualizer = PathVisualizer()
graph_plot = path_visualizer.plot_routes
