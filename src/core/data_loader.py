import sqlite3
import networkx as nx
from .node import Node
from .graph import Graph
import json

class DataLoader:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Veritabanı tablolarını (yoksa) oluşturur."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Üniversiteler Tablosu
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS Üniversiteler
                       (
                           uni_id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           adi
                           TEXT,
                           sehir
                           TEXT,
                           ilce
                           TEXT,
                           kurulus_yil
                           INTEGER,
                           ogrenci_sayisi
                           INTEGER,
                           fakulte_sayisi
                           TEXT,
                           akademik_sayisi
                           INTEGER,
                           tr_siralama
                           INTEGER
                       )
                       """)

        # İlişkiler (Edges) Tablosu - YENİ
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS Iliskiler
                       (
                           source_id
                           INTEGER,
                           target_id
                           INTEGER,
                           PRIMARY
                           KEY
                       (
                           source_id,
                           target_id
                       )
                           )
                       """)
        conn.commit()
        conn.close()

    def load_graph(self, graph: Graph):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        G_nx = nx.Graph()

        # 1. Node'ları Yükle
        cursor.execute("SELECT * FROM Üniversiteler")
        rows = cursor.fetchall()

        if not rows:
            conn.close()
            print("DataLoader: Veritabanında üniversite kaydı bulunamadı.")
            return graph

        for row in rows:
            # row[6] fakülte sayısı, int beklenir
            try:
                fakulte_sayisi = int(row[6]) if row[6] is not None else 0
            except ValueError:
                fakulte_sayisi = 0

            node = Node(row[0], row[1], row[2], row[3], row[4], row[5], fakulte_sayisi, row[7], row[8])
            graph.add_node(node)
            G_nx.add_node(node.uni_id)

        # 2. Edge'leri (İlişkileri) Yükle
        cursor.execute("SELECT source_id, target_id FROM Iliskiler")
        edges = cursor.fetchall()

        for u, v in edges:
            if u in graph.nodes and v in graph.nodes:
                n1 = graph.nodes[u]
                n2 = graph.nodes[v]
                weight = graph.calculate_weight(n1, n2)

                # SADECE BURADA GRAPH VE NETWORKX İKİSİNE DE KENAR EKLENİR
                graph.add_edge(u, v)
                G_nx.add_edge(u, v, weight=weight)

        conn.close()

        if not G_nx.nodes:
            # Eğer düğümler bir nedenden dolayı G_nx'e eklenmediyse, layout atlanır.
            return graph

        # 3. Pozisyonlama (Layout) - Sadece düğüm varsa çalıştır
        if len(G_nx.nodes) > 0:
            try:
                # weight=None  -> ÇOK ÖNEMLİ: Binlerce puanlık çekim gücünü iptal eder.
                #                 Sadece "bağ var mı yok mu" ona bakar.
                # k=0.7        -> İtme gücü. 0.7 düğümleri birbirinden net ayırır.
                # scale=1000   -> Harita genişliği. Yazıların okunması için yeterli alan.
                # iterations=100 -> Düğümlerin yerleşmesi için yeterli süre.

                pos = nx.spring_layout(G_nx, seed=42, k=0.7, iterations=100, scale=1000, weight=None)

                # Haritayı tam merkeze oturtuyoruz
                center_x, center_y = 1000, 800

                for nid, p in pos.items():
                    if nid in graph.nodes:
                        graph.nodes[nid].x = int(center_x + p[0])
                        graph.nodes[nid].y = int(center_y + p[1])

            except Exception as e:
                print(f"Layout Hatası: {e}")


    def get_university_names(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT uni_id, adi FROM Üniversiteler ORDER BY adi ASC")
        data = cursor.fetchall()
        conn.close()
        return data

    def add_university(self, info_dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = """
                INSERT INTO Üniversiteler
                (adi, sehir, ilce, kurulus_yil, ogrenci_sayisi, fakulte_sayisi, akademik_sayisi, tr_siralama)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?) \
                """
        values = (
            info_dict["adi"], info_dict["sehir"], info_dict["ilce"],
            info_dict["kurulus_yil"], info_dict["ogrenci_sayisi"],
            info_dict["fakulte_sayisi"], info_dict["akademik_sayisi"],
            info_dict["tr_siralama"]
        )
        cursor.execute(query, values)
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id

    # def add_relation(self, u_id, v_id):
    #     """İki üniversite arasındaki ilişkiyi DB'ye kaydeder."""
    #     conn = sqlite3.connect(self.db_path)
    #     cursor = conn.cursor()
    #     # Çift yönlü kontrol (1-2 ve 2-1 aynıdır, ama basitlik için direkt ekliyoruz, unique constraint var)
    #     try:
    #         # ID'leri sıralı kaydedelim ki (1,2) ile (2,1) aynı olsun
    #         s, t = sorted((u_id, v_id))
    #         cursor.execute("INSERT OR IGNORE INTO Iliskiler (source_id, target_id) VALUES (?, ?)", (s, t))
    #         conn.commit()
    #     except:
    #         pass
    #     conn.close()

    def delete_university(self, uni_id):
        """Üniversiteyi ve ilişkilerini siler."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Üniversiteler WHERE uni_id = ?", (uni_id,))
        cursor.execute("DELETE FROM Iliskiler WHERE source_id = ? OR target_id = ?", (uni_id, uni_id))
        conn.commit()
        conn.close()

    def update_university(self, uni_id, info):
        """Üniversite bilgilerini günceller."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = """
                UPDATE Üniversiteler \
                SET adi=?, \
                    sehir=?, \
                    ilce=?, \
                    kurulus_yil=?, \
                    ogrenci_sayisi=?, \
                    fakulte_sayisi=?, \
                    akademik_sayisi=?, \
                    tr_siralama=?
                WHERE uni_id = ? \
                """
        values = (
            info["adi"], info["sehir"], info["ilce"],
            info["kurulus_yil"], info["ogrenci_sayisi"],
            info["fakulte_sayisi"], info["akademik_sayisi"],
            info["tr_siralama"], uni_id
        )
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def delete_relation(self, id1, id2):
        """Veritabanından iki üniversite arasındaki bağı siler."""
        # 1. Diğer metotlardaki gibi yeni bir bağlantı oluşturuyoruz
        conn = sqlite3.connect(self.db_path)

        # 2. Tablo adınız 'Iliskiler', sütunlarınız 'source_id' ve 'target_id'
        # add_relation içinde sorted() kullandığınız için burada da sıralıyoruz
        s, t = sorted((id1, id2))

        query = "DELETE FROM Iliskiler WHERE source_id = ? AND target_id = ?"

        try:
            cursor = conn.cursor()
            cursor.execute(query, (s, t))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"DB: {s} ve {t} arasındaki bağlantı başarıyla silindi.")
            else:
                print(f"DB UYARI: Silinecek bağlantı bulunamadı (IDler: {s}-{t}).")

        except Exception as e:
            print(f"Bağlantı silinirken DB hatası: {e}")
            raise e  # Hatayı MainWindow'un yakalaması için yukarı fırlatıyoruz
        finally:
            conn.close()

    def add_relation(self, u_id, v_id):
        """İki üniversite arasındaki ilişkiyi DB'ye kaydeder."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            s, t = sorted((u_id, v_id))
            query = "INSERT OR IGNORE INTO Iliskiler (source_id, target_id) VALUES (?, ?)"

            cursor.execute(query, (s, t))
            conn.commit()

            # Eğer etkilenen satır sayısı 0'dan büyükse yeni eklenmiştir
            if cursor.rowcount > 0:
                print(f"DB: {s} ve {t} arasında yeni bağlantı oluşturuldu.")
                return True
            else:
                print(f"DB: Bu bağlantı zaten mevcut, eklenmedi.")
                return False  # Bağlantı zaten var

        except Exception as e:
            print(f"Bağlantı eklenirken DB hatası: {e}")
            return None  # Teknik bir hata oluştu
        finally:
            conn.close()

    def is_ranking_taken(self, ranking, exclude_id=None):
        """Belirtilen sıralamanın başka bir üniversite tarafından kullanılıp kullanılmadığını kontrol eder."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if exclude_id:
            # Düzenleme modunda, kendi ID'si dışındaki kayıtları kontrol et
            cursor.execute("SELECT 1 FROM Üniversiteler WHERE tr_siralama = ? AND uni_id != ?", (ranking, exclude_id))
        else:
            # Yeni ekleme modunda direkt kontrol et
            cursor.execute("SELECT 1 FROM Üniversiteler WHERE tr_siralama = ?", (ranking,))

        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    # def import_from_json(self, file_path):
    #     """JSON dosyasındaki verileri DB'ye aktarır."""
    #     with open(file_path, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #
    #     conn = sqlite3.connect(self.db_path)
    #     cursor = conn.cursor()
    #
    #     try:
    #         # 1. Üniversiteleri ekle
    #         for uni in data.get('universiteler', []):
    #             cursor.execute("""
    #                 INSERT OR REPLACE INTO Üniversiteler
    #                 (uni_id, adi, sehir, ilce, kurulus_yil, ogrenci_sayisi, fakulte_sayisi, akademik_sayisi, tr_siralama)
    #                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    #             """, (uni['uni_id'], uni['adi'], uni['sehir'], uni['ilce'], uni['kurulus_yil'],
    #                   uni['ogrenci_sayisi'], uni['fakulte_sayisi'], uni['akademik_sayisi'], uni['tr_siralama']))
    #
    #         # 2. İlişkileri ekle
    #         for rel in data.get('iliskiler', []):
    #             s, t = sorted((rel['source_id'], rel['target_id']))
    #             cursor.execute("INSERT OR IGNORE INTO Iliskiler (source_id, target_id) VALUES (?, ?)", (s, t))
    #
    #         conn.commit()
    #         return True
    #     except Exception as e:
    #         print(f"JSON Import Hatası: {e}")
    #         return False
    #     finally:
    #         conn.close()

    def import_from_json(self, file_path):
        """JSON dosyasındaki verileri doğrulayarak DB'ye aktarır."""
        import json
        import sqlite3

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if 'universiteler' in data:
                for uni in data['universiteler']:
                    # 1. EKSİK BİLGİ KONTROLÜ
                    required_fields = ['adi', 'sehir', 'ilce', 'tr_siralama']
                    if not all(uni.get(field) for field in required_fields):
                        raise ValueError(f"Eksik alan: {uni.get('adi', 'Bilinmiyor')}")

                    ranking = uni['tr_siralama']
                    uni_id = uni.get('uni_id')

                    # 2. SIRALAMA ÇAKIŞMASI KONTROLÜ (GÜNCELLENDİ)
                    # Sadece ID farklı olup sıralama aynı olan bir kayıt var mı bakıyoruz
                    if uni_id is not None:
                        cursor.execute(
                            "SELECT adi FROM Üniversiteler WHERE tr_siralama = ? AND uni_id != ?",
                            (ranking, uni_id)
                        )
                    else:
                        cursor.execute(
                            "SELECT adi FROM Üniversiteler WHERE tr_siralama = ?",
                            (ranking,)
                        )

                    conflict = cursor.fetchone()

                    if conflict:
                        conn.close()  # Bağlantıyı kapatıp hata fırlatıyoruz
                        return False, f"Sıralama Çakışması: {ranking}. sıra zaten '{conflict[0]}' üniversitesine ait."

                    # 3. VERİ EKLEME (INSERT OR REPLACE yerine INSERT INTO ve UPDATE kontrolü)
                    # Eğer ID zaten varsa bilgilerini güncelle, yoksa yeni ekle
                    cursor.execute("""
                        INSERT INTO Üniversiteler 
                        (uni_id, adi, sehir, ilce, kurulus_yil, ogrenci_sayisi, fakulte_sayisi, akademik_sayisi, tr_siralama)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(uni_id) DO UPDATE SET
                        adi=excluded.adi, sehir=excluded.sehir, ilce=excluded.ilce, 
                        kurulus_yil=excluded.kurulus_yil, ogrenci_sayisi=excluded.ogrenci_sayisi,
                        fakulte_sayisi=excluded.fakulte_sayisi, akademik_sayisi=excluded.akademik_sayisi,
                        tr_siralama=excluded.tr_siralama
                    """, (
                        uni_id, uni['adi'], uni['sehir'], uni['ilce'],
                        uni.get('kurulus_yil', 0), uni.get('ogrenci_sayisi', 0),
                        uni.get('fakulte_sayisi', 0), uni.get('akademik_sayisi', 0), ranking
                    ))

            # 4. İlişkileri Ekle
            if 'iliskiler' in data:
                for rel in data['iliskiler']:
                    s, t = sorted((rel['source_id'], rel['target_id']))
                    cursor.execute("INSERT OR IGNORE INTO Iliskiler (source_id, target_id) VALUES (?, ?)", (s, t))

            conn.commit()
            conn.close()
            return True, "Başarıyla eklendi."
        except Exception as e:
            if 'conn' in locals(): conn.close()
            return False, str(e)

    def import_from_csv(self, file_path):
        """CSV dosyasındaki verileri ve İLİŞKİLERİ doğrulayarak DB'ye aktarır."""
        import csv
        import sqlite3

        try:
            # utf-8-sig: Türkçe karakterleri düzeltir
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                # Ayırıcıyı otomatik algıla
                sample = f.read(1024)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample)

                reader = csv.DictReader(f, dialect=dialect)

                # Verileri hafızaya alalım (Dosyayı iki kere okumamak için)
                rows = list(reader)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            required_fields = ['adi', 'sehir', 'ilce', 'tr_siralama']
            pending_relations = []  # İlişkileri en son eklemek için burada tutacağız

            # --- 1. AŞAMA: Üniversiteleri (Düğümleri) Ekle ---
            for row in rows:
                if not all(field in row for field in required_fields):
                    conn.close()
                    return False, f"CSV sütunları eksik. Zorunlu: {', '.join(required_fields)}"

                if not all(row.get(field) for field in required_fields):
                    continue

                try:
                    ranking = int(row['tr_siralama'])

                    # Sayısal verileri güvenli al
                    kurulus = int(row.get('kurulus_yil')) if row.get('kurulus_yil') and row.get(
                        'kurulus_yil').isdigit() else 2000
                    ogrenci = int(row.get('ogrenci_sayisi')) if row.get('ogrenci_sayisi') and row.get(
                        'ogrenci_sayisi').isdigit() else 0
                    akademik = int(row.get('akademik_sayisi')) if row.get('akademik_sayisi') and row.get(
                        'akademik_sayisi').isdigit() else 0
                    fakulte = str(row.get('fakulte_sayisi', "0"))

                    # ID varsa al, yoksa None
                    uni_id = row.get('uni_id')
                    if uni_id and uni_id.strip() == "": uni_id = None

                    # Üniversiteyi Ekle/Güncelle
                    cursor.execute("""
                                   INSERT INTO Üniversiteler
                                   (uni_id, adi, sehir, ilce, kurulus_yil, ogrenci_sayisi, fakulte_sayisi,
                                    akademik_sayisi, tr_siralama)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(uni_id) DO
                                   UPDATE SET
                                       adi=excluded.adi, sehir=excluded.sehir, tr_siralama=excluded.tr_siralama
                                   """,
                                   (uni_id, row['adi'], row['sehir'], row['ilce'], kurulus, ogrenci, fakulte, akademik,
                                    ranking))

                    # Eğer ID otomatik verildiyse, son eklenen ID'yi bulmalıyız (ilişkiler için gerekli değil ama iyi pratik)
                    # Ancak CSV ile ilişki kuracaksanız, CSV içinde ID'leri elle vermeniz EN SAĞLIKLISIDIR.

                    # İlişkileri listeye at (Sonra işleyeceğiz)
                    # Sütun adı: 'iliskili_idleri' -> Format: "1|5|12" (Dik çizgi ile ayrılmış ID'ler)
                    if 'iliskili_idleri' in row and row['iliskili_idleri']:
                        source_id = uni_id if uni_id else cursor.lastrowid
                        targets = row['iliskili_idleri'].split('|')
                        for t in targets:
                            if t.strip().isdigit():
                                pending_relations.append((source_id, int(t.strip())))

                except ValueError as ve:
                    conn.close()
                    return False, f"Veri Hatası: {ve}"

            # --- 2. AŞAMA: İlişkileri (Kenarları) Ekle ---
            count_edges = 0
            for u, v in pending_relations:
                # Kendine ilişki eklemeyi engelle
                if u != v:
                    # İki yönlü ekle (Source -> Target ve Target -> Source çakışmasını önlemek için IGNORE)
                    # ID'leri sıralayıp eklersek çift kaydı önleriz ama Graph yapısı çift yönlü olabilir.
                    # Basitlik için direkt ekliyoruz:
                    cursor.execute("INSERT OR IGNORE INTO Iliskiler (source_id, target_id) VALUES (?, ?)", (u, v))
                    count_edges += 1

            conn.commit()
            conn.close()
            return True, f"Başarılı! Üniversiteler güncellendi ve {count_edges} bağlantı kuruldu."

        except Exception as e:
            if 'conn' in locals(): conn.close()
            return False, f"CSV Okuma Hatası: {str(e)}"