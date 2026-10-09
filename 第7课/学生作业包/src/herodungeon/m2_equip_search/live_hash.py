from __future__ import annotations


def bucket_index(item_id: str, bucket_count: int) -> int:
    """柜号 = 各字符编码之和 % bucket_count。
    字符编码用 ord()。例如 "sword" 是 115+119+111+114+100 = 559，
    bucket_count 为 8 时柜号是 7。
    """
    total = 0
    for c in item_id:
        total += ord(c)
    return total % bucket_count


def put(buckets: list[list[str]], item_id: str) -> None:
    """把 item_id 挂到对应柜子那条链的末尾。
    buckets 的长度就是柜子数。同号的 ID 按放入顺序排在同一条链上。
    """
    idx = bucket_index(item_id, len(buckets))
    buckets[idx].append(item_id)


def get(buckets: list[list[str]], item_id: str) -> str | None:
    """沿链逐个比较。找到就返回这个 ID，没有就返回 None。不要抛异常。"""
    idx = bucket_index(item_id, len(buckets))
    for val in buckets[idx]:
        if val == item_id:
            return val
    return None


def load_factor(n: int, bucket_count: int) -> float:
    """负载因子 = 装备件数 / 柜子数。用普通除法，不要整除。"""
    return n / bucket_count


# ------------------- 测试代码 -------------------
if __name__ == "__main__":
    # 创建8个柜子
    buckets = [[] for _ in range(8)]
    put(buckets, "sword")
    put(buckets, "helmet")

    print("7号柜内容：", buckets[7])
    print("查找 helmet：", get(buckets, "helmet"))
    print("查找不存在的 shield：", get(buckets, "shield"))
    print("负载因子(6,8)：", load_factor(6, 8))
