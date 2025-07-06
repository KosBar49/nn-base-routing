"""
IoT Network Routing Visualization and Analysis Framework

A comprehensive Python package for generating, analyzing, and visualizing
IoT network topologies with interactive web-based exploration.
"""

__version__ = "1.0.0"
__author__ = "IoT Network Team"
__email__ = "team@iot-network.dev"

from .core.network import IoTNetwork
from .core.node import IoTNode
from .core.generator import generate_random_network

__all__ = [
    "IoTNetwork",
    "IoTNode", 
    "generate_random_network",
]
