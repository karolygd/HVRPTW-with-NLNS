# Here I will do all the running of solutions
# Defining the problem instance to solve, getting the initial solution, getting the alns solution, ...

from resources.data import Data
from src.initial_solution import savings_vrptw
from src.operators.remove_operators import RemoveOperators
from src.operators.insertion_operators import InsertionOperators
import time

problem_instance= Data().get_instance("C1_2_1.txt")

initial_solution = savings_vrptw(problem_instance)
print(initial_solution)

# initial_solution = [Route(nodes=[0, 2, 174, 136, 189, 0]), Route(nodes=[0, 4, 72, 165, 188, 108, 0]), Route(nodes=[0, 20, 41, 27, 46, 128, 106, 167, 34, 95, 158, 0]), Route(nodes=[0, 21, 23, 182, 40, 0]), Route(nodes=[0, 26, 80, 31, 25, 172, 77, 0]), Route(nodes=[0, 30, 120, 19, 192, 146, 68, 76, 0]), Route(nodes=[0, 32, 171, 160, 47, 91, 70, 0]), Route(nodes=[0, 44, 0]), Route(nodes=[0, 45, 178, 85, 75, 163, 194, 145, 195, 52, 92, 0]), Route(nodes=[0, 57, 118, 83, 13, 43, 37, 81, 138, 0]), Route(nodes=[0, 59, 198, 0]), Route(nodes=[0, 60, 82, 166, 0]), Route(nodes=[0, 62, 131, 0]), Route(nodes=[0, 73, 116, 102, 22, 151, 16, 181, 117, 49, 0]), Route(nodes=[0, 78, 175, 35, 61, 100, 0]), Route(nodes=[0, 89, 105, 15, 74, 0]), Route(nodes=[0, 93, 55, 135, 150, 0]), Route(nodes=[0, 101, 144, 119, 143, 176, 36, 33, 121, 17, 39, 0]), Route(nodes=[0, 113, 155, 12, 0]), Route(nodes=[0, 114, 159, 38, 8, 186, 127, 98, 157, 137, 183, 63, 56, 0]), Route(nodes=[0, 115, 69, 0]), Route(nodes=[0, 133, 48, 0]), Route(nodes=[0, 148, 103, 65, 86, 0]), Route(nodes=[0, 152, 112, 153, 169, 96, 130, 28, 0]), Route(nodes=[0, 161, 104, 18, 58, 184, 199, 0]), Route(nodes=[0, 164, 66, 147, 129, 11, 6, 122, 139, 0]), Route(nodes=[0, 170, 134, 50, 156, 24, 200, 64, 179, 109, 0]), Route(nodes=[0, 173, 154, 168, 79, 29, 87, 42, 123, 149, 0]), Route(nodes=[0, 177, 3, 88, 54, 185, 132, 7, 0]), Route(nodes=[0, 180, 84, 191, 125, 90, 67, 0]), Route(nodes=[0, 190, 5, 10, 193, 126, 71, 9, 1, 99, 53, 107, 0]), Route(nodes=[0, 196, 97, 14, 140, 187, 142, 111, 0]), Route(nodes=[0, 197, 124, 141, 94, 51, 110, 162, 0])]
cost = 0
for route in initial_solution:
    # print(route.nodes)
    cost += route.cost
    # cost += route.total_cost()
print("cost of initial_solution: ", cost)
print(initial_solution)

# draw_routes(initial_solution)

# Debug destroy operators
print("*** Removing customers ***")
start_time = time.time()
customers_removed = RemoveOperators().a_posteriori_score_related_customers(initial_solution, num_customers_to_remove=5)
cost_removed = 0
for route in initial_solution:
    # print(route.nodes)
    cost_removed += route.cost
print("cost of initial_solution: ", cost_removed)
print("removed_customers: ", customers_removed)
end_time = time.time()
duration = end_time - start_time
print(f"The removal process took {duration:.4f} seconds.")

print("*** Reinserting customers ***")
start_time = time.time()
InsertionOperators().random_order_best_position(initial_solution, customers_removed)
cost_inserted = 0
for route in initial_solution:
    print(route.nodes)
    cost_inserted += route.cost
print("cost of initial_solution: ", cost_inserted)
end_time = time.time()
duration = end_time - start_time
print(f"The insertion process took {duration:.4f} seconds.")

# # draw_routes(initial_solution)