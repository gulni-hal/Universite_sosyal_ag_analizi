from abc import ABC, abstractmethod
import heapq
import math

class GraphAlgorithm(ABC):
    """Tüm algoritmalar için temel soyut sınıf (Interface)"""
    @abstractmethod
    def execute(self, graph, start_node_id, end_node_id=None):
        pass

class PathFindingAlgorithm(GraphAlgorithm):
    """Yol bulma algoritmaları için ortak ata"""
    @abstractmethod
    def calculate_distance(self, n1, n2):
        pass

class DijkstraAlgorithm(PathFindingAlgorithm):
    def execute(self, graph, start_id, end_id):
        if start_id not in graph.nodes or end_id not in graph.nodes:
            return float('inf'), []

        queue = [(0, start_id)]
        distances = {node_id: float('inf') for node_id in graph.nodes}
        distances[start_id] = 0
        predecessors = {node_id: None for node_id in graph.nodes}

        while queue:
            current_cost, current_id = heapq.heappop(queue)
            if current_id == end_id:
                break
            if current_cost > distances[current_id]:
                continue

            for neighbor_id in graph.adj.get(current_id, set()):
                weight = graph.calculate_weight(graph.nodes[current_id], graph.nodes[neighbor_id])
                distance = current_cost + weight
                if distance < distances[neighbor_id]:
                    distances[neighbor_id] = distance
                    predecessors[neighbor_id] = current_id
                    heapq.heappush(queue, (distance, neighbor_id))

        path = []
        curr = end_id
        if distances[end_id] == float('inf'):
            return float('inf'), []
        while curr is not None:
            path.insert(0, graph.nodes[curr])
            curr = predecessors[curr]
        return distances[end_id], path

    def calculate_distance(self, n1, n2): # Interface gereği zorunlu
        pass

class AStarAlgorithm(PathFindingAlgorithm):
    def execute(self, graph, start_id, end_id):
        if start_id not in graph.nodes or end_id not in graph.nodes:
            return float('inf'), []

        target_node = graph.nodes[end_id]

        def heuristic(node_id):
            n = graph.nodes[node_id]
            return math.sqrt((n.x - target_node.x) ** 2 + (n.y - target_node.y) ** 2)

        queue = [(0 + heuristic(start_id), start_id)]
        g_scores = {node_id: float('inf') for node_id in graph.nodes}
        g_scores[start_id] = 0
        predecessors = {node_id: None for node_id in graph.nodes}

        while queue:
            _, current_id = heapq.heappop(queue)
            if current_id == end_id:
                break

            for neighbor_id in graph.adj.get(current_id, set()):
                weight = graph.calculate_weight(graph.nodes[current_id], graph.nodes[neighbor_id])
                tentative_g_score = g_scores[current_id] + weight
                if tentative_g_score < g_scores[neighbor_id]:
                    predecessors[neighbor_id] = current_id
                    g_scores[neighbor_id] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor_id)
                    heapq.heappush(queue, (f_score, neighbor_id))

        path = []
        curr = end_id
        if g_scores[end_id] == float('inf'):
            return float('inf'), []
        while curr is not None:
            path.insert(0, graph.nodes[curr])
            curr = predecessors[curr]
        return g_scores[end_id], path

    def calculate_distance(self, n1, n2):
        pass

class BFSAlgorithm(GraphAlgorithm):
    def execute(self, graph, start_id, end_node_id=None):
        if start_id not in graph.nodes: return []
        visited, queue, order = {start_id}, [start_id], []
        while queue:
            curr_id = queue.pop(0)
            order.append(graph.nodes[curr_id])
            for neighbor in sorted(list(graph.adj.get(curr_id, set()))):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

class DFSAlgorithm(GraphAlgorithm):
    def execute(self, graph, start_id, end_node_id=None):
        if start_id not in graph.nodes: return []
        visited, stack, order = set(), [start_id], []
        while stack:
            curr_id = stack.pop()
            if curr_id not in visited:
                visited.add(curr_id)
                order.append(graph.nodes[curr_id])
                neighbors = sorted(list(graph.adj.get(curr_id, set())), reverse=True)
                for neighbor in neighbors:
                    if neighbor not in visited:
                        stack.append(neighbor)
        return order

class ColoringStrategy(ABC):
    """Renklendirme algoritmaları için özel arayüz (Interface)"""
    @abstractmethod
    def execute(self, graph):
        pass

class WelshPowellAlgorithm(ColoringStrategy):
    """Somut Welsh-Powell Stratejisi"""
    def execute(self, graph):
        # Graph sınıfındaki mantığı çağırır
        return graph.welsh_powell_coloring()