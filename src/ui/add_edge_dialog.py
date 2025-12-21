# ui/add_edge_dialog.py (Yeni dosya oluşturun)
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QDialogButtonBox


class AddEdgeDialog(QDialog):
    def __init__(self, nodes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bağlantı Ekle")
        layout = QVBoxLayout(self)

        self.combo1 = QComboBox()
        self.combo2 = QComboBox()

        for node in nodes.values():
            self.combo1.addItem(node.adi, node.uni_id)
            self.combo2.addItem(node.adi, node.uni_id)

        layout.addWidget(QLabel("1. Üniversite:"))
        layout.addWidget(self.combo1)
        layout.addWidget(QLabel("2. Üniversite:"))
        layout.addWidget(self.combo2)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return self.combo1.currentData(), self.combo2.currentData()