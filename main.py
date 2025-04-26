# Here I will do all the running of solutions
# Defining the problem instance to solve, getting the initial solution, getting the alns solution, ...

from resources.data import parse_problem_instance, parse_reduced_instance
import resources.global_context as global_context
from resources.datatypes.solution import Solution
from src.initial_solution import savings_vrptw
from resources.recording_data import RecordingData
# from src.operators.remove_operators import RemoveOperators
# from src.operators.insertion_operators import InsertionOperators
# from src.helpers.plots import draw_routes
from src.alns_components.local_search import LocalSearch

from src.alns import alns
import time

def print_solution(solution: Solution):
    simplified_solution = []
    for route in solution.routes:
        r = [node.id for node in route.nodes]
        simplified_solution.append(r)
    print(simplified_solution)

# # --- Set the global instance to be solved ---
# # ** for benchmarks **
# instance_name = "C101.txt"
# global_context.global_instance = parse_problem_instance(instance_name, vehicle_cost_structure='a')
# # ** for training **
# # instance_name = "C1_2_1_100.txt"
# # global_context.global_instance = parse_reduced_instance(instance_name, vehicle_cost_structure='a')
#
#
# # --- Get initial solution ---
# initial_solution = savings_vrptw()
# print("cost of initial_solution: ", initial_solution.get_cost())
# #print("total distance: ", initial_solution.get_distance())
# print_solution(initial_solution)
# print(initial_solution)
# print("")

# # --- Solve the alns: define hyperparameters ---
# if instance_name[0] == "C": # C: clustered instance
#     instance_type = 0
# elif instance_name[1] == "C": # RC: random-clustered instance
#     instance_type = 2
# else:                          # R: random instance
#     instance_type = 1
#
# tw_spread = instance_name[1]
# try:
#     tw_spread = int(instance_name[1])
# except:
#     tw_spread = int(instance_name[2])
# print("tw_spread: ", tw_spread)
#
# start_time = time.time()
# alns_solution = alns(instance_type=instance_type, tw_spread=tw_spread, initial_solution=initial_solution, number_of_iterations=1000, operator_selection=1, h_start=1000, h_end=0, temp_update_func='linear', segment_size=20,
#                      o1=5, o2=3, o3=1)
# end_time = time.time()
# duration = end_time - start_time
#
# print(alns_solution)
# print_solution(alns_solution)
# print("cost of alns_solution: ", alns_solution.get_cost())
# #print("total distance: ", alns_solution.get_distance())
# print("computing time: ", duration)



# --- Statistical Analysis ---
# file = "hyperparameters"
# headers_1 = ["Iteration", "Instance", "Execution Time (s)", "Best Cost",  "params_iterations", "params_global_best_score", "params_local_best_score", "params_accepted_score",
#              "params_cooling_function", "params_init_temp", "params_final_temp"]
# rd = RecordingData(file, headers_1)

instances_to_run = ["RC2_2_1_100.txt", "RC2_2_2_100.txt", "RC2_2_3_100.txt", "RC2_2_4_100.txt", "RC2_2_5_100.txt", "RC2_2_6_100.txt",
                    "RC2_2_7_100.txt", "RC2_2_8_100.txt", "RC2_2_9_100.txt"]
parameter_set = {"params_accepted_score":1,
    "params_cooling_function":"exponential",
    "params_final_temp":41.6653632001,
    "params_global_best_score":5,
    "params_init_temp":2000,
    "params_iterations":2000,
    "params_local_best_score":4}

i = 0
for instance in instances_to_run:
    if instance[0] == "C":  # C: clustered instance
        instance_type = 0
    elif instance[1] == "C":  # RC: random-clustered instance
        instance_type = 2
    else:  # R: random instance
        instance_type = 1

    tw_spread = instance[1]
    try:
        tw_spread = int(instance[1])
    except:
        tw_spread = int(instance[2])

    instance_name = instance
    global_context.global_instance = parse_reduced_instance(instance, vehicle_cost_structure='a')

    # --- Get initial solution ---
    initial_solution = savings_vrptw()

    start_time = time.time()
    # 0: random_selector, 1: roulette_wheel
    alns_solution = alns(instance_type=instance_type, tw_spread=tw_spread, initial_solution=initial_solution, operator_selection=0,
                         number_of_iterations=parameter_set['params_iterations'], h_start=parameter_set['params_init_temp'], h_end=parameter_set['params_final_temp'],
                         temp_update_func=parameter_set['params_cooling_function'], segment_size=20,
                         o1=parameter_set['params_global_best_score'], o2=parameter_set['params_local_best_score'], o3=parameter_set['params_accepted_score'])
    end_time = time.time()
    duration = end_time - start_time
    print("done with alns run ")
    #
    # log_dict = {
    #     "Instance": instance,
    #     "Execution Time (s)": duration,
    #     "Best Cost": alns_solution.get_cost(),
    #     "params_iterations": parameter_set['params_iterations'],
    #     "params_global_best_score": parameter_set['params_global_best_score'],
    #     "params_local_best_score": parameter_set['params_local_best_score'],
    #     "params_accepted_score": parameter_set['params_accepted_score'],
    #     "params_cooling_function": parameter_set['params_cooling_function'],
    #     "params_init_temp": parameter_set['params_init_temp'],
    #     "params_final_temp": parameter_set['params_final_temp']
    #     }
    #
    # rd.log_iteration(iteration= i, **log_dict)
    # print("done writing data")
    # print(log_dict)
    # i+=1

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