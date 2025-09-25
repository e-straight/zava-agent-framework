"""
Main entry point for Zava Clothing Concept Analysis System.

This script provides a simple command-line interface for running the
Zava clothing concept evaluation workflow directly or starting the web UI.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def main():
    """
    Main entry point with command-line argument parsing.
    """
    parser = argparse.ArgumentParser(
        description="Zava Clothing Concept Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --ui                           # Start web interface
  python main.py --analyze concept.pptx        # Analyze concept directly
  python main.py --help                        # Show this help message

For the web interface, navigate to http://localhost:8000 after startup.
        """
    )

    parser.add_argument(
        "--ui",
        action="store_true",
        help="Start the web-based user interface"
    )

    parser.add_argument(
        "--analyze",
        type=str,
        metavar="FILE",
        help="Analyze a clothing concept file directly (PowerPoint .pptx)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for web interface (default: 8000)"
    )

    args = parser.parse_args()

    if args.ui:
        start_web_ui(port=args.port)
    elif args.analyze:
        asyncio.run(analyze_concept_file(args.analyze))
    else:
        # Default to web UI if no arguments provided
        print("🎨 Starting Zava Clothing Concept Analysis System")
        print("🌐 No specific action requested, launching web interface...")
        start_web_ui(port=args.port)


def start_web_ui(port: int = 8000):
    """
    Start the FastAPI web interface.

    Args:
        port: Port number to run the server on
    """
    try:
        import uvicorn
        from backend import app

        print("🎨 Starting Zava Clothing Concept Analysis Web Interface...")
        print(f"🌐 Access the interface at: http://localhost:{port}")
        print("📱 Real-time updates available via WebSocket")
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


async def analyze_concept_file(file_path: str):
    """
    Analyze a clothing concept file directly via command line.

    Args:
        file_path: Path to the PowerPoint file to analyze
    """
    try:
        from core.workflow_manager import ZavaConceptWorkflowManager

        # Validate file exists and is correct format
        concept_file = Path(file_path)
        if not concept_file.exists():
            print(f"ERROR: File not found: {file_path}")
            sys.exit(1)

        if not concept_file.suffix.lower() == '.pptx':
            print(f"ERROR: Invalid file format. Please provide a .pptx PowerPoint file.")
            print(f"   Received: {concept_file.suffix}")
            sys.exit(1)

        print("🎨 Zava Clothing Concept Analysis")
        print(f"📁 Analyzing: {concept_file.name}")
        print("=" * 60)

        # Create workflow manager with console output
        def console_progress(step: str, progress: int, step_data: dict = None):
            """Print progress updates to console."""
            bar_length = 30
            filled_length = int(bar_length * progress / 100)
            bar = "█" * filled_length + "▒" * (bar_length - filled_length)
            print(f"\r🔄 [{bar}] {progress:3d}% - {step}", end="", flush=True)

        def console_output(source: str, content: str, output_type: str = "text"):
            """Print analysis outputs to console."""
            icons = {
                "info": "ℹ️",
                "success": "SUCCESS",
                "warning": "WARNING",
                "error": "ERROR",
                "decision": "🤔"
            }
            icon = icons.get(output_type, "📝")
            print(f"\n{icon} {source}: {content}")

        def console_approval(question: str, context: str):
            """Handle approval requests via console input."""
            print("\n" + "=" * 60)
            print("🤔 ZAVA TEAM APPROVAL REQUIRED")
            print("=" * 60)
            print(f"Question: {question}")
            print("\nContext:")
            print(context[:500] + ("..." if len(context) > 500 else ""))
            print("=" * 60)

        def console_error(error: str):
            """Print errors to console."""
            print(f"\nERROR: {error}")

        # Initialize and run the workflow
        workflow_manager = ZavaConceptWorkflowManager(
            progress_callback=console_progress,
            output_callback=console_output,
            approval_callback=console_approval,
            error_callback=console_error
        )

        # Note: This is a simplified version - full approval workflow
        # requires the interactive web interface for human decisions
        print("NOTE: Command-line analysis has limited approval workflow.")
        print("   For full human approval process, use the web interface (--ui flag)")
        print()

        # Run the analysis
        result = await workflow_manager.analyze_clothing_concept(str(concept_file))

        # Display final result
        print("\n" + "=" * 60)
        if result == "APPROVED":
            print("🎉 CONCEPT APPROVED FOR DEVELOPMENT")
        elif result == "REJECTED":
            print("CONCEPT REJECTED")
        else:
            print(f"📊 ANALYSIS COMPLETED: {result}")
        print("=" * 60)

        # Look for generated report files
        import glob
        report_files = glob.glob("zava_*.md")
        if report_files:
            latest_report = max(report_files, key=lambda x: Path(x).stat().st_mtime)
            print(f"📄 Report generated: {latest_report}")

    except ImportError as e:
        print(f"ERROR: Missing required dependencies: {e}")
        print("   Please install the required packages and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()