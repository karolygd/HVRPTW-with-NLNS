import random
from resources.datatypes.route import Route
from resources.datatypes.operator import Operator
from resources.datatypes.solution import Solution
from resources.datatypes.node import Node

class InsertionOperators:
    def __init__(self):
        self.insertion_cache = {}

    def _calculate_insertion_cost(self, customer: Node, route: Route, position: int) -> float:
        """
        Calculate the insertion cost for a customer at a specific position in the route.
        If insertion is unfeasible, cost is infinite.
        Uses caching to avoid redundant computations.
        """
        cache_key = (customer.id, id(route.nodes), position)
        if cache_key in self.insertion_cache:
            return self.insertion_cache[cache_key]

        # Temporarily insert the customer to check feasibility
        insertion_is_feasible, temp_t_i, temp_z_i, temp_d_i, temp_position, temp_FS_i = route.insertion_is_feasible(customer, position)
        if insertion_is_feasible:
            insertion_cost = route.calculate_insertion_cost(node_to_insert=customer, position=position)
            # Cache the result
            self.insertion_cache[cache_key] = [insertion_cost, temp_t_i, temp_z_i, temp_d_i, temp_position, temp_FS_i]
        else:
            # print("insertion not feasible ", float('inf'))
            insertion_cost = float('inf')  # Infeasible insertion
        return insertion_cost

    def _select_best_insertion_position(self, solution:Solution, customer:Node):
        # For large instances, consider only evaluating a subset of routes (e.g., based on proximity to the customer).
        _solution = solution.routes

        best_insertion_cost = float('inf')
        best_route_id = None
        best_insertion_position = None

        for route_id, route in enumerate(_solution):
            for i in range(len(route.nodes) - 1):  # Possible insertion points
                # after_node = route.nodes[i]
                insertion_position = i + 1

                insertion_cost = self._calculate_insertion_cost(customer, route, insertion_position)
                if insertion_cost < best_insertion_cost:
                    best_insertion_cost = insertion_cost
                    best_route_id = route_id
                    best_insertion_position = insertion_position

        if best_route_id is None or best_insertion_position is None:
            return None, None, None
        else:
            return best_route_id, best_insertion_position, best_insertion_cost

    def random_order_best_position(self):
        """
        Randomizes the order of the removed customers and inserts one by one in their best cost position in the solution.
        """
        def operator(solution: Solution, removed_customers:list[Node]):
            """
            :param solution: list of routes
            :param removed_customers: list of removed customers
            :return: Modifies the solution in place.
            """
            _solution = solution.routes
            # Randomize the order of the removed customers
            random.shuffle(removed_customers)

            for customer in removed_customers:
                route_id, insertion_position, insertion_cost= self._select_best_insertion_position(solution, customer)
                if route_id is not None and insertion_position is not None:
                    temp_params = self.insertion_cache[(customer.id, id(_solution[route_id].nodes), insertion_position)]
                    # temp_params = [insertion_cost, temp_t_i, temp_z_i, temp_d_i, temp_position, temp_FS_i]
                    _solution[route_id].insert_node_at(customer, position=insertion_position, update=temp_params[1:])
                    # Recalculate route cost:
                    _solution[route_id].assign_best_vehicle()
                else:
                    # print(" ... 1 Creating new route for: ")
                    # print(customer)
                    solution.create_new_route(customer)
                    # print("...")
                    # print("-- new route existing in solution? ", solution)

            # Clear the cache since the solution changed
            self.insertion_cache.clear()
            return solution
        return Operator(operator, name="0")

    def customer_with_highest_position_regret_best_position(self, k: int = 2):
        """
        Inserts customers based on the highest position regret value.
        :param k: Number of top insertion costs to consider for regret calculation (default is 2).
        """
        op_name = k-1 #k starts at 2, k=2->op=1, k=3->op=2
        def operator(solution: Solution, removed_customers:list[Node]):
            """
            :param solution: list of routes
            :param removed_customers: List of customers to be inserted.
            :return: Modifies the solution in place.
            """
            _solution = solution.routes

            while removed_customers:
                best_customer = None
                highest_regret_value = float('-inf')
                best_insertion_details = None

                for customer in removed_customers:
                    insertion_costs = []

                    # Evaluate all routes for the current customer
                    for route_id, route in enumerate(_solution):
                        for i in range(len(route.nodes) - 1):  # Possible insertion points
                            insertion_position = i+1
                            cost = self._calculate_insertion_cost(customer, route, insertion_position)
                            insertion_costs.append((cost, route_id, insertion_position))

                    # Sort insertion costs to find the best positions
                    insertion_costs.sort(key=lambda x: x[0])

                    # Calculate regret value
                    if len(insertion_costs) >= k:
                        regret_value = sum(insertion_cost[0] for insertion_cost in insertion_costs[1:k]) - insertion_costs[0][0]
                    else:
                        regret_value = float('-inf')  # Not enough routes to calculate regret

                    # Update customer with the highest regret value and insertion details
                    if regret_value > highest_regret_value:
                        highest_regret_value = regret_value
                        best_customer = customer
                        best_insertion_details = insertion_costs[0] if insertion_costs else None

                # Insert the best customer into its best position
                if best_customer is not None and best_insertion_details is not None:
                    insertion_cost, route_id, insertion_position = best_insertion_details
                    temp_params = self.insertion_cache[(best_customer.id, id(_solution[route_id].nodes), insertion_position)]
                    # temp_params = [insertion_cost, temp_t_i, temp_z_i, temp_d_i, temp_position, temp_FS_i]
                    _solution[route_id].insert_node_at(best_customer, position=insertion_position, update=temp_params[1:])
                    removed_customers.remove(best_customer)
                    # Recalculate route cost:
                    _solution[route_id].assign_best_vehicle()

                    # Clear the cache since the solution changed
                    self.insertion_cache.clear()
                else:
                    solution.create_new_route(removed_customers[0])
                    removed_customers.remove(removed_customers[0])

            return solution
        return Operator(operator, name=str(op_name))




