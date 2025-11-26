# Willowbrook (ExampleWorld)

This example world demonstrates a pre-1900 historical town simulation for llm-sim.

## Scenario
- **Year:** 1885
- **Town:** Willowbrook
- **Population:** 350
- **Features:** Town square, blacksmith, general store, church, schoolhouse
- **Personas:**
  - Abigail (schoolteacher)
  - Thomas (blacksmith)
  - Mary (general store owner)
  - Samuel (pastor)

## Files
- `city.yaml`: Town features and population
- `personas.yaml`: Key personas and their roles/traits
- `names.yaml`: Period-appropriate names
- `world.yaml`: World metadata and scenario
- `conversation_logs/`: Folder for simulation logs

## How to Run
1. List available worlds:
   ```
   python scripts/world_cli.py list
   ```
2. Show info for Willowbrook:
   ```
   python scripts/world_cli.py info ExampleWorld
   ```
3. Run a simulation:
   ```
   python scripts/world_cli.py run ExampleWorld --ticks 100
   ```

## Customization
- Edit the YAML files to add new personas, change town features, or adjust the scenario.
- Use the CLI to create, delete, or run worlds as needed.

---
This template is designed for onboarding and can be duplicated to create new historical worlds.