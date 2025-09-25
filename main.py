"""
Main entry point for Zava Clothing Concept Analysis System.

Starts the web-based user interface for analyzing clothing concepts.
"""

import sys


def main():
    """
    Main entry point - starts the web UI.
    """
    print("Starting Zava Clothing Concept Analysis System")
    start_web_ui()


def start_web_ui(port: int = 8000):
    """
    Start the FastAPI web interface.

    Args:
        port: Port number to run the server on
    """
    try:
        import uvicorn
        from backend import app

        print("Starting Zava Clothing Concept Analysis Web Interface...")
        print(f"Access the interface at: http://localhost:{port}")
        print("Real-time updates available via WebSocket")
        print("Press Ctrl+C to stop the server")

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )

    except ImportError:
        print("ERROR: FastAPI dependencies not available.")
        print("   Install with: pip install fastapi uvicorn[standard]")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to start web interface: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()