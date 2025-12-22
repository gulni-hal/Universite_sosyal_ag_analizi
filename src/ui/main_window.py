# ui/main_window.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout,
                             QHBoxLayout, QFrame, QPushButton, QMessageBox, QFileDialog,)
from PyQt5.QtGui import QColor
from .graph_canvas import GraphCanvas
from .add_node_dialog import AddNodeDialog
from .coloring_dialog import ColoringDialog
from .add_edge_dialog import AddEdgeDialog
import core.node
import random
import time
from .path_dialog import PathDialog
from PyQt5.QtCore import QTimer



class MainWindow(QMainWindow):
    def __init__(self, graph, data_loader):
        super().__init__()
        self.graph = graph
        self.loader = data_loader
        self.selected_node = None  # Seçilen düğümü tutmak için
        self.coloring_result = {}  # Renklendirme sonucunu tutmak için YENİ

        self.setWindowTitle("Sosyal Ağ Analizi - Üniversite Grafı")
        self.setMinimumSize(1000, 600)

        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QHBoxLayout(container)

        # SOL: Canvas
        # Renklendirme sonucunu canvas'a iletmek için güncellendi
        self.canvas = GraphCanvas(graph,
                                  on_node_clicked=self.show_node_details,
                                  on_edge_clicked=self.show_edge_details)  # Güncellendi
        main_layout.addWidget(self.canvas, stretch=3)

        # SAĞ: Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Bilgi Paneli
        self.info_panel = QFrame()
        self.info_panel.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout(self.info_panel)

        self.label_adi = QLabel("Seçim Yapılmadı");
        self.label_adi.setStyleSheet("font-weight:bold")
        self.label_detay = QLabel("")

        info_layout.addWidget(QLabel("<h3>Üniversite Bilgileri</h3>"))
        info_layout.addWidget(self.label_adi)
        info_layout.addWidget(self.label_detay)
        info_layout.addStretch()
        right_layout.addWidget(self.info_panel)

        # --- BUTON GRUBU ---

        # 1. Düzenle Butonu
        self.btn_edit = QPushButton("✏️ Düzenle")
        self.btn_edit.clicked.connect(self.edit_selected_node)
        self.btn_edit.setEnabled(False)  # Başlangıçta pasif
        right_layout.addWidget(self.btn_edit)

        # 2. Sil Butonu
        self.btn_delete = QPushButton("🗑️ Sil")
        self.btn_delete.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_delete.clicked.connect(self.delete_selected_node)
        self.btn_delete.setEnabled(False)  # Başlangıçta pasif
        right_layout.addWidget(self.btn_delete)

        self.btn_delete_edge = QPushButton("🔗 Bağlantıyı Sil")
        self.btn_delete_edge.setStyleSheet("background-color: #ff9800; color: white;")
        self.btn_delete_edge.clicked.connect(self.delete_selected_edge)
        self.btn_delete_edge.setEnabled(False)
        right_layout.addWidget(self.btn_delete_edge)

        # Bağlantı ekleme butonu
        self.btn_add_edge = QPushButton("🔗 Yeni Bağlantı Ekle")
        self.btn_add_edge.clicked.connect(self.open_add_edge_dialog)
        right_layout.addWidget(self.btn_add_edge)

        # 3. Renklendirme Butonu (YENİ)
        btn_color = QPushButton("🎨 Renklendir (Welsh-Powell)")
        btn_color.setStyleSheet("background-color: #33aaff; color: white; font-weight: bold; margin-top: 10px;")
        btn_color.clicked.connect(self.run_coloring)
        right_layout.addWidget(btn_color)

        # 4. BFS Butonu
        btn_bfs = QPushButton("🌊 BFS (Sığ Arama)")
        btn_bfs.setStyleSheet("background-color: #00BCD4; color: white; font-weight: bold; margin-top: 10px;")
        btn_bfs.clicked.connect(lambda: self.run_algo("BFS"))
        right_layout.addWidget(btn_bfs)

        # 5. DFS Butonu
        btn_dfs = QPushButton("⬇️ DFS (Derin Arama)")  # Ok işareti
        btn_dfs.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; margin-top: 10px;")
        btn_dfs.clicked.connect(lambda: self.run_algo("DFS"))
        right_layout.addWidget(btn_dfs)

        # 6. Dijkstra Butonu (YENİ)
        btn_path = QPushButton("📍 En Kısa Yol (Dijkstra)")
        btn_path.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; margin-top: 10px;")
        btn_path.clicked.connect(self.open_path_dialog)
        right_layout.addWidget(btn_path)

        # ui/main_window.py -> __init__ metodunda buton grubuna ekleyin
        self.btn_astar = QPushButton("🚀 En Kısa Yol (A*)")
        self.btn_astar.setStyleSheet("background-color: #3F51B5; color: white; font-weight: bold; margin-top: 10px;")
        self.btn_astar.clicked.connect(self.run_astar_analysis)
        right_layout.addWidget(self.btn_astar)

        # ui/main_window.py -> __init__ metodu içinde
        self.btn_centrality = QPushButton("📊 En Etkili 5 Üniversite")
        self.btn_centrality.setStyleSheet(
            "background-color: #607D8B; color: white; font-weight: bold; margin-top: 10px;")
        self.btn_centrality.clicked.connect(self.show_centrality_table)
        right_layout.addWidget(self.btn_centrality)  # Sağ panele ekler

        # 7. Ekle Butonu
        btn_add = QPushButton("➕ Yeni Üniversite Ekle")
        btn_add.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; margin-top: 10px;")
        btn_add.clicked.connect(self.open_add_dialog)
        right_layout.addWidget(btn_add)

        right_layout.addStretch()
        main_layout.addWidget(right_panel, stretch=1)

        self.btn_import = QPushButton("📥 JSON Veri İçe Aktar")
        self.btn_import.clicked.connect(self.import_json_action)
        right_layout.addWidget(self.btn_import)



    # ... Diğer metodlar (show_node_details, open_add_dialog, save_university, delete_selected_node, edit_selected_node)

    # Renklendirme Metodu (YENİ)
    def run_coloring(self):
        print("NODE SAYISI:", len(self.graph.nodes))
        print("EDGE SAYISI:", len(self.graph.edges))
        print("ADJ:", self.graph.adj)

        node_count = len(self.graph.nodes)
        if node_count == 0:
            QMessageBox.warning(self, "Uyarı", "Grafikte renklendirilecek düğüm yok.")
            return

        QMessageBox.information(
            self,
            "İşlem Başladı",
            f"Welsh-Powell algoritması {node_count} düğüm üzerinde çalışıyor..."
        )

        try:
            # ⏱ BAŞLANGIÇ ZAMANI
            start_time = time.perf_counter()

            # 🎨 ALGORİTMA
            new_coloring = self.graph.welsh_powell_coloring()

            # ⏱ BİTİŞ ZAMANI
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time

            if not new_coloring:
                QMessageBox.critical(self, "Hata", "Algoritma boş sonuç döndürdü!")
                return

            self.canvas.update_coloring(new_coloring)
            self.coloring_result = new_coloring.copy()

            dialog = ColoringDialog(self.graph, self.coloring_result, self)
            dialog.exec_()

            used_colors = len(set(self.coloring_result.values()))

            QMessageBox.information(
                self,
                "Başarılı",
                f"Graf başarıyla renklendirildi.\n\n"
                f"• Düğüm Sayısı: {node_count}\n"
                f"• Kullanılan Renk: {used_colors}\n"
                f"• Çalışma Süresi: {elapsed_time:.6f} saniye"
            )

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Renklendirme hatası: {e}")

    # Mevcut metotlar (Kesilen kısımlar)
    def show_node_details(self, node):
        self.selected_node = node
        self.label_adi.setText(node.adi)
        # Eğer renklendirme yapıldıysa, detaylara renk ID'sini ekle
        color_id_text = f"Renk ID: {self.coloring_result.get(node.uni_id, 'Yok')}\n" if self.coloring_result else ""
        text = f"{color_id_text}Kuruluş: {node.kurulus_yil}\nŞehir: {node.sehir}\nİlçe: {node.ilce}\nSıralama: {node.tr_siralama}"
        self.label_detay.setText(text)

        # Butonları aktifleştir
        self.btn_edit.setEnabled(True)
        self.btn_delete.setEnabled(True)

    def open_add_dialog(self):
        existing_unis = self.loader.get_university_names()
        # AddNodeDialog'un import edilmesi gerekiyor
        from .add_node_dialog import AddNodeDialog
        dialog = AddNodeDialog(existing_unis, self)
        if dialog.exec_():
            info, partners = dialog.get_data()
            self.save_university(info, partners)

    def save_university(self, info, partners):
        try:
            new_id = self.loader.add_university(info)
            new_node = Node(new_id, info["adi"], info["sehir"], info["ilce"],
                            info["kurulus_yil"], info["ogrenci_sayisi"],
                            int(info["fakulte_sayisi"]), info["akademik_sayisi"], info["tr_siralama"])

            # Rastgele konum ata
            cx = (self.canvas.width() / 2 - self.canvas.offset.x()) / self.canvas.scale_factor
            cy = (self.canvas.height() / 2 - self.canvas.offset.y()) / self.canvas.scale_factor
            new_node.x = cx + random.randint(-50, 50)
            new_node.y = cy + random.randint(-50, 50)

            self.graph.add_node(new_node)

            # İlişkileri hem grafa hem DB'ye ekle
            for pid in partners:
                if pid in self.graph.nodes:
                    # DB Kaydı
                    self.loader.add_relation(new_id, pid)
                    # Graph Kaydı
                    self.graph.add_edge(new_id, pid)

            self.canvas.update()
            QMessageBox.information(self, "Başarılı", "Üniversite eklendi!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def delete_selected_node(self):
        if not self.selected_node: return

        reply = QMessageBox.question(self, 'Onay',
                                     f"{self.selected_node.adi} silinecek. Emin misin?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 1. DB'den sil
            self.loader.delete_university(self.selected_node.uni_id)
            # 2. Graph'tan sil
            self.graph.remove_node(self.selected_node.uni_id)
            # 3. UI Temizle
            self.selected_node = None
            self.label_adi.setText("Silindi")
            self.label_detay.setText("")
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)

            # Renklendirme sonucundan sil
            if self.coloring_result and self.selected_node.uni_id in self.coloring_result:
                del self.coloring_result[self.selected_node.uni_id]

            self.canvas.update()

    def edit_selected_node(self):
        if not self.selected_node: return

        # AddNodeDialog'un import edilmesi gerekiyor
        from .add_node_dialog import AddNodeDialog

        # Mevcut veriyi dialoga gönder
        dialog = AddNodeDialog([], self, edit_data=self.selected_node)
        if dialog.exec_():
            info, _ = dialog.get_data()

            # DB güncelle
            self.loader.update_university(self.selected_node.uni_id, info)

            # Bellekteki Node'u güncelle
            self.selected_node.adi = info["adi"]
            self.selected_node.sehir = info["sehir"]
            self.selected_node.ilce = info["ilce"]
            self.selected_node.kurulus_yil = info["kurulus_yil"]
            self.selected_node.ogrenci_sayisi = info["ogrenci_sayisi"]
            # None kontrolü eklenebilir, ancak mevcut yapıda zaten int'e dönüştürülüyor
            self.selected_node.fakulte_sayisi = int(info["fakulte_sayisi"])
            self.selected_node.akademik_sayisi = info["akademik_sayisi"]
            self.selected_node.tr_siralama = info["tr_siralama"]

            self.show_node_details(self.selected_node)  # Paneli güncelle
            self.canvas.update()  # Grafikteki ismin değişmesi için

    def open_path_dialog(self):
        uni_list = self.loader.get_university_names()
        dialog = PathDialog(uni_list, self)

        if dialog.exec_():
            start_id, end_id, start_name, end_name = dialog.get_selection()

            if start_id == end_id:
                QMessageBox.warning(self, "Hata", "Başlangıç ve Bitiş aynı olamaz!")
                return

            # --- SÜRE ÖLÇÜMÜ BAŞLANGIÇ ---
            start_time = time.perf_counter()

            cost, path = self.graph.dijkstra(start_id, end_id)

            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            # --- SÜRE ÖLÇÜMÜ BİTİŞ ---

            if cost == float('inf'):
                QMessageBox.warning(self, "Sonuç",
                                    f"{start_name} ile {end_name} arasında bir bağlantı yolu yok.<br>"
                                    f"Arama Süresi: {elapsed_time:.8f} saniye")
                self.canvas.set_path([])
            else:
                self.canvas.set_path(path)
                QMessageBox.information(self, "Yol Bulundu",
                                        f"<b>Rota:</b> {start_name} → {end_name}<br>"
                                        f"<b>Toplam Maliyet:</b> {cost:.4f}<br>"
                                        f"<b>Adım Sayısı:</b> {len(path) - 1}<br>"
                                        f"<b>Algoritma Çalışma Süresi:</b> {elapsed_time:.8f} saniye")

    # ... (Sınıfın diğer metotları) ...

    def run_algo(self, algo_type):
        """BFS veya DFS animasyonunu başlatır ve çalışma süresini hesaplar."""
        if not self.selected_node:
            QMessageBox.warning(self, "Uyarı", f"{algo_type} başlatmak için haritadan bir Başlangıç Düğümü seçin!")
            return

        start_id = self.selected_node.uni_id

        # --- SÜRE ÖLÇÜMÜ BAŞLANGIÇ ---
        start_time = time.perf_counter()

        if algo_type == "BFS":
            self.animation_sequence = self.graph.bfs(start_id)
        else:
            self.animation_sequence = self.graph.dfs(start_id)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        # --- SÜRE ÖLÇÜMÜ BİTİŞ ---

        if not self.animation_sequence:
            return

        # Animasyon Hazırlığı
        self.canvas.highlighted_path = []
        self.canvas.algo_nodes = []
        self.canvas.update()

        # Bilgi ve Süre Gösterimi
        QMessageBox.information(self, "Algoritma Tamamlandı",
                                f"<b>{algo_type} Algoritması Analizi Bitti</b><br><br>"
                                f"• Başlangıç: {self.selected_node.adi}<br>"
                                f"• Gezilecek Toplam Düğüm: {len(self.animation_sequence)}<br>"
                                f"• Algoritma Çalışma Süresi:</b> {elapsed_time:.8f} saniye<br><br>"
                                f"Animasyon başlatılıyor")

        # Timer Başlat
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_animation_step)
        self.timer.start(200)

    def next_animation_step(self):
        """Timer her çalıştığında bir sonraki düğümü boyar."""
        if self.animation_sequence:
            # Listeden sıradaki düğümü al
            next_node = self.animation_sequence.pop(0)

            # Canvas listesine ekle
            self.canvas.algo_nodes.append(next_node)

            # Ekranı yenile (Bu sayede boyanmış halini görürüz)
            self.canvas.update()
        else:
            # Liste bittiyse durdur
            self.timer.stop()
            QMessageBox.information(self, "Bitti", "Arama tamamlandı!")

    def show_edge_details(self, edge):
        self.selected_edge = edge
        self.label_adi.setText("Bağlantı Seçildi")
        self.label_detay.setText(f"{edge.node1.adi} ↔️ {edge.node2.adi}")
        self.btn_delete_edge.setEnabled(True)
        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

    def delete_selected_edge(self):
        """Seçili kenarı (bağlantıyı) kullanıcı onayıyla hem DB'den hem de Graptan siler."""
        if not hasattr(self, 'selected_edge') or self.selected_edge is None:
            return

        # Bağlantıdaki üniversitelerin isimlerini alalım
        uni1_adi = self.selected_edge.node1.adi
        uni2_adi = self.selected_edge.node2.adi
        u1_id = self.selected_edge.node1.uni_id
        u2_id = self.selected_edge.node2.uni_id

        # --- ONAY PENCERESİ ---
        soru_metni = f"<b>{uni1_adi}</b> ile <b>{uni2_adi}</b> arasındaki akademik bağlantı kalıcı olarak silinecek.\n\nEmin misiniz?"

        onay = QMessageBox.question(
            self,
            "Bağlantıyı Silme Onayı",
            soru_metni,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        # Kullanıcı "Hayır" dediyse işlemi durdur
        if onay == QMessageBox.No:
            return

        # --- SİLME İŞLEMİ ---
        try:
            # 1. Veritabanından sil (data_loader.py içindeki Iliskiler tablosu)
            self.loader.delete_relation(u1_id, u2_id)

            # 2. Grafik yapısından sil (graph.py içindeki edges ve adj listesi)
            self.graph.remove_edge(u1_id, u2_id)

            # 3. UI Temizliği ve Güncelleme
            self.selected_edge = None
            self.btn_delete_edge.setEnabled(False)
            self.label_adi.setText("Bağlantı Silindi")
            self.label_detay.setText("")
            self.canvas.update()

            QMessageBox.information(self, "Başarılı", "Bağlantı başarıyla kaldırıldı.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Silme işlemi sırasında bir hata oluştu:\n{str(e)}")

    def open_add_edge_dialog(self):
        """İki üniversite seçip bağ kurmak için diyaloğu açar."""
        from .add_edge_dialog import AddEdgeDialog
        dialog = AddEdgeDialog(self.graph.nodes, self)

        if dialog.exec_():
            id1, id2 = dialog.get_data()

            if id1 == id2:
                QMessageBox.warning(self, "Hata", "Bir üniversiteyi kendisiyle eşleyemezsiniz.")
                return

            try:
                # DB'ye eklemeyi dene ve sonucu al
                result = self.loader.add_relation(id1, id2)

                if result is True:
                    # 1. Eğer başarıyla eklendiyse belleğe de ekle
                    self.graph.add_edge(id1, id2)
                    self.canvas.update()

                    uni1_adi = self.graph.nodes[id1].adi
                    uni2_adi = self.graph.nodes[id2].adi
                    QMessageBox.information(
                        self,
                        "Başarılı",
                        f"{uni1_adi} ve {uni2_adi} arasında yeni bir bağlantı oluşturuldu."
                    )
                elif result is False:
                    # 2. Eğer bağlantı zaten varsa uyarı ver
                    uni1_adi = self.graph.nodes[id1].adi
                    uni2_adi = self.graph.nodes[id2].adi
                    QMessageBox.warning(
                        self,
                        "Mevcut Bağlantı",
                        f"{uni1_adi} ve {uni2_adi} arasında zaten bir bağlantı bulunuyor."
                    )
                else:
                    # 3. Teknik bir hata (None) döndüyse
                    QMessageBox.critical(self, "Hata", "Veritabanı işlemi sırasında bir hata oluştu.")

            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Beklenmedik bir hata oluştu:\n{str(e)}")

    # ui/main_window.py içine eklenecek yeni metot

    def run_astar_analysis(self):
        """PathDialog'u açar ve seçilen noktalar arasında A* algoritmasını çalıştırır."""
        uni_list = self.loader.get_university_names()
        from .path_dialog import PathDialog
        dialog = PathDialog(uni_list, self)

        if dialog.exec_():
            start_id, end_id, start_name, end_name = dialog.get_selection()

            if start_id == end_id:
                QMessageBox.warning(self, "Hata", "Başlangıç ve Bitiş aynı olamaz!")
                return

            # Süre ölçümü başlangıcı
            start_time = time.perf_counter()

            # A* Algoritmasını çağır
            cost, path = self.graph.a_star(start_id, end_id)

            end_time = time.perf_counter()
            elapsed_time = end_time - start_time

            if cost == float('inf'):
                QMessageBox.warning(self, "Sonuç",
                                    f"{start_name} -> {end_name} arasında yol yok.\n"
                                    f"Analiz Süresi: {elapsed_time:.8f} sn")
                self.canvas.set_path([])
            else:
                # Bulunan yolu Canvas üzerinde çiz
                self.canvas.set_path(path)
                QMessageBox.information(self, "A* Sonucu",
                                        f"<b>Başarı:</b> Hedefe ulaşıldı!<br>"
                                        f"<b>Toplam Maliyet:</b> {cost:.4f}<br>"
                                        f"<b>Algoritma Süresi:</b> {elapsed_time:.8f} saniye")

    # ui/main_window.py içine eklenecek yeni metot

    # ui/main_window.py içindeki show_centrality_table metodunu güncelleyin:

    def show_centrality_table(self):
        """En etkili 5 üniversiteyi tablo halinde gösterir ve CSV çıktısı sunar."""
        top_5 = self.graph.get_top_5_influential_unis()

        if not top_5:
            QMessageBox.warning(self, "Uyarı", "Analiz edilecek veri bulunamadı.")
            return

        # HTML Tablo yapısı (Ağırlık sütunu eklendi)
        table_html = """
        <table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>
            <tr style='background-color: #f2f2f2;'>
                <th>Sıra</th>
                <th>Üniversite Adı</th>
                <th>Derece</th>
                <th>Toplam Ağırlık</th>
                <th>Ort. Ağırlık</th>
            </tr>
        """
        for i, item in enumerate(top_5, 1):
            table_html += f"""
            <tr>
                <td>{i}</td>
                <td>{item['adi']}</td>
                <td align='center'>{item['derece']}</td>
                <td align='center'>{item['toplam_agirlik']}</td>
                <td align='center'>{item['ortalama_agirlik']}</td>
            </tr>
            """
        table_html += "</table>"

        # Mesaj Kutusu Oluşturma
        msg = QMessageBox(self)
        msg.setWindowTitle("Etki Analizi Sonuçları")
        msg.setText("<h3>En Etkili 5 Üniversite ve Bağlantı Güçleri</h3>")
        msg.setInformativeText(table_html)

        # CSV Dışa Aktar Butonu Ekleme
        export_button = msg.addButton("📥 CSV Olarak Dışa Aktar", QMessageBox.ActionRole)
        msg.addButton(QMessageBox.Ok)

        msg.exec_()

        # Eğer kullanıcı CSV butonuna bastıysa
        if msg.clickedButton() == export_button:
            try:
                from core.exporter import Exporter
                exporter = Exporter()
                path = exporter.export_centrality_to_csv(top_5)
                QMessageBox.information(self, "Başarılı", f"Dosya başarıyla kaydedildi:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dışa aktarma başarısız: {e}")

    def import_json_action(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "JSON Dosyası Seç", "", "JSON Files (*.json)")
        if file_path:
            success = self.loader.import_from_json(file_path)
            if success:
                QMessageBox.information(self, "Başarılı", "Veriler içe aktarıldı. Uygulama yeniden başlatılıyor...")
                # Verileri graf nesnesine tekrar yükle (ekranın güncellenmesi için)
                self.graph = self.loader.load_graph()  # Mevcut load_graph metodunuz
                self.canvas.graph = self.graph
                self.canvas.update()
            else:
                QMessageBox.critical(self, "Hata", "JSON aktarımı sırasında bir sorun oluştu.")