"""M2 lesson 11: paste your lesson-9 ``quicksort_by`` here.

第 11 次课不重新评分快排：把第 9 次课已经全绿的实现整段贴进来，替换下面的 TODO。

Implement ``quicksort_by`` yourself. Do not call ``sorted()``, ``list.sort()``
or any library sort.

Requirements:

* return a **new** list; never modify ``items``;
* ascending by ``key(item)``; ``descending=True`` gives the reverse order;
* pick the pivot with a rule that does **not** degrade on already-sorted input
  (median-of-three recommended: the median of ``low`` / ``mid`` / ``high``),
  and write your pivot rule in this docstring;
* quicksort is not stable; equal keys may come out in any order.

Events (``source=SOURCE``), one round of partitioning emits, in this order:

* ``partition``    the range being split (e.g. ``low``, ``high``, ``depth``)
* ``pivot``        the chosen pivot (e.g. ``pivot_index``, ``pivot_key``)
* ``compare``      every element compared against the pivot
* ``swap``         every exchange of two different positions
* ``place_pivot``  where the pivot finally lands

Pivot rule: TODO 写下你的枢轴规则
"""

from __future__ import annotations

from typing import Any, Callable, Sequence, TypeVar

from herodungeon.core.events import EventRecorder

T = TypeVar("T")
SOURCE = "m2.quicksort"


def quicksort_by(
    items: Sequence[T],
    key: Callable[[T], Any],
    recorder: EventRecorder | None = None,
    descending: bool = False,
) -> list[T]:
    """Return a new list sorted by ``key`` using quicksort.

    Pivot rule: median-of-three. Take elements at low, mid=(low+high)//2, high
    indices of current range. Compare their key values, select the index with
    median key as pivot index. This avoids worst-case O(n²) for already-sorted
    sequences.
    """
    if recorder is None:
        recorder = EventRecorder()

    # make a copy, do not mutate original sequence
    arr = list(items)

    def _quicksort(low: int, high: int, depth: int) -> None:
        if low >= high:
            return
        # emit partition event for current range
        recorder.emit("partition", SOURCE, low=low, high=high, depth=depth)

        # -------- median-of-three pivot selection --------
        mid = (low + high) // 2
        # get keys for three candidates
        kl = key(arr[low])
        km = key(arr[mid])
        kh = key(arr[high])

        # find median index among low, mid, high
        candidates = [(kl, low), (km, mid), (kh, high)]
        # sort the three tuples by key to pick median
        candidates.sort(key=lambda x: x[0])
        pivot_idx = candidates[1][1]
        pivot_key = key(arr[pivot_idx])
        recorder.emit("pivot", SOURCE, pivot_index=pivot_idx, pivot_key=pivot_key)

        # swap pivot to high position for Lomuto partition scheme
        arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
        pivot_idx = high

        # -------- Lomuto partition --------
        i = low - 1
        for j in range(low, high):
            current_key = key(arr[j])
            recorder.emit("compare", SOURCE)
            # comparison logic considering descending flag
            if not descending:
                should_swap = current_key <= pivot_key
            else:
                should_swap = current_key >= pivot_key

            if should_swap:
                i += 1
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    recorder.emit("swap", SOURCE, pos1=i, pos2=j)

        # place pivot to its final position
        i += 1
        if i != pivot_idx:
            arr[i], arr[pivot_idx] = arr[pivot_idx], arr[i]
            recorder.emit("swap", SOURCE, pos1=i, pos2=pivot_idx)
        recorder.emit("place_pivot", SOURCE, final_index=i)

        # recurse left and right subarrays
        _quicksort(low, i - 1, depth + 1)
        _quicksort(i + 1, high, depth + 1)

    _quicksort(0, len(arr) - 1, depth=0)
    return arr
