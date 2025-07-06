#!/usr/bin/env python3
"""
Professional IoT network visualization with NetworkX, matplotlib, and plotly.
Provides advanced graph analysis and interactive visualizations.
"""

import argparse
import sys
import json
import numpy as np
from typing import List, Tuple, Dict, Optional
from iot_node import IoTNetwork


def create_networkx_graph(network: IoTNetwork):
    """Create a NetworkX graph from IoT network."""
    try:
        import networkx as nx
    except ImportError:
        print("Error: NetworkX not installed. Install with: pip install networkx")
        return None
    
    G = nx.Graph()
    
    # Add nodes with attributes
    for node in network.nodes:
        G.add_node(node.eui64, 
                   pos=(node.x, node.y),
                   x=node.x,
                   y=node.y,
                   range=node.communication_range,
                   neighbors=len(node.neighbors))
    
    # Add edges
    for node in network.nodes:
        for neighbor in node.neighbors:
            if not G.has_edge(node.eui64, neighbor.eui64):
                distance = node.distance_to(neighbor)
                G.add_edge(node.eui64, neighbor.eui64, 
                          weight=distance,
                          distance=distance)
    
    return G


def analyze_network_topology(G):
    """Perform advanced network topology analysis."""
    try:
        import networkx as nx
    except ImportError:
        return {}
    
    analysis = {}
    
    # Basic metrics
    analysis['nodes'] = G.number_of_nodes()
    analysis['edges'] = G.number_of_edges()
    analysis['density'] = nx.density(G)
    analysis['is_connected'] = nx.is_connected(G)
    
    # Connected components
    components = list(nx.connected_components(G))
    analysis['num_components'] = len(components)
    analysis['largest_component_size'] = max(len(c) for c in components) if components else 0
    
    # Centrality measures
    if G.number_of_nodes() > 0:
        analysis['degree_centrality'] = nx.degree_centrality(G)
        analysis['betweenness_centrality'] = nx.betweenness_centrality(G)
        analysis['closeness_centrality'] = nx.closeness_centrality(G)
        analysis['eigenvector_centrality'] = nx.eigenvector_centrality(G, max_iter=1000)
    
    # Clustering
    analysis['clustering'] = nx.clustering(G)
    analysis['average_clustering'] = nx.average_clustering(G)
    
    # Path lengths
    if nx.is_connected(G):
        analysis['diameter'] = nx.diameter(G)
        analysis['average_shortest_path'] = nx.average_shortest_path_length(G)
    
    return analysis


def visualize_matplotlib_advanced(network: IoTNetwork, output_file: str = None, 
                                 layout: str = 'spring', style: str = 'modern') -> None:
    """
    Create advanced matplotlib visualization with multiple layout options.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.collections import LineCollection
        import networkx as nx
    except ImportError:
        print("Error: Required libraries not installed. Install with: pip install matplotlib networkx")
        return
    
    G = create_networkx_graph(network)
    if G is None:
        return
    
    # Set up the plot style
    if style == 'modern':
        plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('IoT Network Analysis Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Geographic layout (actual positions)
    pos_geo = {node.eui64: (node.x, node.y) for node in network.nodes}
    
    # Get node attributes for coloring
    node_sizes = [G.nodes[node]['neighbors'] * 50 + 100 for node in G.nodes()]
    node_colors = [G.nodes[node]['neighbors'] for node in G.nodes()]
    
    # Plot 1: Geographic layout
    nx.draw(G, pos_geo, ax=ax1, 
            node_color=node_colors, 
            node_size=node_sizes,
            cmap='viridis', 
            with_labels=False,
            edge_color='gray',
            alpha=0.7)
    ax1.set_title('Geographic Layout', fontweight='bold')
    ax1.set_xlabel('X Coordinate')
    ax1.set_ylabel('Y Coordinate')
    
    # Plot 2: Spring layout (force-directed)
    if layout == 'spring':
        pos_spring = nx.spring_layout(G, k=1, iterations=50)
    elif layout == 'circular':
        pos_spring = nx.circular_layout(G)
    elif layout == 'kamada_kawai':
        pos_spring = nx.kamada_kawai_layout(G)
    else:
        pos_spring = nx.spring_layout(G)
    
    nx.draw(G, pos_spring, ax=ax2,
            node_color=node_colors,
            node_size=node_sizes,
            cmap='plasma',
            with_labels=False,
            edge_color='lightblue',
            alpha=0.8)
    ax2.set_title(f'{layout.title()} Layout', fontweight='bold')
    
    # Plot 3: Degree distribution
    degrees = [G.degree(node) for node in G.nodes()]
    ax3.hist(degrees, bins=max(1, max(degrees) if degrees else 1), 
             color='skyblue', alpha=0.7, edgecolor='black')
    ax3.set_xlabel('Node Degree')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Degree Distribution', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Network topology analysis
    analysis = analyze_network_topology(G)
    
    # Create text summary
    summary_text = f"""
