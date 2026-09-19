from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterator
from herodungeon.core.events import AlgorithmEvent, EventRecorder

SOURCE = "m1.queue"


class QueueEmptyError(IndexError):
    """Raised when dequeuing or peeking an empty queue."""


@dataclass(slots=True)
class ActionQueue:
    recorder: EventRecorder = field(default_factory=EventRecorder)
    _buffer: list[Any] = field(default_factory=list, init=False, repr=False)
    _head: int = field(default=0, init=False, repr=False)

    def __len__(self) -> int:
        return len(self._buffer) - self._head

    def __iter__(self) -> Iterator[Any]:
        return iter(self._buffer[self._head:])

    @property
    def is_empty(self) -> bool:
        return len(self) == 0

    @property
    def items(self) -> tuple[Any, ...]:
        return tuple(self._buffer[self._head:])

    def enqueue(self, action: Any) -> AlgorithmEvent:
        """Append to the tail and emit enqueue."""
        self._buffer.append(action)
        size = len(self)
        tail_index = len(self._buffer) - 1
        # 使用 recorder.emit 自动生成step，type就是事件类型
        evt = self.recorder.emit(
            "enqueue",
            SOURCE,
            size=size,
            tail_index=tail_index
        )
        return evt

    def dequeue(self) -> Any:
        """Remove the front item in O(1) amortized time."""
        if self.is_empty:
            evt = self.recorder.emit(
                "underflow",
                SOURCE
            )
            raise QueueEmptyError("dequeue from empty ActionQueue")
        item = self._buffer[self._head]
        self._head += 1
        size = len(self)
        evt = self.recorder.emit(
            "dequeue",
            SOURCE,
            size=size
        )
        self._compact_if_needed()
        return item

    def peek(self) -> Any:
        """Return the front item without removing it."""
        if self.is_empty:
            evt = self.recorder.emit(
                "underflow",
                SOURCE
            )
            raise QueueEmptyError("peek empty ActionQueue")
        item = self._buffer[self._head]
        size = len(self)
        evt = self.recorder.emit(
            "peek",
            SOURCE,
            size=size
        )
        return item

    def drain(self) -> list[Any]:
        """Dequeue everything in FIFO order."""
        result = []
        while not self.is_empty:
            result.append(self.dequeue())
        return result

    def _compact_if_needed(self) -> None:
        """Drop the consumed prefix when it is at least half of the buffer."""
        # 条件：_head>0 并且 _head *2 >= len(_buffer)
        if self._head > 0 and self._head * 2 >= len(self._buffer):
            # 截取有效部分，丢弃前面已消费的前缀
            self._buffer = self._buffer[self._head:]
            reclaimed = self._head
            self._head = 0
            size = len(self)
            evt = self.recorder.emit(
                "compact",
                SOURCE,
                reclaimed=reclaimed,
                size=size
            )