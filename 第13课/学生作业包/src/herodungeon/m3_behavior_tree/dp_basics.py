"""M3 lesson 13: 0-1 knapsack by hand -- the table, the greedy trap, brute force.

You implement two functions:

* ``fill_table`` -- the (n+1) x (W+1) table, every cell = max(skip, take);
* ``greedy_by_ratio`` -- "best value per weight first", to see it lose 160 vs 220.

Provided: ``brute_force_best`` (tries all 2^n subsets -- the answer key),
``best_value`` (reads the bottom-right cell of your table) and the deck's
item lists. Events, trace-back and the equipment version are lesson 16.

``Item.value`` plays the role of 战力 (power) on the slides.
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import combinations

from herodungeon.core.models import Item

#: Deck lesson 13, slides 3-9: hand-fill A(2,3), B(3,4) with W=5.
HAND_FILL_ITEMS: tuple[Item, ...] = (
    Item("A", "A", 2, 3),
    Item("B", "B", 3, 4),
)
HAND_FILL_CAPACITY = 5

#: Deck lesson 13, slide 16 homework: add C(3,5) and fill row 3 by hand.
HOMEWORK_ITEM_C = Item("C", "C", 3, 5)

#: Deck lesson 12 slide 12 / lesson 13 slide 10: greedy 160 vs DP 220, W=50.
GREEDY_TRAP_ITEMS: tuple[Item, ...] = (
    Item("A", "A", 10, 60),
    Item("B", "B", 20, 100),
    Item("C", "C", 30, 120),
)
GREEDY_TRAP_CAPACITY = 50


def brute_force_best(items: Sequence[Item], capacity: int) -> int:
    """Provided oracle: try every subset (2^n of them) and keep the best value."""
    if capacity < 0:
        raise ValueError("capacity cannot be negative")
    best = 0
    for size in range(len(items) + 1):
        for subset in combinations(items, size):
            if sum(item.weight for item in subset) <= capacity:
                best = max(best, sum(item.value for item in subset))
    return best


def fill_table(items: Sequence[Item], capacity: int) -> list[list[int]]:
    """Return the full dynamic programming table for 0-1 knapsack."""
    if capacity < 0:
        raise ValueError("capacity cannot be negative")

    n = len(items)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        item = items[i - 1]

        for w in range(1, capacity + 1):
            # 不拿当前物品
            dp[i][w] = dp[i - 1][w]

            # 如果装得下，比较拿与不拿的战力
            if item.weight <= w:
                take = dp[i - 1][w - item.weight] + item.value
                dp[i][w] = max(dp[i][w], take)

    return dp


def best_value(items: Sequence[Item], capacity: int) -> int:
    """Provided: the answer sits in the bottom-right cell of the table."""
    return fill_table(items, capacity)[-1][-1]


def greedy_by_ratio(items: Sequence[Item], capacity: int) -> list[Item]:
    """Greedy: highest value / weight first, taking each item that fits."""
    if capacity < 0:
        raise ValueError("capacity cannot be negative")

    # 按战力 / 重量从高到低排序；相同则保持原顺序
    sorted_items = sorted(
        items,
        key=lambda item: item.value / item.weight,
        reverse=True,
    )

    chosen = []
    remaining = capacity

    for item in sorted_items:
        if item.weight <= remaining:
            chosen.append(item)
            remaining -= item.weight

    return chosen

