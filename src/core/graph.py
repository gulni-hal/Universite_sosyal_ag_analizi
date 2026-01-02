import math
import heapq
from .edge import Edge


class Graph:
    def __init__(self):
        self.nodes = {}  # {id: Node}
        self.edges = []  # [Edge, Edge, ...]
        self.adj = {}  # {id: {neighbor_id, ...}}

    def add_node(self, node):
        self.nodes[node.uni_id] = node
        if node.uni_id not in self.adj:
            self.adj[node.uni_id] = set()

    def add_edge(self, u_id, v_id):
        if u_id not in self.nodes or v_id not in self.nodes:
            return

        # Komşuluk listesine ekle
        self.adj[u_id].add(v_id)
        self.adj[v_id].add(u_id)

        # Edge nesnesi oluştur ve listeye ekle
        n1 = self.nodes[u_id]
        n2 = self.nodes[v_id]
        weight = self.calculate_weight(n1, n2)

        # Aynı kenar daha önce eklendi mi kontrol et
        exists = False
        for e in self.edges:
            if (e.node1.uni_id == u_id and e.node2.uni_id == v_id) or \
                    (e.node1.uni_id == v_id and e.node2.uni_id == u_id):
                exists = True
                break

        if not exists:
            new_edge = Edge(n1, n2, weight)
            self.edges.append(new_edge)

    def remove_node(self, node_id):
        if node_id in self.nodes:
            del self.nodes[node_id]
        if node_id in self.adj:
            del self.adj[node_id]

        # Diğerlerinin komşuluklarından sil
        for nid in self.adj:
            if node_id in self.adj[nid]:
                self.adj[nid].remove(node_id)

        # Kenarları sil
        self.edges = [e for e in self.edges if e.node1.uni_id != node_id and e.node2.uni_id != node_id]

    def calculate_weight(self, n1, n2):
        # PROJE İSTERİ: Formül -> Weight = 1 + Sqrt(Farklar Kareleri Toplamı)
        fark_ogrenci = (n1.ogrenci_sayisi - n2.ogrenci_sayisi) ** 2
        fark_siralama = (n1.tr_siralama - n2.tr_siralama) ** 2
        fark_yil = (n1.kurulus_yil - n2.kurulus_yil) ** 2

        total = (fark_ogrenci + fark_siralama + fark_yil)/100
        return 1 + math.sqrt(total)

    def get_neighbors(self, node_id):
        return list(self.adj.get(node_id, set()))

    # --- STRATEJİ DESENİ KÖPRÜSÜ ---
    def run_algorithm(self, strategy, start_id, end_id=None):
        """MainWindow'dan gelen algoritma nesnesini çalıştırır."""
        return strategy.execute(self, start_id, end_id)

    # --- ALGORİTMALAR ---

    def bfs(self, start_id):
        if start_id not in self.nodes: return []
        visited = set()
        queue = [start_id]
        visited.add(start_id)
        order = []
        while queue:
            curr_id = queue.pop(0)
            order.append(self.nodes[curr_id])
            neighbors = sorted(list(self.adj.get(curr_id, set())))
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def dfs(self, start_id):
        if start_id not in self.nodes: return []
        visited = set()
        stack = [start_id]
        order = []
        while stack:
            curr_id = stack.pop()
            if curr_id not in visited:
                visited.add(curr_id)
                order.append(self.nodes[curr_id])
                neighbors = sorted(list(self.adj.get(curr_id, set())), reverse=True)
                for neighbor in neighbors:
                    if neighbor not in visited:
                        stack.append(neighbor)
        return order

    def dijkstra(self, start_id, end_id):
        if start_id not in self.nodes or end_id not in self.nodes:
            return float('inf'), []

        queue = [(0, start_id)]
        distances = {node_id: float('inf') for node_id in self.nodes}
        distances[start_id] = 0
        predecessors = {node_id: None for node_id in self.nodes}

        while queue:
            current_cost, current_id = heapq.heappop(queue)
            if current_id == end_id: break
            if current_cost > distances[current_id]: continue

            for neighbor_id in self.adj.get(current_id, set()):
                weight = self.calculate_weight(self.nodes[current_id], self.nodes[neighbor_id])
                new_cost = current_cost + weight
                if new_cost < distances[neighbor_id]:
                    distances[neighbor_id] = new_cost
                    predecessors[neighbor_id] = current_id
                    heapq.heappush(queue, (new_cost, neighbor_id))

        path = []
        if distances[end_id] == float('inf'): return float('inf'), []
        curr = end_id
        while curr is not None:
            path.insert(0, self.nodes[curr])
            curr = predecessors[curr]
        return distances[end_id], path

    def a_star(self, start_id, end_id):
        """A* Algoritması: Dijkstra + Heuristic"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return float('inf'), []

        target_node = self.nodes[end_id]

        def heuristic(nid):
            # Öklid Mesafesi (Kuş uçuşu uzaklık)
            n = self.nodes[nid]
            return math.sqrt((n.x - target_node.x) ** 2 + (n.y - target_node.y) ** 2)

        open_set = [(heuristic(start_id), start_id)]
        g_score = {node_id: float('inf') for node_id in self.nodes}
        g_score[start_id] = 0
        predecessors = {node_id: None for node_id in self.nodes}

        while open_set:
            _, current_id = heapq.heappop(open_set)
            if current_id == end_id: break

            for neighbor_id in self.adj.get(current_id, set()):
                weight = self.calculate_weight(self.nodes[current_id], self.nodes[neighbor_id])
                tentative_g = g_score[current_id] + weight
                if tentative_g < g_score[neighbor_id]:
                    predecessors[neighbor_id] = current_id
                    g_score[neighbor_id] = tentative_g
                    f_score = tentative_g + heuristic(neighbor_id)
                    heapq.heappush(open_set, (f_score, neighbor_id))

        path = []
        if g_score[end_id] == float('inf'): return float('inf'), []
        curr = end_id
        while curr is not None:
            path.insert(0, self.nodes[curr])
            curr = predecessors[curr]
        return g_score[end_id], path

    def welsh_powell_coloring(self):
        sorted_nodes = sorted(self.nodes.keys(),
                              key=lambda nid: len(self.adj.get(nid, set())),
                              reverse=True)
        coloring = {}
        for node_id in sorted_nodes:
            neighbor_colors = {coloring.get(neigh) for neigh in self.adj.get(node_id, set()) if neigh in coloring}
            color = 1
            while color in neighbor_colors: color += 1
            coloring[node_id] = color
        return coloring

    def run_coloring_algorithm(self, strategy):
        """
        Renklendirme stratejisini çalıştıran köprü metot.
        """
        return strategy.execute(self)

    def find_connected_components(self):
        visited = set()
        components = []
        for nid in self.nodes:
            if nid not in visited:
                comp = []
                queue = [nid]
                visited.add(nid)
                while queue:
                    curr = queue.pop(0)
                    comp.append(self.nodes[curr])
                    for neighbor in self.adj.get(curr, set()):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(comp)
        return components

    def get_top_5_influential_unis(self):
        data = []
        for nid, node in self.nodes.items():
            degree = len(self.adj.get(nid, set()))
            total_weight = 0
            for edge in self.edges:
                if edge.node1.uni_id == nid or edge.node2.uni_id == nid:
                    total_weight += edge.weight
            data.append(
                {"adi": node.adi, "sehir": node.sehir, "derece": degree, "toplam_agirlik": round(total_weight, 2)})
        data.sort(key=lambda x: x["derece"], reverse=True)
        return data[:5]