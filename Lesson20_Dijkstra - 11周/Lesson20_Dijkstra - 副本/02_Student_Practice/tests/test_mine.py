
import pytest
from provided import GridGraph
from practice import dijkstra_path


def test_my_variant():
    # 创建一个 3×3 地图
    # 中间 (1,1) 为障碍物
    graph = GridGraph(3, 3, blocked={(1, 1)})

    # 设置起点和终点
    start = (0, 0)
    goal = (2, 2)

    # 运行 Dijkstra 算法
    result = dijkstra_path(graph, start, goal)

    # 预测：最短路径总代价为4
    assert result.cost == 4

    # 检查路径起点和终点
    assert result.path[0] == start
    assert result.path[-1] == goal

    # 检查路径不能经过障碍物
    assert (1, 1) not in result.path
