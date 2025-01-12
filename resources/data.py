import os
import vrplib
import pandas as pd

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
        earliest_arrival = []
        latest_arrival = []
        for node in range(0, len(instance['demand'])):
            earliest_arrival.append(instance['time_window'][node][0])
            latest_arrival.append(instance['time_window'][node][1])

        instance['earliest_arrival'] = earliest_arrival
        instance['latest_arrival'] = latest_arrival
        return instance

    def get_solution(self, solution_name):
        file_path_solution = os.path.join(self.base_dir, "instances", solution_name)
        solution = vrplib.read_solution(file_path_solution)  # only 1 solution format
        # print(solution)
        return solution

    def get_vehicle_data(self) -> pd.DataFrame:
        file_path_instance = os.path.join(self.base_dir, "instances", "vehicles.csv")
        df = pd.read_csv(file_path_instance)
        return df

# instance= Data().get_instance("C1_2_1.txt")
# print(instance)
# solution= Data().get_solution("C1_2_1.sol")