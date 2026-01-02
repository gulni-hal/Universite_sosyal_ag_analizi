# main.py

from PyQt5.QtWidgets import QApplication
import sys
import os

from core.graph import Graph
from core.data_loader import DataLoader
from ui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    graph = Graph()

    # DB yolunu ayarla
    db_path = os.path.join(os.path.dirname(__file__), "../data/universite.db")
    loader = DataLoader(db_path)

    # Grafı yükle
    loader.load_graph(graph)

    # Pencereyi aç
    window = MainWindow(graph, loader)
    window.show()

    sys.exit(app.exec_())