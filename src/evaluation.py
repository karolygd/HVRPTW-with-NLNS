# This class evaluates different aspects of the route:
# Duration of a route, feasibility (according to the constraints modeled), total distance of a route,
# total duration and cost of operations, etc.

# For now, code it for individual routes, later maybe will have to be for the entire solution.
# Or create two classes: Evaluation_route, Evaluation_solution
from resources.data import Data
import random

class EvaluateRoute:
    def __init__(self, route):
        if len(route) == 0:
            raise ValueError("Error: valid route was not provided")
        else:
            # Defining data elements:
            self.problem_instance = Data().get_instance("C1_2_1.txt") # TODO: find a way to define the problem instance globally in main and that it is taken from there
            self.demand = self.problem_instance['demand']
            self.distance_edges = self.problem_instance['edge_weight']
            self.travel_time = self.problem_instance['edge_weight'] # average speed of a truck?
            self.service_time = self.problem_instance['service_time']
            self.earliest_arrival = self.problem_instance['earliest_arrival']
            self.latest_arrival = self.problem_instance['latest_arrival']

            # Defining Route elements
            self.route = route

            self.vehicles = Data().get_vehicle_data()
            self.max_vehicle_capacity = self.vehicles['capacity'].max()

    def total_demand(self):
        total_demand = 0.0
        for node in self.route:
            if self.demand[node] < 0:
                raise ValueError(f"Error: Demand from node {node} is: {self.demand[node]}. No valid distance")
            else:
                total_demand += self.demand[node]
        return total_demand

    def total_distance(self):
        total_distance = 0.0
        for i in range(0, len(self.route)-1):
            node_i = self.route[i]
            node_j = self.route[i+1]

            distance_ij = self.distance_edges[node_i][node_j]
            if distance_ij < 0:
                raise ValueError(f"Error: Distance from node {node_i} to node {node_j} is: {distance_ij}. No valid distance")
            else:
                total_distance += distance_ij
        return total_distance

    def calculate_insertion_cost(self, node_to_insert, position):
        # Identify the nodes before and after the insertion position
        prev_node = self.route[position - 1]
        next_node = self.route[position]

        # Compute the cost change (delta) from the insertion
        delta = (self.distance_edges[prev_node][node_to_insert] + self.distance_edges[node_to_insert][next_node]
                 - self.distance_edges[prev_node][next_node])
        return delta

    def calculate_removal_cost(self, position):
        # Identify the nodes before and after the node to be removed
        prev_node = self.route[position - 1]
        node_to_remove = self.route[position]
        next_node = self.route[position + 1]

        # Compute the cost change (delta) from the removal
        delta = self.distance_edges[prev_node][next_node] - (
                    self.distance_edges[prev_node][node_to_remove] + self.distance_edges[node_to_remove][next_node])
        return delta

    def get_arrival_times(self) -> dict:
        """
        :return: Returns a list of the arrival time to each customer in the route, excludes leaving the depot at time 0
        """
        arrival_at_i = 0
        arrival_times = {}
        for k in range(1, 1 + len(self.route[1:])):
            node_k = self.route[k]
            previous_node = self.route[k - 1]
            # Either the car arrives at the earliest possible arrival time, or at the time it takes to travel from depot to node, whichever is greater
            arrival_at_i = float(max(self.earliest_arrival[node_k],
                               arrival_at_i + self.travel_time[previous_node][node_k] + self.service_time[
                                   previous_node]))
            arrival_times[node_k] = arrival_at_i

        return arrival_times

    def route_total_duration(self) -> float:
        """
        Calculates the total duration of a route (includes service time) - assumes time windows are already feasible
        :return: duration as float
        """
        arrival_times = self.get_arrival_times()
        total_duration = list(arrival_times.values())[-1]

        return total_duration

    def time_window_feasibility(self) -> bool:
        arrival_at_i = 0
        for k in range(1, 1 + len(self.route[1:])):
            node_k = self.route[k]
            previous_node = self.route[k - 1]
            # Either the car arrives at the earliest possible arrival time, or at the time it takes to travel from depot to node, whichever is greater
            arrival_at_i = max(self.earliest_arrival[node_k],
                               arrival_at_i + self.travel_time[previous_node][node_k] + self.service_time[
                                   previous_node])

            if arrival_at_i > self.latest_arrival[node_k]:
                return False
        return True

    def is_feasible(self):
        if self.time_window_feasibility() and self.total_demand() <= self.max_vehicle_capacity:
            return True
        else:
            return False

    def assign_random_vehicle_to_route(self):
        """
        Assigns a random vehicle to the route, taking care that the vehicle load capacity is not exceeded.
        :return:
        """
        # select a random car from the ones which capacity is more or enough to satisfy the route demand
        route_demand = self.total_demand()
        feasible_vehicles = self.vehicles[self.vehicles['capacity'] >= route_demand]['vehicle_id'].tolist()
        return random.choice(feasible_vehicles)

    # def assign_best_cost_vehicle_to_route(self):



