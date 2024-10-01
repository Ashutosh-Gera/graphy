# graph algorithms

def dfs(G, start_node):
    visited = []
    stack = [start_node]
    steps = []
    traversed_edges = []

    while stack:
        node = stack.pop()
        if node not in visited:
            if visited:
                traversed_edges.append((visited[-1], node))
            visited.append(node)
            steps.append({
                'visited': visited.copy(),
                'current': node,
                'edges': traversed_edges.copy()
            })
            neighbors = list(G.neighbors(node))
            stack.extend(reversed(neighbors))
    return steps

# algorithms.py

def bfs(G, start_node):
    visited = []
    queue = [start_node]
    steps = []
    traversed_edges = []

    # Keep track of which nodes have been enqueued to avoid duplicates
    enqueued = {start_node}

    while queue:
        node = queue.pop(0)
        visited.append(node)

        # Record the state at this step
        steps.append({
            'visited': visited.copy(),
            'current': node,
            'edges': traversed_edges.copy()
        })

        # Iterate over neighbors
        neighbors = list(G.neighbors(node))
        for neighbor in neighbors:
            if neighbor not in visited and neighbor not in enqueued:
                queue.append(neighbor)
                enqueued.add(neighbor)
                # Record the edge from the current node to the neighbor
                traversed_edges.append((node, neighbor))

    return steps



