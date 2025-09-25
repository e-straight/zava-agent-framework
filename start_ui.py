#!/usr/bin/env python3
"""
Convenience script to start the Zava Clothing Concept Analysis web interface.

This script provides a simple way to launch the web-based UI for
analyzing clothing concept submissions at Zava.
"""

import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    import uvicorn
    from backend import app

    def main():
        """Start the Zava concept analysis web interface."""
        print("🎨 Zava Clothing Concept Analysis System")
        print("=" * 50)
        print("🚀 Starting web interface...")
        print("🌐 Access at: http://localhost:8000")
        print("📱 Real-time updates via WebSocket")
        print("Press Ctrl+C to stop")
        print("=" * 50)

        # Start the FastAPI server
        uvicorn.run(
            app,
            host="127.0.0.1",  # Localhost only for security
            port=8000,
            log_level="info",
            reload=False  # Set to True for development
        )

    if __name__ == "__main__":
        main()

except ImportError as e:
    print("ERROR: Missing required dependencies for web interface:")
    print(f"   {e}")
    print("\n💡 To install required packages:")
    print("   pip install fastapi uvicorn[standard]")
    print("\n   Or use uv (recommended):")
    print("   uv sync")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Failed to start web interface: {e}")
    sys.exit(1)