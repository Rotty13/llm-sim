# llm-sim GUI Architecture Diagram

## Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SimMainWindow                                │
│                      (QMainWindow 1600x900)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    QStackedWidget                            │   │
│  │                   (View Switcher)                            │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                              │   │
│  │  VIEW 0: Sidebar Only (World Selection)                     │   │
│  │  ┌────────────────────────────────────────────────────┐    │   │
│  │  │           MainMenuPanel                            │    │   │
│  │  │  ┌──────────────────────────────────────────────┐ │    │   │
│  │  │  │     WorldControlsPanel                       │ │    │   │
│  │  │  │  - World Dropdown                            │ │    │   │
│  │  │  │  - Load/Delete Buttons                       │ │    │   │
│  │  │  └──────────────────────────────────────────────┘ │    │   │
│  │  │  (Other panels hidden)                             │    │   │
│  │  └────────────────────────────────────────────────────┘    │   │
│  │                                                              │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │                                                              │   │
│  │  VIEW 1: Full Layout (Simulation)                           │   │
│  │  ┌────────────────────────────────────────────────────┐    │   │
│  │  │          Vertical Splitter                         │    │   │
│  │  │  ┌──────────────────────────────────────────────┐ │    │   │
│  │  │  │     Horizontal Splitter                      │ │    │   │
│  │  │  │  ┌────────┬────────────┬────────────────┐   │ │    │   │
│  │  │  │  │  Menu  │   Graph    │   Info Panels  │   │ │    │   │
│  │  │  │  │  Panel │   Widget   │                │   │ │    │   │
│  │  │  │  │  300px │   800px    │     400px      │   │ │    │   │
│  │  │  │  └────────┴────────────┴────────────────┘   │ │    │   │
│  │  │  │                                              │ │    │   │
│  │  │  │  700px                                       │ │    │   │
│  │  │  └──────────────────────────────────────────────┘ │    │   │
│  │  │  ┌──────────────────────────────────────────────┐ │    │   │
│  │  │  │     LogsOutputPanel (200px)                  │ │    │   │
│  │  │  └──────────────────────────────────────────────┘ │    │   │
│  │  └────────────────────────────────────────────────────┘    │   │
│  │                                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Detailed Component Breakdown

### MainMenuPanel (Left Sidebar)
```
┌──────────────────────────────┐
│    WorldControlsPanel        │
│  ┌────────────────────────┐  │
│  │ World: [Dropdown]      │  │
│  │ [Load] [Delete]        │  │
│  │ OR                     │  │
│  │ Loaded: World_0        │  │
│  │ [Save] [Close]         │  │
│  └────────────────────────┘  │
├──────────────────────────────┤
│  SimulationControlsPanel     │
│  ┌────────────────────────┐  │
│  │ Status: Tick: 42       │  │
│  │ [▶Start] [⏸Pause]     │  │
│  │ [⏹Stop] [⏭Step]       │  │
│  │ Tick Speed: [1.0s]     │  │
│  │ Max Ticks: [1000]      │  │
│  └────────────────────────┘  │
├──────────────────────────────┤
│   AgentControlsPanel         │
│  ┌────────────────────────┐  │
│  │ Agents:                │  │
│  │ ┌────────────────────┐ │  │
│  │ │ - Emilie LaFleur   │ │  │
│  │ │ - Auguste Dumont   │ │  │
│  │ │ - Sophie Dupont    │ │  │
│  │ └────────────────────┘ │  │
│  │ Quick Select:          │  │
│  │ [All Agents ▼]        │  │
│  │ [✏Edit] [➕Add] [➖]   │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```

### SimGraphWidget (Center)
```
┌────────────────────────────────┐
│   Interactive Graph View       │
│                                 │
│     ◯ Place 1    ◯ Place 2    │
│           ╲        ╱           │
│            ╲      ╱            │
│             ◯ Hub              │
│            ╱      ╲            │
│           ╱        ╲           │
│     ◯ Place 3    ◯ Place 4    │
│                                 │
│  Controls:                      │
│  - Mouse wheel: Zoom           │
│  - Click+Drag: Pan             │
│  - (Future: Click agent)       │
└────────────────────────────────┘
```

