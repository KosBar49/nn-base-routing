"""
IoT Network management for collections of IoT nodes and their connections.
"""

import json
from typing import List, Dict, Optional

from .node import IoTNode


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
                # Check if nodes can communicate (use the maximum range for broader connectivity)
                distance = node1.distance_to(node2)
                max_range = max(node1.communication_range, node2.communication_range)
                
                if distance <= max_range:
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
