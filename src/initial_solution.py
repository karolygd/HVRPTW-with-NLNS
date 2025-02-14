# Here is where I code the savings algorithm
import resources.global_context as global_context
from src.evaluation import EvaluateMerge
from resources.datatypes.route import Route
from resources.datatypes.solution import Solution
from resources.datatypes.node import Node

def savings_vrptw():
    """
    This savings heuristic is adapted to respect the time windows for each node and vehicle maximum capacity limits
    :return Solution:
    """
    problem_instance = global_context.global_instance
    nodes = problem_instance.vertices
    edges = problem_instance.edges
    route_id = [-1]
    routes: list[Route] = []
    route_demand = []

    # 1. Create a route per vertex and get required information
    for i in range(1, len(nodes)):
        # create a single route for each node, leaving and coming back to the depot 0
        depot = Node(id=0, t_i=0.0, z_i = 0.0, d_i=0.0, route_id=0, position=0, predecessor_node=0, successor_node=0)
        new_node = Node(id=i, t_i=max(nodes[i].earliest_start, edges[(0, i)].distance), z_i = nodes[i].demand,
                        d_i=edges[(0, i)].distance, route_id=i-1, position=1, predecessor_node=0, successor_node=0)
        route = Route(nodes=[depot, new_node, depot], id=i - 1)
        route_id.append(i - 1) # keep track of the nodes added. node -1 to start at 0, 0 is the depot
        routes.append(route)
        route_demand.append(int(nodes[i].demand))

    # 2. Calculate all savings between routes
    savings = []
    for c_i in range(1, len(nodes)): # since zero is the depot we start at 1
        for c_j in range(1, len(nodes)):
            if c_i == c_j:
                pass
            else:
                d_i0 = edges[(c_i,0)].distance
                d_0j = edges[(0,c_j)].distance
                d_ij = edges[(c_i,c_j)].distance
                s_ij = d_i0 + d_0j - d_ij
                savings.append((s_ij, c_i, c_j))
    savings.sort(reverse=True)

    # print("savings", savings[:10])

    # 3. Check if routes can be concatenated according to different criteria
    for s_ij, c_i, c_j in savings:
        if s_ij <= 0:
            break

        route_id_c_i = route_id[c_i]
        route_id_c_j = route_id[c_j]

        r_i = routes[route_id_c_i].nodes
        r_j = routes[route_id_c_j].nodes

        # a. Check that routes are not the same, that they are not empty, and that they can be concatenated.
        if route_id_c_i != route_id_c_j and len(r_i) > 0 and len(r_j) > 0 \
            and r_i[-2].id == c_i and r_j[1].id == c_j:
            # b. Check that capacity constraints are met: time_window, vehicle capacity, etc.
            routes_to_merge = EvaluateMerge(r_i, r_j).evaluate_and_merge_routes()
            if not routes_to_merge:
                # here I need to use the EvaluateMerge function if I don't want to merge the route first
                pass
            else:
                # 4. Merge routes:
                r_i = routes_to_merge                           # r_i = r_i + r_j  # new r_i = [..,4,5,8,9,..]
                routes[route_id_c_i].nodes = r_i
                routes[route_id_c_j].clear()                    # new r_j = []
                route_id[r_i[-2].id] = route_id_c_i             # the new route_id of route r_j changes to the route_id of r_i
                # route_demand[route_id_c_i] = new_demand

    # 5. Get final solution
    ##   a. Remove empty routes from routes
    routes = [route for route in routes if not route.is_empty()]

    ##   b. Assign vehicles randomly to each route
    for route in routes:
        route.set_available_vehicles()
        route.assign_best_vehicle()
    return Solution(routes)