class EvaluateMerge:
    def __init__(self, route_i, route_j):
        # Check that the routes begin and end at the depot, and that they are not empty:
        if (route_i is None or len(route_i) <= 2) or (route_i[0] != 0 or route_i[-1] != 0):
            print("Error: Not a valid route_1")
            exit()
        else:
            self.route_i = route_i
        if (route_j is None or len(route_j) <= 2) or (route_j[0] != 0 or route_j[-1] != 0):
            print("Error: Not a valid route_2")
            exit()
        else:
            self.route_j = route_j
        # Get information form the problem instance:
        self.problem_instance = Data().get_instance("C1_2_1.txt")  # TODO: find a way to define the problem instance globally in main and that it is taken from there
        self.travel_time = self.problem_instance['edge_weight'] # TODO: add * car speed
        self.service_time = self.problem_instance['service_time']
        self.earliest_arrival = self.problem_instance['earliest_arrival']
        self.latest_arrival = self.problem_instance['latest_arrival']

    def valid_time_windows(self)-> bool:
        """
        Checks if two routes (starting and ending at depot) can be merged based on their time windows.
        route_i: [0, ..., last_node_1, 0]
        route_j: [0, first_node_2, ..., 0]
        :return: bool
        """
        last_node_i = self.route_i[-2]  # Last customer in route_1
        first_node_j = self.route_j[1]  # First customer in route_2

        # 1. Calculate the arrival time at the last node of route_i:
        arrival_at_i = 0
        for k in range(1, 1+len(self.route_i[1:-1])):
            node_k = self.route_i[k]
            previous_node = self.route_i[k - 1]
            # Either the car arrives at the earliest possible arrival time, or at the time it takes to travel from depot to node, whichever is greater
            arrival_at_i =  max(self.earliest_arrival[node_k],
                            arrival_at_i + self.travel_time[previous_node][node_k] + self.service_time[previous_node])

        departure_from_i = arrival_at_i + self.service_time[last_node_i]
        arrival_at_j = departure_from_i + self.travel_time[last_node_i][first_node_j]
        # 2. Check that the arrival time at the new node respects the time window boundaries:
        #   If the time of arrival at the first_node_j is earlier than the earliest possible time, or later than the latest possible time, cannot be merged
        if arrival_at_j < self.earliest_arrival[first_node_j] or arrival_at_j > self.latest_arrival[first_node_j]:
            return False

        # 3. Check that the new propagated arrival times are within each node time window of route_j, includes the feasibility of returning to the depot
        arrival_at_j = max(arrival_at_j, self.earliest_arrival[first_node_j])
        for k in range(2, 2+len(self.route_j[2:])):
            node_k = self.route_j[k]
            previous_node = self.route_j[k-1]
            arrival_at_j =  max(self.earliest_arrival[node_k],
                            arrival_at_j + self.travel_time[previous_node][node_k] + self.service_time[previous_node])
            if arrival_at_j > self.latest_arrival[node_k]:
                return False
        return True