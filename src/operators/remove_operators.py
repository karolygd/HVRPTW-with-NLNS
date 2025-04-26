import random
from resources.datatypes.route import Route
import resources.global_context as global_context
from resources.datatypes.operator import Operator
from resources.datatypes.solution import Solution

class RemoveOperators:
    def __init__(self):
        self.problem_instance = global_context.global_instance
        self.vertices = self.problem_instance.vertices
        self.edges = self.problem_instance.edges

        self.max_distance = max(edge.distance for edge in self.edges.values())
        self.max_demand_diff = max(vertex.demand for vertex in self.vertices) - min(vertex.demand for vertex in self.vertices)

        earliest_latest_times = [(v.earliest_start, v.latest_start) for v in self.vertices]
        min_earliest_start = float("inf")
        max_earliest_start = float("-inf")
        min_latest_start = float("inf")
        max_latest_start = float("-inf")

        for earliest, latest in earliest_latest_times:
            min_earliest_start = min(min_earliest_start, earliest)
            max_earliest_start = max(max_earliest_start, earliest)
            min_latest_start = min(min_latest_start, latest)
            max_latest_start = max(max_latest_start, latest)

        self.max_earliest_diff = max_earliest_start - min_earliest_start
        self.max_latest_diff = max_latest_start - max_earliest_start

    @staticmethod
    def _map_customers_to_route(solution: list[Route]):
        # 1. Create a mapping from customer ID to the route they belong to
        node_to_route = {}
        for route in solution:
            for node in route.nodes:
                if node.id != 0:  # Exclude the depot
                    node_to_route[node] = route

        return node_to_route

    def _relatedness_score(self, seed_customer, all_customers, solution: list[Route]):
        # Weighted sum of terms (weights can be adjusted)
        weight_distance = 1.0
        weight_time = 1.0
        weight_demand = 1.0
        weight_earliest_time = 1.0
        weight_latest_time = 1.0

        scores = {}
        all_arrival_times = {}
        for route in solution:
            route_arrival_times = route.nodes_arrival_times()
            all_arrival_times.update(route_arrival_times)
        max_start_diff = max(all_arrival_times.values()) - min(all_arrival_times.values())

        for customer in all_customers:
            if customer != seed_customer:
                # All terms are normalized
                distance_ij = self.edges[(seed_customer.id,customer.id)].distance / self.max_distance
                start_times_ij = abs(all_arrival_times[seed_customer.id] - all_arrival_times[customer.id]) / max_start_diff
                demand_ij = abs(self.vertices[seed_customer.id].demand - self.vertices[customer.id].demand) / self.max_demand_diff
                earliest_time_ij = abs(self.vertices[customer.id].earliest_start - self.vertices[seed_customer.id].earliest_start) / self.max_earliest_diff
                latest_time_ij = abs(self.vertices[customer.id].latest_start - self.vertices[seed_customer.id].latest_start) / self.max_latest_diff

                score = (
                        weight_distance * distance_ij +
                        weight_time * start_times_ij +
                        weight_demand * demand_ij +
                        weight_earliest_time * earliest_time_ij +
                        weight_latest_time * latest_time_ij
                )
                scores[customer] = score

        return scores

    def random_customers(self):
        """
        Randomly selects customers to remove from their respective routes.
        """

        def operator(solution: Solution, num_customers_to_remove: int):
            """
            :param solution: list of routes
            :param num_customers_to_remove: Number of customers to remove.
            :return nodes_to_remove: list of nodes that were removed from the solution.
            """
            # Select which customers to remove
            all_nodes_to_route = self._map_customers_to_route(solution.routes)
            all_nodes = list(all_nodes_to_route.keys())
            nodes_to_remove = random.sample(all_nodes, min(num_customers_to_remove, len(all_nodes)))

            # Remove selected customers from their respective routes
            for node in nodes_to_remove:
                all_nodes_to_route[node].remove_node(node)
                all_nodes_to_route[node].assign_best_vehicle()

            return nodes_to_remove

        return Operator(operator, name=1)

    def randomly_selected_sequence_within_concatenated_routes(self):
        """
        Removes a randomly selected sequence of customers from concatenated routes.
        """
        def operator(solution: Solution, num_customers_to_remove: int):
            """
            :param solution: list of routes
            :param num_customers_to_remove: Number of customers to remove.
            :return nodes_to_remove: list of nodes that were removed from the solution.
            """
            all_nodes_to_route = self._map_customers_to_route(solution.routes)
            concatenated_nodes = list(all_nodes_to_route.keys()) # nodes are in the order that the solution had

            # Randomly select a starting index for the sequence to remove.
            start_idx = random.randint(0, len(concatenated_nodes) - num_customers_to_remove)
            nodes_to_remove = concatenated_nodes[start_idx: start_idx + num_customers_to_remove]

            # Remove selected customers from their respective routes
            for node in nodes_to_remove:
                all_nodes_to_route[node].remove_node(node)
                all_nodes_to_route[node].assign_best_vehicle()

            return nodes_to_remove
        return Operator(operator, name=2)

    def a_posteriori_score_related_customers(self):
        """
        Removes a set of related customers from the current solution. The relatedness is calculated in terms of:
         distance between customers, service start time of customers, and customers' demand
        """
        def operator(solution: Solution, num_customers_to_remove: int):
            """
            :param solution: list of routes
            :param num_customers_to_remove: Number of customers to remove.
            :return nodes_to_remove: list of nodes that were removed from the solution.
            """
            all_nodes_to_route = self._map_customers_to_route(solution.routes)
            all_customers = list(all_nodes_to_route.keys())

            # Select a random seed customer
            seed_customer = random.choice(all_customers)

            # Calculate relatedness scores for all customers relative to the seed
            relatedness = self._relatedness_score(seed_customer, all_customers, solution.routes)

            # Sort customers by relatedness score (ascending) and select customers to remove
            sorted_customers = sorted(relatedness.keys(), key=lambda x: relatedness[x])
            nodes_to_remove = sorted_customers[:num_customers_to_remove]

            # Remove selected customers from their respective routes
            for node in nodes_to_remove:
                all_nodes_to_route[node].remove_node(node)
                all_nodes_to_route[node].assign_best_vehicle()

            return nodes_to_remove
        return Operator(operator, name=3)

    def worst_cost_customers(self): #num_customers_to_remove: int
        """
        Removes customers with the highest removal cost.
        """
        def operator(solution: Solution, num_customers_to_remove: int):
            """
            :param solution: list of routes
            :param num_customers_to_remove: Number of customers to remove.
            :return nodes_to_remove: list of nodes that were removed from the solution.
            """
            all_nodes_to_route = self._map_customers_to_route(solution.routes)

            removal_costs = {}
            for route in solution.routes:
                for customer in route.nodes:
                    if customer.id != 0:  # Skip depot
                        # position = route.nodes.index(customer)
                        removal_costs[customer] = route.calculate_removal_cost(customer) # original_cost - route.cost

            # Sort customers by removal cost in descending order
            sorted_customers = sorted(removal_costs.keys(), key=lambda c: removal_costs[c], reverse=True)
            # print("sorted customers: ", sorted_customers)

            # Remove selected customers from their respective routes
            nodes_to_remove = sorted_customers[:num_customers_to_remove]
            for node in nodes_to_remove:
                all_nodes_to_route[node].remove_node(node)
                all_nodes_to_route[node].assign_best_vehicle()

            return nodes_to_remove
        return Operator(operator, name=4)

    def random_route(self):
        """
        Removes one route that is randomly selected.
        """
        def operator(solution: Solution, num_customers_to_remove: int):
            """
            :param solution: Solution
            :param num_customers_to_remove: Number of customers to remove.
            :return: nodes_to_remove: list of nodes that were removed from the solution.
            """
            nodes_to_remove = []
            remaining_to_remove = num_customers_to_remove

            # 1. Remove entire routes at random
            while remaining_to_remove > 0:
                route_to_remove = random.choice(solution.routes)
                #print("- debug: route_to_remove", route_to_remove)
                route_nodes = route_to_remove.nodes
                #print("- debug: remaining_to_remove", remaining_to_remove)
                #print("- debug: node length", len(route_nodes[1:-1]))
                # Check if removing this route would exceed the removal target
                number_of_nodes_in_route = len(route_nodes[1:-1])
                if number_of_nodes_in_route <= remaining_to_remove:
                    #print(" * removing route * ")
                    # Remove all nodes from the route
                    # for node in route_nodes[1:-1]: # [1:-1] to exclude depots
                    #     route_to_remove.remove_node(node)
                    #     nodes_to_remove.append(node)
                    nodes_to_remove += route_nodes[1:-1]
                    solution.routes.remove(route_to_remove)

                    # # Remove the route from the solution
                    # solution.routes.remove(route_to_remove)

                    remaining_to_remove -= number_of_nodes_in_route
                else:
                    # If the entire route cannot be removed, break the loop
                    break

            # Apply score related removal for the remaining number of customers
            if remaining_to_remove > 0:
                #print("- debug: * shaw removal * ")
                sequential_removal_operator = self.randomly_selected_sequence_within_concatenated_routes()
                additional_nodes_to_remove = sequential_removal_operator.func(solution, remaining_to_remove)
                #print("- debug: additional_nodes_to_remove", additional_nodes_to_remove)
                # Add these nodes to the nodes_to_remove
                nodes_to_remove.extend(additional_nodes_to_remove)

            return nodes_to_remove
        return Operator(operator, name=5)