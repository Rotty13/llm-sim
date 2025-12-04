"""
World Event Dispatcher for llm-sim

This module provides a generic event dispatcher for world events.
It allows subsystems (weather, scheduler, agent, place, etc.) to register event handlers,
and routes events to the appropriate handlers for processing.

Key Classes:
- WorldEventDispatcher: Central event router for simulation events.

LLM Usage: None
CLI Arguments: None
"""
from typing import Callable, Dict, List, Any

class WorldEventDispatcher:
    """
    Central dispatcher for world events. Handlers can be registered for event types.
    Events are routed to all handlers registered for their type.
    """
    def __init__(self):
        self.handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        """Register a handler for a specific event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def dispatch_event(self, event: Dict[str, Any]):
        """
        Dispatch an event to all registered handlers for its type.
        Event should have a 'type' key.
        """
        event_type = event.get('type')
        if not event_type:
            raise ValueError("Event must have a 'type' key.")
        for handler in self.handlers.get(event_type, []):
            handler(event)

# Example usage:
# dispatcher = WorldEventDispatcher()
# dispatcher.register_handler('weather', weather_system.handle_event)
# dispatcher.register_handler('festival', scheduler.handle_event)
# dispatcher.dispatch_event({'type': 'weather', 'event': 'storm', 'tick': 42})
