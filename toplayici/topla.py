"""Etkinlik Var — etkinlik toplayıcı.

Çalıştırma:  py -I toplayici/topla.py            (tüm hazır iller)
             py -I toplayici/topla.py adana      (tek il)

Her il için `iller/<il>.py` dosyasındaki KAYNAKLAR listesini dolaşır,
bulunan etkinlikleri temizler, tekrarları ayıklar ve `site/veri/<il>.json` yazar.
Bir kaynak hata verirse diğerleri etkilenmez; hata kaynak tablosunda görünür.
"""
import datetime as dt
import importlib
import json
import os
import re
import sys
import time
import traceback

KLASOR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KLASOR)
import ortak  # noqa: E402

ARSIV_GUN = 365        # arşivde en fazla bu kadar eski etkinlik tutulur


def il_kodu(ad):
    """'Afyonkarahisar' -> 'afyonkarahisar', 'Ağrı' -> 'agri' (dosya adı ve site adresi için)."""
    return re.sub(r"[^a-z0-9]", "", ortak.kucuk(ad).translate(str.maketrans("çğıöşü", "cgiosu")))


# Hazır iller = iller/ klasöründe dosyası olanlar, plaka sırasıyla. Yeni il için sadece dosya eklemek yeter.
_DOSYALAR = {f[:-3] for f in os.listdir(os.path.join(KLASOR, "iller")) if f.endswith(".py") and not f.startswith("_")}
HAZIR_ILLER = [il_kodu(ad) for ad in ortak.ILLER if il_kodu(ad) in _DOSYALAR]
ILERI_GUN = 90          # bugünden en fazla bu kadar ilerisi listelenir
TR = dt.timezone(dt.timedelta(hours=3))


