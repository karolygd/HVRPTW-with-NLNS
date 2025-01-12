import random
from resources.datatypes.route import Route
from resources.datatypes.operator import Operator

class InsertionOperators:
    def __init__(self):
        self.insertion_cache = {}

        # A dictionary to store callable insertion operators

    def _calculate_insertion_cost(self, customer: int, route: Route, position: int) -> float:
        """
        Calculate the insertion cost for a customer at a specific position in the route.
        If insertion is unfeasible, cost is infinite.
        Uses caching to avoid redundant computations.
        """
        cache_key = (customer, id(route.nodes), position)
        if cache_key in self.insertion_cache:
            return self.insertion_cache[cache_key]

        # Temporarily insert the customer to check feasibility
        # Todo: Do the is_feasible without having to insert the node before
        route.insert_node_at(customer, position)
        insertion_is_feasible = route.is_feasible()
        route.remove_node(customer)
        if insertion_is_feasible:
            insertion_cost = route.calculate_insertion_cost(node_to_insert=customer, position=position)
        else:
            insertion_cost = float('inf')  # Infeasible insertion

        # Cache the result
        self.insertion_cache[cache_key] = insertion_cost
        return insertion_cost

    def _select_best_insertion_position(self, solution:list[Route], customer:int):
        # For large instances, consider only evaluating a subset of routes (e.g., based on proximity to the customer).

        best_insertion_cost = float('inf')
        best_route_id = None
        best_insertion_position = None

        for route_id, route in enumerate(solution):
            for i in range(len(route.nodes) - 1):  # Possible insertion points
                # after_node = route.nodes[i]
                insertion_position = i + 1

                insertion_cost = self._calculate_insertion_cost(customer, route, insertion_position)
                if insertion_cost < best_insertion_cost:
                    best_insertion_cost = insertion_cost
                    best_route_id = route_id
                    best_insertion_position = insertion_position

        if best_route_id is None or best_insertion_position is None:
            raise ValueError(f"Customer {customer} could not be feasibly inserted into any route.")

        return best_route_id, best_insertion_position, best_insertion_cost

    def random_order_best_position(self):
        """
        Randomizes the order of the removed customers and inserts one by one in their best cost position in the solution.
        :param removed_customers: List of customers to be inserted.
        :return: Modifies the solution in place.
        """
        def operator(solution: list[Route], removed_customers:list[int]):
            # Randomize the order of the removed customers
            random.shuffle(removed_customers)

            for customer in removed_customers:
                route_id, insertion_position, insertion_cost= self._select_best_insertion_position(solution, customer)
                solution[route_id].insert_node_at(customer, position= insertion_position)
                # Recalculate route cost:
                solution[route_id].cost += insertion_cost

            # Clear the cache since the solution changed
            self.insertion_cache.clear()
            return solution
        return Operator(operator, name="random_order_best_position")

    def customer_with_highest_position_regret_best_position(self, k: int = 2):
        """
        Inserts customers based on the highest position regret value.
        :param removed_customers: List of customers to be inserted.
        :param k: Number of top insertion costs to consider for regret calculation (default is 2).
        :return: Modifies the solution in place.
        """
        op_name = "customer_with_highest_position_regret_" + str(k) + "_best_position"
        def operator(solution: list[Route], removed_customers:list[int]):
            while removed_customers:
                best_customer = None
                highest_regret_value = float('-inf')
                best_insertion_details = None

                for customer in removed_customers:
                    insertion_costs = []

                    # Evaluate all routes for the current customer
                    for route_id, route in enumerate(solution):
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
                    solution[route_id].insert_node_at(best_customer, insertion_position)
                    removed_customers.remove(best_customer)
                    # Recalculate route cost:
                    # print(f"node: {best_customer} insertion cost: {insertion_cost}")
                    solution[route_id].cost += insertion_cost

                    # Clear the cache since the solution changed
                    self.insertion_cache.clear()
                else:
                    raise ValueError("No feasible insertion found for remaining customers.")
        return Operator(operator, name=op_name)


    # what if I first calculate all the regret values and then insert everything according to that order:
    def customer_with_highest_position_regret_best_position_2(self, removed_customers: list[int], k: int = 2):
        """
        Inserts customers based on the highest position regret value.
        First calculates the regret values for all customers and sorts them in descending order.
        :param removed_customers: List of customers to be inserted.
        :param k: Number of top insertion costs to consider for regret calculation (default is 2).
        :return: Modifies the solution in place.
        """
        def operator(solution: list[Route]):
            customer_regret_values = []
            for customer in removed_customers:
                insertion_costs = []

                # Evaluate all routes for the current customer
                for route_id, route in enumerate(solution):
                    for i in range(len(route.nodes) - 1):  # Possible insertion points
                        insertion_position = i + 1
                        cost = self._calculate_insertion_cost(customer, route, insertion_position)
                        insertion_costs.append((cost, route_id, insertion_position))

                # Sort insertion costs to find the best positions
                insertion_costs.sort(key=lambda x: x[0])

                # Calculate regret value
                if len(insertion_costs) >= k:
                    regret_value = sum(insertion_cost[0] for insertion_cost in insertion_costs[1:k]) - insertion_costs[0][0]
                else:
                    regret_value = float('-inf')  # Not enough routes to calculate regret

                # Store the customer and its regret value
                if insertion_costs:
                    customer_regret_values.append({
                        "customer": customer,
                        "regret_value": regret_value,
                        "best_insertion": insertion_costs[0]
                    })

            # Sort customers by regret value in descending order
            customer_regret_values.sort(key=lambda x: x["regret_value"], reverse=True)

            for customer in customer_regret_values:
                route_id, insertion_position, insertion_cost = self._select_best_insertion_position(solution, customer["customer"])
                solution[route_id].insert_node_at(customer["customer"], position=insertion_position)
                # print(f"node: {customer} insertion cost: {insertion_cost}")
                # Recalculate route cost:
                solution[route_id].cost += insertion_cost

            # Clear the cache since the solution changed
            self.insertion_cache.clear()
        return Operator(operator, name="customer_with_highest_position_regret_best_position_2")



