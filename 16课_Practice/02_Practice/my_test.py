from copy import deepcopy
from lesson16_practice import reconstruct_items
from lesson_data import ITEMS, TABLE

# 测试：只考虑 A 和 B，背包限重 2 公斤
chosen = reconstruct_items(
    ITEMS[:2],
    deepcopy(TABLE[:3]),
    2
)

ids = [item.item_id for item in chosen]

assert ids == ["a"], "限重2公斤，预期只能带走A"

print("我的测试通过！", ids)