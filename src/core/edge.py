class Edge:
    """
    İki üniversite arasındaki bağlantıyı temsil eder.
    Kenar yönsüzdür (undirected).
    """

    def __init__(self, node1, node2, weight: float = 1.0):
        self.node1 = node1
        self.node2 = node2
        self.weight = weight

    def __repr__(self):
        return f"Edge({self.node1.adi} <-> {self.node2.adi}, w={self.weight})"

    def get_nodes(self):
        return self.node1, self.node2
