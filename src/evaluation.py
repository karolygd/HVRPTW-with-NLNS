# This class evaluates different aspects of the route:
# Duration of a route, feasibility (according to the constraints modeled), total distance of a route,
# total duration and cost of operations, etc.

# For now, code it for individual routes, later maybe will have to be for the entire solution.
# Or create two classes: Evaluation_route, Evaluation_solution
from resources.data import Data

class Evaluation:
    def __init__(self, route):
        if route is None or len(route) == 0:
            print("valid route was not provided")
            exit()
        else:
            self.route = route
            self.problem_instance = Data().get_instance("C1_2_1.txt") # TODO: find a way to define the problem instance globally in main and that it is taken from there
            self.distance_edges = self.problem_instance['edge_weight']
            self.service_time = self.problem_instance['service_time']

    def total_distance(self):
        total_distance = 0.0
        for i in range(0, len(self.route)-1):
            node_i = self.route[i]
            node_j = self.route[i+1]

            distance_ij = self.distance_edges[node_i][node_j]
            if distance_ij < 0:
                print(f"Distance from node {node_i} to node {node_j} is: {distance_ij}. No valid distance")
                exit()
            else:
                total_distance += distance_ij
        return total_distance

    def route_duration(self):
        total_service_time = 0.0
        for i in range(0, len(self.route)):
            node_i = self.route[i]
            service_time_i = self.service_time[node_i]
            if service_time_i < 0:
                print(f"Service time from node {node_i} is: {service_time_i}. No valid time")
                exit()
            else:
                total_service_time += service_time_i
        total_duration = total_service_time # + self.total_distance()*car_velocity
        return total_duration

    def is_feasible(self):
        pass

route = [0, 38, 150, 22, 0]
td = Evaluation(route).total_distance()
rd = Evaluation(route).route_duration()
print(td)
print(rd)