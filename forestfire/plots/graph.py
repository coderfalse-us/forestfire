import matplotlib
import os
import platform
from datetime import datetime

# Use Agg backend if no display available
if os.environ.get('DISPLAY') is None:
    matplotlib.use('Agg')
    
import matplotlib.pyplot as plt
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.utils.config import *
from forestfire.database.picklist import PicklistRepository 
import logging

logger = logging.getLogger(__name__)

class PathVisualizer:
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
        filename = f"route_visualization_{timestamp}.png" if plot_name is None else f"{plot_name}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        logger.info(f"Plot saved to: {filepath}")
        return filepath
    
    def plot_routes(self, final_solution):
        """Plot optimized routes for each picker"""
        # Map orders to pickers
        orders = {picker_id: [] for picker_id in range(NUM_PICKERS)}
        picktasks, orders_assign, stage_result = self.picklist_repo.get_optimized_data()
        
        for item_id, picker_id in enumerate(final_solution):
            orders[picker_id].append(item_id)

        print("\nOrders for Each Picker:")
        for picker_id, items in orders.items():
            print(f"Picker {picker_id}: Orders Tasks {items}")

        # Generate optimized routes for plotting
        _, routes, assignments = self.route_optimizer.calculate_shortest_route(
            PICKER_LOCATIONS, 
            final_solution, 
            orders_assign, 
            picktasks, 
            stage_result
        )
        
        # Setup plot
        fig, axes = plt.subplots(nrows=1, ncols=len(PICKER_LOCATIONS), 
                                figsize=(30, 6), sharex=True, sharey=True)

        picker_x, picker_y = zip(*PICKER_LOCATIONS)
        item_x, item_y = zip(*ITEM_LOCATIONS)

        # Plot routes for each picker
        for group, ax in enumerate(axes):
            if group >= len(PICKER_LOCATIONS):
                continue

            # Plot picker start location
            ax.scatter(*PICKER_LOCATIONS[group], c='blue', s=150, 
                      label='Picker Start', marker='o')

            # Plot all item locations
            ax.scatter(item_x, item_y, c='red', s=50, 
                      label='Items', marker='*')

            # Plot optimized path
            if group < len(routes):
                route = routes[group]
                points = [PICKER_LOCATIONS[group]] + route.locations

                if len(points) > 1:
                    x, y = zip(*points)
                    ax.plot(x, y, label=f'Picker {group + 1} Path', 
                           linestyle='-', linewidth=2)

            # Plot assigned items
            if group < len(assignments):
                assignment_points = assignments[group]
                if assignment_points:
                    assign_x, assign_y = zip(*assignment_points)
                    ax.scatter(assign_x, assign_y, c='green', s=60, 
                             label='Assigned Items', marker='o')

            ax.set_title(f"Picker {group + 1}", fontsize=12)
            ax.set_xlabel("X Coordinate", fontsize=10)
            ax.set_ylabel("Y Coordinate", fontsize=10)
            ax.grid(True)

        filepath = self.save_plot()
        plt.close()
        return filepath

        try:
            plt.show()
        except Exception as e:
            logger.info("Could not display plot interactively, saving to file instead")
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            plt.savefig(os.path.join(output_dir, "route_visualization.png"))
            logger.info(f"Plot saved to {output_dir}/route_visualization.png")
        finally:
            plt.close()

# Create instance for backwards compatibility
path_visualizer = PathVisualizer()
graph_plot = path_visualizer.plot_routes