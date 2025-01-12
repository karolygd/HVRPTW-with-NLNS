import os
import vrplib
import pandas as pd
from resources.datatypes.instance import *

from itertools import product
# from pathlib import Path

class Data:
    def __init__(self, instance_name: str):
        self.base_dir = os.path.dirname(__file__)
        self.instance_name = instance_name
        self.solution_name = instance_name[:-3]+'.sol'
        self.vehicle_instance_name = "R1.csv" #instance_name[:-6]+'.csv'

    def get_instance(self):
        file_path_instance = os.path.join(self.base_dir, "instances/Vrp-Set-Solomon", self.instance_name)
        instance = vrplib.read_instance(file_path_instance, instance_format="solomon")
        # The instance path already calculates the edge distances using euclidean.
        # print(instance.keys()) --> ['name', 'vehicles', 'capacity', 'node_coord', 'demand', 'time_window', 'service_time', 'edge_weight']

        # --- Getting time window components to simplify step afterwards ---
        earliest_arrival = []
        latest_arrival = []
        for node in range(0, len(instance['demand'])):
            earliest_arrival.append(instance['time_window'][node][0])
            latest_arrival.append(instance['time_window'][node][1])

        instance['earliest_arrival'] = earliest_arrival
        instance['latest_arrival'] = latest_arrival
        return instance

    def get_solution(self, solution_name):
        file_path_solution = os.path.join(self.base_dir, "instances/Vrp-Set-Solomon", solution_name)
        solution = vrplib.read_solution(file_path_solution)  # only 1 solution format
        # print(solution)
        return solution

    def get_vehicle_data(self) -> pd.DataFrame:
        file_path_vehicle = os.path.join(self.base_dir, "instances/vehicles", self.vehicle_instance_name)
        df = pd.read_csv(file_path_vehicle)
        return df

def parse_problem_instance(instance_name: str, vehicle_cost_structure: str):
    # --- Get v information: ---
    vertices: list[Vertex] = []

    data = Data(instance_name)
    instance = data.get_instance()

    # Warning for when checking solutions: unlike the benchmark data, depot is customer 0 and not 1, last client is 100 and not 101.
    for i in range(0, len(instance['demand'])):
        v = Vertex(
            vertex_id=i,
            demand=int(instance["demand"][i]),
            earliest_start=int(instance["earliest_arrival"][i]),
            latest_start=int(instance["latest_arrival"][i]),
            service_time=int(instance["service_time"][i])
        )
        vertices.append(v)

    # --- Get edge information: ---
    edge_dict: dict[ArcID, Edge] = {
        (i.vertex_id, j.vertex_id): Edge(distance=float(instance["edge_weight"][i.vertex_id][j.vertex_id])) for i, j in product(vertices, repeat=2)
    }

    # --- Get vehicle information: ---

    if vehicle_cost_structure not in ['a', 'b', 'c']:
        raise ValueError('Invalid vehicle cost structure, can only be: a, b or c')

    df_v = data.get_vehicle_data()
    vehicles: list[VehicleType] = []
    # cost_structure = 'cost_')
    for index, row in df_v.iterrows():
        vehicle = VehicleType(
                id=row['vehicle_id'],
                cost=row['cost_'+vehicle_cost_structure],
                capacity=row['capacity'])
        vehicles.append(vehicle)

    return Instance(name= instance['name'], vertices=vertices, edges=edge_dict, vehicles=vehicles)
