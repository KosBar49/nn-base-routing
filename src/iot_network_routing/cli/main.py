"""
Main CLI entry point for IoT Network Management.
"""

import argparse
import sys
from typing import Optional

from ..core.generator import generate_random_network
from ..core.network import IoTNetwork


def main(argv: Optional[list] = None) -> int:
    """
    Main CLI function for network generation and management.
    
    Args:
        argv: List of command-line arguments
    
    Returns:
        Exit code
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description='IoT Network Management CLI')
    parser.add_argument('n_nodes', type=int, help='Number of nodes to generate')
    parser.add_argument('-o', '--output', default='network.json',
                       help='Output filename (default: network.json)')
    parser.add_argument('-w', '--width', type=float, default=1000.0,
                       help='Map width (default: 1000.0)')
    parser.add_argument('--height', type=float, default=1000.0,
                       help='Map height (default: 1000.0)')
    parser.add_argument('-r', '--max-range', type=float, default=150.0,
                       help='Maximum communication range (default: 150.0)')
    parser.add_argument('-s', '--seed', type=int,
                       help='Random seed for reproducible results')

    args = parser.parse_args(argv)

    if args.n_nodes <= 0:
        print("Error: Number of nodes must be positive", file=sys.stderr)
        return 1

    try:
        # Generate the network
        network = generate_random_network(
            n_nodes=args.n_nodes,
            map_width=args.width,
            map_height=args.height,
            max_range=args.max_range,
            seed=args.seed
        )

        # Print a summary
        print(f"Generated Network: {len(network)} nodes, {network.get_connection_count()} connections")

        # Save to file
        network.save_to_file(args.output)
        print(f"Network saved to {args.output}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())

