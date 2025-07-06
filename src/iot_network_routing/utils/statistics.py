"""
Network statistics calculation utilities.
"""

from typing import Dict, List, Any
from ..core.network import IoTNetwork


class NetworkStatistics:
    """Calculate and analyze IoT network statistics."""
    
    def __init__(self, network: IoTNetwork):
        self.network = network
    
    def basic_stats(self) -> Dict[str, Any]:
        """Calculate basic network statistics."""
        if not self.network.nodes:
            return {"error": "No nodes in network"}
        
        total_nodes = len(self.network.nodes)
        total_connections = self.network.get_connection_count()
        
        connection_counts = [len(node.neighbors) for node in self.network.nodes]
        avg_connections = sum(connection_counts) / len(connection_counts) if connection_counts else 0
        max_connections = max(connection_counts) if connection_counts else 0
        min_connections = min(connection_counts) if connection_counts else 0
        isolated_nodes = sum(1 for count in connection_counts if count == 0)
        
        return {
            "total_nodes": total_nodes,
            "total_connections": total_connections,
            "avg_connections": round(avg_connections, 2),
            "max_connections": max_connections,
            "min_connections": min_connections,
            "isolated_nodes": isolated_nodes,
            "network_density": round(total_connections / (total_nodes * (total_nodes - 1) / 2), 4) if total_nodes > 1 else 0
        }
    
    def connectivity_distribution(self) -> Dict[int, int]:
        """Get distribution of connectivity levels."""
        distribution = {}
        for node in self.network.nodes:
            count = len(node.neighbors)
            distribution[count] = distribution.get(count, 0) + 1
        return distribution
    
    def range_statistics(self) -> Dict[str, float]:
        """Calculate communication range statistics."""
        ranges = [node.communication_range for node in self.network.nodes]
        if not ranges:
            return {}
        
        return {
            "avg_range": round(sum(ranges) / len(ranges), 2),
            "max_range": round(max(ranges), 2),
            "min_range": round(min(ranges), 2)
        }
    
    def position_bounds(self) -> Dict[str, float]:
        """Get network position boundaries."""
        if not self.network.nodes:
            return {}
        
        x_coords = [node.x for node in self.network.nodes]
        y_coords = [node.y for node in self.network.nodes]
        
        return {
            "x_min": min(x_coords),
            "x_max": max(x_coords),
            "y_min": min(y_coords),
            "y_max": max(y_coords)
        }
    
    def full_report(self) -> Dict[str, Any]:
        """Generate a complete statistics report."""
        return {
            "basic_stats": self.basic_stats(),
            "connectivity_distribution": self.connectivity_distribution(),
            "range_stats": self.range_statistics(),
            "position_bounds": self.position_bounds()
        }