### Info Panels (Right)
```
┌────────────────────────────────┐
│   AgentInfoWidget              │
│  ┌──────────────────────────┐  │
│  │ Name: Emilie LaFleur     │  │
│  │ Age: 28                  │  │
│  │ Job: Baker               │  │
│  │ City: Paris              │  │
│  │ Bio: ...                 │  │
│  │ Values: curiosity, ...   │  │
│  │ Goals: ...               │  │
│  │ Traits: ...              │  │
│  └──────────────────────────┘  │
├────────────────────────────────┤
│   WorldInfoWidget              │
│  ┌──────────────────────────┐  │
│  │ Places in world:         │  │
│  │ - Home: {...}           │  │
│  │ - Bakery: {...}         │  │
│  │ - Park: {...}           │  │
│  │ - ...                    │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
```

### LogsOutputPanel (Bottom)
```
┌──────────────────────────────────────────────────┐
│   Simulation Output / Logs                       │
│  ┌────────────────────────────────────────────┐  │
│  │ [GUI] llm-sim GUI initialized              │  │
│  │ [GUI] Loading world: World_0               │  │
│  │ [GUI] Loaded 20 agents                     │  │
│  │ [GUI] World 'World_0' loaded successfully  │  │
│  │ [GUI] Selected agent: Emilie LaFleur       │  │
│  │ [Sim] Starting simulation                  │  │
│  │ [Sim] Tick: 1                              │  │
│  │ ...                                        │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## Signal Flow

```
User Action → Qt Signal → Main Window Handler → Controller/Manager → Update Display

Example: Load World
──────────────────
1. User clicks "Load World"
   ↓
2. WorldControlsPanel.load_btn.clicked signal
   ↓
3. SimMainWindow.on_world_loaded(world_name)
   ↓
4. WorldManager.load_agents_with_schedules(world_name)
   ↓
5. AgentControlsPanel.load_agents(agents)
   ↓
6. Display updates automatically

Example: Start Simulation
────────────────────────
1. User clicks "▶ Start"
   ↓
2. SimulationControlsPanel.start_btn.clicked signal
   ↓
3. SimMainWindow.on_simulation_start()
   ↓
4. SimulationController.start()
   ↓
5. QTimer starts (500ms interval)
   ↓
6. SimMainWindow._update_simulation_display()
   ↓
7. Display refreshes every 500ms
```

## State Management

```
Application States
────────────────

State 0: No World Loaded
├─ View: Sidebar Only
├─ Available: World selection, load, delete
└─ Disabled: Simulation controls, agent controls

State 1: World Loaded
├─ View: Full Layout
├─ Available: All panels visible, simulation controls, agent selection
└─ Disabled: World selection (must close first)

State 2: Simulation Running
├─ View: Full Layout (active)
├─ Available: Pause, stop, step
├─ Disabled: Start (already running)
└─ Updates: Real-time via timer

State 3: Simulation Paused
├─ View: Full Layout (frozen)
├─ Available: Resume, stop, step
└─ Disabled: Start, pause
```

## Data Flow

```
WorldManager
     ↓
     ├─→ load_agents_with_schedules()
     │       ↓
     │   [Agent Objects]
     │       ↓
     ├─→ AgentControlsPanel.load_agents()
     │       ↓
     │   List & Dropdown Population
     │
     └─→ load_places()
             ↓
         WorldInfoWidget.display_world()

SimulationController
     ↓
     ├─→ start() / pause() / resume() / stop()
     │       ↓
     │   Update internal state
     │
     └─→ get_state()
             ↓
         SimMainWindow._update_simulation_display()
             ↓
         Status Label Updates
```

## Thread Model

```
Main Thread (Qt Event Loop)
     │
     ├─→ GUI Updates (always here)
     │
     └─→ Signal/Slot Connections
         
Simulation Thread (if running)
     │
     ├─→ SimulationController._run_loop()
     │   (tick logic, agent updates)
     │
     └─→ Thread-safe via locks
     
Update Timer (Main Thread)
     │
     └─→ Fires every 500ms when sim running
         ├─→ Fetches state (thread-safe)
         └─→ Updates display widgets
```

## Extension Points

```
Future Enhancements (Hooks Ready)
────────────────────────────────

1. Real-time Agent Visualization
   Hook: SimGraphWidget.paintEvent()
   Data: SimulationController.get_state()['agents']

2. Agent Editor
   Hook: AgentControlsPanel.edit_btn.clicked
   Dialog: New QDialog with agent forms

3. World Editor
   Hook: WorldControlsPanel (new button)
   Dialog: Place/config editor

4. Metrics Dashboard
   New Panel: MetricsDashboardWidget
   Location: Right panel or new tab

5. Save/Load State
   Hook: WorldControlsPanel.save_btn
   Backend: World.serialize() (already exists)
```

---

This architecture provides:
- Clear separation of concerns
- Modular, extensible design
- Thread-safe operations
- Signal-based loose coupling
- Professional user experience
