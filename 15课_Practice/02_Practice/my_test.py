from monster_ai import build_monster_tree, BehaviorStatus


def test_low_hp_should_flee():
    # 1. 创建测试环境
    world = {
        "hero_pos": (3, 0),
        "monster_pos": (6, 0),
        "monster_hp": 2,
        "monster_max_hp": 20,
        "hero_hp": 100,
        "sight_range": 5,
        "attack_cooldown": 0,
        "hp_threshold": 0.3,
        "damage": 5,
        "cooldown": 2,
        "grid": (10, 10),
    }

    # 2. 创建怪物行为树
    tree = build_monster_tree()

    # 3. 执行一次行为树
    tree.tick(world)

    # 4. 检查怪物是否选择逃跑
    assert world["last_action"] == "flee"

    # 5. 检查怪物是否远离了勇者
    assert world["monster_pos"] == (7, 0)


if __name__ == "__main__":
    test_low_hp_should_flee()
    print("测试通过：怪物低血量时优先逃跑！")