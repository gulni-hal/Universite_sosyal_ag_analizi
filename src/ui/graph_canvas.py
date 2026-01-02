from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QPoint


class GraphCanvas(QWidget):
    # Renk paleti
    COLOR_PALETTE_INFO = [
        {"id": 1, "name": "Kırmızı", "color": QColor("#FF5733")},
        {"id": 2, "name": "Yeşil", "color": QColor("#33FF57")},
        {"id": 3, "name": "Mavi", "color": QColor("#3357FF")},
        {"id": 4, "name": "Pembe", "color": QColor("#FF33F5")},
        {"id": 5, "name": "Altın Sarısı", "color": QColor("#FFD733")},
        {"id": 6, "name": "Turkuaz", "color": QColor("#33FFF0")},
        {"id": 7, "name": "Mor", "color": QColor("#9933FF")},
        {"id": 8, "name": "Turuncu", "color": QColor("#FF8D33")},
        {"id": 9, "name": "Gri", "color": QColor("#A0A0A0")},
        {"id": 10, "name": "Açık Yeşil", "color": QColor("#33FFC0")}
    ]
    COLOR_PALETTE = [info["color"] for info in COLOR_PALETTE_INFO]
    COLOR_NAME_MAP = {info["id"]: info["name"] for info in COLOR_PALETTE_INFO}

    def __init__(self, graph, on_node_clicked=None, on_edge_clicked=None, coloring_result=None, parent=None):
        super().__init__(parent)
        self.algo_nodes = []
        self.graph = graph
        self.on_node_clicked = on_node_clicked
        self.coloring_result = {}
        self.on_edge_clicked = on_edge_clicked  # Yeni callback
        self.selected_edge = None

        self.highlighted_path = []

        self.node_radius = 20
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.last_mouse_pos = QPoint(0, 0)
        self.is_panning = False
        self.first_resize = True

        self.setStyleSheet("background-color: #f0f0f0;")

    def update_coloring(self, coloring: dict):
        self.coloring_result = coloring
        self.highlighted_path = []  # Renklendirme yapılırsa yolu temizle
        self.update()

    def set_path(self, path_nodes):
        """Dijkstra sonucunu çizmek için yolu ayarlar."""
        self.highlighted_path = path_nodes
        # Renklendirmeyi temizleyelim ki yol belli olsun
        self.coloring_result = {}
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.first_resize and self.graph.nodes:
            self.fit_view()
            self.first_resize = False

    def fit_view(self):
        if not self.graph.nodes: return
        xs = [node.x for node in self.graph.nodes.values()]
        ys = [node.y for node in self.graph.nodes.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        graph_width = max(max_x - min_x, 100)
        graph_height = max(max_y - min_y, 100)

        # Padding değerini biraz artırarak düğümlerin kenara yapışmasını engeller
        padding = 200

        scale_x = self.width() / (graph_width + padding)
        scale_y = self.height() / (graph_height + padding)

        # Ölçeğin çok küçülüp her şeyi birbirine sokmasını engeller
        new_scale = min(scale_x, scale_y)
        if new_scale < 0.05: new_scale = 0.05
        if new_scale > 2.0: new_scale = 2.0

        self.scale_factor = new_scale

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        # Merkeze odakla
        self.offset = QPoint(
            int(self.width() / 2 - center_x * self.scale_factor),
            int(self.height() / 2 - center_y * self.scale_factor)
        )
        self.update()

    def paintEvent(self, event):
        import math

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.save()
        painter.translate(self.offset)
        painter.scale(self.scale_factor, self.scale_factor)

        # 1. Normal Kenarlar (Parçalı Çizgi ve Eğimli Yazı)
        pen_edge = QPen(Qt.darkGray, 2)
        painter.setPen(pen_edge)

        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        for edge in self.graph.edges:
            x1, y1 = edge.node1.x, edge.node1.y
            x2, y2 = edge.node2.x, edge.node2.y

            # Orta noktayı bul
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2

            # Açı ve Uzaklık Hesapları
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)

            # Eğer mesafe çok kısaysa (üst üsteyse) çizme
            if length == 0: continue

            # Birim vektörler (Çizgi yönü)
            ux = dx / length
            uy = dy / length

            # Metin için boşluk (Yarıçap kadar, örneğin merkezden 15px sağa ve sola)
            gap_size = 15

            if self.selected_edge == edge:
                painter.setPen(QPen(Qt.yellow, 4))  # Seçili kenarı sarı ve kalın yap
            else:
                painter.setPen(pen_edge)

            # Eğer çizgi çok kısaysa boşluk bırakma, direkt çiz
            if length < gap_size * 3:
                painter.setPen(pen_edge)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            else:
                # 1. Parça: Başlangıçtan -> Ortadaki boşluğun başına
                # Boşluk başı = Orta nokta - (Birim Vektör * Gap)
                end_x1 = mid_x - (ux * gap_size)
                end_y1 = mid_y - (uy * gap_size)

                # 2. Parça: Ortadaki boşluğun sonundan -> Bitişe
                start_x2 = mid_x + (ux * gap_size)
                start_y2 = mid_y + (uy * gap_size)

                painter.setPen(pen_edge)
                painter.drawLine(int(x1), int(y1), int(end_x1), int(end_y1))
                painter.drawLine(int(start_x2), int(start_y2), int(x2), int(y2))

                # --- EĞİMLİ YAZI ---
                painter.save()

                # Merkeze git
                painter.translate(mid_x, mid_y)

                # Açıyı hesapla (radyan -> derece)
                angle_deg = math.degrees(math.atan2(dy, dx))

                # Yazının ters durmaması için kontrol
                if abs(angle_deg) > 90:
                    angle_deg += 180

                painter.rotate(angle_deg)

                # Yazıyı çiz (0,0 artık orta nokta)
                painter.setPen(QPen(Qt.darkBlue))
                weight_text = f"{int(edge.weight)}"

                # Metni tam ortalamak için ölçüm (isteğe bağlı ama şık durur)
                metrics = painter.fontMetrics()
                text_w = metrics.width(weight_text)
                text_h = metrics.height()

                # (x, y) -> Hafif yukarı kaydırarak tam ortaya koy
                painter.drawText(int(-text_w / 2), int(text_h / 4), weight_text)

                painter.restore()

        # 2. Vurgulanan Yol (Dijkstra - Kırmızı)
        if self.highlighted_path and len(self.highlighted_path) > 1:
            pen_path = QPen(Qt.red, 5)
            painter.setPen(pen_path)
            for i in range(len(self.highlighted_path) - 1):
                n1 = self.highlighted_path[i]
                n2 = self.highlighted_path[i + 1]
                painter.drawLine(int(n1.x), int(n1.y), int(n2.x), int(n2.y))

        # 3. Düğümler (Aynı kalıyor)
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)

        for node in self.graph.nodes.values():
            uni_id = node.uni_id

            # Renk seçimi
            fill_color = QColor("#00FF00")
            if self.coloring_result:
                c_id = self.coloring_result.get(uni_id)
                if c_id:
                    idx = (c_id - 1) % len(self.COLOR_PALETTE)
                    fill_color = self.COLOR_PALETTE[idx]

            if node in self.highlighted_path:
                fill_color = QColor("white")
                painter.setPen(QPen(Qt.red, 3))
            elif hasattr(self, 'algo_nodes') and node in self.algo_nodes:
                fill_color = QColor("#00BFFF")
                painter.setPen(QPen(Qt.blue, 3))
            else:
                painter.setPen(QPen(Qt.black, 2))

            painter.setBrush(QBrush(fill_color))
            painter.drawEllipse(int(node.x - self.node_radius), int(node.y - self.node_radius),
                                self.node_radius * 2, self.node_radius * 2)

            # paintEvent içindeki düğüm çizim kısmında:
            painter.setPen(QPen(Qt.black))
            # Ölçek çok küçükse yazıyı çizme veya küçült
            if self.scale_factor > 0.5:
                painter.drawText(int(node.x - self.node_radius), int(node.y - self.node_radius - 5), node.adi)

        painter.restore()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale_factor *= 1.1
        else:
            self.scale_factor *= 0.9
        if self.scale_factor < 0.01: self.scale_factor = 0.01
        if self.scale_factor > 10.0: self.scale_factor = 10.0
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
            self.is_panning = True

    def mouseMoveEvent(self, event):
        if self.is_panning:
            self.offset += event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            click_pos = event.pos()
            real_x = (click_pos.x() - self.offset.x()) / self.scale_factor
            real_y = (click_pos.y() - self.offset.y()) / self.scale_factor
            for node in self.graph.nodes.values():
                dx = node.x - real_x
                dy = node.y - real_y
                if (dx * dx + dy * dy) <= (self.node_radius ** 2):
                    if self.on_node_clicked: self.on_node_clicked(node)
                    return

            self.check_edge_click(real_x, real_y)

    def check_edge_click(self, x, y):
        threshold = 5.0
        for edge in self.graph.edges:
            x1, y1 = edge.node1.x, edge.node1.y
            x2, y2 = edge.node2.x, edge.node2.y

            # Noktanın doğru parçasına olan uzaklığını hesapla
            dist = self.dist_to_line(x, y, x1, y1, x2, y2)
            if dist < threshold:
                if self.on_edge_clicked:
                    self.on_edge_clicked(edge)
                return

    def dist_to_line(self, px, py, x1, y1, x2, y2):
        # Klasik nokta-doğru parçası uzaklık formülü
        L2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if L2 == 0: return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / L2
        t = max(0, min(1, t))
        return ((px - (x1 + t * (x2 - x1))) ** 2 + (py - (y1 + t * (y2 - y1))) ** 2) ** 0.5

