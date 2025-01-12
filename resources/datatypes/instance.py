from dataclasses import dataclass

ArcID = tuple[int, int]

@dataclass
class Vertex:
    vertex_id: int
    demand: int
    earliest_start: float
    latest_start: float
    service_time: float

@dataclass
class Edge:
    distance: float

@dataclass(frozen=True)
class VehicleType:
    id: str
    cost: float
    capacity: float

@dataclass
class Instance:
    name: str
    vehicles: list[VehicleType]
    vertices: list[Vertex]
    edges: dict[ArcID, Edge]

