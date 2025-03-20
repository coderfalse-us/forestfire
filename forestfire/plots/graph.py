import matplotlib.pyplot as plt
from forestfire.optimizer.fitness import calc_distance_with_shortest_route
from forestfire.utils.config import *
from forestfire.database.picklist import PicklistRepository 

picklist_repo = PicklistRepository()

def graph_plot(final_solution):
    orders = {picker_id: [] for picker_id in range(NUM_PICKERS)}
    picktasks,orders_assign,stage_result = picklist_repo.get_optimized_data()
    for item_id, picker_id in enumerate(final_solution):
        orders[picker_id].append(item_id)

    print("\nOrders for Each Picker:")
    for picker_id, items in orders.items():
        print(f"Picker {picker_id}: Orders Tasks {items}")

    # Generate **sorted paths** for plotting
    _,sorted_paths,assignments = calc_distance_with_shortest_route(PICKER_LOCATIONS, final_solution, orders_assign, picktasks, stage_result)

    # Plot results with sorted paths
    fig, axes = plt.subplots(nrows=1, ncols=len(PICKER_LOCATIONS), figsize=(30, 6), sharex=True, sharey=True)

    picker_x, picker_y = zip(*PICKER_LOCATIONS)  # Original picker locations
    item_x, item_y = zip(*ITEM_LOCATIONS)  # All item locations

    for group, ax in enumerate(axes):
        if group >= len(PICKER_LOCATIONS):  # Prevent index errors
            continue

        ax.scatter(*PICKER_LOCATIONS[group], c='blue', s=150, label='Picker Start', marker='o')  # Start picker locations

        ax.scatter(item_x, item_y, c='red', s=50, label='Items', marker='*')

        if group < len(sorted_paths):
            points = [PICKER_LOCATIONS[group]] + sorted_paths[group]

            if len(points) > 1:
                x, y = zip(*points)
                ax.plot(x, y, label=f'Picker {group + 1} Path', linestyle='-', linewidth=2)

        if group < len(assignments):
            assignment_points = assignments[group]
        if assignment_points:
            assign_x, assign_y = zip(*assignment_points)
            ax.scatter(assign_x, assign_y, c='green', s=60, label='Assigned Items', marker='o')

        ax.set_title(f"Picker {group + 1}", fontsize=12)
        ax.set_xlabel("X Coordinate", fontsize=10)
        ax.set_ylabel("Y Coordinate", fontsize=10)
        ax.grid(True)

    plt.show()