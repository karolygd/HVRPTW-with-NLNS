# This class evaluates different aspects of the route:
# Duration of a route, feasibility (according to the constraints modeled), total distance of a route,
# total duration and cost of operations, etc.

import resources.global_context as global_context
import random

class EvaluateRoute:
    def __init__(self, route):
        if len(route) == 0:
            raise ValueError("Error: valid route was not provided")
        else:
            # Defining data elements:
            self.problem_instance = global_context.global_instance
            self.vertices = self.problem_instance.vertices
            self.edges = self.problem_instance.edges
            self.vehicles = self.problem_instance.vehicles
            self.max_vehicle_capacity = max(vehicle.capacity for vehicle in self.vehicles)

            # Defining Route elements
            self.route = route

    def total_demand(self):
        return self.route[-1].z_i

    def total_distance(self):
        return self.route[-1].d_i

    def calculate_insertion_cost(self, node_to_insert, position):
        # Identify the nodes before and after the insertion position
        prev_node = self.route[position-1]
        next_node = self.route[position]

        # Compute the cost change (delta) from the insertion
        delta_distance = (self.edges[(prev_node.id,node_to_insert.id)].distance + self.edges[(node_to_insert.id,next_node.id)].distance
                 - self.edges[(prev_node.id,next_node.id)].distance)
        delta_demand = self.vertices[node_to_insert.id].demand + self.route[-1].z_i
        available_vehicles = [vehicle.id for vehicle in self.vehicles if vehicle.capacity >= delta_demand]
        # the vehicle with the lowest capacity is always cheaper in my vehicle datasets, and they are order by cost/capacity
        delta_vehicles = self.vehicles[available_vehicles[0]].cost - self.vehicles[self.route[-1].FS_i[0]].cost

        return delta_distance + delta_vehicles

    def evaluate_insertion(self, node_to_insert, position):
        """
        Evaluates if a node can be inserted in a route based on time windows and capacity constraints.
        If valid, updates accumulated distance, node arrival times (t_i), and accumulated demand (z_i) and returns the merged route.
        If not valid, it returns False.
        """

        try:
            # 1. Check capacity feasibility
            # total_demand = accumulated demand until last node + demand of node to insert
            total_demand = self.route[-1].z_i + self.vertices[node_to_insert.id].demand
            if total_demand > self.max_vehicle_capacity:
                return False, {}, {}, {}, {}, {}  # Capacity exceeds limit, merge is invalid

            # 2. Calculate new arrival times (store temporarily)
            predecessor_node = self.route[position - 1]  # node previous to insertion
            successor_node = self.route[position]
            route_id = successor_node.route_id

            temp_t_i = {}
            temp_z_i = {}
            temp_d_i = {}
            temp_position = {}
            temp_FS_i = {}

            # -- inserted node:
            arrival_at_node = max(self.vertices[node_to_insert.id].earliest_start,
                               predecessor_node.t_i  + self.vertices[predecessor_node.id].service_time +
                               self.edges[(predecessor_node.id, node_to_insert.id)].distance)
            if arrival_at_node > self.vertices[node_to_insert.id].latest_start:
                return False, {}, {}, {}, {}, {}  # Time window violated

            # -- successor node:
            arrival_at_suc = max(self.vertices[successor_node.id].earliest_start,
                                  arrival_at_node + self.vertices[node_to_insert.id].service_time +
                                  self.edges[(node_to_insert.id, successor_node.id)].distance)
            if arrival_at_suc > self.vertices[successor_node.id].latest_start:
                return False, {}, {}, {}, {}, {}  # Time window violated

            # Store temporary values instead of updating
            temp_t_i[node_to_insert.id] = arrival_at_node
            temp_z_i[node_to_insert.id] = predecessor_node.z_i + self.vertices[node_to_insert.id].demand
            temp_d_i[node_to_insert.id] = predecessor_node.d_i +  self.edges[(predecessor_node.id, node_to_insert.id)].distance
            temp_position[node_to_insert.id] = position
            temp_FS_i[node_to_insert.id] = [vehicle.id for vehicle in self.vehicles if vehicle.capacity >= temp_z_i[node_to_insert.id]]

            temp_t_i[successor_node.id] = arrival_at_suc
            temp_z_i[successor_node.id] = temp_z_i[node_to_insert.id] + self.vertices[successor_node.id].demand
            temp_d_i[successor_node.id] = temp_d_i[node_to_insert.id] + self.edges[(node_to_insert.id, successor_node.id)].distance
            temp_position[successor_node.id] = position + 1
            temp_FS_i[successor_node.id] = [vehicle.id for vehicle in self.vehicles if vehicle.capacity >= temp_z_i[successor_node.id]]

            # 3. Propagate arrival times across route_j
            if len(self.route) > 2:
                for node in self.route[position+1:]: # after the successor node onwards
                    # print(f"checking arrival time to node {node}, with previous node {node.predecessor_node}")
                    previous_node = node.predecessor_node
                    arrival_at_node = max(self.vertices[node.id].earliest_start,
                                       temp_t_i[previous_node] + self.edges[(previous_node, node.id)].distance +
                                       self.vertices[previous_node].service_time)
                    if arrival_at_node > self.vertices[node.id].latest_start:
                        # print(" - debug: arrival_at_node loop")
                        return False, {}, {}, {}, {}, {}  # Time window violated

                    temp_t_i[node.id] = arrival_at_node
                    temp_z_i[node.id] = temp_z_i[previous_node] + self.vertices[node.id].demand
                    temp_d_i[node.id] = temp_d_i[previous_node] + self.edges[(previous_node, node.id)].distance
                    temp_position[node.id] = temp_position[previous_node] + 1
                    temp_FS_i[node.id] = [vehicle.id for vehicle in self.vehicles if vehicle.capacity >= temp_z_i[node.id]]

            return True, temp_t_i, temp_z_i, temp_d_i, temp_position, temp_FS_i
        except Exception as e:
            print(e)
            print(f"debug 'evaluate insertion' insert {node_to_insert.id} in {self.route} at position {position}")
            if len(self.route) > 2:
                for node in self.route[position+1:]: # after the successor node onwards
                    print(f"checking arrival time to node {node}, with previous node {node.predecessor_node}")

    def calculate_removal_cost(self, position):
        # Identify the nodes before and after the node to be removed
        prev_node = self.route[position - 1]
        node_to_remove = self.route[position]
        next_node = self.route[position + 1]

        # Compute the cost change (delta) from the removal
        delta_distance = ((self.edges[(prev_node.id,node_to_remove.id)].distance + self.edges[(node_to_remove.id,next_node.id)].distance) -
                 self.edges[(prev_node.id,next_node.id)].distance)
        # but the past route "original" route might be able to suffice it's demand with less capacity
        delta_demand = self.route[-1].z_i - self.vertices[node_to_remove.id].demand
        available_vehicles = [vehicle.id for vehicle in self.vehicles if vehicle.capacity >= delta_demand]
        # the vehicle with the lowest capacity is always cheaper in my vehicle datasets, and they are order by cost/capacity
        delta_vehicles = self.vehicles[self.route[-1].FS_i[0]].cost - self.vehicles[available_vehicles[0]].cost
        return delta_distance + delta_vehicles

    def update_node_parameters_at_remove(self, node):
        """
        Updates node parameters when a node is removed from a route.
        :param node: (Node.id, Node.position)
        """
        start_update_position = node.position

        # 1. Update predecessor and successor nodes
        predecessor = self.route[node.position - 1]
        successor = self.route[node.position + 1]
        predecessor.successor_node = successor.id
        successor.predecessor_node = predecessor.id

        # 2. Remove node from route
        self.route.remove(node)
        # new parameters of node to remove:
        node.z_i = 0
        node.d_i = 0
        node.t_i = 0
        node.FS_i = []
        # node.route_id = 0 # keep to be able to print routes that changed
        node.position = 0
        node.predecessor_node = 0
        node.successor_node = 0

        # 3. Update rest of the parameters - starting with successor
        arrival_time = predecessor.t_i
        accumulated_distance = predecessor.d_i
        accumulated_demand = predecessor.z_i

        for current_node in self.route[start_update_position:]:
            current_node.position -= 1
            prev_node = self.route[current_node.position-1]
            accumulated_distance += self.edges[(prev_node.id, current_node.id)].distance
            arrival_time = max(self.vertices[current_node.id].earliest_start,
                               arrival_time + self.edges[(prev_node.id, current_node.id)].distance +
                               self.vertices[prev_node.id].service_time)
            accumulated_demand += self.vertices[current_node.id].demand
            current_node.t_i = arrival_time
            current_node.d_i = accumulated_distance
            current_node.z_i = accumulated_demand
            current_node.FS_i = [vehicle.id for vehicle in self.vehicles if vehicle.capacity >= accumulated_demand]

    def calculate_total_cost(self, vehicle_id: int):
        cost = self.total_distance() + self.vehicles[vehicle_id].cost
        return cost

    def get_arrival_times(self) -> dict:
        """
        :return: Returns a list of the arrival time to each customer in the route, excludes leaving the depot at time 0
        """
        arrival_times = {node.id: node.t_i for node in self.route[1:-1].nodes}
        return arrival_times

    def route_total_duration(self) -> float:
        """
        Calculates the total duration of a route (includes service time) - assumes time windows are already feasible
        :return: duration as float
        """
        return self.route.nodes[-1].t_i

    def time_window_feasibility(self) -> bool:
        arrival_at_i = 0
        for k in range(1, 1 + len(self.route[1:])):
            node_k = self.route[k].id
            previous_node = self.route[k - 1].id
            # Either the car arrives at the earliest possible arrival time, or at the time it takes to travel from depot to node, whichever is greater
            arrival_at_i = max(self.vertices[node_k].earliest_start,
                               arrival_at_i + self.edges[(previous_node,node_k)].distance + self.vertices[
                                   previous_node].service_time)

            if arrival_at_i > self.vertices[node_k].latest_start:
                return False
        return True

    # todo: evaluate if used:
    def is_feasible(self):
        if self.time_window_feasibility() and self.total_demand() <= self.max_vehicle_capacity:
            return True
        else:
            return False

    def set_list_of_available_vehicles(self):
        for node in self.route[1:]:
            node.FS_i = [vehicle.id for vehicle in self.vehicles if vehicle.capacity >= node.z_i]

    def assign_random_vehicle_to_route(self):
        """
        Assigns a random vehicle to the route, taking care that the vehicle load capacity is not exceeded.
        :return:
        """
        # select a random car from the ones which capacity is more or enough to satisfy the route demand
        route_demand = self.total_demand()
        feasible_vehicles = [vehicle.id for vehicle in self.vehicles if vehicle.capacity >= route_demand]
        return int(random.choice(feasible_vehicles))

    def assign_best_cost_vehicle_to_route(self):
        """
        Assigns the best cost vehicle to the route
        :return: vehicle type
        """
        available_vehicles = self.route[-1].FS_i
        # vehicle_cost_mapping = {vehicle: self.calculate_total_cost(vehicle_id=vehicle) for vehicle in available_vehicles}
        lowest_cost_vehicle = available_vehicles[0] # min(vehicle_cost_mapping, key=vehicle_cost_mapping.get)
        lowest_cost = self.calculate_total_cost(vehicle_id=lowest_cost_vehicle) # vehicle_cost_mapping[lowest_cost_vehicle]
        return lowest_cost_vehicle, lowest_cost

