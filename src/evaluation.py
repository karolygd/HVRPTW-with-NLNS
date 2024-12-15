# This class evaluates different aspects of the route:
# Duration of a route, feasibility (according to the constraints modeled), total distance of a route,
# total duration and cost of operations, etc.

# For now, code it for individual routes, later maybe will have to be for the entire solution.
# Or create two classes: Evaluation_route, Evaluation_solution
from resources.data import Data

class EvaluateRoute:
    def __init__(self, route):
        if route is None or len(route) == 0:
            print("Error: valid route was not provided")
            exit()
        else:
            self.route = route
            self.problem_instance = Data().get_instance("C1_2_1.txt") # TODO: find a way to define the problem instance globally in main and that it is taken from there
            self.distance_edges = self.problem_instance['edge_weight']
            self.travel_time = self.problem_instance['edge_weight']
            self.service_time = self.problem_instance['service_time']
            self.earliest_arrival = self.problem_instance['earliest_arrival']
            self.latest_arrival = self.problem_instance['latest_arrival']

    def total_distance(self):
        total_distance = 0.0
        for i in range(0, len(self.route)-1):
            node_i = self.route[i]
            node_j = self.route[i+1]

            distance_ij = self.distance_edges[node_i][node_j]
            if distance_ij < 0:
                print(f"Error: Distance from node {node_i} to node {node_j} is: {distance_ij}. No valid distance")
                exit()
            else:
                total_distance += distance_ij
        return total_distance

    def route_total_duration(self):
        """
        Calculates the total duration of a route (includes service time)
        :return:
        """
        arrival_at_i = 0
        for k in range(1, 1 + len(self.route[1:])):
            node_k = self.route[k]
            previous_node = self.route[k - 1]
            # Either the car arrives at the earliest possible arrival time, or at the time it takes to travel from depot to node, whichever is greater
            arrival_at_i = max(self.earliest_arrival[node_k],
                               arrival_at_i + self.travel_time[previous_node][node_k] + self.service_time[
                                   previous_node])

        # # 2. Check that the arrival time at the new node respects the time window boundaries:
        # #   If the time of arrival at the first_node_j is earlier than the earliest possible time, or later than the latest possible time, cannot be merged
        # if arrival_at_j < self.earliest_arrival[first_node_j] or arrival_at_j > self.latest_arrival[first_node_j]:
        #     return False
        return arrival_at_i

    def is_feasible(self):
        pass

# route = [0, 38, 150, 22, 0]
# rd = Evaluation(route).route_duration()

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

# print(EvaluateRoute([0, 164, 66, 147, 160, 47, 91, 70, 0]).route_total_duration())
