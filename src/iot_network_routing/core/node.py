"""
IoT Node implementation with 2D coordinates and communication capabilities.
"""

import random
import math
from typing import List, Dict, Optional


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
