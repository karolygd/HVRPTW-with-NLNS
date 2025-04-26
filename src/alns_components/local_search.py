import resources.global_context as global_context

class LocalSearch:
    def __init__(self): #solution
        self.problem_instance = global_context.global_instance
        self.vertices = self.problem_instance.vertices
        self.edges = self.problem_instance.edges

        self.vehicles = self.problem_instance.vehicles
        self.max_vehicle_capacity = max(vehicle.capacity for vehicle in self.vehicles)

        #self.operator_used = 0

    def _order_by_lowest_distance(self, i, neighborhood):
        ordered_neighborhood = []
        for j in neighborhood:
            d_ij = self.edges[(i.id, j.id)].distance
            ordered_neighborhood.append((d_ij, j))
        ordered_neighborhood.sort(key=lambda x: x[0])
        return ordered_neighborhood

    def _time_window_feasibility(self, exchanged_route):
        arrival_at_i = exchanged_route[0].t_i
        for k, node in enumerate(exchanged_route):
            if k > 0:
                previous_node = exchanged_route[k-1].id
                arrival_at_i = max(self.vertices[node.id].earliest_start, arrival_at_i + self.edges[(previous_node,node.id)].distance
                                   + self.vertices[previous_node].service_time)
                if arrival_at_i > self.vertices[node.id].latest_start:
                    return False
        return True

    def relocate_intra_route(self):
        for route in self.routes:
            for i in route.nodes[1:-1]:
                _neighborhood = [j for j in route.nodes[1:-1] if i.id != j.id and j.id != i.successor_node and j.id != i.predecessor_node] # if j is successor of i, no change in delta
                neighborhood = self._order_by_lowest_distance(i, _neighborhood)
                for d_ij, j in neighborhood:
                    i_prev, i_next = i.predecessor_node, i.successor_node
                    j_prev, j_next = j.predecessor_node, j.successor_node
                    delta = ((self.edges[(i_prev, i_next)].distance + d_ij + self.edges[(i.id, j_next)].distance)
                    - (self.edges[(i_prev, i.id)].distance + self.edges[(i.id, i_next)].distance + self.edges[(j.id, j_next)].distance))
                    if delta < 0.0:
                        exchanged_route = [route.nodes[j.position]] + [i] + [node for node in route.nodes[j.position + 1:] if node != i]
                        if self._time_window_feasibility(exchanged_route):
                            #self.operator_used += 1
                            route.remove_node(i)
                            route.insert_node_at(node_to_insert=i, position=j.position+1, update=[])
                            route.assign_best_vehicle()

    def relocate_inter_route(self):
        for route_1 in self.routes:
            for i in route_1.nodes[1:-1]:  # Skip depot nodes
                i_earliest_arrival = self.vertices[i.id].earliest_start
                i_latest_arrival = self.vertices[i.id].latest_start
                # this neighborhood already checks for possible time windows
                _neighborhood = [j for route in self.routes if route.id != route_1.id for j in route.nodes[1:-1]
                                 if i_earliest_arrival <= j.t_i + self.vertices[j.id].service_time + self.edges[(j.id, i.id)].distance <= i_latest_arrival]
                neighborhood = self._order_by_lowest_distance(i, _neighborhood)
                #print(f"i: {i.id}, _neighborhood: {_neighborhood}, neighborhood: {neighborhood}")
                for d_ij, j in neighborhood:
                    route_2 = [route for route in self.solution.routes if route.id == j.route_id][0]
                    i_prev, i_next = i.predecessor_node, i.successor_node
                    j_next = j.successor_node

                    delta = ((self.edges[(i_prev, i_next)].distance + d_ij + self.edges[(i.id, j_next)].distance)
                             - (self.edges[(i_prev, i.id)].distance + self.edges[(i.id, i_next)].distance + self.edges[(j.id, j_next)].distance))
                    #print(f"delta: {delta}")
                    if delta < 0.0:
                        # print(f"delta <0 in relocate inter. i: {i}, j: {j}")
                        # simulate route change
                        exchanged_route = [route_2.nodes[j.position]] + [i] + route_2.nodes[j.position+1:]
                        #exchanged_route = [node.id for node in exchanged_route]
                        # Check feasibility (time windows & capacity)

                        if (self._time_window_feasibility(exchanged_route) and
                                route_2.demand() + self.vertices[i.id].demand <= self.max_vehicle_capacity):
                            #self.operator_used += 1
                            # apply move
                            route_1.remove_node(i)
                            route_2.insert_node_at(node_to_insert=i, position=j.position+1, update=[])
                            route_1.assign_best_vehicle()
                            route_2.assign_best_vehicle()
                            return  # First improvement → stop search

    def exchange(self):
        for route_1 in self.routes:
            for i in route_1.nodes[1:-1]:
                i_earliest_arrival = self.vertices[i.id].earliest_start
                i_latest_arrival = self.vertices[i.id].latest_start
                _neighborhood = [j for route in self.routes if route.id != route_1.id for j in route.nodes[1:-1]
                                 if i_earliest_arrival <= route.nodes[j.position-1].t_i + self.vertices[route.nodes[j.position-1].id].service_time +
                                 self.edges[(route.nodes[j.position-1].id, i.id)].distance <= i_latest_arrival] #todo: to do neighborhood check here, I would need to do it with the predecessor of j and predecessor of i
                neighborhood = self._order_by_lowest_distance(i, _neighborhood)
                #print(f"i: {i.id}")
                #print(f"_neighborhood: {_neighborhood}")
                #print(f"neighborhood: {neighborhood}")
                for d_ij, j in neighborhood:
                    route_2 = [route for route in self.solution.routes if route.id == j.route_id][0]
                    # Get predecessors and successors
                    i_prev, i_next = i.predecessor_node, i.successor_node
                    j_prev, j_next = j.predecessor_node, j.successor_node

                    old_cost = (
                            self.edges[(i_prev, i.id)].distance +
                            self.edges[(i.id, i_next)].distance +
                            self.edges[(j_prev, j.id)].distance +
                            self.edges[(j.id, j_next)].distance
                    )
                    new_cost = (
                            self.edges[(i_prev, j.id)].distance +
                            self.edges[(j.id, i_next)].distance +
                            self.edges[(j_prev, i.id)].distance +
                            self.edges[(i.id, j_next)].distance
                    )
                    delta = new_cost - old_cost
                    #print(f"delta: {delta}")
                    # If the exchange improves the solution
                    if delta < 0.0:
                        # print(f"delta <0 in exchange. i: {i}, j: {j}")
                        # Simulate exchange
                        exchanged_route_1 = route_1.nodes[i.position-1:] + [j] + route_1.nodes[i.position + 1:]
                        exchanged_route_2 = route_2.nodes[j.position-1:] + [i] + route_2.nodes[j.position + 1:]
                        # print(f"exchanged_route_1: {exchanged_route_1}")
                        # print(f"exchanged_route_2: {exchanged_route_2}")
                        # Check feasibility (time windows & capacity)
                        route_1_new_demand = route_1.demand() - self.vertices[i.id].demand + self.vertices[j.id].demand
                        route_2_new_demand = route_2.demand() - self.vertices[j.id].demand + self.vertices[i.id].demand
                        if (self._time_window_feasibility(exchanged_route_2) and
                                self._time_window_feasibility(exchanged_route_1) and
                                route_1_new_demand <= self.max_vehicle_capacity and route_2_new_demand <= self.max_vehicle_capacity):
                            #self.operator_used += 1
                            # Calculate exchange positions before they get changed
                            position_i = i.position
                            position_j = j.position
                            # Apply exchange:
                            route_1.remove_node(i)
                            route_2.remove_node(j)
                            route_2.insert_node_at(node_to_insert=i, position=position_j, update=[])
                            route_1.insert_node_at(node_to_insert=j, position=position_i, update=[])

                            route_1.assign_best_vehicle()
                            route_2.assign_best_vehicle()
                            return  # First improvement → stop search

    def apply_local_search(self, solution):
        self.solution = solution
        self.routes = self.solution.routes

        self.relocate_intra_route()
        self.relocate_inter_route()
        self.exchange()


