"""
AgentInventory module for managing agent inventory and possessions.
Handles adding, removing, and querying items held by the agent.
"""

class AgentInventory:
    def __init__(self):
        self.items = {}

    def add(self, item, quantity=1):
        return self.add_item(item, quantity)

    def remove(self, item, quantity=1):
        prev_qty = self.get_quantity(item)
        self.remove_item(item, quantity)
        return self.get_quantity(item) < prev_qty

    def has(self, item, quantity=1):
        return self.get_quantity(item) >= quantity

    def add_item(self, item, quantity=1):
        item_id = getattr(item, 'id', item)
        self.items[item_id] = self.items.get(item_id, 0) + quantity

    def remove_item(self, item, quantity=1):
        item_id = getattr(item, 'id', item)
        if item_id in self.items:
            self.items[item_id] -= quantity
            if self.items[item_id] <= 0:
                del self.items[item_id]

    def has_item(self, item):
        item_id = getattr(item, 'id', item)
        return item_id in self.items

    def get_quantity(self, item):
        item_id = getattr(item, 'id', item)
        return self.items.get(item_id, 0)

    def all_items(self):
        return self.items.copy()

    def serialize(self):
        """Return a serializable copy of inventory items."""
        return self.items.copy()

    def load(self, data):
        """Load inventory items from a dict."""
        if isinstance(data, dict):
            self.items = data.copy()
