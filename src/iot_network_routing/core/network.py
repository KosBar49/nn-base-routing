"""
IoT Network management for collections of IoT nodes and their connections.
"""

import json
import math
from typing import List, Dict, Optional
import networkx as nx

from .node import IoTNode


class IoTNetwork:
    """Manages a collection of IoT nodes and their connections using NetworkX."""
    
    def __init__(self):
        self.graph = nx.Graph()  # Use NetworkX undirected graph for bidirectional connections
        self._node_objects: Dict[str, IoTNode] = {}  # Keep IoTNode objects for backward compatibility
    
    @property
    def nodes(self) -> List[IoTNode]:
        """Property to maintain backward compatibility with the nodes list."""
        return list(self._node_objects.values())
    
    @property
    def nodes_by_eui64(self) -> Dict[str, IoTNode]:
        """Property to maintain backward compatibility with the nodes_by_eui64 dict."""
        return self._node_objects
    
    def add_node(self, node: IoTNode) -> bool:
        """Add a node to the network."""
        if node.eui64 in self._node_objects:
            return False
            
        # Add node to NetworkX graph with all attributes
        self.graph.add_node(node.eui64, 
                           x=node.x, 
                           y=node.y, 
                           communication_range=node.communication_range)
        self._node_objects[node.eui64] = node
        return True
    
    def remove_node(self, eui64: str) -> bool:
        """Remove a node from the network."""
        if eui64 not in self._node_objects:
            return False
            
        node = self._node_objects[eui64]
        
        # Remove from NetworkX graph (this automatically removes all edges)
        self.graph.remove_node(eui64)
        del self._node_objects[eui64]
        
        # Update neighbor lists in remaining node objects for backward compatibility
        for other_node in self.nodes:
            other_node.remove_neighbor(node)
            
        return True
    
    def update_all_connections(self) -> None:
        """Update all node connections based on current positions and ensure bidirectional connections."""
        # Clear all existing edges in the graph
        self.graph.clear_edges()
        
        # Clear neighbor lists in node objects for backward compatibility
        for node in self.nodes:
            node.neighbors.clear()
        
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
                    
                    # Update neighbor lists in node objects for backward compatibility
                    node1_obj = self._node_objects[node1_id]
                    node2_obj = self._node_objects[node2_id]
                    if node2_obj not in node1_obj.neighbors:
                        node1_obj.neighbors.append(node2_obj)
                    if node1_obj not in node2_obj.neighbors:
                        node2_obj.neighbors.append(node1_obj)
    
    def get_node_by_eui64(self, eui64: str) -> Optional[IoTNode]:
        """Get node by EUI-64 identifier."""
        return self._node_objects.get(eui64)
    
    def validate_bidirectional_connections(self) -> bool:
        """Validate that all connections are bidirectional."""
        # NetworkX undirected graphs are inherently bidirectional, but check node objects for consistency
        for node in self.nodes:
            for neighbor in node.neighbors:
                if node not in neighbor.neighbors:
                    return False
        
        # Also verify graph consistency with node objects
        for node_id in self.graph.nodes():
            node_obj = self._node_objects[node_id]
            graph_neighbors = set(self.graph.neighbors(node_id))
            obj_neighbors = set(neighbor.eui64 for neighbor in node_obj.neighbors)
            if graph_neighbors != obj_neighbors:
                return False
        
        return True
    
    def fix_bidirectional_connections(self) -> int:
        """Fix any unidirectional connections and return number of fixes made."""
        fixes = 0
        
        # Since NetworkX undirected graphs are inherently bidirectional,
        # we mainly need to sync the node objects with the graph
        for node_id in self.graph.nodes():
            node_obj = self._node_objects[node_id]
            graph_neighbors = set(self.graph.neighbors(node_id))
            obj_neighbors = set(neighbor.eui64 for neighbor in node_obj.neighbors)
            
            # Add missing neighbors to node object
            for neighbor_id in graph_neighbors - obj_neighbors:
                neighbor_obj = self._node_objects[neighbor_id]
                node_obj.neighbors.append(neighbor_obj)
                fixes += 1
            
            # Remove extra neighbors from node object
            for neighbor in list(node_obj.neighbors):
                if neighbor.eui64 not in graph_neighbors:
                    node_obj.neighbors.remove(neighbor)
                    fixes += 1
        
        # Also check for unidirectional connections in node objects and fix them
        for node in self.nodes:
            for neighbor in list(node.neighbors):
                if node not in neighbor.neighbors:
                    # Check if they should still be connected
                    if node.can_communicate_with(neighbor):
                        neighbor.neighbors.append(node)
                        # Ensure edge exists in graph
                        if not self.graph.has_edge(node.eui64, neighbor.eui64):
                            distance = node.distance_to(neighbor)
                            self.graph.add_edge(node.eui64, neighbor.eui64, weight=distance)
                        fixes += 1
                    else:
                        # Remove the unidirectional connection
                        node.neighbors.remove(neighbor)
                        # Remove edge from graph if it exists
                        if self.graph.has_edge(node.eui64, neighbor.eui64):
                            self.graph.remove_edge(node.eui64, neighbor.eui64)
                        fixes += 1
        
        return fixes
    
    def get_connection_count(self) -> int:
        """Get total number of connections in the network."""
        return self.graph.number_of_edges()
    
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
                if neighbor and not network.graph.has_edge(node.eui64, neighbor.eui64):
                    # Add edge to NetworkX graph
                    distance = node.distance_to(neighbor)
                    network.graph.add_edge(node.eui64, neighbor.eui64, weight=distance)
                    # Add to node object neighbors for backward compatibility
                    node.add_neighbor(neighbor)
        
        return network
    
    def __len__(self) -> int:
        return self.graph.number_of_nodes()
    
    def __str__(self) -> str:
        return f"IoTNetwork({len(self.nodes)} nodes, {self.get_connection_count()} connections)"
