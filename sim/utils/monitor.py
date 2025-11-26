"""
monitor.py

Provides hooks for monitoring agent behavior, resource flows, and world events during simulation runs.
"""
def log_agent_action(agent, action, tick):
    print(f"[Tick {tick}] Agent {getattr(agent, 'persona', getattr(agent, 'name', 'Unknown')).name} performed action: {action}")

def log_resource_flow(entity, item_id, qty, tick):
    print(f"[Tick {tick}] {entity} resource flow: {item_id} x{qty}")

def log_world_event(event, tick):
    print(f"[Tick {tick}] World event: {event}")
