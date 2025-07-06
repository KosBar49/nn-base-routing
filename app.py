#!/usr/bin/env python3
"""
Flask web application for IoT network visualization.
Provides interactive web interface for network analysis and visualization.
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import math
from typing import Dict, List, Any
from iot_node import IoTNetwork, IoTNode

app = Flask(__name__)

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
    min_range = min(ranges) if ranges else 0
    
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
            "max_range": round(max_range, 2),
            "min_range": round(min_range, 2)
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
            "group": min(len(node.neighbors), 5)  # Group by connectivity (max 5)
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


def validate_and_fix_network(network: IoTNetwork) -> str:
    """Validate and fix network connections, return status message."""
    if not network.validate_bidirectional_connections():
        fixes = network.fix_bidirectional_connections()
        return f"Fixed {fixes} unidirectional connections"
    return "All connections are bidirectional"


@app.route('/')
def index():
    """Main page with network visualization."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_network():
    """Upload and load network file."""
    global current_network, network_data
    
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
            
            # Validate and fix bidirectional connections
            validation_msg = validate_and_fix_network(current_network)
            
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
    global current_network, network_data
    
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
        
        # Validate and fix bidirectional connections
        validation_msg = validate_and_fix_network(current_network)
        
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
    global network_data
    
    if not network_data:
        return jsonify({"error": "No network loaded"}), 404
    
    return jsonify(network_data)


@app.route('/api/network_stats')
def get_network_stats():
    """Get comprehensive network statistics."""
    global current_network
    
    if not current_network:
        return jsonify({"error": "No network loaded"}), 404
    
    return jsonify(calculate_network_stats(current_network))


@app.route('/api/node_details/<node_id>')
def get_node_details(node_id):
    """Get detailed information about a specific node."""
    global current_network
    
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
def generate_network():
    """Generate a new random network."""
    global current_network, network_data
    
    try:
        data = request.get_json()
        n_nodes = data.get('nodes', 25)
        width = data.get('width', 500)
        height = data.get('height', 500)
        min_range = data.get('min_range', 60)
        max_range = data.get('max_range', 120)
        
        # Import and use the generation function
        from generate_network import generate_random_network
        
        current_network = generate_random_network(
            n_nodes=n_nodes,
            map_width=width,
            map_height=height,
            min_range=min_range,
            max_range=max_range
        )
        
        # Validate and fix bidirectional connections (should be good already, but double-check)
        validation_msg = validate_and_fix_network(current_network)
        
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
    global current_network
    
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)