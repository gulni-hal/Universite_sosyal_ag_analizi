from .node import Node
from .edge import Edge
from datetime import datetime

class Graph:
    """
    Üniversiteler arası sosyal ağ grafı.
    Düğümler Node objeleri,
    Kenarlar Edge objeleri olarak saklanır.
    """

    def __init__(self):
        self.nodes = {}     # uni_id → Node
        self.edges = []     # Edge listesi

    # -----------------------
    # NODE YÖNETİMİ
    # -----------------------
    def add_node(self, node: Node):
        if node.uni_id in self.nodes:
            raise ValueError(f"Node already exists: {node.uni_id}")
        self.nodes[node.uni_id] = node

    def remove_node(self, uni_id: int):
        if uni_id not in self.nodes:
            return
        # Kenarları sil
        self.edges = [e for e in self.edges
                      if e.node1.uni_id != uni_id and e.node2.uni_id != uni_id]
        # Düğümü sil
        del self.nodes[uni_id]

    # -----------------------
    # EDGE YÖNETİMİ
    # -----------------------
    def add_edge(self, node_id1: int, node_id2: int):
        if node_id1 == node_id2:
            raise ValueError("Self-loop edge oluşturulamaz.")

        n1 = self.nodes.get(node_id1)
        n2 = self.nodes.get(node_id2)

        if not n1 or not n2:
            raise ValueError("Node bulunamadı.")

        # Edge mevcut mu?
        for e in self.edges:
            if (e.node1 == n1 and e.node2 == n2) or (e.node1 == n2 and e.node2 == n1):
                return  # Çift eklemeyi engelle

        weight = self.calculate_weight(n1, n2)
        self.edges.append(Edge(n1, n2, weight))

    def remove_edge(self, node_id1: int, node_id2: int):
        self.edges = [
            e for e in self.edges
            if not (
                (e.node1.uni_id == node_id1 and e.node2.uni_id == node_id2) or
                (e.node1.uni_id == node_id2 and e.node2.uni_id == node_id1)
            )
        ]

    # -----------------------
    # DİNAMİK AĞIRLIK HESABI
    # -----------------------
    def calculate_weight(self, n1: Node, n2: Node) -> float:
        """
        Yeni formül:
        weight = 1 / (1 + (akademik_sayisi farkı)^2 +
                          (tr_siralama farkı)^2 +
                          (ogrenci_sayisi farkı)^2 +
                          (universite_yasi farkı)^2 )
        """
        now = datetime.now().year
        uni_yasi_1 = now - n1.kurulus_yil
        uni_yasi_2 = now - n2.kurulus_yil

        akademik = (n1.akademik_sayisi - n2.akademik_sayisi) ** 2
        tr_siralama = (n1.tr_siralama - n2.tr_siralama) ** 2
        ogrenci = (n1.ogrenci_sayisi - n2.ogrenci_sayisi) ** 2
        uni_yasi = (uni_yasi_1 - uni_yasi_2) ** 2

        weight = 1 / (1 + akademik + tr_siralama + ogrenci + uni_yasi)
        return weight

    # -----------------------
    # GRAF SELLEŞTİRME DESTEK FONK.
    # -----------------------
    def get_neighbors(self, uni_id: int):
        neighbors = []
        for e in self.edges:
            if e.node1.uni_id == uni_id:
                neighbors.append((e.node2, e.weight))
            elif e.node2.uni_id == uni_id:
                neighbors.append((e.node1, e.weight))
        return neighbors

    def __repr__(self):
        return f"Graph(nodes={len(self.nodes)}, edges={len(self.edges)})"