# def two_opt(self):
#     for route in self.routes:
#         for i in route.nodes[1:-1]:
#             _neighborhood = [j for j in route.nodes[1:-1] if i.id != j.id and j.id != i.successor_node and j.id != i.predecessor_node] # if j is successor of i, no change in delta
#             neighborhood = self._order_by_lowest_distance(i, _neighborhood)
#             #print(i.id, neighborhood)
#             for d_ij, j in neighborhood:
#                 delta = ((d_ij + self.edges[(i.successor_node, j.successor_node)].distance) -
#                          (self.edges[(i.id, i.successor_node)].distance + self.edges[(j.id, j.successor_node)].distance))
#                 #print(delta)
#                 if delta < 0.0:
#                     #print(f"delta <0 in 2-opt. i: {i}, j: {j}")
#                     exchanged_route = [route.nodes[i.position]] + route.nodes[j.position:i.position:-1] + route.nodes[j.position + 1:]
#                     #exchanged_route = [node.id for node in exchanged_route]
#                     # check if time windows remain feasible:
#                     if self._time_window_feasibility(exchanged_route):
#                         print("debugging 2-opt:")
#                         #print(f"i: {i}, j: {j}, exchanged_route: {exchanged_route}")
#                         # do 2-opt and terminate loop
#                         route.remove_node(j)
#                         i_successor = route.nodes[i.position + 1]
#                         route.remove_node(i_successor)
#                         route.insert_node_at(j, position=i.position+1)
#                         route.insert_node_at(i_successor, position=j.position-1)
#
#                         route.assign_best_vehicle()
#                         #print("- debug: 2-opt done for route: ", route.nodes, "with delta: ", delta)
#                         return # First improvement → stop search