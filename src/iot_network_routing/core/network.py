"""
IoT Network management for collections of IoT nodes and their connections.
"""

import json
import math
from typing import List, Dict, Optional
import networkx as nx

from .node import IoTNode


class IoTNetwork:
    """Manages a collection of IoT nodes and their connections using NetworkX as single source of truth."""
    
    def __init__(self):
        self.graph = nx.Graph()  # NetworkX undirected graph is the single source of truth
    
    @property
    def nodes(self) -> List[IoTNode]:
        """Get all nodes as IoTNode views over the graph."""
        return [IoTNode(self.graph, node_id) for node_id in self.graph.nodes()]
    
    @property
    def nodes_by_eui64(self) -> Dict[str, IoTNode]:
        """Get nodes dictionary mapped by EUI-64."""
        return {node_id: IoTNode(self.graph, node_id) for node_id in self.graph.nodes()}
    
    def add_node(self, node: IoTNode) -> bool:
        """Add a node to the network."""
        if node.eui64 in self.graph.nodes:
            return False
            
        # Add node to NetworkX graph with all attributes
        self.graph.add_node(node.eui64, 
                           x=node.x, 
                           y=node.y, 
                           communication_range=node.communication_range)
        return True
    
    def add_node_direct(self, eui64: str, x: float, y: float, communication_range: float) -> IoTNode:
        """Add a node directly to the graph and return IoTNode view."""
        if eui64 in self.graph.nodes:
            raise ValueError(f"Node {eui64} already exists in network")
            
        self.graph.add_node(eui64, x=x, y=y, communication_range=communication_range)
        return IoTNode(self.graph, eui64)
    
    def remove_node(self, eui64: str) -> bool:
        """Remove a node from the network."""
        if eui64 not in self.graph.nodes:
            return False
            
        # Remove from NetworkX graph (this automatically removes all edges)
        self.graph.remove_node(eui64)
        return True
    
    def update_all_connections(self) -> None:
        """Update all node connections based on current positions and ensure bidirectional connections."""
        # Clear all existing edges in the graph
        self.graph.clear_edges()
        
        # Create bidirectional connections using NetworkX
        node_ids = list(self.graph.nodes())
        for i, node1_id in enumerate(node_ids):
            for node2_id in node_ids[i+1:]:
                # Get node attributes from graph
                node1_attrs = self.graph.nodes[node1_id]
                node2_attrs = self.graph.nodes[node2_id]
                
                # Calculate distance
                distance = math.sqrt((node1_attrs['x'] - node2_attrs['x'])**2 + 
                                   (node1_attrs['y'] - node2_attrs['y'])**2)
                
                # Check if nodes can communicate (use the maximum range for broader connectivity)
                max_range = max(node1_attrs['communication_range'], node2_attrs['communication_range'])
                
                if distance <= max_range:
                    # Add edge to NetworkX graph with distance as weight
                    self.graph.add_edge(node1_id, node2_id, weight=distance)
    
    def get_node_by_eui64(self, eui64: str) -> Optional[IoTNode]:
        """Get node by EUI-64 identifier."""
        if eui64 in self.graph.nodes:
            return IoTNode(self.graph, eui64)
        return None
    
    def validate_bidirectional_connections(self) -> bool:
        """Validate that all connections are bidirectional."""
        # NetworkX undirected graphs are inherently bidirectional
        return True
    
    def fix_bidirectional_connections(self) -> int:
        """Fix any unidirectional connections and return number of fixes made."""
        # NetworkX undirected graphs are inherently bidirectional, no fixes needed
        return 0
    
    def get_connection_count(self) -> int:
        """Get total number of connections in the network."""
        return self.graph.number_of_edges()
    
    def to_dict(self) -> Dict:
        """Convert network to dictionary for serialization."""
        nodes_data = []
        for node_id in self.graph.nodes():
            node = IoTNode(self.graph, node_id)
            nodes_data.append(node.to_dict())
        
        return {
            'nodes': nodes_data,
            'total_nodes': len(self.graph.nodes),
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
            network.add_node_direct(
                eui64=node_data['eui64'],
                x=node_data['x'],
                y=node_data['y'],
                communication_range=node_data['communication_range']
            )
        
        # Second pass: establish connections
        for node_data in data['nodes']:
            node_id = node_data['eui64']
            for neighbor_eui64 in node_data['neighbors']:
                if neighbor_eui64 in network.graph.nodes:
                    if not network.graph.has_edge(node_id, neighbor_eui64):
                        # Calculate distance and add edge
                        node1_attrs = network.graph.nodes[node_id]
                        node2_attrs = network.graph.nodes[neighbor_eui64]
                        distance = math.sqrt((node1_attrs['x'] - node2_attrs['x'])**2 + 
                                           (node1_attrs['y'] - node2_attrs['y'])**2)
                        network.graph.add_edge(node_id, neighbor_eui64, weight=distance)
        
        return network
    
    def __len__(self) -> int:
        return self.graph.number_of_nodes()
    
    def __str__(self) -> str:
        return f"IoTNetwork({len(self.graph.nodes)} nodes, {self.get_connection_count()} connections)"