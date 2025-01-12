from copy import deepcopy
from dataclasses import dataclass, field
from resources.datatypes.route import Route

@dataclass
class Solution:
    """
    Class to keep track of a solution
    """
    routes: list[Route]
    cost: float = field(default=None, init=False)
    # hash: int = field(default=None, init=True)

    def apply_destroy_operator(self, operator, num_customers_to_remove:int):
        """
        Applies a given operator.py to the solution.
        :param operator: class InsertOperators or RemoveOperators
        :return: removed_customers
        """
        removed_customers = operator.func(self.routes, num_customers_to_remove)
        # probably I can also update the costs here :)
        return removed_customers

    def apply_insert_operator(self, operator, removed_customers):
        operator.func(self.routes, removed_customers)
        return Solution
        # probably I can also update the costs here :)

    def get_cost(self):
        all_routes_cost = 0
        for route in self.routes:
            all_routes_cost += route.cost
        return all_routes_cost

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



