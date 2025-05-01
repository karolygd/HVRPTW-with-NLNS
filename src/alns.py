import random
import math
from src.operators.remove_operators import RemoveOperators
from src.operators.insertion_operators import InsertionOperators
from src.alns_components.adaptive_layer import AdaptiveOperatorSelector
from src.alns_components.neural_operator_selector.nn_op_selector import NeuralOperatorSelector
from src.alns_components.adaptive_removal import AdaptiveRemovalManager
#from src.alns_components.local_search import LocalSearch
from src.alns_components.setting_temperature import SettingTemperature
from src.helpers.features import EngFeatures
import pandas as pd
import logging

# --- Configure the logging:
logging.basicConfig(
    filename='test_benchmark_alns.log',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def alns(instance_type: int, tw_spread: int, initial_solution, number_of_iterations: int, operator_selection:int,
         h_start, h_end, temp_update_func, segment_size:int, o1: float, o2: float, o3: float):

    # --- initialize the solution:
    solution = initial_solution.copy()
        # best solution:
    best_solution = initial_solution
    best_cost = solution.get_cost()
        # current solution:
    current_solution = initial_solution.copy()
    current_cost = best_cost
        # keeping track of visited solutions:
    accepted_solutions = set()

    # --- define initial and final temperature for SA
    sa_temp = SettingTemperature(h_start, h_end, temp_update_func, current_cost, number_of_iterations)
    temperature =  sa_temp.initial_temperature()
    sa_temp.final_temperature()

    # --- select the pool of removal and insertion operators:
    remove_operators = RemoveOperators()
    insert_operators = InsertionOperators()
    remove_operators_list = [remove_operators.random_customers(),
                        remove_operators.randomly_selected_sequence_within_concatenated_routes(),
                        remove_operators.a_posteriori_score_related_customers(),
                        remove_operators.worst_cost_customers(),
                        remove_operators.random_route()]
    insert_operators_list = [insert_operators.random_order_best_position(),
                        insert_operators.customer_with_highest_position_regret_best_position(k=2),
                        insert_operators.customer_with_highest_position_regret_best_position(k=3)]

    # --- Define the adaptive layer: operator selector and number of customers to remove
    number_of_customers = len(remove_operators.vertices)
    aos = AdaptiveOperatorSelector(remove_operators_list, insert_operators_list)
    nos = NeuralOperatorSelector(remove_operators_list, insert_operators_list)
    adaptive_removal = AdaptiveRemovalManager(number_of_customers)

    # --- initialize features needed
    e_feature = EngFeatures()
    n_accepted_solutions = e_feature.recent_acceptances(segment_size)
    prev_remove_operator = None
    prev_insert_operator = None
    prev_features = {"rel_delta_last_improv": 0, "acceptance_ratio": 0, "i_last_improv": 0}
    i_last_improv = 0
    delta_last_improv = 0
    for i in range(1, number_of_iterations+1):
        # --- define number of nodes/customers to remove
        number_of_vertices_to_remove = adaptive_removal.get_removal_size()
            # for ablation analysis:
            # number_of_vertices_to_remove =  random.randrange(5, 25, 5)
        # --- define input data for neural network
        nn_input_features = [
            i,
            prev_features["acceptance_ratio"],
            number_of_vertices_to_remove,
            prev_features["i_last_improv"],
            e_feature.route_imbalance(solution),
            e_feature.capacity_utilization(solution)
            ]

        success_remove_operators = []
        for operator in remove_operators_list:
            success_remove_operators.append(operator.weight)
        success_insert_operators = []
        for operator in insert_operators_list:
            success_insert_operators.append(operator.weight)

        sign_features = [prev_features["rel_delta_last_improv"]]

        cat_features = [
            instance_type,
            tw_spread,
            1, #operator_selection, #todo:check the effect of changing this to 1 in next run
            prev_remove_operator,
            prev_insert_operator
        ]

        nn_input_features = nn_input_features + success_remove_operators + success_insert_operators + sign_features + cat_features
        dict_features = {'1': nn_input_features}
        feature_log = f""
        for feature in nn_input_features:
            feature_log += f"{feature},"

        col_names = ['iterations', 'acceptance_ratio', 'number_of_vertices_to_remove', 'i_last_improv',
                     'route_imbalance', 'capacity_utilization', 'success_r_op_1', 'success_r_op_2', 'success_r_op_3',
                     'success_r_op_4', 'success_r_op_5', 'success_i_op_1', 'success_i_op_2', 'success_i_op_3',
                     'rel_delta_last_improv', 'instance_type', 'tw_spread', 'operator_selection_mechanism',
                     'prev_remove_operator', 'prev_insert_operator']

        X_predict = pd.DataFrame.from_dict(dict_features, orient='index', columns=col_names)

        # --- set insert and remove operators and apply to the solution:
        if operator_selection == 1:
            remove_operator, insert_operator = aos.roulete_wheel()  # or random selection
        else:
            #remove_operator, insert_operator = aos.random_selection()
            # Todo: here incorporate the neural network
            remove_operator, insert_operator = nos.select_operator(X_predict)

        removed_customers = solution.apply_destroy_operator(remove_operator, num_customers_to_remove=number_of_vertices_to_remove)
        solution.apply_insert_operator(insert_operator, removed_customers) # check a way to return a solution
        new_cost = solution.get_cost()

        # --- recalculate data for adaptive number of customers to remove
        adaptive_removal.update_mu(new_cost, best_cost, current_cost)

            # Due to ablation analysis local search will no longer be used
            # ls.apply_local_search(solution)
            # new_cost = solution.get_cost()

        # --- acceptance criteria: SA

        delta_cost = new_cost - current_cost
        relative_delta_cost = delta_cost/current_cost
        if delta_cost < 0:
            accept_prob = 1.0
        else:
            exponent = -delta_cost / temperature
            if abs(exponent) > 700:
                accept_prob = 0.0
            else:
                accept_prob = math.exp(-delta_cost / temperature)
        if delta_cost < 0 or random.random() < math.exp(accept_prob):
            n_accepted_solutions.append(1)
            current_solution = solution.copy()
            current_cost = new_cost
            solution = solution
            # --- Check if the new solution is a global best
            if new_cost < best_cost:
                i_last_improv = 0  # an improvement occurred, so last improvement is restarted
                delta_last_improv = relative_delta_cost #delta_cost
                best_cost = new_cost
                best_solution = current_solution.copy()
                # reward operators for best global solution -> o1
                remove_operator.update_score(score = o1) #4.0
                insert_operator.update_score(score = o1)
                # Add the new solution to the set of accepted solutions
                accepted_solutions.add(solution.__hash__())
            elif solution.__hash__() not in accepted_solutions:
                # Add the new solution to the set of accepted solutions
                accepted_solutions.add(solution.__hash__())
                if delta_cost < 0:  # Better than the current solution
                    i_last_improv = 0   # an improvement occurred, so last improvement is restarted
                    delta_last_improv = relative_delta_cost #delta_cost
                    # reward operators for best current solution -> o2
                    remove_operator.update_score(score=o2) #2.5
                    insert_operator.update_score(score=o2)
                    pass
                else:
                    i_last_improv += 1
                    # DO NOT update delta_last_improv here (keeps the last improvement magnitude)
                    #reward operators for different solution -> o3
                    remove_operator.update_score(score=o3) #1.0
                    insert_operator.update_score(score=o3)
                    pass
            else:
                i_last_improv += 1
                # DO NOT update delta_last_improv here (keeps the last improvement magnitude)
                # solution was accepted, but it has already been visited:
                remove_operator.update_score()
                insert_operator.update_score()
        else:
            # still update operator score (frequency + 1, score + 0)
            n_accepted_solutions.append(0)
            solution = current_solution.copy()
            remove_operator.update_score()
            insert_operator.update_score()

        # --- Update the temperature:
        temperature = sa_temp.update_temperature()

        # --- calculate new operator weights based on the last segment.
        if i % segment_size == 0:
            aos.adapt_operator_weights()
            # after the new weights have been calculated, the score and frequency for the new segment are re-initialized
            aos.initialize_weights()

        # --- Get output features and log them
        output = f"{delta_cost}, {new_cost}, {remove_operator.name}, {insert_operator.name}"
        feature_log += output

        logger.info(feature_log)

        # --- Get and store features for the next iteration
        acceptance_ratio = sum(n_accepted_solutions) / len(n_accepted_solutions)

        prev_features["rel_delta_last_improv"] = delta_last_improv #changed variable name to fit new df
        prev_features["acceptance_ratio"] = acceptance_ratio
        prev_features["i_last_improv"] = i_last_improv
        prev_remove_operator = remove_operator.name
        prev_insert_operator = insert_operator.name

    return best_solution

