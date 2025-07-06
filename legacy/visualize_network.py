#!/usr/bin/env python3
"""
Script to parse IoT network file and visualize node connections on a 2D map.
"""

import argparse
import sys
import json
from typing import List, Tuple
from iot_node import IoTNetwork


def create_ascii_map(network: IoTNetwork, width: int = 80, height: int = 40) -> List[str]:
    """
    Create an ASCII representation of the network map.
    
    Args:
        network: IoT network to visualize
        width: Width of ASCII map in characters
        height: Height of ASCII map in characters
    
    Returns:
        List of strings representing the ASCII map
    """
    if not network.nodes:
        return ["Empty network"]
    
    # Find bounds of the network
    min_x = min(node.x for node in network.nodes)
    max_x = max(node.x for node in network.nodes)
    min_y = min(node.y for node in network.nodes)
    max_y = max(node.y for node in network.nodes)
    
    # Add padding
    padding = 0.1
    x_range = max_x - min_x
    y_range = max_y - min_y
    
    if x_range == 0:
        x_range = 1
    if y_range == 0:
        y_range = 1
    
    min_x -= x_range * padding
    max_x += x_range * padding
    min_y -= y_range * padding
    max_y += y_range * padding
    
    # Create empty map
    map_grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Place nodes on the map
    for node in network.nodes:
        # Convert coordinates to map position
        map_x = int((node.x - min_x) / (max_x - min_x) * (width - 1))
        map_y = int((node.y - min_y) / (max_y - min_y) * (height - 1))
        
        # Ensure coordinates are within bounds
        map_x = max(0, min(width - 1, map_x))
        map_y = max(0, min(height - 1, map_y))
        
        # Choose symbol based on number of connections
        neighbor_count = len(node.neighbors)
        if neighbor_count == 0:
            symbol = '.'  # Isolated node
        elif neighbor_count <= 2:
            symbol = 'o'  # Low connectivity
        elif neighbor_count <= 5:
            symbol = 'O'  # Medium connectivity
        else:
            symbol = '@'  # High connectivity
        
        map_grid[map_y][map_x] = symbol
    
    # Convert grid to strings (flip Y axis for proper display)
    return [''.join(row) for row in reversed(map_grid)]


def print_detailed_stats(network: IoTNetwork) -> None:
    """Print detailed network statistics."""
    print(f"Network Statistics:")
    print(f"=" * 50)
    print(f"Total nodes: {len(network)}")
    print(f"Total connections: {network.get_connection_count()}")
    
    if not network.nodes:
        return
    
    # Calculate connectivity statistics
    connection_counts = [len(node.neighbors) for node in network.nodes]
    avg_connections = sum(connection_counts) / len(connection_counts)
    max_connections = max(connection_counts)
    min_connections = min(connection_counts)
    isolated_nodes = sum(1 for count in connection_counts if count == 0)
    
    print(f"Average connections per node: {avg_connections:.2f}")
    print(f"Max connections: {max_connections}")
    print(f"Min connections: {min_connections}")
    print(f"Isolated nodes: {isolated_nodes}")
    
    # Communication range statistics
    ranges = [node.communication_range for node in network.nodes]
    avg_range = sum(ranges) / len(ranges)
    max_range = max(ranges)
    min_range = min(ranges)
    
    print(f"\nCommunication Range Statistics:")
    print(f"Average range: {avg_range:.2f}")
    print(f"Max range: {max_range:.2f}")
    print(f"Min range: {min_range:.2f}")
    
    # Position statistics
    x_coords = [node.x for node in network.nodes]
    y_coords = [node.y for node in network.nodes]
    
    print(f"\nPosition Statistics:")
    print(f"X range: {min(x_coords):.2f} to {max(x_coords):.2f}")
    print(f"Y range: {min(y_coords):.2f} to {max(y_coords):.2f}")
    
    # Connectivity distribution
    print(f"\nConnectivity Distribution:")
    for i in range(max_connections + 1):
        count = sum(1 for c in connection_counts if c == i)
        if count > 0:
            percentage = (count / len(network.nodes)) * 100
            print(f"  {i} connections: {count} nodes ({percentage:.1f}%)")


