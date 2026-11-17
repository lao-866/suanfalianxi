
"""只修改标有TODO的 priority 和 relax；其余搜索骨架已经提供。"""
from provided import search


def priority(g, h):
    """TODO 1：返回候选排队使用的 f。"""
    return g + h


def relax(g, parent, u, v, edge_cost):
    """TODO 2：尝试用 u 到 v 的边改进记录。"""
    candidate = g[u] + edge_cost

    if v not in g or candidate < g[v]:
        g[v] = candidate
        parent[v] = u
        return True

    return False


def dijkstra(graph, start, goal):
    """完整搜索入口：不使用目标估计。"""
    return search(graph, start, goal, {}, priority, relax)


def astar(graph, start, goal, heuristic):
    """完整搜索入口：优先处理 f=g+h 小的候选。"""
    return search(graph, start, goal, heuristic, priority, relax)

