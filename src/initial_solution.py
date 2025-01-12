# Here is where I code the savings algorithm
import resources.global_context as global_context
from src.evaluation import EvaluateMerge
from resources.datatypes.route import Route
from resources.datatypes.solution import Solution

def savings_vrptw():
    """
    This savings heuristic is adapted to respect the time windows for each node
    :return:
    """
    problem_instance = global_context.global_instance

    capacity = max(vehicle.capacity for vehicle in problem_instance.vehicles) # checked according to vehicle with the highest capacity
    nodes = problem_instance.vertices
    edges = problem_instance.edges
    route_id = [-1]
    routes: list[Route] = []
    route_demand = []

    # 1. Create a route per vertex and get required information
    for i in range(1, len(nodes)):
        # create a single route for each node, leaving and coming back to the depot 0
        route = Route([0, i, 0])
        route_id.append(i - 1) # keep track of the nodes added. node -1 to start at 0, 0 is the depot
        routes.append(route)
        route_demand.append(int(problem_instance.vertices[i].demand))

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
            and r_i[-2] == c_i and r_j[1] == c_j:
            # b. Check that capacity constraints are met: time_window, vehicle capacity, etc.
            # TODO: find a better way to evaluate merge (REFs?)
            new_demand = route_demand[route_id_c_i] + route_demand[route_id_c_j]
            valid_time_windows = EvaluateMerge(r_i, r_j).valid_time_windows()
            if new_demand > capacity or not valid_time_windows:
                # here I need to use the EvaluateMerge function if I don't want to merge the route first
                # and use the EvaluateRoute(merged_route).time_window_feasibility or the .is_feasible function:
                pass
            else:
                # 4. Merge routes:
                r_i = routes[route_id_c_i].nodes[:-1]             # r_i = [..,4,5] ([:-1] to remove the depot at the end)
                r_j = routes[route_id_c_j].nodes[1:]              # r_j = [8,9,..] ([1:] to remove the depot at the start)
                r_i = r_i + r_j                                   # new r_i = [..,4,5,8,9,..]
                routes[route_id_c_i].nodes = r_i
                routes[route_id_c_j].clear()                      # new r_j = []
                # the new route_id of route r_j changes to the route_id of r_i
                route_id[r_i[-2]] = route_id_c_i

                route_demand[route_id_c_i] = new_demand

    # 5. Get final solution
    #   a. Remove empty routes from routes
    routes = [route for route in routes if not route.is_empty()]

    #   b. Assign vehicles randomly to each route
    for route in routes:
        route.assign_vehicle()
    return Solution(routes)