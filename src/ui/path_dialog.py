from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QAbstractItemView

class PathDialog(QDialog):
    def __init__(self, university_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("En Kısa Yol")
        self.resize(350, 250)
        self.university_list = university_list

        layout = QVBoxLayout(self)

        # Başlangıç
        layout.addWidget(QLabel("Başlangıç Üniversitesi:"))
        self.combo_start = QComboBox()
        self.setup_combo(self.combo_start)
        layout.addWidget(self.combo_start)

        layout.addSpacing(10)

        # Bitiş
        layout.addWidget(QLabel("Hedef Üniversite:"))
        self.combo_end = QComboBox()
        self.setup_combo(self.combo_end)
        layout.addWidget(self.combo_end)

        btn_calc = QPushButton("Yolu Hesapla")
        btn_calc.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        btn_calc.clicked.connect(self.accept)
        layout.addWidget(btn_calc)

    def setup_combo(self, combo):
        combo.setEditable(True)
        combo.setMaxVisibleItems(12) # Kaydırma çubuğu çıkmadan önce görünecek satır sayısı
        
        sorted_unis = sorted(self.university_list, key=lambda x: x[1])
        for uni_id, uni_name in sorted_unis:
            combo.addItem(uni_name, uni_id)

    def get_selection(self):
        return (self.combo_start.currentData(), self.combo_end.currentData(),
                self.combo_start.currentText(), self.combo_end.currentText())