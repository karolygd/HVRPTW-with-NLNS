from dataclasses import dataclass, field

@dataclass
class Node:
    """
    Class to keep track of the node information:
    d_i =  accumulated distance until node i
    t_i = arrival time at node i,
    z_i = accumulated demand until node i
    FS_i = set of vehicle types that can satisfy the demand requirement on the route after visiting node
    """
    d_i: float
    t_i: float
    z_i: float
    FS_i: list[str] = field(default_factory=list, init=False)

    id: int
    route_id: int
    position: int
    predecessor_node: int
    successor_node: int

    def __hash__(self):
        return hash(self.id)  # Hash only the `id`, assuming it's unique