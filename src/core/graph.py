import math
from .node import Node
from .edge import Edge
from .algorithms import GraphAlgorithm  # Soyut sınıfı import ediyoruz


class Graph:
    def __init__(self):
        self.nodes = {}  # uni_id -> Node
        self.edges = []  # Edge listesi
        self.adj = {}  # Komşuluk listesi

    def add_node(self, node: Node):
        if node.uni_id in self.nodes:
            raise ValueError(f"Node already exists: {node.uni_id}")
        self.nodes[node.uni_id] = node
        self.adj[node.uni_id] = set()

    def remove_node(self, uni_id: int):
        if uni_id not in self.nodes: return
        if uni_id in self.adj:
            for neighbor_id in list(self.adj[uni_id]):
                if neighbor_id in self.adj:
                    self.adj[neighbor_id].discard(uni_id)
        del self.adj[uni_id]
        self.edges = [e for e in self.edges if e.node1.uni_id != uni_id and e.node2.uni_id != uni_id]
        del self.nodes[uni_id]

    def add_edge(self, node_id1: int, node_id2: int):
        if node_id1 == node_id2: return
        n1, n2 = self.nodes.get(node_id1), self.nodes.get(node_id2)
        if not n1 or not n2: return
        if node_id2 in self.adj.get(node_id1, set()): return

        weight = self.calculate_weight(n1, n2)
        self.edges.append(Edge(n1, n2, weight))
        self.adj[node_id1].add(node_id2)
        self.adj[node_id2].add(node_id1)

    def run_algorithm(self, algorithm: GraphAlgorithm, start_id, end_id=None):
        """
        STRATEGY PATTERN: Algoritma nesnesini kabul eder ve çalıştırır.
        Hocanızın istediği 'Soyutlama Kullanımı' burasıdır.
        """
        return algorithm.execute(self, start_id, end_id)

    def calculate_weight(self, n1: Node, n2: Node) -> float:
        # PDF Formülüne göre dinamik ağırlık hesabı
        fark_akademik = (n1.akademik_sayisi - n2.akademik_sayisi) ** 2
        fark_siralama = (n1.tr_siralama - n2.tr_siralama) ** 2
        fark_ogrenci = (n1.ogrenci_sayisi - n2.ogrenci_sayisi) ** 2
        fark_yas = (n1.kurulus_yil - n2.kurulus_yil) ** 2

        total_diff = fark_akademik + fark_siralama + fark_ogrenci + fark_yas
        return (1 + math.sqrt(total_diff)) / 100

    def get_degree(self, uni_id: int) -> int:
        return len(self.adj.get(uni_id, set()))

    def welsh_powell_coloring(self) -> dict:
        # Renklendirme mantığı (Strategy'ye de taşınabilir ama Graph'a özgü kalabilir)
        if not self.nodes: return {}
        coloring, color_id = {}, 1
        uncolored_nodes = set(self.nodes.keys())
        while uncolored_nodes:
            sorted_uncolored = sorted(list(uncolored_nodes), key=lambda x: self.get_degree(x), reverse=True)
            current_color_batch = []
            for node_id in sorted_uncolored:
                if not any(node_id in self.adj.get(c, set()) for c in current_color_batch):
                    current_color_batch.append(node_id)
            for node_id in current_color_batch:
                coloring[node_id] = color_id
                uncolored_nodes.remove(node_id)
            color_id += 1
        return coloring

    def find_connected_components(self):
        visited, components = set(), []
        for node_id in self.nodes:
            if node_id not in visited:
                comp, queue = [], [node_id]
                visited.add(node_id)
                while queue:
                    curr = queue.pop(0)
                    comp.append(self.nodes[curr])
                    for neighbor in self.adj.get(curr, set()):
                        if neighbor not in visited:
                            visited.add(neighbor);
                            queue.append(neighbor)
                components.append(comp)
        return components