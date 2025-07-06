"""
Web application entry point for IoT Network Routing.
"""

import sys
from .app import create_app


def main():
    """Main entry point for the web application."""
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
                print(f"Invalid port: {sys.argv[i + 1]}")
                sys.exit(1)
    
    print(f"🚀 Starting IoT Network Routing Web Interface")
    print(f"   Server: http://localhost:{port}")
    print(f"   Debug mode: {debug}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)


if __name__ == "__main__":
    main()
