from __future__ import annotations
from herodungeon.core.events import AlgorithmEvent, EventRecorder
from herodungeon.core.models import Item


class InventoryFullError(ValueError):
    pass


class ItemNotFoundError(KeyError):
    pass


class Inventory:
    def __init__(self, capacity: int, recorder: EventRecorder | None = None):
        self.capacity = capacity
        if recorder is None:
            self.recorder = EventRecorder()
        else:
            self.recorder = recorder
        self._items: list[Item] = []
        if self.capacity <= 0:
            raise ValueError("capacity must be positive")

    @property
    def items(self) -> tuple[Item, ...]:
        return tuple(self._items)

    def add(self, item: Item) -> AlgorithmEvent:
        """Append `item` if there is room; otherwise reject and raise."""
        # 先判断背包容量
        if len(self._items) >= self.capacity:
            evt = self.recorder.emit("reject", self)
            raise InventoryFullError("inventory is full")

        # 检查重复item_id
        for existing in self._items:
            if existing.item_id == item.item_id:
                raise ValueError("duplicate item id")

        self._items.append(item)
        evt = self.recorder.emit("insert", self)
        return evt

    def remove(self, item_id: str) -> Item:
        """Find `item_id` from the front, emit compare/remove/miss, and return it."""
        for idx, it in enumerate(self._items):
            self.recorder.emit("compare", self)
            if it.item_id == item_id:
                found_item = self._items.pop(idx)
                self.recorder.emit("remove", self)
                return found_item
        self.recorder.emit("miss", self)
        raise ItemNotFoundError(f"item {item_id} not found")

    def total_value(self) -> int:
        """Return the sum of item values currently in the bag."""
        return sum(item.value for item in self._items)
