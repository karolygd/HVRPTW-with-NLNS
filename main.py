# Here I will do all the running of solutions
# Defining the problem instance to solve, getting the initial solution, getting the alns solution, ...

from resources.data import parse_problem_instance
import resources.global_context as global_context
from resources.datatypes.solution import Solution
from src.initial_solution import savings_vrptw
from src.operators.remove_operators import RemoveOperators
from src.operators.insertion_operators import InsertionOperators
from src.helpers.plots import draw_routes

from src.alns import alns
import time

# --- Set the global instance to be solved ---
instance_name = "C101.txt"
global_context.global_instance = parse_problem_instance(instance_name, vehicle_cost_structure='a')

def print_solution(solution: Solution):
    simplified_solution = []
    for route in solution.routes:
        r = [node.id for node in route.nodes]
        simplified_solution.append(r)
    print(simplified_solution)

# --- Get initial solution ---
initial_solution = savings_vrptw()
print("cost of initial_solution: ", initial_solution.get_cost())
print("total distance: ", initial_solution.get_distance())
print_solution(initial_solution)
print(initial_solution)
print("")

# --- Solve the alns: define hyperparameters ---
start_time = time.time()
alns_solution = alns(initial_solution, number_of_iterations=5000)
print(alns_solution)


print_solution(alns_solution)
end_time = time.time()
duration = end_time - start_time
print("cost of alns_solution: ", alns_solution.get_cost())
print("total distance: ", alns_solution.get_distance())
print("computing time: ", duration)

"""
# Debug destroy operators
print("*** Removing customers ***")
start_time = time.time()
remove_operator = RemoveOperators().random_route()
customers_removed = initial_solution.apply_destroy_operator(remove_operator, num_customers_to_remove=10)
removed_ = [node.route_id for node in customers_removed]
removed_route_ids = set(removed_)
print("removed routes_ids: ", removed_route_ids)
cost_removed = 0
total_distance = 0
# Need to recalculate the costs ALWAYS
for route in initial_solution.routes:
    # route.calculate_total_cost()
    total_distance += route.total_distance()
    # print(route.nodes, "-", route.cost)
    cost_removed += route.cost
    if route.nodes[-1].route_id in removed_route_ids:
        print(route)
print("cost of initial_solution: ", cost_removed)
print("total distance: ", total_distance)
print("customers_removed: ", customers_removed)
removed_customers = [customer.id for customer in customers_removed]
print("removed_customers: ", removed_customers)
print_solution(initial_solution)
end_time = time.time()
duration = end_time - start_time
print(f"The removal process took {duration:.4f} seconds.")
print("")


print("*** Reinserting customers ***")
start_time = time.time()
insert_operator = InsertionOperators().customer_with_highest_position_regret_best_position()
initial_solution.apply_insert_operator(insert_operator, customers_removed)
cost_inserted = 0
total_distance = 0
# routes_changed = set()
for route in initial_solution.routes:
    # route.calculate_total_cost()
    # print(route.nodes, "-", route.cost)
    cost_inserted += route.cost
    total_distance += route.total_distance()
    for node in route.nodes:
        if node.id in removed_customers:
            print(route)
print("cost of new_solution: ", cost_inserted)
print("total distance: ", total_distance)
# print(routes_changed)
print_solution(initial_solution)
end_time = time.time()
duration = end_time - start_time
print(f"The insertion process took {duration:.4f} seconds.")
"""
# draw_routes(alns_solution.routes, instance_name)