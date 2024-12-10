# Here is where I code the savings algorithm
# import numpy as np
# from resources.data import Data

# print(len(instance['edge_weight']))

def savings(problem_instance, evaluation): #can add -> solution: to sate that the return type is a solution
    """
    Performs the parallel version of the Clark & Wright Savings Heuristic (Clark & Wright, 1964) to construct a
    solution. First, the savings value  is calculated for all pair of customers (s_ij = c_i0 + c_0j - c_ij).
    Then the solution is initialized by creating a route for each customer, going from
    the depot to the customer and immediately back to the depot.
    Starting with the largest savings s_ij, we test whether the route r_i ending with node i and r_j beginning with
    node j can be merged, and if possible, they are indeed merged. Then we continue with the largest savings value
    until no more merges are possible.

    :param problem_instance: corresponding problem instance to solve
    :param evaluation: function to calculate total cost (and feasibility)
    :return solution: check
    """
    capacity = problem_instance['capacity'] # this is in the case of only one car
    route_demand = []
    # service_time = problem_instance['service_time']
    # time_window = problem_instance['time_window']
    nodes = problem_instance['service_time'] # what we get here doesn't matter, just add variable nodes for readability
    distance_edges = problem_instance['edge_weight']
    route_id = [-1] # TODO: check why -1 here: (-1) is depot?
    routes = []

    # 1. Create a route per vertex
    for node in range(1, len(nodes)):
        route_id.append(node - 1) # keep track of the nodes added. node -1 to start at 0, 0 is the depot
        routes.append([0, node, 0]) # create a single route for each node, leaving and coming back to the depot 0
        route_demand.append(int(problem_instance['demand'][node]))
    # debug:
    # print(route_id)
    # print(routes)
    # print(route_demand)

    # 2. Calculate all savings between routes
    savings = []
    for c_i in range(1, len(nodes)): # since zero is the depot we start at 1
        for c_j in range(1, len(nodes)):
            if c_i == c_j:
                pass
            else:
                # TODO: because of the loop, it adds savings s_12 and s_21 which have the same savings value, should I remove this?
                d_i0 = distance_edges[c_i][0]
                d_0j = distance_edges[0][c_j]
                d_ij = distance_edges[c_i][c_j]
                s_ij = d_i0 + d_0j - d_ij
                savings.append((s_ij, c_i, c_j))
    # print(savings[:10]) # good, starts savings from (1,2), (1,3), (1,4)...
    savings.sort(reverse=True)
    # print(savings)

    # 3. Check if routes can be concatenated according to different criteria
    for s_ij, c_i, c_j in savings:
        if s_ij <= 0:
            break
        # TODO: check why this and not take c_i directly
        route_id_c_i = route_id[c_i]
        # print(route_id_c_i, c_i)
        route_id_c_j = route_id[c_j]
        # print(route_id_c_j, c_j)
        # a. Check that routes are not the same, that they are not empty, and that they can be concatenated.
        if route_id_c_i != route_id_c_j and len(routes[route_id_c_i]) > 0 and len(routes[route_id_c_j]) > 0 \
            and routes[route_id_c_i][-2] == c_i and routes[route_id_c_j][1] == c_j:
            # b. Check that capacity constraints are met: time, vehicle capacity, etc.
            # TODO: check which more capacities to consider
            # keep track of time to see if we are still within time window: service_time[c_i] + total_travel_distance within time_window[c_j]
            if route_demand[route_id_c_i] + route_demand[route_id_c_j] > capacity:
                pass
            else:
                # 4. Merge routes:
                r_i = routes[route_id_c_i][:-1]             # r_i = [..,4,5] ([:-1] to remove the depot at the end)
                r_j = routes[route_id_c_j][1:]              # r_j = [8,9,..] ([1:] to remove the depot at the start)
                routes[route_id_c_i] = r_i + r_j            # new r_i = [..,4,5,8,9,..]
                routes[route_id_c_j] = []                   # new r_j = []

                route_demand[route_id_c_i] = route_demand[route_id_c_i] + route_demand[route_id_c_j]
                # TODO: calculate new duration
                # route_duration[route_id_c_i] = route_duration[route_id_c_i] + route_duration[route_id_c_j]

    # 5. Remove empty routes from routes
    i = 0
    while i < len(routes):
        if len(routes[i]) == 0:
            del routes[i]
        else:
            i = i + 1
    return routes


