# Here code the alns metaheuristic
# Use the operators from the operator.py folder.
import random
import math
from src.operators.remove_operators import RemoveOperators
from src.operators.insertion_operators import InsertionOperators
from src.alns_components.adaptive_layer import AdaptiveLayer


def alns(initial_solution, number_of_iterations: int):

    # --- initialize the solution:
    solution = initial_solution.copy() #probably need to do a copy for when the new_solution doesn't get accepted, check deepcopy()
    # best solution:
    best_solution = initial_solution #Solution(routes=initial_solution)
    best_cost = solution.get_cost()
    # current solution:
    current_solution = initial_solution.copy()
    current_cost = best_cost
    # keeping track of visited solutions:
    accepted_solutions = set()

    temperature = 10  # TODO: check how to define the initial temp
    cooling_rate = 0.05     # TODO: check how to define the cooling rate

    remove_operators = RemoveOperators()
    insert_operators = InsertionOperators()
    # --- select the pool of remove operators:
    remove_operators_list = [remove_operators.random_customers(),
                        remove_operators.randomly_selected_sequence_within_concatenated_routes(),
                        remove_operators.a_posteriori_score_related_customers(),
                        remove_operators.worst_cost_customers()]

    # --- select the pool of insertion operators:
    insert_operators_list = [insert_operators.random_order_best_position(),
                        insert_operators.customer_with_highest_position_regret_best_position(k=2),
                        insert_operators.customer_with_highest_position_regret_best_position(k=3)]

    adl = AdaptiveLayer(remove_operators_list, insert_operators_list)
    # adl.adapt_operator_weights() # to initialize the weights of all operators at 1

    for i in range(1, number_of_iterations+1):
        number_of_vertices_to_remove = 5 #adjust this
        print("iteration: ", i)
        # --- set insert and remove operators:
        remove_operator, insert_operator = adl.roulete_wheel() # roulette_wheel(remove_operators, insert_operators)
        print(f"selected remove operator: {remove_operator.name}, selected insert operator: {insert_operator.name}")
        # print(f"selected remove operator: {remove_operator.__name__}, selected insert operator: {insert_operator.__name__}") #not working __name__

        removed_customers = solution.apply_destroy_operator(remove_operator, num_customers_to_remove=5) # TODO: set a destruction rate
        print(f"removed customers: {removed_customers}")
        solution.apply_insert_operator(insert_operator, removed_customers) # check a way to return a solution
        new_cost = solution.get_cost()
        # debugging:
        print(f"new solution: {solution}")
        print(f"new cost: {new_cost}")
        print("old solution: ", best_solution)

        # --- acceptance criteria
        delta_cost = new_cost - current_cost
        if delta_cost < 0 or random.random() < math.exp(-delta_cost/temperature):
            current_solution = solution.copy()
            current_cost = new_cost
            solution = solution
            print("solution hash: ", solution.__hash__())
            # Check if the new solution is a global best
            if new_cost < best_cost:
                best_cost = new_cost
                best_solution = current_solution.copy()
                # reward operators for best global solution -> o2
                remove_operator.update_score(score = 4.0)
                insert_operator.update_score(score = 4.0)
                # Add the new solution to the set of accepted solutions
                accepted_solutions.add(solution.__hash__())
            elif solution.__hash__() not in accepted_solutions:
                # Add the new solution to the set of accepted solutions
                accepted_solutions.add(solution.__hash__())
                if delta_cost < 0:  # Better than the current solution
                    # reward operators for best current solution -> o2
                    remove_operator.update_score(score=2.5)
                    insert_operator.update_score(score=2.5)
                    pass
                else:
                    # reward operators for different solution -> o3
                    remove_operator.update_score(score=1.0)
                    insert_operator.update_score(score=1.0)
                    pass
            else:
                # solution was accepted, but it has already been visited:
                remove_operator.update_score()
                insert_operator.update_score()
        else:
            # still update operator score (frequency + 1, score + 0)
            # debug, check that if the solution is not accepted, it goes back to the one before
            print("--- not accepted :( ---")
            solution = current_solution.copy()
            remove_operator.update_score()
            insert_operator.update_score()

        print(accepted_solutions)
        # Update the temperature
        temperature = temperature * cooling_rate # TODO: set the cooling mechanism

        # --- calculate new operator weights based on the last segment.
        segment_size = 20
        if i % segment_size == 0:
            score_frequency_list = [(op.score, op.frequency) for op in remove_operators_list]
            print(score_frequency_list)
            print("---- adapted operator weight ----")
            adl.adapt_operator_weights()
            # after the new weights have been calculated, the score and frequency for the new segment are re-initialized
            adl.initialize_weights()
            score_frequency_list = [(op.score, op.frequency) for op in remove_operators_list]
            print(score_frequency_list)

        print(
            f"Remove operator score: {remove_operator.score, remove_operator.frequency}, Insert operator score: {insert_operator.score, insert_operator.frequency}")
        print("")

    return solution

