"""M1 lesson 5: implement a LIFO undo stack.
Push/pop the newest operation. If max_depth is set, evict the oldest entry
before pushing a new one that would overflow.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterator
from herodungeon.core.events import AlgorithmEvent, EventRecorder
SOURCE = "m1.stack"


class StackEmptyError(IndexError):
    """Raised when popping or peeking an empty stack."""


@dataclass(slots=True)
class UndoStack:
    max_depth: int | None = None
    recorder: EventRecorder = field(default_factory=EventRecorder)
    _buffer: list[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.max_depth is not None and self.max_depth <= 0:
            raise ValueError("max_depth must be positive when provided")

    def __len__(self) -> int:
        return len(self._buffer)

    def __iter__(self) -> Iterator[Any]:
        return reversed(self._buffer)

    @property
    def is_empty(self) -> bool:
        return not self._buffer

    @property
    def items(self) -> tuple[Any, ...]:
        return tuple(self._buffer)

    def push(self, operation: Any) -> AlgorithmEvent:
        """Push to the top; evict the oldest item if max_depth is exceeded."""
        evicted = None
        # 栈已满，先驱逐最旧元素（buffer[0]）
        if self.max_depth is not None and len(self._buffer) >= self.max_depth:
            evicted = self._buffer.pop(0)
            self.recorder.emit(
                source=SOURCE,
                event_type="evict",
                payload={"evicted": evicted, "depth": len(self._buffer)}
            )
        # 压入新操作
        self._buffer.append(operation)
        evt = self.recorder.emit(
            source=SOURCE,
            event_type="push",
            payload={
                "operation": operation,
                "depth": len(self._buffer),
                "evicted": evicted
            }
        )
        return evt

    def pop(self) -> Any:
        """Remove and return the top operation."""
        if self.is_empty:
            self.recorder.emit(source=SOURCE, event_type="underflow", payload={"action": "pop"})
            raise StackEmptyError("Cannot pop from empty UndoStack")
        val = self._buffer.pop()
        self.recorder.emit(
            source=SOURCE,
            event_type="pop",
            payload={"operation": val, "depth": len(self._buffer)}
        )
        return val

    def peek(self) -> Any:
        """Return the top operation without removing it."""
        if self.is_empty:
            self.recorder.emit(source=SOURCE, event_type="underflow", payload={"action": "peek"})
            raise StackEmptyError("Cannot peek empty UndoStack")
        val = self._buffer[-1]
        self.recorder.emit(
            source=SOURCE,
            event_type="peek",
            payload={"operation": val, "depth": len(self._buffer)}
        )
        return val
