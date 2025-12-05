"""
test_event_dispatcher.py

Unit tests for WorldEventDispatcher in llm-sim.
Tests handler registration, event dispatch, and handler invocation.
"""
import pytest
from sim.world.event_dispatcher import WorldEventDispatcher


def test_handler_registration_and_dispatch():
    dispatcher = WorldEventDispatcher()
    called = {'flag': False, 'event_type': None}
    def handler(event):
        called['flag'] = True
        called['event_type'] = event['type']
    dispatcher.register_handler('test_event', handler)
    dispatcher.dispatch_event({'type': 'test_event', 'data': 123})
    assert called['flag']
    assert called['event_type'] == 'test_event'

def test_multiple_handlers():
    dispatcher = WorldEventDispatcher()
    calls = []
    def handler1(event):
        calls.append('h1')
    def handler2(event):
        calls.append('h2')
    dispatcher.register_handler('multi_event', handler1)
    dispatcher.register_handler('multi_event', handler2)
    dispatcher.dispatch_event({'type': 'multi_event'})
    assert 'h1' in calls
    assert 'h2' in calls

def test_no_handler():
    dispatcher = WorldEventDispatcher()
    # Should not raise error if no handler
    try:
        dispatcher.dispatch_event({'type': 'no_handler_event'})
    except Exception as e:
        pytest.fail(f"Dispatching with no handler raised: {e}")
