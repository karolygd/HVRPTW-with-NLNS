import os
import vrplib

class Data:
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)

    def get_instance(self, instance_name):
        file_path_instance = os.path.join(self.base_dir, "instances", instance_name)
        instance = vrplib.read_instance(file_path_instance, instance_format="solomon")
        # The instance path already calculates the edge distances using euclidean.
        # TODO: for the time, I would need to transform the distance to time using the speed of the car?
        # Would it be then duration: travel_time + service_time?
        # print(instance.keys()) --> ['name', 'vehicles', 'capacity', 'node_coord', 'demand', 'time_window', 'service_time', 'edge_weight']
        return instance

    def get_solution(self, solution_name):
        file_path_solution = os.path.join(self.base_dir, "instances", solution_name)
        solution = vrplib.read_solution(file_path_solution)  # only 1 solution format
        # print(solution)
        return solution

    def get_vehicle_data(self):
        # here get data for all vehicles, for the start only one vehicle
        pass

instance= Data().get_instance("C1_2_1.txt")
# print(instance['edge_weight'][0][38] + instance['edge_weight'][38][150] + instance['edge_weight'][150][22] + instance['edge_weight'][22][0])