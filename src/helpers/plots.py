import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from resources.data import Data

def draw_routes(routes=list):
    # List of unique colors
    instance_name = "C1_2_1.txt"
    data = Data().get_instance("C1_2_1.txt")
    colors = list(mcolors.TABLEAU_COLORS.values())  # Use tableau colors for distinct colors

    # Initialize plot
    plt.figure(figsize=(10, 8))

    # Plot depot
    depot_x = data['node_coord'][0][0]
    depot_y = data['node_coord'][0][1]
    plt.scatter(depot_x, depot_y, c='black', s=60, label='Depot', zorder=5)

    # Plot each route
    for idx, route in enumerate(routes):
        # Get the color for this route
        color = colors[idx % len(colors)]  # Cycle through colors if there are more routes than colors

        # Extract x and y coordinates for the route
        x_coords = [data['node_coord'][node][0] for node in route]
        y_coords = [data['node_coord'][node][1] for node in route]

        # Plot the route
        plt.plot(x_coords, y_coords, color=color, label=f'Route {idx + 1}', linewidth=2, zorder=2)
        plt.scatter(x_coords, y_coords, color=color, s=30, zorder=3)  # Mark nodes on the route

    # Add labels and title
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title(f'Vehicle Routes for instance {instance_name[:-4]}', fontdict={'fontsize': 16, 'fontname': 'arial'})
    # plt.legend()
    plt.grid(True)
    plt.show()

draw_routes([[0, 1, 3, 5, 0],[0,2,4,6,7,8,0]])