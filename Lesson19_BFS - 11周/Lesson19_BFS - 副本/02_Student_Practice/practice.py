"""30分钟：只补全bfs_path。5分钟初始化、15分钟循环、3分钟边界、7分钟测试修正。"""

from collections import deque
from support import RunSupport


def bfs_path(graph, start, goal, recorder=None):
    run = RunSupport('bfs', recorder, start, goal)

    # 检查起点和终点是否可以通行
    if not graph.passable(start) or not graph.passable(goal):
        return run.failure(blocked=True)

    # TODO 1：初始化
    frontier = deque([start])
    seen = {start}
    came_from = {}

    # TODO 2：BFS 主循环
    while frontier:
        # 从队首取出节点，保证先进先出
        current = frontier.popleft()

        # 记录当前扩展的节点
        run.expand(current, len(frontier))

        # 到达终点，返回路径
        if current == goal:
            return run.success(came_from, start, goal)

        # 遍历当前节点的所有邻居
        for nxt in graph.neighbors(current):

            # 已访问过的节点直接跳过
            if nxt in seen:
                continue

            # 标记新节点已访问
            seen.add(nxt)

            # 记录新节点从哪个节点到达
            came_from[nxt] = current

            # 将新节点加入队尾
            frontier.append(nxt)

            # 记录入队事件
            run.enqueue(nxt, current, len(frontier))

    # TODO 3：队列耗尽仍未找到终点
    return run.failure()

