"""M2 lesson 10: binary search and lower-bound over already-sorted equipment.

The input must already be sorted by ``key``. Ascending ``binary_search_by``
should be implemented via ``lower_bound_by`` so duplicate keys return the
*first* match. Do not scan from left to right.
"""

from __future__ import annotations

from typing import Any, Callable, Sequence, TypeVar

from herodungeon.core.events import EventRecorder

T = TypeVar("T")

SOURCE = "m2.binary_search"
SOURCE_LOWER = "m2.lower_bound"



def lower_bound_by(
    sorted_items: Sequence[T],
    target_key: Any,
    key: Callable[[T], Any],
    recorder: EventRecorder | None = None,
) -> int:
    """Return the first index whose key is >= target_key.

    Use a closed interval lo..hi and an ans slot.
    """
    if recorder is None:
        recorder = EventRecorder()

    n = len(sorted_items)
    lo = 0
    hi = n - 1
    ans = n

    while lo <= hi:
        mid = (lo + hi) // 2
        current_key = key(sorted_items[mid])
        go_left = current_key >= target_key

        recorder.emit(
            "probe",
            SOURCE_LOWER,
            lo=lo,
            hi=hi,
            mid=mid,
            item_key=current_key,
            target_key=target_key,
            go_left=go_left,
        )

        if go_left:
            ans = mid
            hi = mid - 1
        else:
            lo = mid + 1

    recorder.emit(
        "bound",
        SOURCE_LOWER,
        index=ans,
    )

    return ans


def binary_search_by(
    sorted_items: Sequence[T],
    target_key: Any,
    key: Callable[[T], Any],
    recorder: EventRecorder | None = None,
    descending: bool = False,
) -> int:
    """Return the first matching index, or -1 if not found.

    Ascending search uses lower_bound_by so duplicate keys return
    the first occurrence. Descending search uses binary search directly.
    """
    if recorder is None:
        recorder = EventRecorder()

    n = len(sorted_items)

    # 升序：使用 lower_bound_by 保证重复键返回第一个
    if not descending:
        index = lower_bound_by(
            sorted_items,
            target_key,
            key,
            recorder=recorder,
        )

        if index < n and key(sorted_items[index]) == target_key:
            recorder.emit(
                "found",
                SOURCE,
                index=index,
                target_key=target_key,
            )
            return index

        recorder.emit(
            "not_found",
            SOURCE,
            target_key=target_key,
        )
        return -1

    # 降序：直接使用二分查找
    lo = 0
    hi = n - 1
    ans = -1

    while lo <= hi:
        mid = (lo + hi) // 2
        current_key = key(sorted_items[mid])

        recorder.emit(
            "probe",
            SOURCE,
            lo=lo,
            hi=hi,
            mid=mid,
            item_key=current_key,
            target_key=target_key,
        )

        if current_key == target_key:
            ans = mid
            hi = mid - 1
        elif current_key < target_key:
            hi = mid - 1
        else:
            lo = mid + 1

    if ans != -1:
        recorder.emit(
            "found",
            SOURCE,
            index=ans,
            target_key=target_key,
        )
        return ans

    recorder.emit(
        "not_found",
        SOURCE,
        target_key=target_key,
    )
    return -1