class EvaluateMerge:
    def __init__(self, route_i, route_j):
        # Check that the routes begin and end at the depot, and that they are not empty:
        if (route_i is None or len(route_i) <= 2) or (route_i[0].id != 0 or route_i[-1].id != 0):
            print("Error: Not a valid route_1")
            exit()
        else:
            self.route_i = route_i
        if (route_j is None or len(route_j) <= 2) or (route_j[0].id != 0 or route_j[-1].id != 0):
            print("Error: Not a valid route_2")
            exit()
        else:
            self.route_j = route_j
        # Get information form the problem instance:
        self.problem_instance = global_context.global_instance
        self.vertices = self.problem_instance.vertices
        self.edges = self.problem_instance.edges
        self.vehicles = self.problem_instance.vehicles
        self.capacity_limit = max(vehicle.capacity for vehicle in self.vehicles)

    def evaluate_and_merge_routes(self):
        """
        Evaluates if two routes can be merged based on time windows and capacity constraints.
        If valid, updates accumulated distance, node arrival times (t_i), and accumulated demand (z_i) and returns the merged route.
        If not valid, it returns False.
        """

        last_node_i = self.route_i[-2]  # Last customer in route_i
        first_node_j = self.route_j[1]  # First customer in route_j
        route_id = last_node_i.route_id

        # 1. Check capacity feasibility
        total_demand = self.route_i[-2].z_i + self.route_j[-2].z_i

        if total_demand > self.capacity_limit:
            return False  # Capacity exceeds limit, merge is invalid

        # 2. Calculate new arrival times (store temporarily)
        temp_t_i = {}
        temp_z_i = {}
        temp_d_i = {}
        temp_position = {}

        arrival_at_i = last_node_i.t_i
        departure_from_i = arrival_at_i + self.vertices[last_node_i.id].service_time

        arrival_at_j = max(self.vertices[first_node_j.id].earliest_start,
                           departure_from_i + self.edges[(last_node_i.id, first_node_j.id)].distance)


        if arrival_at_j > self.vertices[first_node_j.id].latest_start:
            return False  # Time window violated

        # Store temporary values instead of updating
        temp_t_i[first_node_j.id] = arrival_at_j
        temp_z_i[first_node_j.id] = last_node_i.z_i + self.vertices[first_node_j.id].demand
        temp_d_i[first_node_j.id] = last_node_i.d_i +  self.edges[(last_node_i.id, first_node_j.id)].distance
        temp_position[first_node_j.id] = last_node_i.position + 1

        # 3. Propagate arrival times across route_j
        for k in range(2, 2 + len(self.route_j[2:])):  # Skip depot at end
            node_k = self.route_j[k]
            previous_node = self.route_j[k - 1]

            arrival_at_j = max(self.vertices[node_k.id].earliest_start,
                               arrival_at_j + self.edges[(previous_node.id, node_k.id)].distance +
                               self.vertices[previous_node.id].service_time)

            if arrival_at_j > self.vertices[node_k.id].latest_start:
                return False  # Time window violated

            temp_t_i[node_k.id] = arrival_at_j
            temp_z_i[node_k.id] = temp_z_i[previous_node.id] + self.vertices[node_k.id].demand
            temp_d_i[node_k.id] = temp_d_i[previous_node.id] + self.edges[(previous_node.id, node_k.id)].distance
            temp_position[node_k.id] = last_node_i.position  + k

        # 4. Apply updates to node parameters only if the merge is feasible
        # since we append route_i to route_j, no need to change predecessors and successors only for the last node of route_i and first node of route_j
        last_node_i.successor_node = first_node_j.id
        first_node_j.predecessor_node = last_node_i.id
        for node in self.route_j[1:]:  # Skip first depot
            node.t_i = temp_t_i[node.id]
            node.z_i = temp_z_i[node.id]
            node.d_i = temp_d_i[node.id]
            node.route_id = route_id
            node.position = temp_position[node.id]
        # update depots successor and predecessor
        self.route_i[0].successor_node = self.route_i[1].id
        self.route_j[-1].predecessor_node = self.route_j[-2].id

        # Step 5: Merge routes
        merged_route = self.route_i[:-1] + self.route_j[1:]  # Remove depot at end of route_i and start of route_j
        return merged_route


