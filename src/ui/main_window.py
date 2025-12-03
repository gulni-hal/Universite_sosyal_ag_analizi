from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication, QFrame
from .graph_canvas import GraphCanvas

class MainWindow(QMainWindow):
    def __init__(self, graph):
        super().__init__()
        self.setWindowTitle("Sosyal Ağ Analizi - Üniversite Grafı")
        self.setMinimumSize(1000, 600)

        # Merkezi widget
        container = QWidget()
        self.setCentralWidget(container)

        # Yatay layout
        layout = QHBoxLayout()
        container.setLayout(layout)

        # Sol: Canvas
        self.canvas = GraphCanvas(
            graph,
            on_node_clicked=self.show_node_details
        )
        self.canvas.setMinimumWidth(700)

        # Sağ: Bilgi paneli
        self.info_panel = self.create_info_panel()

        layout.addWidget(self.canvas)
        layout.addWidget(self.info_panel)

    def create_info_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setMinimumWidth(260)

        layout = QVBoxLayout(panel)

        self.label_title = QLabel("Üniversite Bilgileri")
        self.label_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.label_adi = QLabel("Adı: -")
        self.label_kurulus = QLabel("Kuruluş: -")
        self.label_il = QLabel("İl: -")
        self.label_ilce = QLabel("İlçe: -")
        self.label_siralama = QLabel("TR Sıralama: -")

        layout.addWidget(self.label_title)
        layout.addSpacing(15)
        layout.addWidget(self.label_adi)
        layout.addWidget(self.label_kurulus)
        layout.addWidget(self.label_il)
        layout.addWidget(self.label_ilce)
        layout.addWidget(self.label_siralama)
        layout.addStretch()

        return panel

    # ---------------------------------------
    # Node’a tıklanınca sağ panel güncellenir
    # ---------------------------------------
    def show_node_details(self, node):
        self.label_adi.setText(f"Adı: {node.adi}")
        self.label_kurulus.setText(f"Kuruluş: {node.kurulus_yil}")
        self.label_il.setText(f"İl: {node.sehir}")
        self.label_ilce.setText(f"İlçe: {node.ilce}")
        self.label_siralama.setText(f"TR Sıralama: {node.tr_siralama}")


