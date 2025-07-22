import json
import sys
import argparse
import networkx as nx
from typing import Dict, List, Tuple, Optional
from ..core.network import IoTNetwork
from .logging_config import setup_logging, get_logger

logger = get_logger(__name__)


def find_shortest_path(graph: nx.Graph, source_id: str, destination_id: str) -> Tuple[Optional[List[str]], int]:
    """Find shortest path between two nodes.
    
    Returns:
        Tuple of (path, distance) where path is list of node IDs or None if no path exists,
        and distance is hop count or float('inf') if no path exists.
    """
    if source_id not in graph:
        raise ValueError(f"Source node {source_id} not found in graph")
    if destination_id not in graph:
        raise ValueError(f"Destination node {destination_id} not found in graph")
    
    try:
        path = nx.shortest_path(graph, source_id, destination_id)
        return path, len(path) - 1
    except nx.NetworkXNoPath:
        return None, float('inf')


def calculate_paths_from_source(graph: nx.Graph, source_id: str) -> Dict[str, List[str]]:
    """Calculate shortest paths from a single source node to all reachable nodes.
    
    Returns:
        Dictionary mapping destination node IDs to path lists.
    """
    if source_id not in graph:
        raise ValueError(f"Source node {source_id} not found in graph")
    
    return nx.single_source_shortest_path(graph, source_id)


def calculate_all_shortest_paths(graph: nx.Graph) -> Dict[str, Dict[str, List[str]]]:
    """Calculate shortest paths between all pairs of nodes.
    
    Returns:
        Nested dictionary: {source_id: {dest_id: [path]}}
    """
    return dict(nx.all_pairs_shortest_path(graph))


def format_paths_for_export(all_paths: Dict[str, Dict[str, List[str]]]) -> List[Dict]:
    """Transform all-pairs shortest paths into export format.
    
    Args:
        all_paths: Result from calculate_all_shortest_paths()
        
    Returns:
        List of path entries with source, destination, distance, and previous node.
    """
    path_data = []
    for source_id, paths in all_paths.items():
        for dest_id, path in paths.items():
            if source_id != dest_id:  # Skip self-paths
                distance = len(path) - 1 if path else float('inf')
                previous_node = path[-2] if len(path) > 1 else None
                    
                path_entry = {
                    'source': source_id,
                    'destination': dest_id,
                    'distance': distance,
                    'previous': previous_node
                }
                path_data.append(path_entry)
    
    return path_data


def save_paths_to_file(path_data: List[Dict], output_file: str) -> None:
    """Save path data to a JSON file."""
    try:
        with open(output_file, 'w') as f:
            json.dump(path_data, f, indent=2)
    except IOError as e:
        raise IOError(f"Failed to write to {output_file}: {e}")


def load_network_from_file(network_file: str) -> IoTNetwork:
    """Load network from file."""
    try:
        return IoTNetwork.load_from_file(network_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise IOError(f"Failed to load network from {network_file}: {e}")


def main() -> None:
    """CLI entry point for pathfinding."""
    parser = argparse.ArgumentParser(description='Calculate shortest paths in IoT network')
    parser.add_argument('input_file', help='Path to the network JSON file')
    parser.add_argument('-o', '--output', default='paths.json', help='Output file path (default: paths.json)')
    parser.add_argument('--log-level', default='INFO', help='Logging level (DEBUG, INFO, WARNING, ERROR)')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level)

    try:
        logger.info("Loading network from %s", args.input_file)
        network = load_network_from_file(args.input_file)
        
        logger.info("Calculating all-pairs shortest paths for %d nodes", len(network.graph.nodes))
        all_paths = calculate_all_shortest_paths(network.graph)
        
        logger.info("Formatting path data for export")
        path_data = format_paths_for_export(all_paths)
        
        logger.info("Saving %d paths to %s", len(path_data), args.output)
        save_paths_to_file(path_data, args.output)
        
        logger.info("Completed successfully: %d paths calculated and saved", len(path_data))
        
    except (ValueError, IOError) as e:
        logger.error("Failed to process paths: %s", e)
        sys.exit(1)


if __name__ == '__main__':
    main()