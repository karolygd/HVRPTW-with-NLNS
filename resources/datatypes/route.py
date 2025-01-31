from dataclasses import dataclass, field
from src.evaluation import EvaluateRoute

# From routingblocks documentation:
# Routes carry a globally unique modification timestamp which can be used to efficiently test
# two routes for equality: On each modification of the route, the modification timestamp is incremented,
# while copying a route preserves it’s timestamp. Hence, two routes with the same modification timestamp
# are guaranteed to be equal, although the converse does not necessarily apply.

# from datetime import datetime

@dataclass
class Route:
    """
    Class to keep track of a route
    """
    nodes: list[int] # TODO: change to node date type with REF
    vehicle: int = field(default=None, init=False)
    cost: float = field(default=None, init=False)

    def demand(self) -> float:
        return  EvaluateRoute(self.nodes).total_demand()

    def assign_vehicle(self, vehicle_id: int=None):
        """
        If the vehicle_id is not given, it will assign a random vehicle that suffices the route's demand.
        """
        if vehicle_id:
            self.vehicle = int(vehicle_id) # Assign user-specified vehicle
        else:
            self.vehicle = EvaluateRoute(self.nodes).assign_random_vehicle_to_route()

    def is_empty(self):
        # Checks if the route list is empty
        if not self.nodes:
            return True
        else:
            return False

    def clear(self):
        """
        Marks the route nodes as empty
        """
        self.nodes = []

    def remove_node(self, node_id: int):
        """
        Removes the specified node from the route if it exists.
        :param node_id: The ID of the node to remove.
        """
        if node_id in self.nodes:
            self.nodes.remove(node_id)
        else:
            raise ValueError(f"Node {node_id} not found in the route.")

    # TODO: check if this is used:
    def nodes_arrival_times(self):
        """
        :return: Returns a list of the arrival time to each customer in the route
        """
        return EvaluateRoute(self.nodes).get_arrival_times()

    def calculate_total_cost(self):
        """
        The cost can only be calculated when the vehicle has been assigned.
        """
        self.cost = EvaluateRoute(self.nodes).calculate_total_cost(self.vehicle) # TODO: substitute for a cost function - dependent on car?

    def calculate_insertion_cost(self, node_to_insert: int, position: int):
        return EvaluateRoute(self.nodes).calculate_insertion_cost(node_to_insert, position)

    def calculate_removal_cost(self, node: int):
        position = self.nodes.index(node)
        return EvaluateRoute(self.nodes).calculate_removal_cost(position)

    def insert_node_at(self, node_to_insert: int, position: int): # change to position
        """
        :param node_to_insert: Node to be inserted in the route
        :param position: position at which customer will be inserted
        """

        self.nodes.insert(position, node_to_insert)

    def is_feasible(self):
        if EvaluateRoute(self.nodes).is_feasible():
            return True
        else:
            return False