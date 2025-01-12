import random
from resources.datatypes.route import Route
import resources.global_context as global_context
from resources.datatypes.operator import Operator

class RemoveOperators:
    def __init__(self):
        self.problem_instance = global_context.global_instance
        self.vertices = self.problem_instance.vertices
        self.edges = self.problem_instance.edges

        self.max_distance = max(edge.distance for edge in self.edges.values())
        self.max_demand_diff = max(vertex.demand for vertex in self.vertices) - min(vertex.demand for vertex in self.vertices)

    @staticmethod
    def _map_customers_to_route(solution: list[Route]):
        # 1. Create a mapping from customer ID to the route they belong to
        node_to_route = {}
        for route in solution:
            for node in route.nodes:
                if node != 0:  # Exclude the depot
                    node_to_route[node] = route

        return node_to_route

    def _relatedness_score(self, seed_customer, all_customers, solution: list[Route]):
        # Weighted sum of terms (weights can be adjusted)
        weight_distance = 1.0
        weight_time = 2.0
        weight_demand = 1.0

        scores = {}
        all_arrival_times = {}
        for route in solution:
            route_arrival_times = route.nodes_arrival_times()
            all_arrival_times.update(route_arrival_times)
        max_start_diff = max(all_arrival_times.values()) - min(all_arrival_times.values())

        for customer in all_customers:
            if customer != seed_customer:
                # All terms are normalized
                distance_ij = self.edges[(seed_customer,customer)].distance / self.max_distance
                start_times_ij = abs(all_arrival_times[seed_customer] - all_arrival_times[customer]) / max_start_diff
                demand_ij = abs(self.vertices[seed_customer].demand - self.vertices[customer].demand) / self.max_demand_diff

                score = (
                        weight_distance * distance_ij +
                        weight_time * start_times_ij +
                        weight_demand * demand_ij
                )
                scores[customer] = score

        return scores

    def random_customers(self): #num_customers_to_remove: int
        """
        Randomly selects customers to remove from their respective routes.
        :param num_customers_to_remove: Number of customers to remove.
        :return nodes_to_remove: list of nodes that were removed from the solution.
        """

        def operator(solution: list[Route], num_customers_to_remove: int):
            # Select which customers to remove
            all_nodes_to_route = self._map_customers_to_route(solution)
            all_nodes = list(all_nodes_to_route.keys())
            nodes_to_remove = random.sample(all_nodes, min(num_customers_to_remove, len(all_nodes)))

            # Remove selected customers from their respective routes
            for node in nodes_to_remove:
                all_nodes_to_route[node].cost -= all_nodes_to_route[node].calculate_removal_cost(node)
                all_nodes_to_route[node].remove_node(node)
            return nodes_to_remove

        return Operator(operator, name="random_customers")

    def randomly_selected_sequence_within_concatenated_routes(self):
        """
        Removes a randomly selected sequence of customers from concatenated routes.
        :param num_customers_to_remove: Number of customers to remove.
        :return nodes_to_remove: list of nodes that were removed from the solution.
        """
        def operator(solution: list[Route], num_customers_to_remove: int):
            all_nodes_to_route = self._map_customers_to_route(solution)
            concatenated_nodes = list(all_nodes_to_route.keys()) # nodes are in the order that the solution had

            # Randomly select a starting index for the sequence to remove.
            start_idx = random.randint(0, len(concatenated_nodes) - num_customers_to_remove)
            nodes_to_remove = concatenated_nodes[start_idx: start_idx + num_customers_to_remove]

            # Remove selected customers from their respective routes
            for node in nodes_to_remove:
                all_nodes_to_route[node].cost -= all_nodes_to_route[node].calculate_removal_cost(node)
                all_nodes_to_route[node].remove_node(node)

            return nodes_to_remove
        return Operator(operator, name="randomly_selected_sequence_within_concatenated_routes")

    def a_posteriori_score_related_customers(self):
        """
        Removes a set of related customers from the current solution. The relatedness is calculated in terms of:
         distance between customers, service start time of customers, and customers' demand
        :param num_customers_to_remove: Number of customers to remove.
        :return: nodes_to_remove: list of nodes that were removed from the solution.
        """
        def operator(solution: list[Route], num_customers_to_remove: int):
            all_nodes_to_route = self._map_customers_to_route(solution)
            all_customers = list(all_nodes_to_route.keys())

            # Select a random seed customer
            seed_customer = random.choice(all_customers)
            # print("seed customer: ", seed_customer)

            # Calculate relatedness scores for all customers relative to the seed
            relatedness = self._relatedness_score(seed_customer, all_customers, solution)
            # print("relatedness: ", relatedness)

            # Sort customers by relatedness score (ascending) and select customers to remove
            sorted_customers = sorted(relatedness.keys(), key=lambda x: relatedness[x])
            nodes_to_remove = sorted_customers[:num_customers_to_remove]
            # print("sorted relatedness: ", sorted_customers)

            # Remove selected customers from their respective routes
            for node in nodes_to_remove:
                all_nodes_to_route[node].cost -= all_nodes_to_route[node].calculate_removal_cost(node)
                all_nodes_to_route[node].remove_node(node)
            return nodes_to_remove
        return Operator(operator, name="a_posteriori_score_related_customers")

    def worst_cost_customers(self): #num_customers_to_remove: int
        """
        Removes customers with the highest removal cost.
        :param num_customers_to_remove: Number of customers to remove.
        :return: nodes_to_remove: list of nodes that were removed from the solution.
        """
        def operator(solution: list[Route], num_customers_to_remove: int):
            all_nodes_to_route = self._map_customers_to_route(solution)

            removal_costs = {}
            for route in solution:
                for customer in route.nodes:
                    if customer != 0:  # Skip depot
                        # position = route.nodes.index(customer)
                        removal_costs[customer] = route.calculate_removal_cost(customer) # original_cost - route.cost

            # Sort customers by removal cost in descending order
            sorted_customers = sorted(removal_costs.keys(), key=lambda c: removal_costs[c], reverse=True)
            # print("sorted customers: ", sorted_customers)

            # Remove selected customers from their respective routes
            nodes_to_remove = sorted_customers[:num_customers_to_remove]
            for node in nodes_to_remove:
                all_nodes_to_route[node].cost -= all_nodes_to_route[node].calculate_removal_cost(node)
                all_nodes_to_route[node].remove_node(node)
            return nodes_to_remove
        return Operator(operator, name="worst_cost_customers")

    def remove_route(self, solution: list[Route], num_routes_to_remove: int):
        pass