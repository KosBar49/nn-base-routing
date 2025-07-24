"""
Network visualization utilities for ASCII and matplotlib output.
"""

from typing import List, Optional
from ..core.network import IoTNetwork
from .logging_config import get_logger

logger = get_logger(__name__)


class NetworkVisualizer:
    """Create visualizations of IoT networks."""
    
    def __init__(self, network: IoTNetwork):
        self.network = network
    
    def ascii_map(self, width: int = 80, height: int = 40) -> List[str]:
        """
        Create an ASCII representation of the network map.
        
        Args:
            width: Width of ASCII map in characters
            height: Height of ASCII map in characters
        
        Returns:
            List of strings representing the ASCII map
        """
        if not self.network.nodes:
            return ["Empty network"]
        
        # Find bounds of the network
        min_x = min(node.x for node in self.network.nodes)
        max_x = max(node.x for node in self.network.nodes)
        min_y = min(node.y for node in self.network.nodes)
        max_y = max(node.y for node in self.network.nodes)
        
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
        for node in self.network.nodes:
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
    
    def print_network_summary(self) -> None:
        """Log a summary of the network."""
        logger.info("Network Summary:")
        logger.info("=" * 50)
        logger.info("Total nodes: %d", len(self.network))
        logger.info("Total connections: %d", self.network.get_connection_count())
        
        if not self.network.nodes:
            return
        
        # Calculate connectivity statistics
        connection_counts = [len(node.neighbors) for node in self.network.nodes]
        avg_connections = sum(connection_counts) / len(connection_counts)
        max_connections = max(connection_counts)
        min_connections = min(connection_counts)
        isolated_nodes = sum(1 for count in connection_counts if count == 0)
        
        logger.info("Average connections per node: %.2f", avg_connections)
        logger.info("Max connections: %d", max_connections)
        logger.info("Min connections: %d", min_connections)
        logger.info("Isolated nodes: %d", isolated_nodes)
        
        # Communication range statistics
        ranges = [node.communication_range for node in self.network.nodes]
        avg_range = sum(ranges) / len(ranges)
        max_range = max(ranges)
        min_range = min(ranges)
        
        logger.info("Communication Range Statistics:")
        logger.info("Average range: %.2f", avg_range)
        logger.info("Max range: %.2f", max_range)
        logger.info("Min range: %.2f", min_range)
    
    def print_node_details(self, limit: int = 10) -> None:
        """Log detailed information about individual nodes."""
        logger.info("Node Details (showing first %d nodes):", limit)
        logger.info("=" * 80)
        
        for i, node in enumerate(self.network.nodes[:limit]):
            logger.info("Node %d: %s", i+1, node.eui64)
            logger.info("  Position: (%.2f, %.2f)", node.x, node.y)
            logger.info("  Range: %.2f", node.communication_range)
            logger.info("  Neighbors: %d", len(node.neighbors))
            
            if node.neighbors:
                logger.info("  Connected to:")
                for neighbor in node.neighbors[:5]:  # Show first 5 neighbors
                    distance = node.distance_to(neighbor)
                    logger.info("    %s (distance: %.2f)", neighbor.eui64, distance)
                if len(node.neighbors) > 5:
                    logger.info("    ... and %d more", len(node.neighbors) - 5)
            else:
                logger.info("  No connections (isolated node)")
    
    def matplotlib_plot(self, output_file: Optional[str] = None) -> None:
        """
        Create a matplotlib visualization of the network.
        
        Args:
            output_file: Optional filename to save the plot
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.collections import LineCollection
        except ImportError:
            logger.warning("matplotlib not available. Skipping graphical visualization")
            return
        
        if not self.network.nodes:
            logger.warning("No nodes to visualize")
            return
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot nodes
        x_coords = [node.x for node in self.network.nodes]
        y_coords = [node.y for node in self.network.nodes]
        neighbor_counts = [len(node.neighbors) for node in self.network.nodes]
        
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
        for node in self.network.nodes:
            for neighbor in node.neighbors:
                # Only draw each connection once
                if node.eui64 < neighbor.eui64:
                    lines.append([(node.x, node.y), (neighbor.x, neighbor.y)])
        
        if lines:
            line_collection = LineCollection(lines, colors='gray', alpha=0.3, linewidths=0.5)
            ax.add_collection(line_collection)
        
        # Add labels for highly connected nodes
        for node in self.network.nodes:
            if len(node.neighbors) > max(neighbor_counts) * 0.8:  # Top 20% connected nodes
                ax.annotate(f'{len(node.neighbors)}', 
                           (node.x, node.y), 
                           xytext=(5, 5), 
                           textcoords='offset points',
                           fontsize=8,
                           alpha=0.7)
        
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.set_title(f'IoT Network Topology ({len(self.network.nodes)} nodes, {self.network.get_connection_count()} connections)')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info("Visualization saved to %s", output_file)
        else:
            plt.show()
