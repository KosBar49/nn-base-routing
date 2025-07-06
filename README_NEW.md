# IoT Network Routing - Professional Edition

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive Python framework for generating, analyzing, and visualizing IoT network topologies with interactive web-based exploration.

## 🚀 Features

- **Network Generation**: Create random IoT networks with configurable parameters
- **Interactive Visualization**: Web-based D3.js visualization with 9-level color coding
- **Comprehensive Analysis**: Statistical analysis and network metrics
- **Professional Architecture**: Modern Python package structure
- **Multiple Interfaces**: CLI, Web UI, and programmatic API
- **Export/Import**: JSON-based network serialization

## 📦 Installation

### From Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/iot-team/iot-network-routing.git
cd iot-network-routing

# Install in development mode with all dependencies
pip install -e ".[dev,web,visualization]"
```

### Production Install

```bash
pip install iot-network-routing[web,visualization]
```

## 🏗️ Project Structure

```
iot-network-routing/
├── src/iot_network_routing/     # Main package source
│   ├── core/                    # Core network logic
│   │   ├── node.py             # IoT node implementation
│   │   ├── network.py          # Network management
│   │   └── generator.py        # Network generation
│   ├── web/                     # Web interface
│   │   ├── app.py              # Flask application
│   │   └── run.py              # Web server entry point
│   ├── cli/                     # Command line interface
│   └── utils/                   # Utility modules
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── templates/                   # HTML templates
├── static/                      # Static web assets
├── examples/                    # Sample networks
├── docs/                        # Documentation
└── scripts/                     # Utility scripts
```

## 🛠️ Quick Start

### Command Line Interface

```bash
# Generate a network with 25 nodes
iot-network-cli 25 --output my_network.json --max-range 150

# Generate a dense network
iot-network-cli 50 --width 300 --height 300 --max-range 200
```

### Web Interface

```bash
# Start the web server
iot-network-web

# With custom port and debug mode
iot-network-web --port 8080 --debug
```

Visit `http://localhost:5000` to access the interactive visualization.

### Programmatic Usage

```python
from iot_network_routing import IoTNetwork, generate_random_network

# Generate a random network
network = generate_random_network(
    n_nodes=30,
    map_width=500,
    map_height=500,
    max_range=120
)

# Analyze the network
print(f"Generated {len(network)} nodes with {network.get_connection_count()} connections")

# Save to file
network.save_to_file("my_network.json")

# Load from file
loaded_network = IoTNetwork.load_from_file("my_network.json")
```

## 🎨 Color Legend System

The visualization uses a 9-level color coding system for node connectivity:

- 🔴 **Red** - Isolated (0 connections)
- 🟠 **Orange** - Very Low (1 connection)
- 🟡 **Yellow** - Low (2 connections)
- 🟢 **Green** - Medium (3 connections)
- 🔵 **Blue** - Good (4 connections)
- 🟣 **Purple** - High (5 connections)
- 🩷 **Pink** - Very High (6 connections)
- 🤎 **Brown** - Extremely High (7 connections)
- 🔘 **Blue Grey** - Maximum (8+ connections)

## 📊 Network Analysis

### Statistics API

```python
from iot_network_routing.utils import NetworkStatistics

# Create statistics analyzer
stats = NetworkStatistics(network)

# Get basic statistics
basic = stats.basic_stats()
print(f"Network density: {basic['network_density']}")

# Get connectivity distribution
distribution = stats.connectivity_distribution()

# Generate full report
report = stats.full_report()
```

### Visualization API

```python
from iot_network_routing.utils import NetworkVisualizer

# Create visualizer
viz = NetworkVisualizer(network)

# Print ASCII map
ascii_map = viz.ascii_map(width=80, height=40)
for line in ascii_map:
    print(line)

# Create matplotlib plot
viz.matplotlib_plot("network_plot.png")
```

## 🧪 Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# All quality checks
make check-all
```

### Building Package

```bash
# Clean and build
make build

# Install development version
make install-dev
```

## 📈 Performance

- **Generation**: Can generate networks with 1000+ nodes in seconds
- **Visualization**: Optimized D3.js rendering for networks up to 500 nodes
- **Memory**: Efficient node storage with O(n) memory complexity
- **Connections**: Bidirectional connection validation with O(n²) complexity

## 🔧 Configuration

### Web Interface Configuration

```python
from iot_network_routing.web import create_app

# Custom configuration
config = {
    'DEBUG': True,
    'SECRET_KEY': 'your-secret-key'
}

app = create_app(config)
```

### CLI Configuration

Environment variables:
- `IOT_NETWORK_DEFAULT_RANGE`: Default communication range
- `IOT_NETWORK_DEFAULT_SIZE`: Default map size

## 📚 API Reference

### Core Classes

- **`IoTNode`**: Individual network node with EUI-64 identifier
- **`IoTNetwork`**: Network container with connection management
- **`NetworkStatistics`**: Statistical analysis utilities
- **`NetworkVisualizer`**: Visualization and rendering utilities

### Key Methods

- `generate_random_network()`: Create random networks
- `network.update_all_connections()`: Recalculate connections
- `network.validate_bidirectional_connections()`: Validate network integrity
- `network.save_to_file()` / `load_from_file()`: Persistence

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install development dependencies: `make install-dev`
4. Make changes and add tests
5. Run quality checks: `make check-all`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Recent Improvements

### v1.0.0 - Professional Edition

- ✅ **Simplified Connection Logic**: Removed min_range, uses only max_range
- ✅ **Enhanced Color System**: 9-level color coding with purple and additional colors
- ✅ **Professional Structure**: Modern Python package organization
- ✅ **Comprehensive Testing**: Unit and integration test suites
- ✅ **Developer Tools**: Makefile, pre-commit hooks, type checking
- ✅ **Multiple Interfaces**: CLI, Web UI, and programmatic API
- ✅ **Documentation**: Complete API documentation and examples

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/iot-team/iot-network-routing/issues)
- **Documentation**: [Read the Docs](https://iot-network-routing.readthedocs.io/)
- **Email**: team@iot-network.dev

---

**Built with ❤️ for the IoT research community**
