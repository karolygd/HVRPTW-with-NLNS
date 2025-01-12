import random
from resources.datatypes import Route
from resources.data import Data

class InsertionOperators:
    def __init__(self):
        self.problem_instance = Data().get_instance("C1_2_1.txt")
        self.demand = self.problem_instance['demand']
        self.distance_edges = self.problem_instance['edge_weight']
        self.insertion_cache = {}

    @staticmethod
    def _select_best_insertion_position(solution:list[Route], customer:int):
        # For large instances, consider only evaluating a subset of routes (e.g., based on proximity to the customer).

        best_cost = float('inf')
        best_route_id = None
        best_after_node = None

        for route_id, route in enumerate(solution):
            for i in range(len(route.nodes) - 1):  # Possible insertion points
                after_node = route.nodes[i]

                # Temporarily insert the customer
                route.insert_node_after(customer, after_node)
                # insertion_position = i+1

                # Check feasibility (e.g., time windows, capacity)
                if route.is_feasible:
                    # Calculate cost of the modified route
                    # Before:
                    cost = route.cost
                    if cost < best_cost:
                        best_cost = cost
                        best_route_id = route_id
                        best_after_node = after_node

                    # After:
                    # insertion_cost = route.calculate_insertion_cost(customer, insertion_position)
                    #
                    # if insertion_cost < best_cost:
                    #     best_cost = insertion_cost
                    #     best_route_id = route_id
                    #     best_after_node = after_node

                # Remove the customer to restore the original route
                route.remove_node(customer)

        if best_route_id is None or best_after_node is None:
            raise ValueError(f"Customer {customer} could not be feasibly inserted into any route.")

        return best_route_id, best_after_node, best_cost

    def random_order_best_position(self, solution: list[Route], removed_customers:list[int]):
        """
        Randomizes the order of the removed customers and inserts one by one in their best cost position in the solution.
        :param solution:
        :param removed_customers:
        """
        # Randomize the order of the removed customers
        random.shuffle(removed_customers)

        for customer in removed_customers:
            route_id, node_id, insertion_cost= self._select_best_insertion_position(solution, customer)
            solution[route_id].insert_node_after(customer, after_node= node_id)
            # # Recalculate route cost:
            # solution[route_id].cost = solution[route_id].cost + insertion_cost

    def customer_with_highest_position_regret_best_position(self, solution: list[Route], removed_customers:list[int], k: int = 2):
        """
        Inserts customers based on the highest position regret value.
        :param solution:
        :param removed_customers:
        :param k: Number of top insertion costs to consider for regret calculation (default is 2).
        """
        pass

# def highest_position_regret_insertion_with_cache(
#     self, solution: list[Route], removed_customers: list[int], k: int = 2
# ):
#     """
#     Inserts customers based on the highest position regret value with caching.
#
#     Parameters:
#     - solution (list[Route]): Current solution (list of routes).
#     - removed_customers (list[int]): List of customers to be inserted.
#     - k (int): Number of top insertion costs to consider for regret calculation (default is 2).
#
#     Returns:
#     - None: Modifies the solution in place.
#     """
#     # Initialize a cache for insertion costs
#     insertion_cache = {}
#
#
#
#     while removed_customers:
#         best_customer = None
#         best_regret_value = float('-inf')
#         best_insertion_details = None
#
#         for customer in removed_customers:
#             insertion_costs = []
#
#             # Evaluate all routes for the current customer
#             for route_id, route in enumerate(solution):
#                 for i in range(len(route.nodes) - 1):  # Possible insertion points
#                     after_node = route.nodes[i]
#                     cost, is_feasible = calculate_insertion_cost(customer, route, after_node)
#
#                     if is_feasible:
#                         insertion_costs.append((cost, route_id, after_node))
#
#             # Sort insertion costs to find the best positions
#             insertion_costs.sort(key=lambda x: x[0])
#
#             # Calculate regret value
#             if len(insertion_costs) >= k:
#                 regret_value = sum(insertion_cost[0] for insertion_cost in insertion_costs[1:k]) - insertion_costs[0][0]
#             else:
#                 regret_value = float('-inf')  # Not enough routes to calculate regret
#
#             # Update best customer and insertion details
#             if regret_value > best_regret_value:
#                 best_regret_value = regret_value
#                 best_customer = customer
#                 best_insertion_details = insertion_costs[0] if insertion_costs else None
#
#         # Insert the best customer into its best position
#         if best_customer is not None and best_insertion_details is not None:
#             cost, route_id, after_node = best_insertion_details
#             solution[route_id].insert_node_after(best_customer, after_node)
#             removed_customers.remove(best_customer)
#
#             # Clear the cache since the solution changed
#             insertion_cache.clear()
#         else:
#             raise ValueError("No feasible insertion found for remaining customers.")

