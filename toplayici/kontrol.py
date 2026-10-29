"""Bir ilin kalite kontrolü. Yeni il eklendikten sonra mutlaka çalıştırılır.

Çalıştırma:  py -X utf8 -I toplayici/kontrol.py agri          (tek il)
             py -X utf8 -I toplayici/kontrol.py --hepsi        (tüm hazır iller, toplama yapmadan sadece dosyaları kontrol eder)

Toplayıcıyı çalıştırır, sonra çıkan dosyayı ve gezilecek yerleri kurallara göre denetler.
Sonunda "GEÇTİ" ya da hataların listesi yazar.
"""
import datetime as dt
import importlib
import json
import os
import sys
import urllib.request

KLASOR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KLASOR)
import ortak  # noqa: E402
import topla  # noqa: E402

VERI = os.path.join(KLASOR, "..", "site", "veri")


def url_calisiyor_mu(url):
    try:
        istek = urllib.request.Request(url, headers={"User-Agent": ortak.TARAYICI}, method="GET")
        with urllib.request.urlopen(istek, timeout=20) as y:
            return y.status == 200
    except Exception:
        return False


def kontrol(il, topla_calistir=True):
    hatalar, uyarilar = [], []
    ad = next((a for a in ortak.ILLER if topla.il_kodu(a) == il), None)
    if not ad:
        return [f"'{il}' geçerli bir il kodu değil"], []
    try:
        modul = importlib.import_module("iller." + il)
    except Exception as h:
        return [f"iller/{il}.py yüklenemedi: {h}"], []

    if not getattr(modul, "ILCELER", None):
        hatalar.append("ILCELER listesi boş")
    kaynaklar = getattr(modul, "KAYNAKLAR", [])
    if not any(k.get("cek") for k in kaynaklar):
        hatalar.append("Hiç çalışan (cek=...) kaynak yok")
    for k in kaynaklar:
        for alan in ("ad", "tur"):
            if not k.get(alan):
                hatalar.append(f"Kaynakta '{alan}' eksik: {k}")
        if k.get("cek") and k["cek"].__name__ in ("devlet_tiyatrosu", "etkinlik_io") and not k.get("sehir"):
            hatalar.append(f"{k['ad']}: 'sehir' alanı eksik")

    if topla_calistir:
        topla.il_topla(il)
    yol = os.path.join(VERI, il + ".json")
    if not os.path.exists(yol):
        return hatalar + [f"{yol} oluşmadı"], uyarilar
    veri = json.load(open(yol, encoding="utf-8"))
    bugun = dt.date.today()
    kimlikler = set()
    for e in veri["etkinlikler"]:
        etiket = f"'{e['baslik'][:50]}'"
        if (e.get("bitis") or e["tarih"]) < (bugun - dt.timedelta(days=1)).isoformat():
            hatalar.append(f"{etiket} geçmiş tarihli ({e['tarih']})")
        if e["tarih"] > (bugun + dt.timedelta(days=topla.ILERI_GUN + 1)).isoformat():
            hatalar.append(f"{etiket} çok ileri tarihli ({e['tarih']})")
        if e["id"] in kimlikler:
            hatalar.append(f"{etiket} tekrar ediyor")
        kimlikler.add(e["id"])
        if e.get("ilce") and e["ilce"] not in modul.ILCELER:
            hatalar.append(f"{etiket} ilçesi listede yok: {e['ilce']}")
        if e.get("mekan") and ortak.baska_il_mi(e["mekan"], ad):
            hatalar.append(f"{etiket} başka ilde: {e['mekan']}")
        if not (e.get("kaynak_url") or "").startswith("http"):
            uyarilar.append(f"{etiket} bağlantısı yok")
        if e["baslik"].isupper() and len(e["baslik"]) > 12:
            uyarilar.append(f"{etiket} tamamı büyük harf (basliklar() kullan)")
        g = e.get("gorsel")
        if g and g.startswith("http") and not url_calisiyor_mu(g):
            hatalar.append(f"{etiket} görseli açılmıyor: {g[:90]}")
    for k in veri["kaynaklar"]:
        if k["durum"].startswith("hata"):
            uyarilar.append(f"Kaynak hata verdi: {k['ad']} — {k['durum']}")

    myol = os.path.join(VERI, il + "_mekanlar.json")
    if not os.path.exists(myol):
        hatalar.append(f"{il}_mekanlar.json yok")
    else:
        mekanlar = json.load(open(myol, encoding="utf-8"))
        if not 6 <= len(mekanlar) <= 14:
            uyarilar.append(f"Gezilecek yer sayısı {len(mekanlar)} (6-14 önerilir)")
        for m in mekanlar:
            for alan in ("ad", "ilce", "tur", "simge", "aciklama"):
                if not m.get(alan):
                    hatalar.append(f"Mekan '{m.get('ad')}': '{alan}' eksik")
            if m.get("ilce") and m["ilce"] not in modul.ILCELER:
                hatalar.append(f"Mekan '{m['ad']}' ilçesi listede yok: {m['ilce']}")
            if m.get("gorsel") and not url_calisiyor_mu(m["gorsel"]):
                hatalar.append(f"Mekan '{m['ad']}' fotoğrafı açılmıyor")
        if sum(1 for m in mekanlar if m.get("gorsel")) < len(mekanlar) // 2:
            uyarilar.append("Gezilecek yerlerin yarısından azında fotoğraf var")

    return hatalar, uyarilar


if __name__ == "__main__":
    hepsi = "--hepsi" in sys.argv
    iller = topla.HAZIR_ILLER if hepsi else [a for a in sys.argv[1:] if not a.startswith("--")]
    genel = 0
    for il in iller:
        hatalar, uyarilar = kontrol(il, topla_calistir=not hepsi)
        veri = os.path.join(VERI, il + ".json")
        sayi = len(json.load(open(veri, encoding="utf-8"))["etkinlikler"]) if os.path.exists(veri) else 0
        print(f"\n=== {il}: {sayi} etkinlik — {'GEÇTİ' if not hatalar else 'KALDI (' + str(len(hatalar)) + ' hata)'}")
        for h in hatalar:
            print("  HATA  ", h)
        for u in uyarilar[:15]:
            print("  uyarı ", u)
        genel += len(hatalar)
    sys.exit(1 if genel else 0)
