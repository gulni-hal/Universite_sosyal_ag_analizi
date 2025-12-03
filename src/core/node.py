class Node:
    """
    Üniversite düğümünü temsil eden sınıf.
    Her düğüm, veritabanındaki bir üniversitenin bilgilerini içerir.
    """

    def __init__(
        self,
        uni_id: int,
        adi: str,
        sehir: str,
        ilce: str,
        kurulus_yil: int,
        ogrenci_sayisi: int,
        fakulte_sayisi: int,
        akademik_sayisi: int,
        tr_siralama: int
    ):
        self.uni_id = uni_id
        self.adi = adi
        self.sehir = sehir
        self.ilce = ilce
        self.kurulus_yil = kurulus_yil
        self.ogrenci_sayisi = ogrenci_sayisi
        self.fakulte_sayisi = fakulte_sayisi
        self.akademik_sayisi = akademik_sayisi
        self.tr_siralama = tr_siralama

        # Canvas için pozisyon bilgisi (UI tarafından atanır)
        self.x = 0
        self.y = 0

    def __repr__(self):
        return f"Node({self.adi}, {self.sehir}, {self.ilce})"

    def to_dict(self):
        """JSON/CSV dışa aktarma için kullanılacak format."""
        return {
            "uni_id": self.uni_id,
            "adi": self.adi,
            "sehir": self.sehir,
            "ilce": self.ilce,
            "kurulus_yil": self.kurulus_yil,
            "ogrenci_sayisi": self.ogrenci_sayisi,
            "fakulte_sayisi": self.fakulte_sayisi,
            "akademik_sayisi": self.akademik_sayisi,
            "tr_siralama": self.tr_siralama
        }
