# Scenario Folder Structure and Format

This folder contains YAML scenario files for automated agent/world behavior testing. Scenarios are organized by complexity into three tiers:

## Scenario YAML Format

Each scenario YAML should define:
- **world**: World name, year, and a list of places (with capabilities and optional inventory)
- **agents**: List of agents, each with:
  - name, place, job, values, goals, traits, and physio (hunger, energy, etc.)

### Example
```yaml
world:
  name: ExampleWorld
  year: 2025
  places:
    - name: Kitchen
      capabilities: [food]
      inventory:
        - item_id: apple
          qty: 1
    - name: LivingRoom
      capabilities: []
agents:
  - name: HungryAgent
    place: Kitchen
    job: None
    values: [curiosity]
    goals: [exploration]
    traits:
      extraversion: 0.5
      openness: 0.5
      conscientiousness: 0.5
    physio:
      hunger: 0.95
      energy: 0.8
      stress: 0.2
      mood: neutral
      social: 0.5
      fun: 0.5
      hygiene: 0.8
      comfort: 0.8
      bladder: 0.8
```

## Tiers of Complexity

- **tier1_simple/**: Basic, single-agent or single-action scenarios. Test core needs, simple decisions, or one-step behaviors (e.g., eat, sleep, relax, explore, use bathroom, basic social interaction).
- **tier2_intermediate/**: Multi-agent, multi-step, or environment-interaction scenarios. Test scheduling, inventory transfer, social chains, or more complex needs/goals.
- **tier3_complex/**: Full simulation scenarios, emergent behavior, or edge cases. Test long-term planning, group dynamics, or rare/edge-case logic.

Each tier folder contains only scenarios of that complexity. Add a README to each tier for specific guidelines if needed.
