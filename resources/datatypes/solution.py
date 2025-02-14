from copy import deepcopy
from dataclasses import dataclass, field
from resources.datatypes.route import Route
from resources.datatypes.node import Node

@dataclass
class Solution:
    """
    Class to keep track of a solution
    """
    routes: list[Route]
    cost: float = field(default=None, init=False)

    def create_new_route(self, node:Node):
        # get new id for route
        ids = set([route.id for route in self.routes])
        route_id = 0
        while route_id in ids:
            route_id+=1

        # need to do two different depots for information update later:
        depot_start = Node(id=0, t_i=0.0, z_i=0.0, d_i=0.0, route_id=route_id, position=0, predecessor_node=0, successor_node=0)
        depot_end = Node(id=0, t_i=0.0, z_i=0.0, d_i=0.0, route_id=route_id, position=1, predecessor_node=0, successor_node=0)
        route = Route(nodes=[depot_start, depot_end], id=route_id)
        route.insert_node_at(node_to_insert=node, position=1)

        # assign vehicle and update cost:
        route.assign_best_vehicle()
        self.routes.append(route)

    def apply_destroy_operator(self, operator, num_customers_to_remove:int):
        removed_customers = operator.func(self, num_customers_to_remove)
        return removed_customers

    def apply_insert_operator(self, operator, removed_customers):
        operator.func(self, removed_customers)
        return Solution

    def get_cost(self):
        all_routes_cost = 0
        for route in self.routes:
            all_routes_cost += route.cost
        return all_routes_cost

    def get_distance(self):
        all_routes_distance = 0
        for route in self.routes:
            all_routes_distance += route.total_distance()
        return all_routes_distance

    def copy(self):
        return deepcopy(Solution(self.routes))

    def __hash__(self):
        return self.get_hash()

    def get_hash(self):
        out = []
        for route in self.routes:
            out.extend(route.nodes)
            out.append(route.vehicle) # add vehicle in hash in case it changes
        return hash(tuple(out))



