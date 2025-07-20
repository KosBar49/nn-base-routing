import json
import sys
import argparse
import networkx as nx
from ..core.network import IoTNetwork

class PathFinder:
    def __init__(self, network_file):
        self.network_file = network_file
        self.network = None
        self.graph = None
        
    def load_network(self):
        """Load the network from a JSON file"""
        self.network = IoTNetwork.load_from_file(self.network_file)
        self.graph = self.network.graph

    def initialize(self):
        """Initialize the pathfinder - NetworkX handles initialization internally"""
        if self.graph is None:
            raise ValueError("Network must be loaded before initialization")

    def calculate_paths_from_source(self, source_id):
        """Calculate shortest paths from a single source node using NetworkX"""
        if source_id not in self.graph:
            raise ValueError(f"Source node {source_id} not found in network")
        
        # Use NetworkX's single_source_shortest_path_length for hop count
        return nx.single_source_shortest_path_length(self.graph, source_id)

    def calculate_paths(self):
        """Calculate shortest paths between all nodes using NetworkX"""
        print("Calculating all-pairs shortest paths using NetworkX...")
        
        # Use NetworkX's all_pairs_shortest_path_length for efficiency
        self.all_paths = dict(nx.all_pairs_shortest_path_length(self.graph))
        
        print("Path calculations completed.")

    def find_path(self, source_id, destination_id):
        """Find shortest path between source and destination nodes using NetworkX"""
        if source_id not in self.graph:
            raise ValueError(f"Source node {source_id} not found in network")
        if destination_id not in self.graph:
            raise ValueError(f"Destination node {destination_id} not found in network")
        
        try:
            # Use NetworkX's shortest_path to get the actual path
            path = nx.shortest_path(self.graph, source_id, destination_id)
            # Get the path length (hop count)
            distance = len(path) - 1
            return path, distance
        except nx.NetworkXNoPath:
            # No path exists between the nodes
            return None, float('inf')

    def save_paths(self, output_file):
        """Save the calculated paths to a JSON file"""
        if not hasattr(self, 'all_paths'):
            print("No paths calculated. Run calculate_paths() first.")
            return
        
        # Convert NetworkX all-pairs shortest paths to the expected format
        path_data = []
        for source_id, paths in self.all_paths.items():
            for dest_id, distance in paths.items():
                if source_id != dest_id:  # Skip self-paths
                    try:
                        # Get the actual path
                        path = nx.shortest_path(self.graph, source_id, dest_id)
                        previous_node = path[-2] if len(path) > 1 else None
                    except nx.NetworkXNoPath:
                        previous_node = None
                        
                    path_entry = {
                        'source': source_id,
                        'destination': dest_id,
                        'distance': distance,
                        'previous': previous_node
                    }
                    path_data.append(path_entry)

        with open(output_file, 'w') as f:
            json.dump(path_data, f, indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate shortest paths in IoT network')
    parser.add_argument('input_file', help='Path to the network JSON file')
    parser.add_argument('-o', '--output', default='paths.json', help='Output file path (default: paths.json)')
    
    args = parser.parse_args()

    path_finder = PathFinder(args.input_file)
    path_finder.load_network()
    path_finder.initialize()
    path_finder.calculate_paths()
    path_finder.save_paths(args.output)

    print("Path calculations completed.")
