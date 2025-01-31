# Here I will do all the running of solutions
# Defining the problem instance to solve, getting the initial solution, getting the alns solution, ...

from resources.data import parse_problem_instance
import resources.global_context as global_context
from src.initial_solution import savings_vrptw
from src.operators.remove_operators import RemoveOperators
from src.operators.insertion_operators import InsertionOperators
from src.alns import alns
import time

# --- Set the global instance to be solved ---
instance_name = "C1_2_1.txt"
global_context.global_instance = parse_problem_instance(instance_name, vehicle_cost_structure='a')

# --- Get initial solution ---
initial_solution = savings_vrptw()
all_routes_cost = 0
for route in initial_solution.routes:
    # print(route.nodes)
    route.calculate_total_cost()
    all_routes_cost += route.cost
print("cost of initial_solution: ", all_routes_cost)
print(initial_solution)
print("")

# --- Solve the alns: define hyperparameters ---
alns_ = alns(initial_solution, number_of_iterations=5)
# print(alns_)

# all_routes_cost = 0
# for route in alns_.routes:
#     # print(route.nodes)
#     # route.calculate_total_cost()
#     all_routes_cost += route.cost
# print("cost of alns_solution: ", all_routes_cost)

# # Debug destroy operators
# print("*** Removing customers ***")
# start_time = time.time()
# customers_removed = RemoveOperators().worst_cost_customers(initial_solution, num_customers_to_remove=20)
# cost_removed = 0
# # Need to recalculate the costs ALWAYS
# for route in initial_solution:
#     route.calculate_total_cost()
#     # print(route.nodes, "-", route.cost)
#     cost_removed += route.cost
# print("cost of initial_solution: ", cost_removed)
# print("removed_customers: ", customers_removed)
# end_time = time.time()
# duration = end_time - start_time
# print(f"The removal process took {duration:.4f} seconds.")
#
# print("*** Reinserting customers ***")
# start_time = time.time()
# InsertionOperators().customer_with_highest_position_regret_best_position_2(initial_solution, customers_removed)
# cost_inserted = 0
# for route in initial_solution:
#     route.calculate_total_cost()
#     print(route.nodes, "-", route.cost)
#     cost_inserted += route.cost
# print("cost of initial_solution: ", cost_inserted)
# end_time = time.time()
# duration = end_time - start_time
# print(f"The insertion process took {duration:.4f} seconds.")

# draw_routes(initial_solution)