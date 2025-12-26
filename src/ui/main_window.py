# ui/main_window.py

import sys
import os
import time  # Süre ölçümü için

# Import yollarını garantiye al
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout,
                             QHBoxLayout, QFrame, QPushButton, QMessageBox,
                             QAction, QToolBar, QDockWidget, QTabWidget,
                             QTextEdit, QFormLayout, QStyle, QApplication,
                             QStackedWidget, QGraphicsDropShadowEffect,QInputDialog, QComboBox,
                             QSizePolicy, QSpacerItem, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QDialog)
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QFontDatabase, QLinearGradient, QPainter

# Modüller
from .graph_canvas import GraphCanvas
from .add_node_dialog import AddNodeDialog
from .coloring_dialog import ColoringDialog
from .path_dialog import PathDialog
from .add_edge_dialog import AddEdgeDialog
from core.node import Node


class ModernButton(QPushButton):
    """Modern tasarımlı, hover efektli buton sınıfı"""

    def __init__(self, text="", icon=None, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)
        self._opacity = 1.0

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.isEnabled():
            if self.underMouse():
                bg_color = QColor(42, 130, 218)
            else:
                bg_color = QColor(62, 150, 248)
        else:
            bg_color = QColor(108, 117, 125)

        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, bg_color.lighter(110))
        gradient.setColorAt(1, bg_color.darker(110))

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 8, 8)

        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())


class CardWidget(QFrame):
    """Gölge efektli beyaz kart paneli"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            CardWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # 🔽 🔽 🔽 EN ÖNEMLİ DEĞİŞİKLİK 🔽 🔽 🔽
        self.title_label = None

        if title:
            self.title_label = QLabel(title)   # 👈 self. EKLENDİ
            self.title_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #f0f0f0;
                }
            """)
            layout.addWidget(self.title_label)

        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
        self.setLayout(layout)

    # 👇 DIŞARIDAN GÜVENLİ BAŞLIK DEĞİŞTİRME
    def setTitle(self, text):
        if self.title_label:
            self.title_label.setText(text)