def print_node_details(network: IoTNetwork, limit: int = 10) -> None:
    """Print detailed information about individual nodes."""
    print(f"\nNode Details (showing first {limit} nodes):")
    print(f"=" * 80)
    
    for i, node in enumerate(network.nodes[:limit]):
        print(f"Node {i+1}: {node.eui64}")
        print(f"  Position: ({node.x:.2f}, {node.y:.2f})")
        print(f"  Range: {node.communication_range:.2f}")
        print(f"  Neighbors: {len(node.neighbors)}")
        
        if node.neighbors:
            print(f"  Connected to:")
            for neighbor in node.neighbors[:5]:  # Show first 5 neighbors
                distance = node.distance_to(neighbor)
                print(f"    {neighbor.eui64} (distance: {distance:.2f})")
            if len(node.neighbors) > 5:
                print(f"    ... and {len(node.neighbors) - 5} more")
        else:
            print(f"  No connections (isolated node)")
        print()


def visualize_with_matplotlib(network: IoTNetwork, output_file: str = None) -> None:
    """
    Create a matplotlib visualization of the network.
    Requires matplotlib to be installed.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.collections import LineCollection
    except ImportError:
        print("Warning: matplotlib not available. Skipping graphical visualization.")
        return
    
    if not network.nodes:
        print("No nodes to visualize")
        return
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot nodes
    x_coords = [node.x for node in network.nodes]
    y_coords = [node.y for node in network.nodes]
    neighbor_counts = [len(node.neighbors) for node in network.nodes]
    
    # Create scatter plot with size based on connectivity
    scatter = ax.scatter(x_coords, y_coords, 
                        c=neighbor_counts, 
                        s=[50 + count * 10 for count in neighbor_counts],
                        cmap='viridis', 
                        alpha=0.7,
                        edgecolors='black',
                        linewidth=0.5)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Number of Connections', rotation=270, labelpad=20)
    
    # Plot connections
    lines = []
    for node in network.nodes:
        for neighbor in node.neighbors:
            # Only draw each connection once
            if node.eui64 < neighbor.eui64:
                lines.append([(node.x, node.y), (neighbor.x, neighbor.y)])
    
    if lines:
        line_collection = LineCollection(lines, colors='gray', alpha=0.3, linewidths=0.5)
        ax.add_collection(line_collection)
    
    # Add labels for highly connected nodes
    for node in network.nodes:
        if len(node.neighbors) > max(neighbor_counts) * 0.8:  # Top 20% connected nodes
            ax.annotate(f'{len(node.neighbors)}', 
                       (node.x, node.y), 
                       xytext=(5, 5), 
                       textcoords='offset points',
                       fontsize=8,
                       alpha=0.8)
    
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title(f'IoT Network Visualization\n{len(network)} nodes, {network.get_connection_count()} connections')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {output_file}")
    else:
        plt.show()
    
    plt.close()


def main():
    """Main function to load and visualize IoT network."""
    parser = argparse.ArgumentParser(description='Visualize IoT network from file')
    parser.add_argument('input_file', help='Input JSON file containing network data')
    parser.add_argument('-a', '--ascii', action='store_true',
                       help='Show ASCII map visualization')
    parser.add_argument('-g', '--graph', action='store_true',
                       help='Show graphical visualization (requires matplotlib)')
    parser.add_argument('-o', '--output', 
                       help='Output file for graphical visualization')
    parser.add_argument('-d', '--details', action='store_true',
                       help='Show detailed node information')
    parser.add_argument('--node-limit', type=int, default=10,
                       help='Limit number of nodes shown in details (default: 10)')
    parser.add_argument('--ascii-width', type=int, default=80,
                       help='Width of ASCII map (default: 80)')
    parser.add_argument('--ascii-height', type=int, default=40,
                       help='Height of ASCII map (default: 40)')
    
    args = parser.parse_args()
    
    # If no visualization options specified, show all
    if not (args.ascii or args.graph or args.details):
        args.ascii = True
        args.graph = True
        args.details = True
    
    try:
        # Load network from file
        print(f"Loading network from {args.input_file}...")
        network = IoTNetwork.load_from_file(args.input_file)
        print(f"Network loaded successfully!")
        
        # Print statistics
        print_detailed_stats(network)
        
        # Show node details
        if args.details:
            print_node_details(network, args.node_limit)
        
        # Show ASCII visualization
        if args.ascii:
            print(f"\nASCII Map (Legend: . = isolated, o = low connectivity, O = medium, @ = high):")
            print(f"=" * args.ascii_width)
            ascii_map = create_ascii_map(network, args.ascii_width, args.ascii_height)
            for line in ascii_map:
                print(line)
        
        # Show graphical visualization
        if args.graph:
            print(f"\nGenerating graphical visualization...")
            visualize_with_matplotlib(network, args.output)
            
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{args.input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()