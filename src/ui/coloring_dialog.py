# ui/coloring_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QPushButton, QAbstractItemView, QMessageBox)
from PyQt5.QtCore import Qt
# GÜNCELLEME: İçe aktarma yolu düzeltildi
from core.graph import Graph
from core.exporter import Exporter

COLOR_NAMES = {
    1: "Kırmızı",
    2: "Mavi",
    3: "Yeşil",
    4: "Sarı",
    5: "Mor",
    6: "Turuncu",
    7: "Pembe",
    8: "Turkuaz",
    9: "Kahverengi",
    10: "Gri"
}

class ColoringDialog(QDialog):


    def __init__(self, graph: Graph, coloring: dict, parent=None):
        super().__init__(parent)
        self.graph = graph
        self.coloring = coloring
        self.setWindowTitle("Welsh-Powell Renklendirme Sonuçları")
        self.setMinimumSize(800, 500)
        self.exporter = Exporter()

        main_layout = QVBoxLayout(self)

        # Tablo Oluşturma
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(['ID', 'Üniversite Adı', 'Şehir', 'Renk ID', 'Renk Adı', 'Komşular'])
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Düzenlemeyi engelle

        # Sütunları içeriğe göre ayarla
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self._populate_table()

        main_layout.addWidget(self.table_widget)

        # Dışa Aktar Butonu
        btn_export = QPushButton("CSV Olarak Dışa Aktar")
        btn_export.clicked.connect(self._export_to_csv)
        main_layout.addWidget(btn_export)

    def _populate_table(self):
        """Tabloyu renklendirme verileriyle doldurur."""
        self.table_widget.setRowCount(len(self.coloring))
        row = 0

        # Renk ID'sine göre sırala
        sorted_items = sorted(self.coloring.items(), key=lambda item: item[1])

        for uni_id, color_id in sorted_items:
            node = self.graph.nodes.get(uni_id)
            if not node:
                continue

            color_name = COLOR_NAMES.get(color_id, f"Renk {color_id}")
            # Komşu isimlerini al
            neighbor_ids = self.graph.get_neighbors(uni_id)
            neighbor_names = [self.graph.nodes[nid].adi for nid in neighbor_ids if nid in self.graph.nodes]
            neighbors_str = ", ".join(sorted(neighbor_names))

            self.table_widget.setItem(row, 0, QTableWidgetItem(str(node.uni_id)))
            self.table_widget.setItem(row, 1, QTableWidgetItem(node.adi))
            self.table_widget.setItem(row, 2, QTableWidgetItem(node.sehir))
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(color_id)))
            self.table_widget.setItem(row, 4, QTableWidgetItem(color_name))
            self.table_widget.setItem(row, 5, QTableWidgetItem(neighbors_str))

            row += 1

        self.table_widget.resizeColumnsToContents()

    def _export_to_csv(self):
        try:
            print("EXPORT TIKLANDI")
            print("COLORING:", self.coloring)
            print("COLORING LEN:", len(self.coloring))

            output_path = self.exporter.export_coloring_to_csv(
                self.graph,
                self.coloring
            )

            QMessageBox.information(
                self,
                "Başarılı",
                f"Renklendirme sonuçları başarıyla dışa aktarıldı:\n{output_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))
