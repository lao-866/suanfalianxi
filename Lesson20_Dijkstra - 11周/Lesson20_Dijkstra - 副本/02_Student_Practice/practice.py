"""30分钟：只补全dijkstra_path。5分钟初始化、15分钟核心、3分钟边界、7分钟测试修正。"""

"""30分钟：只补全dijkstra_path。5分钟初始化、15分钟核心、3分钟边界、7分钟测试修正。"""

import heapq
from support import RunSupport


def dijkstra_path(graph, start, goal, recorder=None):
    run = RunSupport('dijkstra', recorder, start, goal)

    # 判断起点和终点是否可以通行
    if not graph.passable(start) or not graph.passable(goal):
        return run.failure(blocked=True)

    # TODO 1：初始化
    heap = [(0, start[0], start[1], start)]
    best = {start: 0}
    came_from = {}
    closed = set()

    # TODO 2：Dijkstra 核心搜索
    while heap:
        # 从优先队列中取出当前代价最小的节点
        g, _r, _c, current = heapq.heappop(heap)

        # 如果节点已经处理过，则跳过
        if current in closed:
            continue

        # 标记节点已经处理
        closed.add(current)

        # 记录扩展事件
        run.expand(current, len(heap), g)

        # 如果找到终点，返回路径和总代价
        if current == goal:
            return run.success(came_from, start, goal, g)

        # 遍历当前节点的邻居
        for nxt in graph.neighbors(current):

            # 已经处理过的节点不再搜索
            if nxt in closed:
                continue

            # 计算到邻居的新总代价
            candidate = g + graph.cost(current, nxt)

            # 如果找到更低代价的路径
            if candidate < best.get(nxt, float('inf')):

                # 更新最小代价
                best[nxt] = candidate

                # 记录路径来源
                came_from[nxt] = current

                # 将邻居加入优先队列
                heapq.heappush(
                    heap,
                    (candidate, nxt[0], nxt[1], nxt)
                )

                # 记录松弛事件
                run.relax(nxt, current, candidate)

    # TODO 3：没有找到路径
    return run.failure()

