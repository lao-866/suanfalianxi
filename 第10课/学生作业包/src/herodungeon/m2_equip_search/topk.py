"""M2 lesson 10: distance helpers + top_k_by_value are provided; you implement top_k_similar.

Similarity uses Euclidean distance after min-max normalizing each field of
``to_vector()`` by ``FIELD_RANGES`` into ``[0, 1]``. A size-K max-heap of
distances (``heapq`` with negated distance) keeps the nearest K candidates;
the target itself (same ``item_id``) is excluded.
"""

from __future__ import annotations

import heapq
import math
from typing import Sequence

from herodungeon.core.events import EventRecorder
from herodungeon.core.models import Item
from herodungeon.m2_equip_search.equipment import FIELD_RANGES, VECTOR_FIELDS, Equipment

SOURCE = "m2.topk"
SOURCE_SIMILAR = "m2.topk_similar"


def normalized_vector(equipment: Equipment) -> tuple[float, ...]:
    """Scale ``to_vector()`` into ``[0, 1]`` per ``FIELD_RANGES`` (min-max)."""
    return tuple(
        (value - low) / (high - low)
        for value, (low, high) in zip(
            equipment.to_vector(), (FIELD_RANGES[name] for name in VECTOR_FIELDS), strict=True
        )
    )


def distance(a: Equipment, b: Equipment) -> float:
    """Normalized Euclidean distance between two pieces of equipment."""
    return math.dist(normalized_vector(a), normalized_vector(b))


def top_k_by_value(
    items: Sequence[Item], k: int, recorder: EventRecorder | None = None
) -> list[Item]:
    """Return the ``k`` highest-value items, highest first.

    Ties keep the item seen earliest, which keeps classroom output stable.
    Kept for older demos and TG-11; lesson 10 uses ``top_k_similar``.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    recorder = recorder or EventRecorder()

    heap: list[tuple[int, int, Item]] = []
    for index, item in enumerate(items):
        if len(heap) < k:
            heapq.heappush(heap, (item.value, -index, item))
            recorder.emit(
                "push", SOURCE, item_id=item.item_id, value=item.value, heap_size=len(heap)
            )
        elif item.value > heap[0][0]:
            evicted = heapq.heapreplace(heap, (item.value, -index, item))
            recorder.emit(
                "replace",
                SOURCE,
                item_id=item.item_id,
                value=item.value,
                evicted=evicted[2].item_id,
            )
        else:
            recorder.emit("skip", SOURCE, item_id=item.item_id, value=item.value)

    ordered = sorted(heap, key=lambda entry: (entry[0], entry[1]), reverse=True)
    result = [entry[2] for entry in ordered]
    recorder.emit("final", SOURCE, top_k=[item.item_id for item in result])
    return result



def top_k_similar(
    items: Sequence[Equipment],
    target: Equipment,
    k: int,
    recorder: EventRecorder | None = None,
) -> list[Equipment]:
    """Return the k nearest equipment to target, nearest first.

    Use a size-k max-heap represented by negative distances.
    Equal distances prefer smaller item_id.
    """
    if k <= 0:
        raise ValueError("k must be positive")

    if recorder is None:
        recorder = EventRecorder()

    # 堆中存储 (-distance, item_id, item)
    # 负距离使最远的候选排在堆顶
    heap: list[tuple[float, str, Equipment]] = []

    for item in items:
        # 1. 排除目标装备本身（根据 item_id 判断）
        if item.item_id == target.item_id:
            recorder.emit(
                "skip",
                SOURCE_SIMILAR,
                item_id=item.item_id,
                reason="self",
            )
            continue

        # 2. 计算归一化欧氏距离
        item_distance = distance(target, item)

        # 3. 堆未满时，直接加入
        if len(heap) < k:
            heapq.heappush(
                heap,
                (-item_distance, item.item_id, item),
            )

            recorder.emit(
                "push",
                SOURCE_SIMILAR,
                item_id=item.item_id,
                distance=item_distance,
                heap_size=len(heap),
            )
            continue

        # 4. 获取当前堆中最远的候选
        worst_distance = -heap[0][0]
        worst_item_id = heap[0][1]

        # 5. 判断当前候选是否优于堆顶
        # 距离更小优先；距离相同则 item_id 字典序更小优先
        is_better = (
            item_distance < worst_distance
            or (
                item_distance == worst_distance
                and item.item_id < worst_item_id
            )
        )

        if is_better:
            evicted = heapq.heapreplace(
                heap,
                (-item_distance, item.item_id, item),
            )

            recorder.emit(
                "replace",
                SOURCE_SIMILAR,
                item_id=item.item_id,
                distance=item_distance,
                evicted=evicted[2].item_id,
                heap_size=len(heap),
            )
        else:
            recorder.emit(
                "skip",
                SOURCE_SIMILAR,
                item_id=item.item_id,
                distance=item_distance,
                reason="not_better",
            )

    # 6. 从大根堆取出所有候选
    result = []

    while heap:
        _negative_distance, _item_id, item = heapq.heappop(heap)
        result.append(item)

    # 7. 插入排序：距离升序，相同距离按 item_id 升序
    for i in range(1, len(result)):
        current = result[i]
        current_distance = distance(target, current)
        j = i - 1

        while j >= 0:
            previous_distance = distance(target, result[j])

            if (
                previous_distance < current_distance
                or (
                    previous_distance == current_distance
                    and result[j].item_id < current.item_id
                )
            ):
                break

            result[j + 1] = result[j]
            j -= 1

        result[j + 1] = current

    # 8. 记录最终结果
    recorder.emit(
        "final",
        SOURCE_SIMILAR,
        top_k=[item.item_id for item in result],
    )

    return result

