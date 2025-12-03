import sqlite3
import networkx as nx
from .node import Node
from .graph import Graph

class DataLoader:
    def __init__(self, db_path):
        self.db_path = db_path

    def load_graph(self, graph: Graph):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT uni_id, adi, sehir, ilce, kurulus_yil, ogrenci_sayisi, fakulte_sayisi, akademik_sayisi, tr_siralama 
            FROM Üniversiteler
        """)
        rows = cursor.fetchall()

        # NetworkX grafı oluştur
        G_nx = nx.Graph()

        for row in rows:
            node = Node(
                uni_id=row[0],
                adi=row[1],
                sehir=row[2],
                ilce=row[3],
                kurulus_yil=row[4],
                ogrenci_sayisi=row[5],
                fakulte_sayisi=row[6],
                akademik_sayisi=row[7],
                tr_siralama=row[8]
            )
            graph.add_node(node)
            G_nx.add_node(node.uni_id, node=node)

        # Kenarları otomatik eklemek istersen burada ağırlık hesaplayıp ekleyebilirsin
        node_ids = list(graph.nodes.keys())
        for i in range(len(node_ids)):
            for j in range(i+1, len(node_ids)):
                n1 = graph.nodes[node_ids[i]]
                n2 = graph.nodes[node_ids[j]]
                weight = graph.calculate_weight(n1, n2)
                graph.add_edge(n1.uni_id, n2.uni_id)
                G_nx.add_edge(n1.uni_id, n2.uni_id, weight=weight)

        # Pozisyonları hesapla (spring layout)
        pos = nx.spring_layout(G_nx, seed=42)  # seed reproducible

        # Canvas için x,y değerlerini 0..1 → pixel ölçeğine çevir
        width, height = 700, 500
        for uni_id, p in pos.items():
            node = graph.nodes[uni_id]
            node.x = int(p[0] * width) + 50
            node.y = int(p[1] * height) + 50

        conn.close()
        return graph
