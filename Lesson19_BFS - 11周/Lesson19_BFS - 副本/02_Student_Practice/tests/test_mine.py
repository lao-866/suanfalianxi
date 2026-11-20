
import pytest
from provided import GridGraph
from practice import bfs_path


def test_my_variant():
    # 创建3×3地图
    # 障碍物位于(1,1)和(2,0)
    graph = GridGraph(
        width=3,
        height=3,
        blocked={(1, 1), (2, 0)}
    )

    # 设置起点和终点
    start = (0, 0)
    goal = (2, 2)

    # 预测：最短路径为4步
    result = bfs_path(graph, start, goal)

    # 检查起点、终点和最短路径长度
    assert result.path[0] == start
    assert result.path[-1] == goal
    assert len(result.path) - 1 == 4

    print("我的测试通过！")
