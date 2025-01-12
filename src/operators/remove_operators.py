import random
from resources.datatypes import Route
from resources.data import Data

class RemoveOperators:
    def __init__(self):
        self.problem_instance = Data().get_instance("C1_2_1.txt")
        self.demand = self.problem_instance['demand']
        self.distance_edges = self.problem_instance['edge_weight']

        self.max_distance = max(max(row) for row in self.distance_edges)
        self.max_demand_diff = max(self.demand) - min(self.demand)
        # not needed now but could potentially use to add a time_windows-based destroy operator:
        # self.travel_time = self.problem_instance['edge_weight']  # average speed of a truck?
        # self.service_time = self.problem_instance['service_time']
        # self.earliest_arrival = self.problem_instance['earliest_arrival']
        # self.latest_arrival = self.problem_instance['latest_arrival']

    # If _map_customers_to_route is only useful within the context of removing customers or other destroy operations, keep it in DestroyOperators.
    # If mapping customers to routes has a broader use (e.g., other algorithms or analyses need this mapping), consider moving it to a helper class or making it a static utility method unrelated to either class.
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
            route_arrival_times = route.nodes_arrival_times
            all_arrival_times.update(route_arrival_times)
        max_start_diff = max(all_arrival_times.values()) - min(all_arrival_times.values())

        for customer in all_customers:
            if customer != seed_customer:
                # All terms are normalized
                distance_ij = self.distance_edges[seed_customer][customer] / self.max_distance
                start_times_ij = abs(all_arrival_times[seed_customer] - all_arrival_times[customer]) / max_start_diff
                demand_ij = abs(self.demand[seed_customer] - self.demand[customer]) / self.max_demand_diff

                score = (
                        weight_distance * distance_ij +
                        weight_time * start_times_ij +
                        weight_demand * demand_ij
                )
                scores[customer] = score

        return scores

    def random_customers(self, solution: list[Route], num_customers_to_remove: int):
        """
        Randomly selects customers to remove from their respective routes.
        :param solution: List of Route objects representing the current solution.
        :param num_customers_to_remove: Number of customers to remove.
        :return nodes_to_remove: list of nodes that were removed from the solution.
        """
        # Select which customers to remove
        all_nodes_to_route = self._map_customers_to_route(solution)
        all_nodes = list(all_nodes_to_route.keys())
        nodes_to_remove = random.sample(all_nodes, min(num_customers_to_remove, len(all_nodes)))

        # Remove selected customers from their respective routes
        for node in nodes_to_remove:
            all_nodes_to_route[node].remove_node(node)

        return nodes_to_remove

    def randomly_selected_sequence_within_concatenated_routes(self, solution: list[Route], num_customers_to_remove: int):
        """
        Removes a randomly selected sequence of customers from concatenated routes.
        :param solution: List of Route objects representing the current solution.
        :param num_customers_to_remove: Number of customers to remove.
        :return nodes_to_remove: list of nodes that were removed from the solution.
        """
        all_nodes_to_route = self._map_customers_to_route(solution)
        concatenated_nodes = list(all_nodes_to_route.keys()) # nodes are in the order that the solution had

        # Randomly select a starting index for the sequence to remove.
        start_idx = random.randint(0, len(concatenated_nodes) - num_customers_to_remove)
        nodes_to_remove = concatenated_nodes[start_idx: start_idx + num_customers_to_remove]

        # Remove selected customers from their respective routes
        for node in nodes_to_remove:
            all_nodes_to_route[node].remove_node(node)

        return nodes_to_remove

    def a_posteriori_score_related_customers(self, solution: list[Route], num_customers_to_remove: int):
        """
        Removes a set of related customers from the current solution. The relatedness is calculated in terms of:
         distance between customers, service start time of customers, and customers' demand
        :param solution: List of Route objects representing the current solution.
        :param num_customers_to_remove: Number of customers to remove.
        :return: nodes_to_remove: list of nodes that were removed from the solution.
        """
        all_nodes_to_route = self._map_customers_to_route(solution)
        all_customers = list(all_nodes_to_route.keys())

        # Select a random seed customer
        seed_customer = 173 #random.choice(all_customers)
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
            all_nodes_to_route[node].remove_node(node)

        return nodes_to_remove

    def worst_cost_customers(self, solution: list[Route], num_customers_to_remove: int):
        """
        Removes customers with the highest removal cost.
        :param solution: List of Route objects representing the current solution.
        :param num_customers_to_remove: Number of customers to remove.
        :return: nodes_to_remove: list of nodes that were removed from the solution.
        """
        all_nodes_to_route = self._map_customers_to_route(solution)

        removal_costs = {}
        for route in solution:
            for customer in route.nodes:
                if customer != 0:  # Skip depot
                    # Temporarily remove the customer and calculate the cost
                    original_nodes = route.nodes[:]
                    original_cost = route.cost
                    route.remove_node(customer)
                    removal_costs[customer] = original_cost - route.cost
                    route.nodes = original_nodes  # Restore the original route

        # Sort customers by removal cost in descending order
        sorted_customers = sorted(removal_costs.keys(), key=lambda c: removal_costs[c], reverse=True)
        print("removal costs: ", removal_costs)
        print("sorted customers: ", sorted_customers)

        # Remove selected customers from their respective routes
        nodes_to_remove = sorted_customers[:num_customers_to_remove]
        for node in nodes_to_remove:
            all_nodes_to_route[node].remove_node(node)

        return nodes_to_remove