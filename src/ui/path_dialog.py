from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox,
                             QPushButton, QMessageBox)


class PathDialog(QDialog):
    def __init__(self, university_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("En Kısa Yol Bul (Dijkstra)")
        self.resize(300, 200)
        self.university_list = university_list  # [(id, isim), ...]

        layout = QVBoxLayout(self)

        # Başlangıç
        layout.addWidget(QLabel("Başlangıç Üniversitesi:"))
        self.combo_start = QComboBox()
        self.populate_combo(self.combo_start)
        layout.addWidget(self.combo_start)

        # Bitiş
        layout.addWidget(QLabel("Hedef Üniversite:"))
        self.combo_end = QComboBox()
        self.populate_combo(self.combo_end)
        layout.addWidget(self.combo_end)

        # Hesapla Butonu
        btn_calc = QPushButton("Yolu Hesapla")
        btn_calc.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        btn_calc.clicked.connect(self.accept)
        layout.addWidget(btn_calc)

    def populate_combo(self, combo):
        # Listeyi isme göre sıralı ekle
        sorted_unis = sorted(self.university_list, key=lambda x: x[1])
        for uni_id, uni_name in sorted_unis:
            combo.addItem(uni_name, uni_id)  # uni_id gizli veri olarak saklanır

    def get_selection(self):
        start_id = self.combo_start.currentData()
        end_id = self.combo_end.currentData()
        start_name = self.combo_start.currentText()
        end_name = self.combo_end.currentText()
        return start_id, end_id, start_name, end_name