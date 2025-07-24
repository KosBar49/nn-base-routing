"""
IoT Network Generator: Utility to create random IoT networks.
"""

import random
from typing import Optional

from .network import IoTNetwork
from .node import IoTNode
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


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
    
    logger.info("Generating %d random IoT nodes", n_nodes)
    logger.info("Map dimensions: %.1f x %.1f", map_width, map_height)
    logger.info("Communication range: up to %.1f", max_range)
    
    # Generate nodes with random positions and ranges
    for i in range(n_nodes):
        x = random.uniform(0, map_width)
        y = random.uniform(0, map_height)
        # Use a range from 30% to 100% of max_range for variety
        comm_range = random.uniform(max_range * 0.3, max_range)
        
        # Create node with generated EUI-64
        eui64 = IoTNode.generate_eui64()
        network.add_node(eui64, x, y, comm_range)
        
        if (i + 1) % 100 == 0 or i == n_nodes - 1:
            logger.debug("Generated %d/%d nodes", i + 1, n_nodes)
    
    # Update all connections based on positions and ranges
    logger.info("Calculating node connections")
    network.update_all_connections()
    logger.info("Network generation completed: %d nodes, %d connections", len(network), network.get_connection_count())
    
    return network