Network Statistics:
Nodes: {analysis.get('nodes', 0)}
Edges: {analysis.get('edges', 0)}
Density: {analysis.get('density', 0):.3f}
Connected: {analysis.get('is_connected', False)}
Components: {analysis.get('num_components', 0)}
Avg Clustering: {analysis.get('average_clustering', 0):.3f}
"""
    
    if analysis.get('is_connected', False):
        summary_text += f"Diameter: {analysis.get('diameter', 'N/A')}\n"
        summary_text += f"Avg Path Length: {analysis.get('average_shortest_path', 0):.3f}\n"
    
    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, 
             verticalalignment='top', fontsize=10, fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    ax4.set_title('Network Analysis', fontweight='bold')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Advanced visualization saved to {output_file}")
    else:
        plt.show()
    
    plt.close()


def visualize_plotly_interactive(network: IoTNetwork, output_file: str = None) -> None:
    """
    Create interactive plotly visualization with hover info and controls.
    """
    try:
        import plotly.graph_objects as go
        import plotly.express as px
        from plotly.subplots import make_subplots
        import networkx as nx
    except ImportError:
        print("Error: Plotly not installed. Install with: pip install plotly")
        return
    
    G = create_networkx_graph(network)
    if G is None:
        return
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Geographic Network Layout', 'Force-Directed Layout', 
                       'Node Connectivity Heatmap', 'Network Statistics'),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "heatmap"}, {"type": "table"}]]
    )
    
    # 1. Geographic layout
    edge_x, edge_y = [], []
    for node in network.nodes:
        for neighbor in node.neighbors:
            edge_x.extend([node.x, neighbor.x, None])
            edge_y.extend([node.y, neighbor.y, None])
    
    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=1, color='lightgray'),
        hoverinfo='none',
        showlegend=False
    ), row=1, col=1)
    
    # Add nodes
    node_x = [node.x for node in network.nodes]
    node_y = [node.y for node in network.nodes]
    node_text = [f"EUI-64: {node.eui64}<br>Position: ({node.x:.1f}, {node.y:.1f})<br>Range: {node.communication_range:.1f}<br>Neighbors: {len(node.neighbors)}" 
                 for node in network.nodes]
    node_colors = [len(node.neighbors) for node in network.nodes]
    
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(
            size=[len(node.neighbors) * 3 + 10 for node in network.nodes],
            color=node_colors,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Connections")
        ),
        text=node_text,
        hoverinfo='text',
        name='IoT Nodes'
    ), row=1, col=1)
    
    # 2. Force-directed layout
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # Force-directed edges
    edge_x_force, edge_y_force = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x_force.extend([x0, x1, None])
        edge_y_force.extend([y0, y1, None])
    
    fig.add_trace(go.Scatter(
        x=edge_x_force, y=edge_y_force,
        mode='lines',
        line=dict(width=1, color='lightblue'),
        hoverinfo='none',
        showlegend=False
    ), row=1, col=2)
    
    # Force-directed nodes
    node_x_force = [pos[node.eui64][0] for node in network.nodes]
    node_y_force = [pos[node.eui64][1] for node in network.nodes]
    
    fig.add_trace(go.Scatter(
        x=node_x_force, y=node_y_force,
        mode='markers',
        marker=dict(
            size=[len(node.neighbors) * 3 + 10 for node in network.nodes],
            color=node_colors,
            colorscale='Plasma',
            showscale=False
        ),
        text=node_text,
        hoverinfo='text',
        name='Force Layout'
    ), row=1, col=2)
    
    # 3. Connectivity heatmap
    # Create adjacency matrix
    node_ids = [node.eui64 for node in network.nodes]
    adj_matrix = np.zeros((len(node_ids), len(node_ids)))
    
    for i, node1 in enumerate(network.nodes):
        for j, node2 in enumerate(network.nodes):
            if node2 in node1.neighbors:
                adj_matrix[i][j] = 1
    
    fig.add_trace(go.Heatmap(
        z=adj_matrix,
        x=[f"Node {i+1}" for i in range(len(node_ids))],
        y=[f"Node {i+1}" for i in range(len(node_ids))],
        colorscale='Blues',
        showscale=False
    ), row=2, col=1)
    
    # 4. Network statistics table
    analysis = analyze_network_topology(G)
    
    stats_data = [
        ['Total Nodes', analysis.get('nodes', 0)],
        ['Total Connections', analysis.get('edges', 0)],
        ['Network Density', f"{analysis.get('density', 0):.3f}"],
        ['Connected', 'Yes' if analysis.get('is_connected', False) else 'No'],
        ['Components', analysis.get('num_components', 0)],
        ['Average Clustering', f"{analysis.get('average_clustering', 0):.3f}"],
    ]
    
    if analysis.get('is_connected', False):
        stats_data.extend([
            ['Diameter', analysis.get('diameter', 'N/A')],
            ['Avg Path Length', f"{analysis.get('average_shortest_path', 0):.3f}"]
        ])
    
    fig.add_trace(go.Table(
        header=dict(values=['Metric', 'Value'],
                   fill_color='lightblue',
                   align='left'),
        cells=dict(values=[[row[0] for row in stats_data],
                          [row[1] for row in stats_data]],
                  fill_color='white',
                  align='left')
    ), row=2, col=2)
    
    # Update layout
    fig.update_layout(
        title_text="Interactive IoT Network Visualization",
        showlegend=True,
        height=800,
        template='plotly_white'
    )
    
    if output_file:
        fig.write_html(output_file)
        print(f"Interactive visualization saved to {output_file}")
    else:
        fig.show()


def print_centrality_analysis(network: IoTNetwork) -> None:
    """Print detailed centrality analysis."""
    G = create_networkx_graph(network)
    if G is None:
        return
    
    analysis = analyze_network_topology(G)
    
    print(f"\nCentrality Analysis:")
    print(f"=" * 50)
    
    # Top nodes by different centrality measures
    centrality_measures = ['degree_centrality', 'betweenness_centrality', 
                          'closeness_centrality', 'eigenvector_centrality']
    
    for measure in centrality_measures:
        if measure in analysis:
            print(f"\nTop 5 nodes by {measure.replace('_', ' ').title()}:")
            sorted_nodes = sorted(analysis[measure].items(), 
                                key=lambda x: x[1], reverse=True)[:5]
            for i, (node_id, score) in enumerate(sorted_nodes, 1):
                # Find the actual node to get position info
                node = network.get_node_by_eui64(node_id)
                pos_info = f"({node.x:.1f}, {node.y:.1f})" if node else "N/A"
                print(f"  {i}. {node_id} - Score: {score:.3f} - Pos: {pos_info}")


def main():
    """Main function for professional network visualization."""
    parser = argparse.ArgumentParser(description='Professional IoT network visualization')
    parser.add_argument('input_file', help='Input JSON file containing network data')
    parser.add_argument('-m', '--matplotlib', action='store_true',
                       help='Create advanced matplotlib visualization')
    parser.add_argument('-p', '--plotly', action='store_true',
                       help='Create interactive plotly visualization')
    parser.add_argument('-c', '--centrality', action='store_true',
                       help='Show centrality analysis')
    parser.add_argument('-o', '--output', 
                       help='Output file for visualization')
    parser.add_argument('-l', '--layout', default='spring',
                       choices=['spring', 'circular', 'kamada_kawai'],
                       help='Layout algorithm for matplotlib (default: spring)')
    parser.add_argument('-s', '--style', default='modern',
                       choices=['modern', 'classic'],
                       help='Visualization style (default: modern)')
    
    args = parser.parse_args()
    
    # If no visualization options specified, show all
    if not (args.matplotlib or args.plotly or args.centrality):
        args.matplotlib = True
        args.plotly = True
        args.centrality = True
    
    try:
        # Load network
        print(f"Loading network from {args.input_file}...")
        network = IoTNetwork.load_from_file(args.input_file)
        print(f"Network loaded successfully: {len(network)} nodes")
        
        # Centrality analysis
        if args.centrality:
            print_centrality_analysis(network)
        
        # Matplotlib visualization
        if args.matplotlib:
            print("\nGenerating advanced matplotlib visualization...")
            output_file = f"{args.output}_matplotlib.png" if args.output else None
            visualize_matplotlib_advanced(network, output_file, args.layout, args.style)
        
        # Plotly visualization
        if args.plotly:
            print("\nGenerating interactive plotly visualization...")
            output_file = f"{args.output}_interactive.html" if args.output else None
            visualize_plotly_interactive(network, output_file)
            
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()