class MainWindow(QMainWindow):
    def __init__(self, graph, data_loader):
        super().__init__()
        self.graph = graph
        self.loader = data_loader
        self.selected_node = None
        self.coloring_result = {}

        self.setWindowTitle("Sosyal Ağ Analiz Platformu")
        self.setMinimumSize(1400, 850)
        self.apply_modern_theme()

        self.animation_sequence = []
        self.current_animation_step = 0

        self.init_ui()

    def init_ui(self):
        # 1. MERKEZİ ALAN (Grafik Canvas)
        self.canvas = GraphCanvas(self.graph, on_node_clicked=self.show_node_details, on_edge_clicked=self.show_edge_details)

        canvas_wrapper = QWidget()
        canvas_layout = QVBoxLayout(canvas_wrapper)
        canvas_layout.setContentsMargins(15, 15, 15, 15)
        canvas_layout.addWidget(self.canvas)
        canvas_wrapper.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 1px solid #dee2e6;
            }
        """)
        self.setCentralWidget(canvas_wrapper)

        # 2. ÜST BAR
        self.create_header_bar()

        # 3. SOL PANEL
        self.create_sidebar()

        # 4. SAĞ PANEL
        self.create_detail_panel()

        # 5. ALT PANEL
        self.create_status_bar()

        QTimer.singleShot(100, self.animate_sidebar)

    def apply_modern_theme(self):
        QApplication.setStyle("Fusion")

        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 242, 245))
        palette.setColor(QPalette.WindowText, QColor(33, 37, 41))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
        palette.setColor(QPalette.Button, QColor(255, 255, 255))
        palette.setColor(QPalette.ButtonText, QColor(33, 37, 41))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)

        self.setStyleSheet("""
            QMainWindow { background-color: #f0f2f5; }
            QDockWidget {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QDockWidget::title {
                background: transparent;
                padding: 10px;
                font-weight: bold;
            }
            QMessageBox { background-color: white; }
            QComboBox { padding: 5px; border-radius: 4px; border: 1px solid #ccc; }
        """)

    def create_header_bar(self):
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: white; border-bottom: 1px solid #dee2e6;")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)

        # lbl_icon = QLabel("🕸️")
        # lbl_icon.setStyleSheet("font-size: 24px;")

        lbl_title = QLabel("Üniversite Sosyal Ağ Analizi")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        lbl_title.setStyleSheet("color: #2c3e50;")

        # layout.addWidget(lbl_icon)
        layout.addSpacing(10)
        layout.addWidget(lbl_title)
        layout.addStretch()

        btn_refresh = ModernButton("Görünümü Sıfırla")
        btn_refresh.clicked.connect(lambda: [self.reset_visuals(), self.canvas.fit_view()])

        btn_help = QPushButton("❓")
        btn_help.setFixedSize(40, 40)
        btn_help.setStyleSheet("border-radius: 20px; background-color: #f1f3f5; border: 1px solid #dee2e6;")
        btn_help.clicked.connect(lambda: QMessageBox.information(self, "Hakkında", "Sosyal Ağ Analizi Projesi v3.0"))

        layout.addWidget(btn_refresh)
        layout.addSpacing(10)
        layout.addWidget(btn_help)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(header)
        self.setMenuWidget(wrapper)

    def create_sidebar(self):
        self.sidebar = QDockWidget("Araçlar", self)
        self.sidebar.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.sidebar.setFeatures(QDockWidget.DockWidgetMovable)
        self.sidebar.setFixedWidth(300)

        content = QWidget()
        content.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- 1. GRUP: ALGORİTMALAR ---
        lbl_algo = QLabel("ALGORİTMALAR")
        lbl_algo.setAlignment(Qt.AlignCenter)
        lbl_algo.setFixedHeight(45)
        lbl_algo.setStyleSheet("background-color: #3e96f8; color: white; font-weight: bold; font-size: 13px;")
        layout.addWidget(lbl_algo)

        algo_items = [
            ("Renklendir (W.Powell)", self.run_coloring),
            ("A* (En Kısa Yol)", lambda: self.open_path_dialog("A*")),
            ("Dijkstra (En Kısa Yol)", lambda: self.open_path_dialog("Dijkstra")),
            ("Toplulukları Bul", self.show_communities),
            ("En Etkili 5 Üniversite", self.show_top_5)
        ]
        for text, func in algo_items:
            btn = self.create_menu_button(text, "#3e96f8")
            btn.clicked.connect(func)
            layout.addWidget(btn)

        # --- 2. GRUP: CANLI SİMÜLASYON ---
        # Görseldeki "Canlı Simülasyon" kutu görünümünü koruyoruz
        sim_card = CardWidget("Canlı Simülasyon")
        sim_layout = QVBoxLayout()

        btn_bfs = ModernButton("BFS Başlat")
        btn_bfs.clicked.connect(lambda: self.run_algo("BFS"))
        btn_dfs = ModernButton("DFS Başlat")
        btn_dfs.clicked.connect(lambda: self.run_algo("DFS"))

        sim_layout.addWidget(btn_bfs)
        sim_layout.addWidget(btn_dfs)
        sim_card.content_layout.addLayout(sim_layout)
        layout.addWidget(sim_card)

        # --- 3. GRUP: NODE & EDGE İŞLEMLERİ ---
        lbl_ops = QLabel("NODE & EDGE İŞLEMLERİ")
        lbl_ops.setAlignment(Qt.AlignCenter)
        lbl_ops.setFixedHeight(45)
        lbl_ops.setStyleSheet("background-color: #3e96f8; color: white; font-weight: bold; font-size: 13px;")
        layout.addWidget(lbl_ops)

        ops_items = [
            ("🏛️ Üniversite Ekle", self.open_add_dialog),
            ("Üniversite Sil", self.open_delete_node_dialog),
            ("🔗 Bağlantı Ekle", self.open_add_edge_dialog),
            ("Bağlantı Sil", self.open_delete_edge_dialog)
        ]
        for text, func in ops_items:
            btn = self.create_menu_button(text, "#f44336")  # Silme işlemleri için kırmızı vurgu
            btn.clicked.connect(func)
            layout.addWidget(btn)

        layout.addStretch()

        # Alt bilgi
        lbl_footer = QLabel(f"Toplam Düğüm: {len(self.graph.nodes)}")
        lbl_footer.setAlignment(Qt.AlignCenter)
        lbl_footer.setStyleSheet("padding: 10px; color: #888; border-top: 1px solid #eee;")
        layout.addWidget(lbl_footer)

        self.sidebar.setWidget(content)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar)

    def create_menu_button(self, text, color):
        btn = QPushButton(text)
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: #333;
                text-align: left;
                padding-left: 20px;
                border: none;
                border-bottom: 1px solid #f0f0f0;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #f8f9fa;
                border-left: 5px solid {color};
            }}
        """)
        return btn

    def create_detail_panel(self):
        self.detail_panel = QDockWidget("Detaylar", self)
        self.detail_panel.setAllowedAreas(Qt.RightDockWidgetArea)
        self.detail_panel.setFeatures(QDockWidget.DockWidgetMovable)
        self.detail_panel.setMinimumWidth(320)


        content = QWidget()
        layout = QVBoxLayout(content)

        self.uni_card = CardWidget("Üniversite Bilgileri")
        self.uni_card_title = self.uni_card.title_label

        self.lbl_uni_icon = QLabel("🏛️")
        self.lbl_uni_icon.setAlignment(Qt.AlignCenter)
        self.lbl_uni_icon.setStyleSheet("font-size: 50px; margin-bottom: 10px;")
        self.uni_card.content_layout.addWidget(self.lbl_uni_icon)

        self.detail_labels = {}
        self.detail_titles = {}
        fields = [
            ("name", "Üniversite:", "Seçim Yok"),
            ("city", "Konum:", "-"),
            ("year", "Kuruluş:", "-"),
            ("students", "Öğrenci:", "-"),
            ("rank", "Sıralama:", "-")
        ]

        for key, title, default in fields:
            row = QHBoxLayout()

            lbl_t = QLabel(title)
            lbl_t.setStyleSheet("color: #777; font-weight: bold;")

            lbl_v = QLabel(default)
            lbl_v.setStyleSheet("color: #333;")
            lbl_v.setWordWrap(True)

            row.addWidget(lbl_t)
            row.addWidget(lbl_v)

            self.uni_card.content_layout.addLayout(row)

            self.detail_titles[key] = lbl_t  # 👈 başlık
            self.detail_labels[key] = lbl_v  # 👈 değer

        layout.addWidget(self.uni_card)

        action_card = CardWidget("İşlemler")
        act_layout = QVBoxLayout()

        self.btn_edit = QPushButton("Bilgileri Düzenle")
        self.btn_edit.setStyleSheet("background-color: #FFC107; padding: 8px; border-radius: 4px;")
        self.btn_edit.clicked.connect(self.edit_selected_node)
        self.btn_edit.setEnabled(False)

        self.btn_delete = QPushButton("Üniversiteyi Sil")
        self.btn_delete.setStyleSheet("background-color: #F44336; color: white; padding: 8px; border-radius: 4px;")
        self.btn_delete.clicked.connect(self.delete_selected_node)
        self.btn_delete.setEnabled(False)

        act_layout.addWidget(self.btn_edit)
        act_layout.addWidget(self.btn_delete)
        action_card.content_layout.addLayout(act_layout)

        layout.addWidget(action_card)
        layout.addStretch()

        self.detail_panel.setWidget(content)
        self.addDockWidget(Qt.RightDockWidgetArea, self.detail_panel)

    def create_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("background-color: white; border-top: 1px solid #ccc; color: #555;")
        self.status_label = QLabel("Sistem Hazır")
        self.status_bar.addWidget(self.status_label)

    def animate_sidebar(self):
        anim = QPropertyAnimation(self.sidebar, b"geometry")
        anim.setDuration(600)
        anim.setEasingCurve(QEasingCurve.OutExpo)
        start = self.sidebar.geometry()
        start.setX(-300)
        end = self.sidebar.geometry()
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.start()

    # ==========================================================
    # İŞLEV FONKSİYONLARI (ZAMAN ÖLÇÜMLÜ)
    # ==========================================================

    # main_window.py içindeki metod güncellemesi

    def show_node_details(self, node):
        self.selected_node = node
        self.selected_edge = None

        # Başlık & ikon düzenleme
        self.lbl_uni_icon.setText("🏛️")
        self.uni_card.setTitle("Üniversite Bilgileri")

        # Alanları görünür yap ve etiketleri düzelt
        for key in self.detail_titles:
            self.detail_titles[key].show()
            self.detail_labels[key].show()
        self.detail_titles["name"].setText("Üniversite:")
        self.detail_titles["rank"].setText("Sıralama:")

        # Verileri doldur
        self.detail_labels["name"].setText(node.adi)
        self.detail_labels["city"].setText(f"{node.sehir} / {node.ilce}")
        self.detail_labels["year"].setText(str(node.kurulus_yil))
        self.detail_labels["students"].setText(f"{node.ogrenci_sayisi:,}")
        self.detail_labels["rank"].setText(f"#{node.tr_siralama}")

        # --- BUTON YÖNLENDİRMELERİ ---
        self.btn_edit.setVisible(True)
        self.btn_edit.setEnabled(True)
        self.btn_delete.setEnabled(True)
        self.btn_delete.setText("Üniversiteyi Sil")

        # Önce eski bağlantıları kopar, sonra ilgili fonksiyonlara bağla
        try:
            self.btn_edit.clicked.disconnect()
        except:
            pass
        self.btn_edit.clicked.connect(self.edit_selected_node)  # Düzenle -> edit_selected_node

        try:
            self.btn_delete.clicked.disconnect()
        except:
            pass
        self.btn_delete.clicked.connect(self.delete_selected_node)  # Sil -> delete_selected_node

    def open_add_dialog(self):
        try:
            existing_unis = self.loader.get_university_names()
            dialog = AddNodeDialog(existing_unis, self, loader=self.loader)
            if dialog.exec_():
                info, partners = dialog.get_data()
                self.save_university(info, partners)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Pencere açılamadı: {str(e)}")

    def open_add_edge_dialog(self):
        try:
            if len(self.graph.nodes) < 2:
                QMessageBox.warning(self, "Yetersiz Veri", "Bağlantı eklemek için en az 2 üniversite olmalı.")
                return
            dialog = AddEdgeDialog(self.graph.nodes, self)
            if dialog.exec_():
                u1_id, u2_id = dialog.get_data()
                if u1_id == u2_id:
                    QMessageBox.warning(self, "Hata", "Bir üniversite kendine bağlanamaz.")
                    return
                # Zaten var mı kontrolü
                exists = False
                for edge in self.graph.edges:
                    ids = [edge.node1.uni_id, edge.node2.uni_id]
                    if u1_id in ids and u2_id in ids:
                        exists = True;
                        break
                if exists:
                    QMessageBox.warning(self, "Bilgi", "Bu bağlantı zaten mevcut.")
                    return
                self.loader.add_relation(u1_id, u2_id)
                self.graph.add_edge(u1_id, u2_id)
                self.canvas.update()
                QMessageBox.information(self, "Başarılı", "Bağlantı eklendi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def open_delete_edge_dialog(self):
        """Bağlantı Silme Penceresi (Hata kontrollü ve Onay mekanizmalı)"""
        try:
            if not self.graph.edges:
                QMessageBox.warning(self, "Veri Yok", "Silinecek bağlantı yok.")
                return

            # AddEdgeDialog'u kullanıyoruz
            dialog = AddEdgeDialog(self.graph.nodes, self)
            dialog.setWindowTitle("Bağlantı Sil")

            if dialog.exec_():
                u1_id, u2_id = dialog.get_data()

                # --- KONTROL 1: Aynı üniversite seçimi ---
                if u1_id == u2_id:
                    QMessageBox.warning(self, "Hata", "Aynı üniversiteyi seçtiniz. Lütfen farklı iki üniversite seçin.")
                    return

                # Bağlantıyı bulmaya çalış
                edge_to_remove = None
                for edge in self.graph.edges:
                    ids = [edge.node1.uni_id, edge.node2.uni_id]
                    if u1_id in ids and u2_id in ids:
                        edge_to_remove = edge
                        break

                if edge_to_remove:
                    # --- KONTROL 2: Silme Onayı ---
                    confirm_msg = f"{edge_to_remove.node1.adi} ve {edge_to_remove.node2.adi} arasındaki bağlantı silinecek. Onaylıyor musunuz?"
                    reply = QMessageBox.question(self, 'Onay', confirm_msg, QMessageBox.Yes | QMessageBox.No,
                                                 QMessageBox.No)

                    if reply == QMessageBox.Yes:
                        # Graf'tan sil
                        self.graph.edges.remove(edge_to_remove)
                        if u1_id in self.graph.adj:
                            self.graph.adj[u1_id].discard(u2_id)
                        if u2_id in self.graph.adj:
                            self.graph.adj[u2_id].discard(u1_id)

                        # Veritabanından sil
                        if hasattr(self.loader, 'delete_relation'):
                            self.loader.delete_relation(u1_id, u2_id)

                        self.canvas.update()
                        QMessageBox.information(self, "Başarılı", "Bağlantı başarıyla silindi.")
                else:
                    QMessageBox.warning(self, "Hata", "Seçilen üniversiteler arasında aktif bir bağlantı bulunamadı.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Silme hatası oluştu: {e}")

    def save_university(self, info, partners):
        try:
            new_id = self.loader.add_university(info)
            new_node = Node(new_id, info["adi"], info["sehir"], info["ilce"],
                            info["kurulus_yil"], info["ogrenci_sayisi"],
                            int(info["fakulte_sayisi"]), info["akademik_sayisi"], info["tr_siralama"])
            import random
            cx = (self.canvas.width() / 2 - self.canvas.offset.x()) / self.canvas.scale_factor
            cy = (self.canvas.height() / 2 - self.canvas.offset.y()) / self.canvas.scale_factor

            new_node.x = cx + random.randint(-250, 250)  # 1200'den 250'ye çektik
            new_node.y = cy + random.randint(-250, 250)

            self.graph.add_node(new_node)
            for pid in partners:
                if pid in self.graph.nodes:
                    self.loader.add_relation(new_id, pid)
                    self.graph.add_edge(new_id, pid)
            self.canvas.update()
            QMessageBox.information(self, "Başarılı", f"{info['adi']} eklendi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def edit_selected_node(self):
        if not self.selected_node: return
        try:
            dialog = AddNodeDialog([], self, edit_data=self.selected_node, loader=self.loader)
            if dialog.exec_():
                info, _ = dialog.get_data()
                self.loader.update_university(self.selected_node.uni_id, info)
                n = self.selected_node
                n.adi = info["adi"]
                n.sehir = info["sehir"]
                n.ilce = info["ilce"]
                n.kurulus_yil = info["kurulus_yil"]
                n.ogrenci_sayisi = info["ogrenci_sayisi"]
                n.fakulte_sayisi = int(info["fakulte_sayisi"])
                n.akademik_sayisi = info["akademik_sayisi"]
                n.tr_siralama = info["tr_siralama"]
                for edge in self.graph.edges:
                    if edge.node1 == n or edge.node2 == n:
                        edge.weight = self.graph.calculate_weight(edge.node1, edge.node2)
                self.show_node_details(n)
                self.canvas.update()
                QMessageBox.information(self, "Güncellendi", "Bilgiler başarıyla güncellendi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def delete_selected_node(self):
        if not self.selected_node: return
        reply = QMessageBox.question(self, 'Onay', f"{self.selected_node.adi} silinecek. Onaylıyor musunuz?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.loader.delete_university(self.selected_node.uni_id)
                self.graph.remove_node(self.selected_node.uni_id)
                self.selected_node = None
                self.btn_edit.setEnabled(False)
                self.btn_delete.setEnabled(False)
                for key in self.detail_labels:
                    self.detail_labels[key].setText("-")
                self.detail_labels["name"].setText("Silindi")
                self.canvas.update()
                QMessageBox.information(self, "Silindi", "Kayıt silindi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def open_path_dialog(self, algo="Dijkstra"):
        """En Kısa Yol Penceresi"""
        try:
            uni_list = self.loader.get_university_names()
            dialog = PathDialog(uni_list, self)
            dialog.setWindowTitle(f"En Kısa Yol ({algo})")

            if dialog.exec_():
                start_id, end_id, s_name, e_name = dialog.get_selection()
                if start_id == end_id:
                    QMessageBox.warning(self, "Hata", "Başlangıç ve Bitiş aynı olamaz.")
                    return

                # --- ÖNCE TEMİZLE ---
                self.reset_visuals()
                # --------------------

                start_time = time.perf_counter()

                if algo == "A*" and hasattr(self.graph, 'a_star'):
                    cost, path = self.graph.a_star(start_id, end_id)
                else:
                    cost, path = self.graph.dijkstra(start_id, end_id)

                elapsed = time.perf_counter() - start_time

                if cost == float('inf'):
                    QMessageBox.warning(self, "Sonuç", "Yol bulunamadı.")
                    self.canvas.set_path([])
                else:
                    self.canvas.set_path(path)
                    msg = f"✅ Yol Başarıyla Bulundu!\n\n Algoritma: {algo}\n Süre: {elapsed:.6f} sn\n Maliyet: {cost:.2f}"
                    QMessageBox.information(self, "Rota Sonucu", msg)

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def run_coloring(self):
        """Welsh-Powell Renklendirme"""
        if not self.graph.nodes: return

        # --- ÖNCE TEMİZLE ---
        self.reset_visuals()
        # --------------------

        try:
            start_time = time.perf_counter()
            new_coloring = self.graph.welsh_powell_coloring()
            elapsed = time.perf_counter() - start_time

            self.canvas.update_coloring(new_coloring)
            self.coloring_result = new_coloring

            QMessageBox.information(self, "Renklendirme Bitti",
                                    f"Graf renklendirme işlemi tamamlandı.\n\n Geçen Süre: {elapsed:.6f} saniye")

            dialog = ColoringDialog(self.graph, self.coloring_result, self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Renklendirme hatası: {e}")

    # ui/main_window.py içindeki show_communities metodunu bununla değiştir:

    def show_communities(self):
        """Topluluk Analizi Sonucu ve Doğrudan CSV Aktar Butonu"""
        if not hasattr(self.graph, 'find_connected_components'):
            QMessageBox.warning(self, "Eksik", "Graph sınıfında analiz metodu yok.")
            return

        import time
        start_time = time.perf_counter()
        comps = self.graph.find_connected_components()
        elapsed = time.perf_counter() - start_time

        # Mesaj içeriği hazırlama (mevcut kodunuzla aynı)
        msg = f" Analiz Süresi: {elapsed:.6f} saniye\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"Toplam {len(comps)} adet ayrık topluluk bulundu.\n\n"

        for i, comp in enumerate(comps, 1):
            names = ", ".join([n.adi[:20] + "..." if len(n.adi) > 20 else n.adi for n in comp[:3]])
            if len(comp) > 3: names += f" ve {len(comp) - 3} diğer..."
            msg += f"🔹 Grup {i} ({len(comp)} Üni): {names}\n"

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Topluluk Analizi Sonucu")
        msg_box.setText(msg)
        export_button = msg_box.addButton("CSV Olarak Dışarı Aktar", QMessageBox.ActionRole)
        close_button = msg_box.addButton("Kapat", QMessageBox.RejectRole)
        msg_box.exec_()

        if msg_box.clickedButton() == export_button:
            try:
                from core.exporter import Exporter
                exporter = Exporter()
                # DİKKAT: Artık ilk parametre olarak self.graph gönderiyoruz
                path = exporter.export_communities_to_csv(self.graph, comps)
                QMessageBox.information(self, "Başarılı", f"Rapor tablo formatında dışa aktarıldı:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dışa aktarma başarısız: {e}")

    def show_top_5(self):
        """En Etkili 5 Üniversite Gösterimi (YENİ)"""
        if not hasattr(self.graph, 'get_top_5_influential_unis'):
            QMessageBox.warning(self, "Eksik", "Metot bulunamadı.")
            return

        start_time = time.perf_counter()
        data = self.graph.get_top_5_influential_unis()
        elapsed = time.perf_counter() - start_time

        # Dialog oluştur
        dialog = QDialog(self)
        dialog.setWindowTitle("En Etkili 5 Üniversite (Merkezilik)")
        dialog.resize(800, 500)
        layout = QVBoxLayout(dialog)

        lbl_time = QLabel(f"Hesaplama Süresi: {elapsed:.6f} sn")
        layout.addWidget(lbl_time)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Sıra", "Üniversite", "Şehir", "Bağlantı Sayısı", "Toplam Ağırlık"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        table.setRowCount(len(data))
        for i, row in enumerate(data):
            table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            table.setItem(i, 1, QTableWidgetItem(row['adi']))
            table.setItem(i, 2, QTableWidgetItem(row['sehir']))
            table.setItem(i, 3, QTableWidgetItem(str(row['derece'])))
            table.setItem(i, 4, QTableWidgetItem(str(row['toplam_agirlik'])))

        layout.addWidget(table)

        # Dışa aktar butonu
        btn_export = QPushButton("Bu Raporu İndir (CSV)")
        btn_export.clicked.connect(lambda: [self.export_centrality_report(), dialog.accept()])
        layout.addWidget(btn_export)

        dialog.exec_()

    def export_centrality_report(self):
        """CSV Raporu Al"""
        if hasattr(self.graph, 'get_top_5_influential_unis'):
            try:
                data = self.graph.get_top_5_influential_unis()
                from core.exporter import Exporter
                exporter = Exporter()
                path = exporter.export_centrality_to_csv(data)
                QMessageBox.information(self, "Başarılı", f"Dosya kaydedildi:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))
        else:
            QMessageBox.warning(self, "Eksik", "Raporlama fonksiyonu bulunamadı.")

    def run_algo(self, algo_type):
        """BFS / DFS Animasyonu"""
        if not self.selected_node:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce haritadan bir Başlangıç Düğümü seçin.")
            return

        # --- ÖNCE TEMİZLE ---
        self.reset_visuals()
        # --------------------

        start_id = self.selected_node.uni_id
        start_time = time.perf_counter()

        if algo_type == "BFS":
            self.animation_sequence = self.graph.bfs(start_id)
        else:
            self.animation_sequence = self.graph.dfs(start_id)

        elapsed = time.perf_counter() - start_time

        msg = f"{algo_type} hesaplandı ({elapsed:.6f} sn).\nAnimasyon başlatılıyor..."
        QMessageBox.information(self, "Hazır", msg)

        self.status_label.setText(f"{algo_type} oynatılıyor...")
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_animation_step)
        self.timer.start(150)

    def next_animation_step(self):
        if self.animation_sequence:
            node = self.animation_sequence.pop(0)
            self.canvas.algo_nodes.append(node)
            self.canvas.update()
        else:
            self.timer.stop()
            current_text = self.status_label.text()
            self.status_label.setText(current_text + " | Animasyon Bitti.")
            QMessageBox.information(self, "Bitti", "Animasyon tamamlandı.")

    def reset_visuals(self):
        """Haritadaki tüm görsel efektleri (yol, animasyon, renk) temizler."""
        # 1. Animasyon listesini temizle (Mavilikler gider)
        self.canvas.algo_nodes = []

        # 2. Çizilmiş yolları temizle (Kırmızılıklar gider)
        self.canvas.highlighted_path = []

        # 3. Renklendirmeyi temizle (İstersen bunu yorum satırı yapabilirsin,
        # ama yeni bir işlem yaparken eskileri silmek daha temizdir)
        # self.canvas.coloring_result = {}
        # self.coloring_result = {}

        # 4. Canvas'ı yenile
        self.canvas.update()

    # main_window.py içine eklenecek metodlar

    # main_window.py içindeki metod güncellemesi

    def show_edge_details(self, edge):
        self.selected_node = None
        self.selected_edge = edge

        # Başlık & ikon düzenleme
        self.lbl_uni_icon.setText("🔗")
        self.uni_card.setTitle("Bağlantı Bilgileri")

        # Kullanılmayan alanları gizle
        for key in ["city", "year", "students"]:
            self.detail_titles[key].hide()
            self.detail_labels[key].hide()

        self.detail_titles["name"].setText("Bağlantı:")
        self.detail_titles["rank"].setText("Ağırlık:")

        # Değerler
        self.detail_labels["name"].setText(f"{edge.node1.adi} ↔\n{edge.node2.adi}")
        self.detail_labels["rank"].setText(f"{edge.weight:.4f}")

        # --- BUTON YÖNLENDİRMELERİ ---
        self.btn_edit.setVisible(False)  # Bağlantıda düzenle butonu gözükmesin
        self.btn_delete.setEnabled(True)
        self.btn_delete.setText("Bağlantıyı Sil")

        # Sil butonunu delete_selected_edge fonksiyonuna bağla
        try:
            self.btn_delete.clicked.disconnect()
        except:
            pass
        self.btn_delete.clicked.connect(self.delete_selected_edge)  # Sil -> delete_selected_edge

    def find_label_by_text(self, text):
        """Yardımcı fonksiyon: Paneldeki statik etiketleri bulur."""
        # self.uni_card içindeki tüm QLabel'ları tara
        for label in self.uni_card.findChildren(QLabel):
            if label.text() in ["Üniversite:", "Bağlantı:", "Sıralama:", "Ağırlık:"]:
                if text in [label.text()]:
                    return label
        return QLabel()  # Güvenlik için boş etiket dön

    def delete_selected_edge(self):
        """Seçili kenarı siler."""
        if not self.selected_edge: return

        u1_id = self.selected_edge.node1.uni_id
        u2_id = self.selected_edge.node2.uni_id

        reply = QMessageBox.question(self, 'Bağlantı Sil', "Bu bağlantıyı silmek istediğinize emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Veritabanından sil
            self.loader.delete_relation(u1_id, u2_id)
            # Graf yapısından sil
            self.graph.remove_edge(u1_id, u2_id)
            # Seçimi temizle
            self.selected_edge = None
            self.reset_visuals()
            QMessageBox.information(self, "Başarılı", "Bağlantı silindi.")

    def open_delete_node_dialog(self):
        """Sadece dropdown üzerinden üniversite seçerek silme işlemi yapar."""
        try:
            # Üniversite isimlerini al
            uni_names = [uni[1] for uni in self.loader.get_university_names()]
            uni_data = self.loader.get_university_names()  # [(id, isim), ...]

            if not uni_names:
                QMessageBox.warning(self, "Hata", "Silinecek üniversite bulunamadı.")
                return

            # Kullanıcıya dropdown listesi sun
            item, ok = QInputDialog.getItem(self, "Üniversite Sil",
                                            "Silmek istediğiniz üniversiteyi seçin:",
                                            uni_names, 0, False)

            if ok and item:
                # Seçilen isme göre ID'yi bul
                selected_id = next(u[0] for u in uni_data if u[1] == item)

                confirm = QMessageBox.question(self, "Onay",
                                               f"'{item}' üniversitesini ve tüm bağlantılarını silmek istediğinize emin misiniz?",
                                               QMessageBox.Yes | QMessageBox.No)

                if confirm == QMessageBox.Yes:
                    # 1. Veritabanından sil
                    self.loader.delete_university(selected_id)
                    # 2. Graf yapısından sil
                    self.graph.remove_node(selected_id)

                    # Eğer silinen düğüm o an sağ panelde seçiliyse temizle
                    if self.selected_node and self.selected_node.uni_id == selected_id:
                        self.selected_node = None
                        self.reset_visuals()

                    self.canvas.update()
                    QMessageBox.information(self, "Başarılı", f"'{item}' başarıyla silindi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Silme işlemi başarısız oldu: {str(e)}")


