#!/usr/bin/env python3
"""
Script to generate N random IoT nodes with IEEE EUI-64 addresses
and save the network configuration to a file.
"""

import random
import argparse
import sys
from iot_node import IoTNode, IoTNetwork


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


def print_network_stats(network: IoTNetwork) -> None:
    """Print network statistics."""
    print(f"\nNetwork Statistics:")
    print(f"Total nodes: {len(network)}")
    print(f"Total connections: {network.get_connection_count()}")
    
    # Calculate connectivity statistics
    connection_counts = [len(node.neighbors) for node in network.nodes]
    if connection_counts:
        avg_connections = sum(connection_counts) / len(connection_counts)
        max_connections = max(connection_counts)
        min_connections = min(connection_counts)
        isolated_nodes = sum(1 for count in connection_counts if count == 0)
        
        print(f"Average connections per node: {avg_connections:.2f}")
        print(f"Max connections: {max_connections}")
        print(f"Min connections: {min_connections}")
        print(f"Isolated nodes: {isolated_nodes}")
    
    # Show a few example nodes
    print(f"\nExample nodes:")
    for i, node in enumerate(network.nodes[:5]):
        print(f"  {node}")


def main():
    """Main function to generate and save IoT network."""
    parser = argparse.ArgumentParser(description='Generate random IoT network')
    parser.add_argument('n_nodes', type=int, help='Number of nodes to generate')
    parser.add_argument('-o', '--output', default='iot_network.json', 
                       help='Output filename (default: iot_network.json)')
    parser.add_argument('-w', '--width', type=float, default=1000.0,
                       help='Map width (default: 1000.0)')
    parser.add_argument('--height', type=float, default=1000.0,
                       help='Map height (default: 1000.0)')
    parser.add_argument('--max-range', type=float, default=150.0,
                       help='Maximum communication range (default: 150.0)')
    parser.add_argument('-s', '--seed', type=int, 
                       help='Random seed for reproducible results')
    
    args = parser.parse_args()
    
    if args.n_nodes <= 0:
        print("Error: Number of nodes must be positive")
        sys.exit(1)
    
    try:
        # Generate the network
        network = generate_random_network(
            n_nodes=args.n_nodes,
            map_width=args.width,
            map_height=args.height,
            max_range=args.max_range,
            seed=args.seed
        )
        
        # Print statistics
        print_network_stats(network)
        
        # Save to file
        print(f"\nSaving network to {args.output}...")
        network.save_to_file(args.output)
        print(f"Network saved successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()