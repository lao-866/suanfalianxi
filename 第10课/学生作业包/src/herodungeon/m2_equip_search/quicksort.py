"""M2 lesson 9: quicksort for equipment.

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
    """Return a new list sorted by key using quicksort.

    Pivot rule: median-of-three. Choose the median key among the
    low, middle, and high elements to avoid poor pivots on sorted input.
    """
    # 1. 复制列表，保证不修改原始数据
    result = list(items)

    # 2. 如果没有传入事件记录器，就创建一个
    if recorder is None:
        recorder = EventRecorder()

    # 3. 定义交换函数，只交换不同位置的元素
    def swap(i: int, j: int, swap_events: list) -> None:
        if i == j:
            return

        result[i], result[j] = result[j], result[i]
        swap_events.append((i, j))

    # 4. 递归执行快速排序
    def quicksort(low: int, high: int, depth: int) -> None:
        if low >= high:
            return

        # 每轮分区先记录 partition 事件
        recorder.emit(
            "partition",
            SOURCE,
            low=low,
            high=high,
            depth=depth,
        )

        # 5. 三数取中：比较 low、mid、high 三个位置的 key
        mid = (low + high) // 2

        candidates = [
            (key(result[low]), low),
            (key(result[mid]), mid),
            (key(result[high]), high),
        ]

        # 只对三个候选值进行比较，不调用任何排序函数
        a, b, c = candidates

        if a[0] > b[0]:
            a, b = b, a
        if b[0] > c[0]:
            b, c = c, b
        if a[0] > b[0]:
            a, b = b, a

        # b 是三个候选值的中位数
        pivot_index = b[1]
        pivot_key = b[0]

        recorder.emit(
            "pivot",
            SOURCE,
            pivot_index=pivot_index,
            pivot_key=pivot_key,
        )

        # 6. 将枢轴移到区间末尾，方便进行 Lomuto 分区
        swap_events = []
        swap(pivot_index, high, swap_events)

        # 7. 先记录本轮所有比较，再记录交换事件
        compare_events = []
        boundary = low

        for j in range(low, high):
            current_key = key(result[j])

            recorder.emit(
                "compare",
                SOURCE,
                index=j,
                item_key=current_key,
                pivot_key=pivot_key,
            )

            # 升序：小于或等于枢轴的元素放左边
            # 降序：大于或等于枢轴的元素放左边
            if (
                current_key >= pivot_key
                if descending
                else current_key <= pivot_key
            ):
                if boundary != j:
                    swap(boundary, j, swap_events)
                boundary += 1

        # 8. 枢轴归位
        if boundary != high:
            swap(boundary, high, swap_events)

        # 9. 按要求依次发出 swap 事件
        for i, j in swap_events:
            recorder.emit(
                "swap",
                SOURCE,
                index_a=i,
                index_b=j,
            )

        # 10. 记录枢轴最终位置
        pivot_final_index = boundary

        recorder.emit(
            "place_pivot",
            SOURCE,
            pivot_index=pivot_final_index,
            pivot_key=pivot_key,
        )

        # 11. 递归处理枢轴左侧和右侧
        quicksort(low, pivot_final_index - 1, depth + 1)
        quicksort(pivot_final_index + 1, high, depth + 1)

    # 12. 空列表和单元素列表不需要排序
    if len(result) > 1:
        quicksort(0, len(result) - 1, 0)

    return result

