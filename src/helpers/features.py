from collections import deque
import statistics
import resources.global_context as global_context

# Class to get engineered features
class EngFeatures:
    def __init__(self):
        self.problem_instance = global_context.global_instance
        self.vehicles = self.problem_instance.vehicles

    def recent_acceptances(self, window_size: int):
        return deque(maxlen=window_size)

    def route_imbalance(self, solution):
        route_lengths = []
        for route in solution.routes:
            route_lengths.append(len(route.nodes))

        return statistics.pstdev(route_lengths)

    def capacity_utilization(self, solution):
        route_utilization = []
        for route in solution.routes:
            route_utilization.append(route.demand()/self.vehicles[route.vehicle].capacity)

        return statistics.mean(route_utilization)