"""M1 lesson 6: sliding window over the recent combat damage log.
Do not recompute each window from scratch. Slide by subtracting the leaving
value and adding the entering value so the whole scan is O(n).
"""
from __future__ import annotations
from typing import Any, Sequence
from herodungeon.core.events import EventRecorder

SOURCE = "m1.sliding_window"


def _validate(damage_log: Sequence[int], size: int) -> None:
    if size <= 0:
        raise ValueError("window size must be positive")
    if size > len(damage_log):
        raise ValueError(
            f"window size {size} exceeds damage log length {len(damage_log)}"
        )


def max_damage_window(
    damage_log: Sequence[int],
    size: int,
    recorder: EventRecorder | None = None,
) -> tuple[int, int]:
    """Return ``(start_index, window_sum)`` of the highest-damage window.
    Ties must keep the earliest window.
    """
    _validate(damage_log, size)
    recorder = recorder or EventRecorder()

    # 1. 初始化第一个窗口
    current_sum = sum(damage_log[0:size])
    best_start = 0
    best_sum = current_sum
    # ========== 删掉第一个参数 SOURCE ==========
    recorder.emit("window_init", {
        "start": 0,
        "window_sum": current_sum
    })

    # 2. 滑动窗口遍历剩余位置
    for new_start in range(1, len(damage_log) - size + 1):
        # 离开窗口的元素：上一轮窗口最左边
        leaving_val = damage_log[new_start - 1]
        # 新进入窗口的元素：本轮窗口最右边
        entering_val = damage_log[new_start + size - 1]
        current_sum = current_sum - leaving_val + entering_val

        # 记录滑动事件，同样去掉SOURCE
        recorder.emit("window_slide", {
            "start": new_start,
            "window_sum": current_sum,
            "removed": leaving_val,
            "added": entering_val
        })

        # ✅ 严格更大才更新最优，平局保留更早窗口
        if current_sum > best_sum:
            best_sum = current_sum
            best_start = new_start

    # 3. 最终最优窗口事件，去掉SOURCE
    recorder.emit("window_best", {
        "best_start": best_start,
        "best_sum": best_sum
    })
    return best_start, best_sum


def window_states(
    damage_log: Sequence[int], size: int
) -> list[dict[str, Any]]:
    """Return every window as {start, end, values, window_sum}."""
    _validate(damage_log, size)
    result = []
    n = len(damage_log)
    # end 是闭区间下标
    for start in range(n - size + 1):
        end = start + size - 1
        values = list(damage_log[start:start + size])
        window_sum = sum(values)
        result.append({
            "start": start,
            "end": end,
            "values": values,
            "window_sum": window_sum
        })
    return result
