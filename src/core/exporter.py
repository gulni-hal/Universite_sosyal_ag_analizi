# core/exporter.py

import csv
import os
from .graph import Graph
# YENİ: Renk haritasını içe aktarın (Eğer ana dosyanızda ui/graph_canvas.py yolunu biliyorsa)
# NOT: Bu örnekte, dışa aktarıcının UI'dan bu bilgiyi alması için doğrudan import yapıyoruz.
# Eğer bu bir döngüsel bağımlılık yaratırsa, bu bilgiyi graph objesine parametre olarak geçmek daha iyi bir çözümdür.
# Ancak mevcut dosya yapınızda en basit çözüm budur.
from ui.graph_canvas import GraphCanvas


class Exporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_coloring_to_csv(self, graph: Graph, coloring: dict, filename="welsh_powell_coloring.csv"):
        """
        Welsh-Powell renklendirme sonuçlarını CSV olarak dışa aktarır.
        """
        output_path = os.path.join(self.output_dir, filename)

        # Renk ismini bulmak için yardımcı haritayı kullan
        color_map = GraphCanvas.COLOR_NAME_MAP
        palette_size = len(color_map)

        # Ayırıcıyı uluslararası standart olan virgül (,) olarak değiştirdik.
        # Noktalı virgül (;) kullanmak isterseniz `delimiter=','` yerine `delimiter=';'` kullanın.
        delimiter = ','

        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                # YENİ ALAN: Renk Adı
                fieldnames = ['ID', 'Üniversite Adı', 'Şehir', 'Renk ID', 'Renk Adı', 'Komşular']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)

                writer.writeheader()
                for uni_id, color_id in coloring.items():
                    node = graph.nodes.get(uni_id)

                    # Renk ID'si palet boyutunu aşsa bile, döngüsel olarak doğru renk adını bul.
                    mapped_color_id = ((color_id - 1) % palette_size) + 1
                    color_name = color_map.get(mapped_color_id, f"Diğer Renk ({color_id})")

                    neighbor_ids = graph.get_neighbors(uni_id)
                    neighbor_names = [graph.nodes[nid].adi for nid in neighbor_ids if nid in graph.nodes]
                    neighbors_str = ", ".join(sorted(neighbor_names))

                    if node:
                        writer.writerow({
                            'ID': node.uni_id,
                            'Üniversite Adı': node.adi,
                            'Şehir': node.sehir,
                            'Renk ID': color_id,
                            'Renk Adı': color_name,  # <<< YENİ ALAN
                            'Komşular': neighbors_str
                        })

            return output_path
        except Exception as e:
            raise Exception(f"CSV dışa aktarma hatası: {e}")

    # core/exporter.py içine eklenecek metot:

    def export_centrality_to_csv(self, data, filename="etki_analizi.csv"):
        """
        Merkezilik analizi sonuçlarını (derece ve ağırlıklar) CSV olarak dışa aktarır.
        """
        import os, csv
        output_path = os.path.join(self.output_dir, filename)

        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['Sıra', 'Üniversite Adı', 'Şehir', 'Derece (Bağlantı Sayısı)', 'Toplam Ağırlık',
                              'Ortalama Ağırlık', 'Komşular']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for i, row in enumerate(data, 1):
                    writer.writerow({
                        'Sıra': i,
                        'Üniversite Adı': row['adi'],
                        'Şehir': row['sehir'],
                        'Derece (Bağlantı Sayısı)': row['derece'],
                        'Toplam Ağırlık': row['toplam_agirlik'],
                        'Ortalama Ağırlık': row['ortalama_agirlik'],
                        'Komşular': row['komsular']
                    })
            return output_path
        except Exception as e:
            raise Exception(f"Merkezilik CSV dışa aktarma hatası: {e}")

    # core/exporter.py içindeki Exporter sınıfına ekle

    # core/exporter.py içindeki export_communities_to_csv metodunu bununla değiştirin:

    def export_communities_to_csv(self, graph, components, filename="topluluk_analizi.csv"):
        """
        Topluluk analizi sonuçlarını (ayrık grupları) CSV olarak dışa aktarır.
        İlçe yerine komşu listesini ekler.
        """
        import os, csv
        output_path = os.path.join(self.output_dir, filename)

        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:

                fieldnames = ['Topluluk No', 'Üniversite ID', 'Üniversite Adı', 'Şehir', 'Komşular']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for i, component in enumerate(components, 1):
                    for node in component:
                        # Graph üzerinden komşuların isimlerini alalım
                        neighbor_ids = graph.get_neighbors(node.uni_id)
                        neighbor_names = [graph.nodes[nid].adi for nid in neighbor_ids if nid in graph.nodes]
                        neighbors_str = ", ".join(sorted(neighbor_names))

                        writer.writerow({
                            'Topluluk No': i,
                            'Üniversite ID': node.uni_id,
                            'Üniversite Adı': node.adi,
                            'Şehir': node.sehir,
                            'Komşular': neighbors_str
                        })
            return output_path
        except Exception as e:
            raise Exception(f"Topluluk CSV dışa aktarma hatası: {e}")

