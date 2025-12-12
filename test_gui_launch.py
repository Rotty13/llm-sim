#!/usr/bin/env python3
"""
Quick test script to launch the GUI in headless mode for testing.
This script will attempt to show the GUI window.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set QT to use offscreen platform for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt5.QtWidgets import QApplication
from scripts.visualization.sim_gui.sim_gui_main import SimMainWindow

def test_gui_launch():
    """Test launching the GUI."""
    print("Initializing QApplication...")
    app = QApplication(sys.argv)
    
    print("Creating main window...")
    window = SimMainWindow()
    
    print("Showing window...")
    window.show()
    
    print("GUI launched successfully!")
    print(f"Window title: {window.windowTitle()}")
    print(f"Window size: {window.width()}x{window.height()}")
    print(f"World manager initialized: {window.world_manager is not None}")
    print(f"Available worlds: {window.world_manager.list_worlds()}")
    
    # Don't actually run the event loop in headless mode
    # sys.exit(app.exec_())
    
    return True

if __name__ == "__main__":
    success = test_gui_launch()
    if success:
        print("\n✓ GUI test passed!")
        sys.exit(0)
    else:
        print("\n✗ GUI test failed!")
        sys.exit(1)
