import json
import heapq
import sys
import argparse

class PathFinder:
    def __init__(self, network_file):
        self.network_file = network_file
        self.network = None
        self.distance = {}
        self.previous_nodes = {}
        
    def load_network(self):
        """Load the network from a JSON file"""
        with open(self.network_file, 'r') as f:
            self.network = json.load(f)

    def initialize(self):
        """Initialize the distance and previous node structures"""
        for node in self.network['nodes']:
            node_id = node['eui64']
            self.distance[node_id] = float('inf')
            self.previous_nodes[node_id] = None

    def calculate_paths_from_source(self, source_id):
        """Calculate shortest paths from a single source node"""
        # Reset distances and previous nodes
        for node in self.network['nodes']:
            node_id = node['eui64']
            self.distance[node_id] = float('inf')
            self.previous_nodes[node_id] = None
        
        # Set source distance to 0
        self.distance[source_id] = 0
        priority_queue = [(0, source_id)]

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            # Skip processing if we already found a shorter path
            if current_distance > self.distance[current_node]:
                continue

            # Iterate over neighbors to find shortest path
            for node in self.network['nodes']:
                if node['eui64'] == current_node:
                    for neighbor_id in node['neighbors']:
                        path = current_distance + 1  # Uniform weight
                        if path < self.distance[neighbor_id]:
                            self.distance[neighbor_id] = path
                            self.previous_nodes[neighbor_id] = current_node
                            heapq.heappush(priority_queue, (path, neighbor_id))
                    break

    def calculate_paths(self):
        """Calculate shortest paths between all nodes"""
        # Initialize progress tracking
        total_nodes = len(self.network['nodes'])
        progress_step = max(total_nodes // 10, 1)  # Show progress for every 10% completed

        for index, start_node in enumerate(self.network['nodes']):
            start_id = start_node['eui64']
            self.distance[start_id] = 0
            priority_queue = [(0, start_id)]

            while priority_queue:
                current_distance, current_node = heapq.heappop(priority_queue)

                # Skip processing if we already found a shorter path
                if current_distance > self.distance[current_node]:
                    continue

                # Iterate over neighbors to find shortest path
                for node in self.network['nodes']:
                    if node['eui64'] == current_node:
                        for neighbor_id in node['neighbors']:
                            path = current_distance + 1  # Uniform weight
                            if path < self.distance[neighbor_id]:
                                self.distance[neighbor_id] = path
                                self.previous_nodes[neighbor_id] = current_node
                                heapq.heappush(priority_queue, (path, neighbor_id))
                        break

            # Print progress
            if (index + 1) % progress_step == 0:
                print(f"Progress: {((index + 1) / total_nodes) * 100:.1f}%")

    def find_path(self, source_id, destination_id):
        """Find shortest path between source and destination nodes"""
        # Calculate paths from source
        self.calculate_paths_from_source(source_id)
        
        # Check if destination is reachable
        if self.distance[destination_id] == float('inf'):
            return None, float('inf')
        
        # Reconstruct path
        path = []
        current = destination_id
        while current is not None:
            path.append(current)
            current = self.previous_nodes[current]
        
        path.reverse()
        return path, self.distance[destination_id]

    def save_paths(self, output_file):
        """Save the calculated paths to a JSON file"""
        path_data = []
        for node in self.network['nodes']:
            node_id = node['eui64']
            path_entry = {
                'eui64': node_id,
                'distance': self.distance[node_id],
                'previous': self.previous_nodes[node_id]
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
