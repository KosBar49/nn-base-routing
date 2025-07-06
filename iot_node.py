import random
import math
import json
from typing import List, Tuple, Dict, Optional


class IoTNode:
    """
    Represents an IoT node with 2D coordinates and range-based neighbor detection.
    Uses IEEE EUI-64 identifier format.
    """
    
    def __init__(self, x: float, y: float, communication_range: float = 100.0, eui64: Optional[str] = None):
        """
        Initialize IoT node with coordinates and communication range.
        
        Args:
            x: X coordinate on 2D map
            y: Y coordinate on 2D map
            communication_range: Maximum communication range in units
            eui64: IEEE EUI-64 identifier (generated if not provided)
        """
        self.x = x
        self.y = y
        self.communication_range = communication_range
        self.eui64 = eui64 if eui64 else self._generate_eui64()
        self.neighbors: List['IoTNode'] = []
    
    def _generate_eui64(self) -> str:
        """Generate a random IEEE EUI-64 identifier."""
        # Generate 8 bytes (64 bits) of random data
        bytes_data = [random.randint(0, 255) for _ in range(8)]
        # Format as EUI-64 (XX-XX-XX-XX-XX-XX-XX-XX)
        return '-'.join(f'{b:02X}' for b in bytes_data)
    
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
        if neighbor == self:
            return False
            
        if not self.can_communicate_with(neighbor):
            return False
            
        # Add bidirectional connection
        added = False
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            added = True
            
        if self not in neighbor.neighbors:
            neighbor.neighbors.append(self)
            added = True
            
        return added
    
    def remove_neighbor(self, neighbor: 'IoTNode') -> bool:
        """Remove a neighbor from the list. Removes bidirectional connection."""
        removed = False
        if neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
            removed = True
            
        if self in neighbor.neighbors:
            neighbor.neighbors.remove(self)
            removed = True
            
        return removed
    
    def update_neighbors(self, all_nodes: List['IoTNode']) -> None:
        """Update neighbor list based on current positions and ranges."""
        self.neighbors.clear()
        for node in all_nodes:
            if node != self and self.can_communicate_with(node):
                self.neighbors.append(node)
    
    def get_neighbor_eui64s(self) -> List[str]:
        """Get list of neighbor EUI-64 identifiers."""
        return [neighbor.eui64 for neighbor in self.neighbors]
    
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
    def from_dict(cls, data: Dict) -> 'IoTNode':
        """Create node from dictionary."""
        return cls(
            x=data['x'],
            y=data['y'],
            communication_range=data['communication_range'],
            eui64=data['eui64']
        )
    
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


class IoTNetwork:
    """Manages a collection of IoT nodes and their connections."""
    
    def __init__(self):
        self.nodes: List[IoTNode] = []
        self.nodes_by_eui64: Dict[str, IoTNode] = {}
    
    def add_node(self, node: IoTNode) -> bool:
        """Add a node to the network."""
        if node.eui64 in self.nodes_by_eui64:
            return False
            
        self.nodes.append(node)
        self.nodes_by_eui64[node.eui64] = node
        return True
    
    def remove_node(self, eui64: str) -> bool:
        """Remove a node from the network."""
        if eui64 not in self.nodes_by_eui64:
            return False
            
        node = self.nodes_by_eui64[eui64]
        self.nodes.remove(node)
        del self.nodes_by_eui64[eui64]
        
        # Remove from all neighbor lists
        for other_node in self.nodes:
            other_node.remove_neighbor(node)
            
        return True
    
    def update_all_connections(self) -> None:
        """Update all node connections based on current positions and ensure bidirectional connections."""
        # First, clear all existing connections
        for node in self.nodes:
            node.neighbors.clear()
        
        # Create bidirectional connections
        for i, node1 in enumerate(self.nodes):
            for j, node2 in enumerate(self.nodes[i+1:], i+1):
                # Check if nodes can communicate (use the smaller range for conservative approach)
                distance = node1.distance_to(node2)
                min_range = min(node1.communication_range, node2.communication_range)
                
                if distance <= min_range:
                    # Add bidirectional connection
                    if node2 not in node1.neighbors:
                        node1.neighbors.append(node2)
                    if node1 not in node2.neighbors:
                        node2.neighbors.append(node1)
    
    def get_node_by_eui64(self, eui64: str) -> Optional[IoTNode]:
        """Get node by EUI-64 identifier."""
        return self.nodes_by_eui64.get(eui64)
    
    def validate_bidirectional_connections(self) -> bool:
        """Validate that all connections are bidirectional."""
        for node in self.nodes:
            for neighbor in node.neighbors:
                if node not in neighbor.neighbors:
                    return False
        return True
    
    def fix_bidirectional_connections(self) -> int:
        """Fix any unidirectional connections and return number of fixes made."""
        fixes = 0
        for node in self.nodes:
            for neighbor in list(node.neighbors):  # Create copy to avoid modification during iteration
                if node not in neighbor.neighbors:
                    # Check if they should still be connected
                    if node.can_communicate_with(neighbor):
                        neighbor.neighbors.append(node)
                        fixes += 1
                    else:
                        # Remove the unidirectional connection
                        node.neighbors.remove(neighbor)
                        fixes += 1
        return fixes
    
    def get_connection_count(self) -> int:
        """Get total number of connections in the network."""
        return sum(len(node.neighbors) for node in self.nodes) // 2
    
    def to_dict(self) -> Dict:
        """Convert network to dictionary for serialization."""
        return {
            'nodes': [node.to_dict() for node in self.nodes],
            'total_nodes': len(self.nodes),
            'total_connections': self.get_connection_count()
        }
    
    def save_to_file(self, filename: str) -> None:
        """Save network to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'IoTNetwork':
        """Load network from JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        network = cls()
        
        # First pass: create all nodes
        for node_data in data['nodes']:
            node = IoTNode.from_dict(node_data)
            network.add_node(node)
        
        # Second pass: establish connections
        for node_data in data['nodes']:
            node = network.get_node_by_eui64(node_data['eui64'])
            for neighbor_eui64 in node_data['neighbors']:
                neighbor = network.get_node_by_eui64(neighbor_eui64)
                if neighbor:
                    node.add_neighbor(neighbor)
        
        return network
    
    def __len__(self) -> int:
        return len(self.nodes)
    
    def __str__(self) -> str:
        return f"IoTNetwork({len(self.nodes)} nodes, {self.get_connection_count()} connections)"