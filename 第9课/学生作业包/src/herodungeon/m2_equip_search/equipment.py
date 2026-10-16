"""M2 lesson 9: the equipment model, ingest (入库) and a reproducible catalogue.

Unified field set (PPT, code and assignments all use these names)::

    item_id     装备编号   str, non-empty, unique inside one catalogue
    name        名称       str, non-empty
    power       战力       int, 1..1000
    speed       攻速       int, 1..100
    weight      重量       int, 1..50
    durability  耐久       int, 1..100
    rarity      稀有度     int, 1..5

The 5-dimensional vector used for similarity is
``(power, speed, weight, durability, rarity)``. Ranges are deliberately left
unnormalised: power dominates a raw Euclidean distance, which is exactly the
"量纲差异" discussion point of lesson 8.

``Equipment`` is independent of ``core.models.Item``; M1/M3/M5 keep using
``Item`` unchanged.

Provided: ``Equipment``, ``to_vector``, ``to_record``, ``generate_equipment``.
You implement: ``load_equipment`` only.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from herodungeon.core.events import EventRecorder

SOURCE = "m2.equipment"

#: Numeric fields in vector order.
VECTOR_FIELDS: tuple[str, ...] = ("power", "speed", "weight", "durability", "rarity")

#: Every field of one equipment record, in declaration order.
EQUIPMENT_FIELDS: tuple[str, ...] = ("item_id", "name", *VECTOR_FIELDS)

#: Inclusive (low, high) bounds for each numeric field.
FIELD_RANGES: dict[str, tuple[int, int]] = {
    "power": (1, 1000),
    "speed": (1, 100),
    "weight": (1, 50),
    "durability": (1, 100),
    "rarity": (1, 5),
}

_ADJECTIVES = ("生锈", "橡木", "疾风", "骑士", "秘银", "火焰", "猎人", "巨人", "精灵", "龙鳞")
_KINDS = ("铁剑", "盾", "匕首", "长剑", "锁甲", "法杖", "短弓", "战斧", "斗篷", "头盔")


@dataclass(frozen=True, slots=True)
class Equipment:
    """One piece of equipment with five numeric attributes."""

    item_id: str
    name: str
    power: int
    speed: int
    weight: int
    durability: int
    rarity: int

    def __post_init__(self) -> None:
        for field_name in ("item_id", "name"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")
        for field_name, (low, high) in FIELD_RANGES.items():
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{field_name} must be an int, got {value!r}")
            if not low <= value <= high:
                raise ValueError(f"{field_name}={value} outside [{low}, {high}]")

    def to_vector(self) -> tuple[int, int, int, int, int]:
        """Return ``(power, speed, weight, durability, rarity)``."""
        return (self.power, self.speed, self.weight, self.durability, self.rarity)

    def to_record(self) -> dict[str, Any]:
        """Plain dict with exactly ``EQUIPMENT_FIELDS`` (JSON friendly)."""
        return {field_name: getattr(self, field_name) for field_name in EQUIPMENT_FIELDS}


def load_equipment(
    records: Iterable[Mapping[str, Any]], recorder: EventRecorder | None = None
) -> list[Equipment]:
    """Ingest raw records (e.g. parsed JSON) into ``Equipment`` objects.
    Rules (each violation raises ``ValueError``):
    1. every record has all of ``EQUIPMENT_FIELDS``;
    2. no unknown keys (catches typos such as ``"attack"``);
    3. ``item_id`` is unique across the whole batch;
    4. types and ranges are checked by ``Equipment`` itself.
    Emits one ``ingest`` event per accepted record (index, item_id) and a final
    ``ingest_done`` event with the total count. Input order is preserved.
    """
    if recorder is None:
        recorder = EventRecorder()

    result: list[Equipment] = []
    seen_item_ids: set[str] = set()

    for idx, rec in enumerate(records):
        rec_keys = set(rec.keys())
        required_keys = set(EQUIPMENT_FIELDS)

        # 1. 检查是否缺少必要字段
        missing = required_keys - rec_keys
        if missing:
            raise ValueError(f"Missing required fields: {sorted(missing)}")
        # 2. 检查是否存在多余未知字段
        extra = rec_keys - required_keys
        if extra:
            raise ValueError(f"Unknown extra fields: {sorted(extra)}")

        # 构造Equipment，类型、范围校验交给Equipment.__post_init__
        equip = Equipment(**rec)

        # 3. 检查item_id全局重复
        if equip.item_id in seen_item_ids:
            raise ValueError(f"Duplicate item_id: {equip.item_id}")
        seen_item_ids.add(equip.item_id)

        result.append(equip)
        # 触发单条入库事件
        recorder.emit("ingest", SOURCE, index=idx, item_id=equip.item_id)

    # 全部处理完成，触发结束事件
    recorder.emit("ingest_done", SOURCE, count=len(result))
    return result



def generate_equipment(n: int, seed: int = 42) -> list[Equipment]:
    """Return ``n`` reproducible random equipment (the shared class catalogue).

    * ``item_id`` is ``EQ-000000``, ``EQ-000001``, ... (unique, zero-padded);
    * ``name`` is an adjective + kind from two fixed 10-word lists;
    * every numeric field is uniform in its ``FIELD_RANGES`` bound;
    * only ``random.Random(seed)`` is used, so one seed gives one catalogue on
      every machine (default seed 42, same as the rest of the course).
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    rng = random.Random(seed)
    catalogue: list[Equipment] = []
    for i in range(n):
        name = rng.choice(_ADJECTIVES) + rng.choice(_KINDS)
        values = {field_name: rng.randint(low, high) for field_name, (low, high) in FIELD_RANGES.items()}
        catalogue.append(Equipment(item_id=f"EQ-{i:06d}", name=name, **values))
    return catalogue
