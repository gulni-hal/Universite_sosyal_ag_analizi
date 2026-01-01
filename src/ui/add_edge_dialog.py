from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QDialogButtonBox, QCompleter
from PyQt5.QtCore import Qt


class AddEdgeDialog(QDialog):
    def __init__(self, nodes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bağlantı İşlemi")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        self.combo1 = QComboBox()
        self.combo2 = QComboBox()

        # Kaydırma ve Arama Özellikleri Ayarı
        for combo in [self.combo1, self.combo2]:
            combo.setEditable(True)  # Yazarak arama yapabilmek için
            combo.setInsertPolicy(QComboBox.NoInsert)


            completer = combo.completer()
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setFilterMode(Qt.MatchContains)  # Kelime içinden arama yapar

            combo.setMaxVisibleItems(12)  # 12 öğeden sonra scroll bar çıkar
            combo.setStyleSheet("QComboBox { combobox-popup: 0; }")  # Scroll barı aktif eder

        # Üniversiteleri isme göre sıralayarak ekle
        sorted_nodes = sorted(nodes.values(), key=lambda x: x.adi)
        for node in sorted_nodes:
            self.combo1.addItem(node.adi, node.uni_id)
            self.combo2.addItem(node.adi, node.uni_id)

        layout.addWidget(QLabel("<b>1. Üniversite:</b>"))
        layout.addWidget(self.combo1)
        layout.addSpacing(10)
        layout.addWidget(QLabel("<b>2. Üniversite:</b>"))
        layout.addWidget(self.combo2)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return self.combo1.currentData(), self.combo2.currentData()