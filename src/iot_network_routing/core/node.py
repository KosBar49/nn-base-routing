"""
IoT Node implementation as a NetworkX graph view with 2D coordinates and communication capabilities.
"""

import random
import math
from typing import List, Dict, Optional, TYPE_CHECKING
import networkx as nx

if TYPE_CHECKING:
    from .network import IoTNetwork


class IoTNode:
    """
    Represents an IoT node as a view over NetworkX graph data.
    Uses IEEE EUI-64 identifier format.
    """
    
    def __init__(self, graph: nx.Graph, eui64: str):
        """
        Initialize IoT node as a view over NetworkX graph data.
        
        Args:
            graph: NetworkX graph containing this node
            eui64: IEEE EUI-64 identifier for this node
        """
        if eui64 not in graph.nodes:
            raise ValueError(f"Node {eui64} not found in graph")
        self._graph = graph
        self._eui64 = eui64
    
    @classmethod
    def create_in_graph(cls, graph: nx.Graph, x: float, y: float, 
                       communication_range: float = 100.0, eui64: Optional[str] = None) -> 'IoTNode':
        """
        Create a new node directly in the NetworkX graph.
        
        Args:
            graph: NetworkX graph to add node to
            x: X coordinate on 2D map
            y: Y coordinate on 2D map
            communication_range: Maximum communication range in units
            eui64: IEEE EUI-64 identifier (generated if not provided)
            
        Returns:
            IoTNode view over the created graph node
        """
        if eui64 is None:
            eui64 = cls._generate_eui64()
        
        # Add node to graph with all attributes
        graph.add_node(eui64, 
                      x=x, 
                      y=y, 
                      communication_range=communication_range)
        
        return cls(graph, eui64)
    
    @staticmethod
    def _generate_eui64() -> str:
        """Generate a random IEEE EUI-64 identifier."""
        # Generate 8 bytes (64 bits) of random data
        bytes_data = [random.randint(0, 255) for _ in range(8)]
        # Format as EUI-64 (XX-XX-XX-XX-XX-XX-XX-XX)
        return '-'.join(f'{b:02X}' for b in bytes_data)
    
    @property
    def eui64(self) -> str:
        """IEEE EUI-64 identifier."""
        return self._eui64
    
    @property
    def x(self) -> float:
        """X coordinate on 2D map."""
        return self._graph.nodes[self._eui64]['x']
    
    @x.setter
    def x(self, value: float) -> None:
        """Set X coordinate."""
        self._graph.nodes[self._eui64]['x'] = value
    
    @property
    def y(self) -> float:
        """Y coordinate on 2D map."""
        return self._graph.nodes[self._eui64]['y']
    
    @y.setter
    def y(self, value: float) -> None:
        """Set Y coordinate."""
        self._graph.nodes[self._eui64]['y'] = value
    
    @property
    def communication_range(self) -> float:
        """Maximum communication range in units."""
        return self._graph.nodes[self._eui64]['communication_range']
    
    @communication_range.setter
    def communication_range(self, value: float) -> None:
        """Set communication range."""
        self._graph.nodes[self._eui64]['communication_range'] = value
    
    @property
    def neighbors(self) -> List['IoTNode']:
        """List of neighboring nodes (computed from graph)."""
        neighbor_nodes = []
        for neighbor_eui64 in self._graph.neighbors(self._eui64):
            neighbor_nodes.append(IoTNode(self._graph, neighbor_eui64))
        return neighbor_nodes
    
    def distance_to(self, other: 'IoTNode') -> float:
        """Calculate Euclidean distance to another node."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def can_communicate_with(self, other: 'IoTNode') -> bool:
        """Check if this node can communicate with another node based on range."""
        return self.distance_to(other) <= self.communication_range
    
    def add_neighbor(self, neighbor: 'IoTNode') -> bool:
        """
        Add a neighbor if within communication range.
        Creates bidirectional connection automatically.
        
        Returns:
            True if neighbor was added, False if out of range or already exists
        """
        if neighbor.eui64 == self.eui64:
            return False
            
        if not self.can_communicate_with(neighbor):
            return False
        
        # Check if edge already exists
        if self._graph.has_edge(self.eui64, neighbor.eui64):
            return False
            
        # Add bidirectional edge with distance as weight
        distance = self.distance_to(neighbor)
        self._graph.add_edge(self.eui64, neighbor.eui64, weight=distance)
        return True
    
    def remove_neighbor(self, neighbor: 'IoTNode') -> bool:
        """Remove a neighbor from the graph. Removes bidirectional connection."""
        if self._graph.has_edge(self.eui64, neighbor.eui64):
            self._graph.remove_edge(self.eui64, neighbor.eui64)
            return True
        return False
    
    def update_neighbors(self, all_nodes: List['IoTNode']) -> None:
        """Update neighbor connections based on current positions and ranges."""
        # Remove all existing edges for this node
        edges_to_remove = list(self._graph.edges(self._eui64))
        self._graph.remove_edges_from(edges_to_remove)
        
        # Add new edges based on current positions and ranges
        for node in all_nodes:
            if node.eui64 != self.eui64 and self.can_communicate_with(node):
                distance = self.distance_to(node)
                self._graph.add_edge(self.eui64, node.eui64, weight=distance)
    
    def get_neighbor_eui64s(self) -> List[str]:
        """Get list of neighbor EUI-64 identifiers."""
        return list(self._graph.neighbors(self._eui64))
    
    def to_dict(self) -> Dict:
        """Convert node to dictionary for serialization."""
        return {
            'eui64': self.eui64,
            'x': self.x,
            'y': self.y,
            'communication_range': self.communication_range,
            'neighbors': self.get_neighbor_eui64s()
        }
    
    @classmethod
    def from_dict(cls, data: Dict, graph: nx.Graph) -> 'IoTNode':
        """Create node from dictionary in the given graph."""
        eui64 = data['eui64']
        
        # Add node to graph if it doesn't exist
        if eui64 not in graph.nodes:
            graph.add_node(eui64,
                          x=data['x'],
                          y=data['y'],
                          communication_range=data['communication_range'])
        
        return cls(graph, eui64)
    
    def __str__(self) -> str:
        return f"IoTNode({self.eui64}, pos=({self.x:.1f}, {self.y:.1f}), range={self.communication_range}, neighbors={len(self.neighbors)})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, IoTNode):
            return False
        return self.eui64 == other.eui64
    
    def __hash__(self) -> int:
        return hash(self.eui64)