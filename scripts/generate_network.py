#!/usr/bin/env python3
"""
Backward compatibility script for network generation.
This script is deprecated. Use 'iot-network-cli' instead.
"""

import sys
import warnings
from src.iot_network_routing.cli.main import main

# Issue deprecation warning
warnings.warn(
    "This script is deprecated. Use 'iot-network-cli' command instead.",
    DeprecationWarning,
    stacklevel=2
)

if __name__ == "__main__":
    sys.exit(main())
