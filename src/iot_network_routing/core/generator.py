"""
IoT Network Generator: Utility to create random IoT networks.
"""

import random
from typing import Optional

from .network import IoTNetwork
from .node import IoTNode


def generate_random_network(n_nodes: int, 
                          map_width: float = 1000.0, 
                          map_height: float = 1000.0,
                          max_range: float = 150.0,
                          seed: int = None) -> IoTNetwork:
    """
    Generate a random IoT network with specified parameters.
    
    Args:
        n_nodes: Number of nodes to generate
        map_width: Width of the 2D map
        map_height: Height of the 2D map
        max_range: Maximum communication range
        seed: Random seed for reproducible results
    
    Returns:
        IoTNetwork with randomly placed nodes
    """
    if seed is not None:
        random.seed(seed)
    
    network = IoTNetwork()
    
    print(f"Generating {n_nodes} random IoT nodes...")
    print(f"Map dimensions: {map_width} x {map_height}")
    print(f"Communication range: up to {max_range}")
    
    # Generate nodes with random positions and ranges
    for i in range(n_nodes):
        x = random.uniform(0, map_width)
        y = random.uniform(0, map_height)
        # Use a range from 30% to 100% of max_range for variety
        comm_range = random.uniform(max_range * 0.3, max_range)
        
        node = IoTNode(x, y, comm_range)
        network.add_node(node)
        
        if (i + 1) % 100 == 0 or i == n_nodes - 1:
            print(f"Generated {i + 1}/{n_nodes} nodes")
    
    # Update all connections based on positions and ranges
    print("Calculating node connections...")
    network.update_all_connections()
    
    return network
