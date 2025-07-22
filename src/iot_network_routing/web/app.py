"""
Flask web application for IoT network visualization.
Provides interactive web interface for network analysis and visualization.
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import math
from typing import Dict, List, Any, Optional

from ..core.network import IoTNetwork
from ..core.node import IoTNode
from ..core.generator import generate_random_network
from ..utils.pathfinder import find_shortest_path, load_network_from_file


def create_app(config: Optional[Dict] = None) -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__, 
                template_folder='../../../templates',
                static_folder='../../../static')
    
    if config:
        app.config.update(config)
    
    # Global variable to store current network
    current_network: IoTNetwork = None
    network_data: Dict[str, Any] = {}

    def calculate_network_stats(network: IoTNetwork) -> Dict[str, Any]:
        """Calculate comprehensive network statistics."""
        if not network.nodes:
            return {"error": "No nodes in network"}
        
        # Basic statistics
        total_nodes = len(network.nodes)
        total_connections = network.get_connection_count()
        
        # Connection statistics
        connection_counts = [len(node.neighbors) for node in network.nodes]
        avg_connections = sum(connection_counts) / len(connection_counts) if connection_counts else 0
        max_connections = max(connection_counts) if connection_counts else 0
        min_connections = min(connection_counts) if connection_counts else 0
        isolated_nodes = sum(1 for count in connection_counts if count == 0)
        
        # Position statistics
        x_coords = [node.x for node in network.nodes]
        y_coords = [node.y for node in network.nodes]
        
        # Communication range statistics
        ranges = [node.communication_range for node in network.nodes]
        avg_range = sum(ranges) / len(ranges) if ranges else 0
        max_range = max(ranges) if ranges else 0
        
        # Connectivity distribution
        connectivity_dist = {}
        for count in connection_counts:
            connectivity_dist[count] = connectivity_dist.get(count, 0) + 1
        
        return {
            "total_nodes": total_nodes,
            "total_connections": total_connections,
            "avg_connections": round(avg_connections, 2),
            "max_connections": max_connections,
            "min_connections": min_connections,
            "isolated_nodes": isolated_nodes,
            "network_density": round(total_connections / (total_nodes * (total_nodes - 1) / 2), 4) if total_nodes > 1 else 0,
            "position_bounds": {
                "x_min": min(x_coords), "x_max": max(x_coords),
                "y_min": min(y_coords), "y_max": max(y_coords)
            },
            "range_stats": {
                "avg_range": round(avg_range, 2),
                "max_range": round(max_range, 2)
            },
            "connectivity_distribution": connectivity_dist
        }

    def prepare_network_data_for_d3(network: IoTNetwork) -> Dict[str, Any]:
        """Prepare network data in D3.js format."""
        if not network.nodes:
            return {"nodes": [], "links": []}
        
        # Prepare nodes
        nodes = []
        node_id_map = {node.eui64: i for i, node in enumerate(network.nodes)}
        
        for i, node in enumerate(network.nodes):
            nodes.append({
                "id": i,
                "eui64": node.eui64,
                "x": node.x,
                "y": node.y,
                "range": node.communication_range,
                "neighbors": len(node.neighbors),
                "group": min(len(node.neighbors), 8)  # Group by connectivity (max 8)
            })
        
        # Prepare links
        links = []
        added_links = set()
        
        for node in network.nodes:
            source_id = node_id_map[node.eui64]
            for neighbor in node.neighbors:
                target_id = node_id_map[neighbor.eui64]
                
                # Avoid duplicate links
                link_key = tuple(sorted([source_id, target_id]))
                if link_key not in added_links:
                    distance = node.distance_to(neighbor)
                    links.append({
                        "source": source_id,
                        "target": target_id,
                        "distance": round(distance, 2),
                        "strength": max(0.1, 1 - distance / 200)  # Link strength based on distance
                    })
                    added_links.add(link_key)
        
        return {"nodes": nodes, "links": links}


    @app.route('/')
    def index():
        """Main page with network visualization."""
        return render_template('index.html')

    @app.route('/upload', methods=['POST'])
    def upload_network():
        """Upload and load network file."""
        nonlocal current_network, network_data
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and file.filename.endswith('.json'):
            try:
                # Save uploaded file temporarily
                temp_path = f"/tmp/{file.filename}"
                file.save(temp_path)
                
                # Load network
                current_network = IoTNetwork.load_from_file(temp_path)
                
                # NetworkX undirected graphs are inherently bidirectional
                validation_msg = "All connections are bidirectional"
                
                network_data = prepare_network_data_for_d3(current_network)
                
                # Clean up temp file
                os.remove(temp_path)
                
                message = f"Network loaded successfully: {len(current_network)} nodes. {validation_msg}"
                
                return jsonify({
                    "success": True,
                    "message": message,
                    "stats": calculate_network_stats(current_network)
                })
                
            except Exception as e:
                return jsonify({"error": f"Failed to load network: {str(e)}"}), 500
        
        return jsonify({"error": "Invalid file format. Please upload a JSON file."}), 400

    @app.route('/load_sample')
    def load_sample():
        """Load sample network for demonstration."""
        nonlocal current_network, network_data
        
        try:
            # Check if sample network exists
            sample_files = ['dense_network.json', 'test_network.json', 'iot_network.json']
            sample_file = None
            
            for file in sample_files:
                if os.path.exists(file):
                    sample_file = file
                    break
            
            if not sample_file:
                return jsonify({"error": "No sample network found. Please generate one first."}), 404
            
            # Load sample network
            current_network = IoTNetwork.load_from_file(sample_file)
            
            # NetworkX undirected graphs are inherently bidirectional
            validation_msg = "All connections are bidirectional"
            
            network_data = prepare_network_data_for_d3(current_network)
            
            message = f"Sample network loaded: {len(current_network)} nodes. {validation_msg}"
            
            return jsonify({
                "success": True,
                "message": message,
                "stats": calculate_network_stats(current_network)
            })
            
        except Exception as e:
            return jsonify({"error": f"Failed to load sample network: {str(e)}"}), 500

    @app.route('/api/network_data')
    def get_network_data():
        """Get current network data for visualization."""
        nonlocal network_data
        
        if not network_data:
            return jsonify({"error": "No network loaded"}), 404
        
        return jsonify(network_data)

    @app.route('/api/network_stats')
    def get_network_stats():
        """Get comprehensive network statistics."""
        nonlocal current_network
        
        if not current_network:
            return jsonify({"error": "No network loaded"}), 404
        
        return jsonify(calculate_network_stats(current_network))

    @app.route('/api/node_details/<node_id>')
    def get_node_details(node_id):
        """Get detailed information about a specific node."""
        nonlocal current_network
        
        if not current_network:
            return jsonify({"error": "No network loaded"}), 404
        
        try:
            node_index = int(node_id)
            if 0 <= node_index < len(current_network.nodes):
                node = current_network.nodes[node_index]
                
                # Get neighbor details
                neighbor_details = []
                for neighbor in node.neighbors:
                    distance = node.distance_to(neighbor)
                    neighbor_details.append({
                        "eui64": neighbor.eui64,
                        "position": {"x": neighbor.x, "y": neighbor.y},
                        "distance": round(distance, 2),
                        "range": neighbor.communication_range
                    })
                
                return jsonify({
                    "eui64": node.eui64,
                    "position": {"x": node.x, "y": node.y},
                    "range": node.communication_range,
                    "neighbor_count": len(node.neighbors),
                    "neighbors": neighbor_details
                })
            else:
                return jsonify({"error": "Node not found"}), 404
                
        except (ValueError, IndexError):
            return jsonify({"error": "Invalid node ID"}), 400

    @app.route('/api/generate_network', methods=['POST'])
    def generate_network_api():
        """Generate a new random network."""
        nonlocal current_network, network_data
        
        try:
            data = request.get_json()
            n_nodes = data.get('nodes', 25)
            width = data.get('width', 500)
            height = data.get('height', 500)
            max_range = data.get('max_range', 120)
            
            current_network = generate_random_network(
                n_nodes=n_nodes,
                map_width=width,
                map_height=height,
                max_range=max_range
            )
            
            # NetworkX undirected graphs are inherently bidirectional
            validation_msg = "All connections are bidirectional"
            
            network_data = prepare_network_data_for_d3(current_network)
            
            message = f"Generated network with {len(current_network)} nodes. {validation_msg}"
            
            return jsonify({
                "success": True,
                "message": message,
                "stats": calculate_network_stats(current_network)
            })
            
        except Exception as e:
            return jsonify({"error": f"Failed to generate network: {str(e)}"}), 500

    @app.route('/api/export_network')
    def export_network():
        """Export current network to JSON file."""
        nonlocal current_network
        
        if not current_network:
            return jsonify({"error": "No network loaded"}), 404
        
        try:
            export_path = "/tmp/exported_network.json"
            current_network.save_to_file(export_path)
            
            return send_file(export_path, 
                            as_attachment=True,
                            download_name='iot_network.json',
                            mimetype='application/json')
            
        except Exception as e:
            return jsonify({"error": f"Failed to export network: {str(e)}"}), 500

    @app.route('/api/find_path', methods=['POST'])
    def find_path():
        """Find shortest path between two nodes."""
        nonlocal current_network
        
        if not current_network:
            return jsonify({"error": "No network loaded"}), 404
        
        try:
            data = request.get_json()
            source_id = data.get('source')
            destination_id = data.get('destination')
            
            if not source_id or not destination_id:
                return jsonify({"error": "Source and destination node IDs are required"}), 400
            
            # Verify nodes exist in network
            node_ids = [node.eui64 for node in current_network.nodes]
            if source_id not in node_ids:
                return jsonify({"error": f"Source node {source_id} not found"}), 404
            if destination_id not in node_ids:
                return jsonify({"error": f"Destination node {destination_id} not found"}), 404
            
            if source_id == destination_id:
                return jsonify({"error": "Source and destination cannot be the same node"}), 400
            
            # Use pathfinder function to find path
            path, distance = find_shortest_path(current_network.graph, source_id, destination_id)
            
            if path is None:
                return jsonify({
                    "source": source_id,
                    "destination": destination_id,
                    "path": None,
                    "distance": float('inf'),
                    "reachable": False,
                    "message": "No path found between nodes"
                })
            
            # Convert path to include node indices for visualization
            node_id_to_index = {node.eui64: i for i, node in enumerate(current_network.nodes)}
            path_indices = [node_id_to_index[node_id] for node_id in path]
            
            return jsonify({
                "source": source_id,
                "destination": destination_id,
                "path": path,
                "path_indices": path_indices,
                "distance": distance,
                "reachable": True,
                "hop_count": len(path) - 1
            })
            
        except Exception as e:
            return jsonify({"error": f"Failed to find path: {str(e)}"}), 500

    return app
