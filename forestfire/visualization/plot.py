import matplotlib.pyplot as plt

def plot_solution(solution, picker_locations):
    """Plot the warehouse layout with picker paths"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot picker locations
    picker_x = [loc[0] for loc in picker_locations]
    picker_y = [loc[1] for loc in picker_locations]
    ax.scatter(picker_x, picker_y, c='blue', s=100, label='Pickers')
    
    # Plot paths for each picker
    for picker_id in range(len(picker_locations)):
        points = [loc for i, loc in enumerate(solution) 
                 if solution[i] == picker_id]
        if points:
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            ax.plot(x, y, '-o', linewidth=1, markersize=4)
    
    ax.legend()
    ax.grid(True)
    plt.show()