# IoT Network Visualizer

A comprehensive Python-based system for modeling, generating, and visualizing IoT networks with 2D positioning, range-based connectivity, and IEEE EUI-64 identifiers.

## Features

### Core Components
- **IoT Node Class**: Represents nodes with 2D coordinates, IEEE EUI-64 identifiers, and communication ranges
- **Network Generation**: Create random networks with configurable parameters
- **Web Visualization**: Interactive browser-based network visualization
- **Professional Analytics**: Advanced network analysis with NetworkX, matplotlib, and plotly

### Web Application Features
- 🌐 **Interactive D3.js Visualization**: Drag, zoom, and explore networks
- 📊 **Real-time Statistics**: Network density, connectivity distribution, centrality measures
- 🎨 **Professional UI**: Bootstrap-based responsive design
- 📁 **File Management**: Upload, generate, and export network configurations
- 🔍 **Node Details**: Click nodes to view detailed information and connections
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### 1. Setup Environment
```bash
python3 -m venv iot_venv
source iot_venv/bin/activate
pip install -r requirements.txt
```

### 2. Generate Sample Network
```bash
python3 generate_network.py 50 -w 400 --height 400 --min-range 60 --max-range 100 -o sample_network.json
```

### 3. Start Web Application
```bash
python3 app.py
```

Visit http://localhost:5000 in your browser.

### 4. Command Line Visualization (Optional)
```bash
# Basic ASCII visualization
python3 visualize_network.py sample_network.json --ascii

# Professional matplotlib/plotly visualization
python3 visualize_network_pro.py sample_network.json --matplotlib --plotly
```

## Usage Examples

### Generate Networks
```bash
# Small dense network
python3 generate_network.py 25 -w 300 --height 300 --min-range 80 --max-range 120

# Large sparse network  
python3 generate_network.py 100 -w 1000 --height 1000 --min-range 30 --max-range 80

# Custom network with seed for reproducibility
python3 generate_network.py 50 --seed 42 -o reproducible_network.json
```

### Web Interface
1. **Load Sample**: Click "Load Sample" to use an existing network
2. **Upload**: Upload your own JSON network file
3. **Generate**: Create new random networks with custom parameters
4. **Interact**: 
   - Click and drag nodes to reposition
   - Zoom and pan the visualization
   - Click nodes to view detailed information
   - Toggle labels and range circles
5. **Export**: Download current network as JSON

## Network Format

Networks are stored as JSON files with this structure:
```json
{
  "nodes": [
    {
      "eui64": "XX-XX-XX-XX-XX-XX-XX-XX",
      "x": 123.45,
      "y": 678.90,
      "communication_range": 100.0,
      "neighbors": ["YY-YY-YY-YY-YY-YY-YY-YY"]
    }
  ],
  "total_nodes": 50,
  "total_connections": 125
}
```

## File Structure

```
iot-network-visualizer/
├── iot_node.py                 # Core IoT node and network classes
├── generate_network.py         # Network generation script
├── visualize_network.py        # ASCII/basic visualization
├── visualize_network_pro.py    # Professional matplotlib/plotly viz
├── app.py                      # Flask web application
├── templates/
│   └── index.html              # Web interface template
├── static/
│   ├── css/style.css           # Styling
│   └── js/
│       ├── network-visualizer.js  # D3.js visualization
│       └── app.js              # Web app logic
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Technical Details

### IoT Node Features
- **IEEE EUI-64 Identifiers**: Globally unique 64-bit identifiers
- **2D Positioning**: Euclidean coordinates for geographic modeling
- **Range-based Connectivity**: Automatic neighbor detection based on communication range
- **Bidirectional Links**: Symmetric connectivity between nodes

### Web Technology Stack
- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, D3.js v7
- **Visualization**: Interactive force-directed graphs
- **Analytics**: NetworkX for graph analysis

### Network Analysis
- Connectivity distribution
- Network density and clustering
- Centrality measures (degree, betweenness, closeness, eigenvector)
- Connected components analysis
- Path length calculations

## API Endpoints

The web application provides REST API endpoints:

- `GET /` - Main web interface
- `POST /upload` - Upload network file
- `GET /load_sample` - Load sample network
- `GET /api/network_data` - Get current network for visualization
- `GET /api/network_stats` - Get comprehensive statistics
- `GET /api/node_details/<id>` - Get detailed node information
- `POST /api/generate_network` - Generate new random network
- `GET /api/export_network` - Export current network

## Contributing

This is a defensive security tool for IoT network analysis and visualization. Feel free to extend the functionality for legitimate research and defensive purposes.

## License

Open source - use responsibly for defensive security research and education.