from dataclasses import dataclass, field
from src.evaluation import EvaluateRoute
from resources.datatypes.node import Node

@dataclass
class Route:
    """
    Class to keep track of a route
    """
    id: int
    nodes: list[Node]
    vehicle: int = field(default=None, init=False)
    cost: float = field(default=None, init=False)
    distance: float = field(default=None, init=False)

    def demand(self) -> float:
        return  EvaluateRoute(self.nodes).total_demand()

    def total_distance(self) -> float:
        self.distance = EvaluateRoute(self.nodes).total_distance()
        return self.distance

    def assign_best_vehicle(self):
        """
        Assigns the best cost vehicle that suffices the route's demand.
        """
        self.id = self.nodes[-1].route_id
        self.vehicle, self.cost = EvaluateRoute(self.nodes).assign_best_cost_vehicle_to_route()

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

    def remove_node(self, node: Node):
        """
        Removes the specified node from the route if it exists. Updates all node information.
        :param node: node to be removed
        """
        if node in self.nodes:
            EvaluateRoute(self.nodes).update_node_parameters_at_remove(node)
        else:
            raise ValueError(f"Node {node} not found in the route.")

    def nodes_arrival_times(self):
        """
        :return: Returns a list of the arrival time to each customer in the route
        """
        arrival_times = {node.id: node.t_i for node in self.nodes[1:-1]}
        return arrival_times

    def set_available_vehicles(self):
        EvaluateRoute(self.nodes).set_list_of_available_vehicles()

    def calculate_total_cost(self):
        """
        The cost can only be calculated when the vehicle has been assigned.
        """
        self.cost = EvaluateRoute(self.nodes).calculate_total_cost(vehicle_id=self.vehicle)

    def calculate_insertion_cost(self, node_to_insert: Node, position: int):
        return EvaluateRoute(self.nodes).calculate_insertion_cost(node_to_insert, position)

    def calculate_removal_cost(self, node: Node):
        return EvaluateRoute(self.nodes).calculate_removal_cost(node.position)

    def insert_node_at(self, node_to_insert: Node, position: int, update: list = None): # change to position
        """
        :param node_to_insert: Node to be inserted in the route
        :param position: position at which customer will be inserted
        :param update: list of updates to apply to the node [temp_t_i, temp_z_i, temp_d_i, temp_position]
        """
        if not update:
            update = EvaluateRoute(self.nodes).evaluate_insertion(node_to_insert, position)[1:]
            #print("debug: update_params: ", update)

        self.nodes.insert(position, node_to_insert)
        route_id = self.id # self.nodes[-1].route_id
        # update nodes information
        prev_node = self.nodes[position - 1]
        suc_node = self.nodes[position + 1]
        node_to_insert.predecessor_node = prev_node.id
        node_to_insert.successor_node = suc_node.id
        prev_node.successor_node = node_to_insert.id
        suc_node.predecessor_node = node_to_insert.id

        temp_t_i = update[0]
        temp_z_i = update[1]
        temp_d_i = update[2]
        temp_position = update[3]
        temp_FS_i = update[4]
        for i, node in enumerate(self.nodes[position:]):
            node.t_i = temp_t_i[node.id]
            node.z_i = temp_z_i[node.id]
            node.d_i = temp_d_i[node.id]
            node.position = temp_position[node.id]
            node.route_id = route_id
            node.FS_i = temp_FS_i[node.id]

    def insertion_is_feasible(self, node_to_insert: Node, position: int):
        return EvaluateRoute(self.nodes).evaluate_insertion(node_to_insert, position)

    def is_feasible(self):
        if EvaluateRoute(self.nodes).is_feasible():
            return True
        else:
            return False

    def get_hash(self):
        out = []
        out.extend(self.nodes)
        return hash(tuple(out))

    def __hash__(self):
        return self.get_hash()