def il_topla(il):
    modul = importlib.import_module("iller." + il)
    il_adi = next((a for a in ortak.ILLER if il_kodu(a) == il), il)
    bugun = dt.datetime.now(TR).date()
    etkinlikler, kaynak_durum = {}, []
    hedef = os.path.join(KLASOR, "..", "site", "veri", il + ".json")
    arsivle(il, hedef, bugun)
    onceki = onceki_veri(hedef, bugun)

    for kaynak in modul.KAYNAKLAR:
        durum = {"ad": kaynak["ad"], "tur": kaynak["tur"], "url": kaynak.get("url"), "etkinlik_sayisi": 0}
        if not kaynak.get("cek"):
            durum["durum"] = kaynak.get("not", "henüz bağlanmadı")
            kaynak_durum.append(durum)
            continue
        bulunan, hata_metni = [], None
        for deneme in range(2):                # boş/hatalı gelirse bir kez daha dene
            try:
                bulunan = [e for e in (duzenle(h, kaynak, bugun) for h in kaynak["cek"](kaynak, bugun))
                           if e and (e["kategori"] in ("Tiyatro", "Çocuk")
                                     or not ortak.baslikta_baska_il(e["baslik"], il_adi, modul.ILCELER))]
                hata_metni = None
            except Exception as hata:  # bir kaynağın bozulması tüm işi durdurmasın
                hata_metni = str(hata)
                if "bekleniyor" in hata_metni:
                    break
                traceback.print_exc()
            if bulunan or not onceki.get(kaynak["ad"]):
                break
            time.sleep(5)
        if hata_metni and "bekleniyor" in hata_metni:
            durum["durum"] = "bekliyor: " + hata_metni[:120]
        elif not bulunan and onceki.get(kaynak["ad"]):
            # Site geçici olarak boş/bozuk döndü: dünkü verinin hâlâ geçerli olanlarını kullan
            bulunan = onceki[kaynak["ad"]]
            durum["durum"] = "geçici sorun: önceki veri gösteriliyor"
        elif hata_metni:
            durum["durum"] = "hata: " + hata_metni[:120]
        else:
            durum["durum"] = "çalışıyor" if bulunan else "çalışıyor (yaklaşan etkinlik yok)"
        for e in bulunan:
            etkinlikler.setdefault(e["id"], e)  # aynı etkinlik iki kaynaktan geldiyse ilkini tut
        durum["etkinlik_sayisi"] = len(bulunan)
        kaynak_durum.append(durum)
        print(f"  {durum['ad']:<45} {durum['durum']:<35} {durum['etkinlik_sayisi']}")

    liste = sorted(etkinlikler.values(), key=lambda e: (e["tarih"], e.get("saat") or "99"))
    sonuc = {
        "il": il,
        "guncelleme": dt.datetime.now(TR).isoformat(timespec="minutes"),
        "ilceler": modul.ILCELER,
        "etkinlikler": liste,
        "kaynaklar": sorted(kaynak_durum, key=lambda k: (-k["etkinlik_sayisi"], k["ad"])),
    }
    with open(hedef, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    print(f"{il}: {len(liste)} etkinlik, {len(kaynak_durum)} kaynak -> {os.path.normpath(hedef)}")
    return sonuc


def arsivle(il, yol, bugun):
    """Süresi dolan etkinlikleri silmek yerine site/veri/arsiv/<il>.json dosyasına taşır (5S: atma, arşivle)."""
    if not os.path.exists(yol):
        return
    klasor = os.path.join(KLASOR, "..", "site", "veri", "arsiv")
    os.makedirs(klasor, exist_ok=True)
    arsiv_yol = os.path.join(klasor, il + ".json")
    arsiv = json.load(open(arsiv_yol, encoding="utf-8")) if os.path.exists(arsiv_yol) else []
    kimlikler = {e["id"] for e in arsiv}
    for e in json.load(open(yol, encoding="utf-8")).get("etkinlikler", []):
        if (e.get("bitis") or e["tarih"]) < bugun.isoformat() and e["id"] not in kimlikler:
            e = dict(e)
            if (e.get("gorsel") or "").startswith("veri/gorsel/"):
                e["gorsel"] = None     # indirilen afiş silineceği için arşivde görsel tutulmaz
            arsiv.append(e)
    sinir = (bugun - dt.timedelta(days=ARSIV_GUN)).isoformat()
    arsiv = sorted((e for e in arsiv if e["tarih"] >= sinir), key=lambda e: e["tarih"], reverse=True)
    with open(arsiv_yol, "w", encoding="utf-8") as f:
        json.dump(arsiv, f, ensure_ascii=False, indent=1)


def onceki_veri(yol, bugun):
    """Bir önceki çalıştırmanın etkinlikleri, kaynak adına göre (sadece hâlâ geçerli olanlar)."""
    if not os.path.exists(yol):
        return {}
    sonuc = {}
    for e in json.load(open(yol, encoding="utf-8")).get("etkinlikler", []):
        if (e.get("bitis") or e["tarih"]) >= bugun.isoformat():
            sonuc.setdefault(e["kaynak_ad"], []).append(e)
    return sonuc


def gorsel_temizle():
    """Hiçbir ilin listesinde kalmayan indirilmiş afişleri siler (otomatik üretilen dosyalar)."""
    veri = os.path.join(KLASOR, "..", "site", "veri")
    kullanilan = set()
    for il in HAZIR_ILLER:
        yol = os.path.join(veri, il + ".json")
        if os.path.exists(yol):
            for e in json.load(open(yol, encoding="utf-8"))["etkinlikler"]:
                if (e.get("gorsel") or "").startswith("veri/gorsel/"):
                    kullanilan.add(os.path.basename(e["gorsel"]))
    if os.path.isdir(ortak.GORSEL_KLASOR):
        for dosya in os.listdir(ortak.GORSEL_KLASOR):
            if dosya not in kullanilan:
                os.remove(os.path.join(ortak.GORSEL_KLASOR, dosya))


def duzenle(e, kaynak, bugun):
    """Ham kaydı standart biçime getirir; geçmiş, tarihsiz ya da 'haber' olanları eler."""
    baslik = ortak.temizle(e.get("baslik"))
    if len(baslik) < 4 or ortak.gecmis_haber_mi(baslik) or ortak.kamuya_kapali_mi(baslik):
        return None
    bas, bit = e.get("tarih"), e.get("bitis")
    if not bas:
        bas, bit = ortak.tarih_bul(baslik + " " + (e.get("metin") or ""), bugun)
    if not bas:
        return None
    bit = bit or bas
    if bit < bugun or bas > bugun + dt.timedelta(days=ILERI_GUN):
        return None
    metin = baslik + " " + (e.get("metin") or "")
    saat = e.get("saat") or ortak.saat_bul(metin)
    ozet = ortak.temizle(e.get("ozet") or "")
    return {
        "id": ortak.kimlik(baslik, bas, saat),
        "baslik": baslik,
        "tarih": bas.isoformat(),
        "bitis": bit.isoformat() if bit != bas else None,
        "saat": saat,
        "ilce": e.get("ilce") or kaynak.get("ilce"),
        "mekan": ortak.temizle(e.get("mekan") or "") or None,
        "kategori": e.get("kategori") or ortak.kategori_tahmin(metin),
        "ucretsiz": e["ucretsiz"] if "ucretsiz" in e else ortak.ucretsiz_mi(metin, kaynak["tur"]),
        "ozet": (ozet[:220] + "…") if len(ozet) > 220 else (ozet or None),
        "kaynak_ad": kaynak["ad"],
        "kaynak_tur": kaynak["tur"],
        "kaynak_url": e.get("url") or kaynak.get("url"),
        "gorsel": e.get("gorsel"),
    }


if __name__ == "__main__":
    bozuk = set()
    for il in (sys.argv[1:] or HAZIR_ILLER):
        print(f"== {il}")
        try:
            il_topla(il)
        except Exception:                    # bir ilin dosyası bozuksa diğer iller yine güncellensin
            traceback.print_exc()
            bozuk.add(il)
    gorsel_temizle()
    # Sitede sadece verisi oluşmuş iller "hazır" görünür
    hazir = [ad for ad in ortak.ILLER if il_kodu(ad) in HAZIR_ILLER and il_kodu(ad) not in bozuk
             and os.path.exists(os.path.join(KLASOR, "..", "site", "veri", il_kodu(ad) + ".json"))]
    with open(os.path.join(KLASOR, "..", "site", "veri", "hazir.json"), "w", encoding="utf-8") as f:
        json.dump(hazir, f, ensure_ascii=False)
    if bozuk:
        print("HATALI İLLER:", ", ".join(sorted(bozuk)))
        sys.exit(1)
