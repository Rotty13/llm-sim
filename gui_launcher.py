#!/usr/bin/env python3
"""
gui_launcher.py - Standalone launcher for the llm-sim GUI

This script provides a convenient entry point for launching the llm-sim graphical
user interface. It handles environment setup, error checking, and provides helpful
feedback if dependencies are missing.

Usage:
    python gui_launcher.py

Or make it executable and run directly:
    chmod +x gui_launcher.py
    ./gui_launcher.py

Requirements:
    - Python 3.8+
    - PyQt5
    - numpy
    - PyYAML
    - requests

LLM Usage: None
CLI Args: None
"""

import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing = []
    
    try:
        import PyQt5
    except ImportError:
        missing.append("PyQt5")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    try:
        import yaml
    except ImportError:
        missing.append("PyYAML")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    if missing:
        print("Error: Missing required dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nPlease install them with:")
        print(f"  pip install {' '.join(missing)}")
        print("\nOr install all requirements:")
        print("  pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main entry point for the GUI launcher."""
    print("=" * 60)
    print("llm-sim GUI Launcher")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✓ All dependencies found")
    print()
    
    # Add project root to path if needed
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        # Import GUI components
        print("Importing GUI components...")
        from PyQt5.QtWidgets import QApplication
        from scripts.visualization.sim_gui.sim_gui_main import SimMainWindow
        print("✓ GUI components loaded")
        print()
        
        # Initialize Qt Application
        print("Initializing Qt Application...")
        app = QApplication(sys.argv)
        app.setApplicationName("llm-sim")
        app.setOrganizationName("llm-sim")
        print("✓ Qt initialized")
        print()
        
        # Create main window
        print("Creating main window...")
        window = SimMainWindow()
        print("✓ Main window created")
        print()
        
        # Show window
        print("Showing GUI window...")
        window.show()
        print("✓ GUI displayed successfully")
        print()
        
        print("=" * 60)
        print("llm-sim GUI is now running")
        print("=" * 60)
        print()
        print("Quick start:")
        print("  1. Select a world from the dropdown")
        print("  2. Click 'Load World'")
        print("  3. Use simulation controls to start/pause/step")
        print("  4. View agents and world information in the panels")
        print()
        print("Close the window or press Ctrl+C to exit.")
        print()
        
        # Run the application event loop
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"\n✗ Import Error: {e}")
        print("\nMake sure you're running this from the llm-sim project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
