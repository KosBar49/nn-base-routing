"""
Web application entry point for IoT Network Routing.
"""

import sys
from .app import create_app
from ..utils.logging_config import setup_logging, get_logger

logger = get_logger(__name__)


def main():
    """Main entry point for the web application."""
    # Setup logging
    setup_logging(level='INFO')
    
    app = create_app()
    
    # Check if we're in debug mode
    debug = "--debug" in sys.argv
    port = 5000
    
    # Parse port if provided
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
            except ValueError:
                logger.error("Invalid port: %s", sys.argv[i + 1])
                sys.exit(1)
    
    logger.info("🚀 Starting IoT Network Routing Web Interface")
    logger.info("   Server: http://localhost:%d", port)
    logger.info("   Debug mode: %s", debug)
    
    app.run(debug=debug, host='0.0.0.0', port=port)


if __name__ == "__main__":
    main()
