"""Ordu kaynakları (plaka 52). Kaynak haritası: 2026-10-29.

Okunan kaynak: Ordu Üniversitesi etkinlik listesi + her etkinliğin sayfası (tarih/saat/yer detayda).
Ordu Büyükşehir Belediyesi etkinlik sayfası var ama gösterdiği oyunlar 2025/Mayıs 2026'dan kalma (güncellenmiyor);
Ünye Belediyesi "yaklaşan etkinlikler" sayfasında sadece geçmiş festival var. İkisi de güncellenince okunabilir.
"""
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Altınordu", "Akkuş", "Aybastı", "Çamaş", "Çatalpınar", "Çaybaşı", "Fatsa", "Gölköy", "Gülyalı", "Gürgentepe",
           "İkizce", "Kabadüz", "Kabataş", "Korgan", "Kumru", "Mesudiye", "Perşembe", "Ulubey", "Ünye"]
SALON_ILCE = {"obbkt": "Altınordu", "cumhuriyet yerleşkesi": "Altınordu", "ordu üniversitesi": "Altınordu",
              "müzik ve sahne sanatları": "Altınordu", "ceren özdemir": "Altınordu"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

ODU = "https://odu.edu.tr"


# ------------------------------------------------------------------
# 1) Ordu Üniversitesi — liste sayfası + detay sayfaları (HTML)
# ------------------------------------------------------------------
def odu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    gorulen = set()
    for link, baslik in re.findall(r'<a href="(https://odu\.edu\.tr/Etkinlikler/\d+/[^"]+)"[^>]*>\s*<div><h6>(.*?)</h6>', sayfa, re.S):
        if link in gorulen or len(gorulen) >= 10:      # en yeni 10 kayıt yeter (liste yeniden eskiye)
            continue
        gorulen.add(link)
        try:
            d = ortak.indir(link)
        except Exception:
            continue
        tarih = re.search(r"<b>Tarih:</b>\s*([^<]+)", d)
        bas, _ = ortak.tarih_bul(tarih[1], bugun) if tarih else (None, None)
        if not bas:
            continue
        saat = re.search(r"<b>Saat:</b>\s*(\d{1,2})[.:](\d{2})", d)
        tur = re.search(r"Tür:</b>\s*([^<]+)", d)
        yer = re.search(r"Yer:</b>\s*([^<]+)", d)
        ad = basliklar(ortak.temizle(baslik))
        mekan = ortak.temizle(yer[1]) if yer and ortak.temizle(yer[1]) else "Ordu Üniversitesi"
        yield {
            "baslik": ad,
            "tarih": bas,
            "saat": f"{int(saat[1]):02d}:{saat[2]}" if saat else None,
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Altınordu"),
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            "url": link,
        }


KAYNAKLAR = [
    {"ad": "Ordu Üniversitesi", "tur": "universite", "url": ODU + "/TumEtkinlikler", "cek": odu},
    {"ad": "Ordu İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://ordu.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Ordu", "ilce_bul": salon_ilce, "varsayilan_ilce": "Altınordu"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/ordu", "cek": etkinlik_io,
     "sehir": "Ordu", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Ordu Büyükşehir Belediyesi (Şehir Tiyatrosu, OBBKT)", "tur": "belediye", "url": "https://www.ordu.bel.tr/etkinlik-takvimi",
     "not": "etkinlik sayfası var ama listesi güncellenmiyor (Ocak 2025 / Mayıs 2026 oyunları); güncellenince okunacak"},
    {"ad": "Ünye Belediyesi", "tur": "belediye", "ilce": "Ünye", "url": "https://www.unye.bel.tr/etkinlikler/yaklasan-etkinlikler/",
     "not": "yaklaşan etkinlikler sayfasında sadece geçmiş festival var"},
    {"ad": "Altınordu Belediyesi", "tur": "belediye", "ilce": "Altınordu", "url": "https://www.altinordu.bel.tr",
     "not": "etkinlik sayfası haber bölümünde; düzenli takvim yok"},
    {"ad": "Fatsa Belediyesi", "tur": "belediye", "ilce": "Fatsa", "url": "https://www.fatsa.bel.tr/etkinlikler",
     "not": "etkinlik sayfası henüz okunmuyor (sonraki tur)"},
    {"ad": "Ordu Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.ordu.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Ünye Kültür Sanat ve Turizm, Fatsa Fındık, Perşembe Yayla…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
