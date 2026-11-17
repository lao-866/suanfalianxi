
"""只补两种探索策略。图、状态记录和路径还原已经给出。"""
from collections import deque
from provided import emit, reconstruct_path, validate_graph


def dfs_path(graph, start, goal, trace=None):
    """用显式栈保留每层未完成的邻居，等价于按顺序递归。"""
    validate_graph(graph, start, goal)
    parent = {start: None}
    emit(trace, "discover", start, None)

    if start == goal:
        return [start]

    stack = [(start, iter(graph[start]))]
    emit(trace, "expand", start)

    while stack:
        current, neighbors = stack[-1]

        try:
            neighbor = next(neighbors)
        except StopIteration:
            stack.pop()
            emit(trace, "backtrack", current)
            continue

        # TODO 1A：跳过已发现的点，登记来路
        if neighbor in parent:
            continue
        parent[neighbor] = current

        emit(trace, "discover", neighbor, current)

        if neighbor == goal:
            # TODO 1C：还原路径
            return reconstruct_path(parent, goal)

        # TODO 1B：继续向深处探索
        stack.append((neighbor, iter(graph[neighbor])))
        emit(trace, "expand", neighbor)

    return []


def bfs_path(graph, start, goal, trace=None):
    """发现时写parent和入队；首次发现目标立即返回。"""
    validate_graph(graph, start, goal)
    parent = {start: None}
    queue = deque([start])

    emit(trace, "discover", start, None)
    emit(trace, "queue", tuple(queue))

    if start == goal:
        return [start]

    while queue:
        # TODO 2A：从队头取出
        current = queue.popleft()
        emit(trace, "expand", current)

        for neighbor in graph[current]:
            # TODO 2B：发现即登记并加入队尾
            if neighbor in parent:
                continue
            parent[neighbor] = current
            queue.append(neighbor)

            emit(trace, "discover", neighbor, current)
            emit(trace, "queue", tuple(queue))

            if neighbor == goal:
                return reconstruct_path(parent, goal)

    return []
