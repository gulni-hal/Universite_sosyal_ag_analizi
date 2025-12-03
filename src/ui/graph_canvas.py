from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt

class GraphCanvas(QWidget):
    """
    Graf düğümlerini çizer ve tıklamaları yakalar.
    UI dışından bir 'graph' objesi alır.
    Node pozisyonları graph.nodes içindeki node.x, node.y'den okunur.
    """

    def __init__(self, graph, on_node_clicked=None, parent=None):
        super().__init__(parent)
        self.graph = graph
        self.on_node_clicked = on_node_clicked  # callback

        self.node_radius = 22

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Kenarları çiz
        pen = QPen(Qt.darkGray, 2)
        painter.setPen(pen)

        painter.setPen(QPen(Qt.black, 2))
        for edge in self.graph.edges:
            x1, y1 = edge.node1.x, edge.node1.y
            x2, y2 = edge.node2.x, edge.node2.y
            painter.drawLine(x1, y1, x2, y2)

        # Sonra tüm Node’ları çiz
        for node in self.graph.nodes.values():
            painter.setBrush(QBrush(Qt.green))
            painter.drawEllipse(node.x - 15, node.y - 15, 30, 30)
            painter.drawText(node.x - 15, node.y - 20, node.adi)

    # -----------------------
    # Mouse ile Node tıklama
    # -----------------------
    def mousePressEvent(self, event):
        x, y = event.x(), event.y()

        for node in self.graph.nodes.values():
            dx = node.x - x
            dy = node.y - y
            if (dx * dx + dy * dy) <= (self.node_radius ** 2):
                if self.on_node_clicked:
                    self.on_node_clicked(node)
                return
