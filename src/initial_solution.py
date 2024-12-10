# Here is where I code the savings algorithm
# import numpy as np
from resources.data import Data

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
    capacity = problem_instance['capacity']
    demand  = problem_instance['demand']
    nodes = problem_instance['service_time'] # what we get here doesn't matter, just add variable nodes for readability
    distance_edges = problem_instance['edge_weight']
    route_id = [-1] # TODO: check why -1 here
    routes = []

    # 1. Create a route per vertex
    for node in range(1, len(nodes)):
        route_id.append(node) # keep track of the nodes added
        routes.append([node]) # create a single route for each node
    # debug
    # print(route_id)
    # print(routes)

    # 2. Calculate all savings between routes
    savings = []
    for c_i in range(1, len(nodes)):
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
    savings.sort(reverse=True)

    for s_ij, c_i, c_j in savings:
        if s_ij <= 0:
            break

        # if c_i =

    return

problem_instance= Data().get_instance("C1_2_1.txt")
evaluation = "evaluation function for the cost"
savings(problem_instance, evaluation)