#!/usr/bin/env python3
"""
Test script to verify GUI integration with world and agent loading.
Tests the full workflow of loading a world and displaying agents.
"""

import sys
import os

# Set QT to use offscreen platform for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from scripts.visualization.sim_gui.sim_gui_main import SimMainWindow

def test_world_loading():
    """Test loading a world and agents in the GUI."""
    print("=" * 60)
    print("GUI World Loading Integration Test")
    print("=" * 60)
    print()
    
    print("1. Initializing QApplication...")
    app = QApplication(sys.argv)
    
    print("2. Creating main window...")
    window = SimMainWindow()
    window.show()
    print("   ✓ Window created")
    
    print("3. Checking available worlds...")
    worlds = window.world_manager.list_worlds()
    print(f"   ✓ Found {len(worlds)} worlds: {worlds}")
    
    if not worlds:
        print("   ✗ No worlds available for testing")
        return False
    
    print("4. Simulating world load...")
    test_world = worlds[0]
    print(f"   Loading: {test_world}")
    window.on_world_loaded(test_world)
    
    print("5. Verifying world state...")
    print(f"   - World is open: {window.world_is_open}")
    print(f"   - Selected world: {window.selected_world}")
    print(f"   - Number of agents: {len(window.agents)}")
    
    if not window.world_is_open:
        print("   ✗ World failed to load")
        return False
    
    if len(window.agents) == 0:
        print("   ⚠ Warning: No agents in world")
    else:
        print(f"   ✓ Loaded {len(window.agents)} agents")
        print("   Agent names:")
        for i, agent in enumerate(window.agents[:5]):  # Show first 5
            print(f"     {i+1}. {agent.persona.name}")
        if len(window.agents) > 5:
            print(f"     ... and {len(window.agents) - 5} more")
    
    print("6. Testing agent selection...")
    if window.agents:
        window.on_agent_selected(0)
        print("   ✓ Selected first agent")
    
    print("7. Checking menu panels...")
    for i, menu_panel in enumerate([window.sidebar_menu_panel, window.full_menu_panel]):
        agent_controls = menu_panel.get_agent_controls()
        list_count = agent_controls.agent_list.count()
        dropdown_count = agent_controls.agent_dropdown.count() - 1  # -1 for "All Agents"
        print(f"   Panel {i+1}: {list_count} in list, {dropdown_count} in dropdown")
        if list_count != len(window.agents):
            print(f"   ✗ Agent count mismatch!")
            return False
    print("   ✓ Agent controls populated correctly")
    
    print("8. Testing world close...")
    window.on_world_closed(test_world)
    print(f"   - World is open: {window.world_is_open}")
    print(f"   - Agents cleared: {len(window.agents) == 0}")
    if window.world_is_open or len(window.agents) > 0:
        print("   ✗ World failed to close properly")
        return False
    print("   ✓ World closed successfully")
    
    print()
    print("=" * 60)
    print("✓ All integration tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_world_loading()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
