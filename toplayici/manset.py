"""Ana sayfa manşetini (site/veri/manset.json) her gün yeniler. topla.py en sonda çağırır; elle de çalışır:
    python toplayici/manset.py

Kurallar:
- "elle": true olan seçimler (Claude'un/Yunus'un elle seçtikleri) etkinlik bitene kadar sırasıyla kalır.
  Seçilen gösterim bittiyse aynı ildeki aynı adlı sıradaki gösterime geçilir.
- Kalan yerler her gün puanla yeniden seçilir: fotoğraflı, 14 gün içinde, türü manşete yakışan,
  yakın tarihli olan önde; aynı ilden en fazla 2, aynı türden en fazla 3, aynı oyun bir kez.
- Site de aynı kuralla eksikleri tamamlar (index.html mansetSec), bu dosya sadece sırayı ve notları belirler.
"""
import datetime as dt
import json
import os

KLASOR = os.path.dirname(os.path.abspath(__file__))
VERI = os.path.join(KLASOR, "..", "site", "veri")
TOPLAM = 16          # manşette en fazla kaç etkinlik
UFUK_GUN = 14        # en fazla kaç gün sonrası

# index.html MANSET_PUAN ile aynı
PUAN = {"Opera & Bale": 6, "Konser": 5, "Festival": 5, "Geleneksel Müzik": 5, "Dans": 4, "Tiyatro": 4, "Komedi": 4,
        "Sergi": 3, "Çocuk": 3, "Sinema": 3, "Fuar & Kermes": 3, "Yemek": 3, "Doğa & Gezi": 3, "Spor": 2,
        "Edebiyat": 2, "Gençlik": 1, "Bilim & Teknoloji": 1}

# Kendiliğinden seçilenler için kısa manşet cümlesi ({il_de} = "Adana'da")
NOTLAR = {
    "Opera & Bale": "{il_de} opera ve bale sahnesinden bir akşam.",
    "Konser": "{il_de} canlı müzik keyfi.",
    "Festival": "{il_de} festival havası.",
    "Geleneksel Müzik": "{il_de} geleneksel ezgiler.",
    "Dans": "{il_de} ritim ve dans dolu bir gösteri.",
    "Tiyatro": "{il_de} perde açılıyor.",
    "Komedi": "{il_de} kahkaha garantili bir akşam.",
    "Sergi": "{il_de} gezip görülecek bir sergi.",
    "Çocuk": "{il_de} çocuklarla gidilecek bir etkinlik.",
    "Sinema": "{il_de} beyaz perdede.",
    "Fuar & Kermes": "{il_de} dolaşıp alışveriş yapılacak bir etkinlik.",
    "Yemek": "{il_de} lezzet dolu bir buluşma.",
    "Doğa & Gezi": "{il_de} doğada bir gün.",
    "Spor": "{il_de} tribünden heyecan.",
    "Edebiyat": "{il_de} kitapseverler için.",
}


def kucuk(s):
    return (s or "").replace("I", "ı").replace("İ", "i").lower()


def de(ad):
    """Türkçe bulunma eki: Adana'da, İzmir'de, Kars'ta, Tokat'ta (index.html de() ile aynı)."""
    k = kucuk(ad)
    unluler = [c for c in k if c in "aeıioöuü"]
    kalin = unluler[-1] in "aıou"
    sert = k[-1] in "fstkçşhp"
    return ad + "'" + ("t" if sert else "d") + ("a" if kalin else "e")


def guncelle(bugun=None):
    bugun = bugun or dt.date.today()
    bugun_s, sinir_s = bugun.isoformat(), (bugun + dt.timedelta(days=UFUK_GUN)).isoformat()
    with open(os.path.join(VERI, "turkiye.json"), encoding="utf-8") as f:
        tr = json.load(f)["etkinlikler"]
    yol = os.path.join(VERI, "manset.json")
    try:
        with open(yol, encoding="utf-8") as f:
            eski = json.load(f)
    except (OSError, ValueError):
        eski = {}

    def uygun(e):
        return e.get("g") and e["il"] != "Online" and (e.get("bt") or e["t"]) >= bugun_s and e["t"] <= sinir_s

    kimlik = {e["id"]: e for e in tr}
    secilen, gorulen, il_say, tur_say = [], set(), {}, {}

    def ekle(e, kayit):
        anahtar = e["il"] + "|" + kucuk(e["b"])
        if anahtar in gorulen:
            return
        gorulen.add(anahtar)
        il_say[e["il"]] = il_say.get(e["il"], 0) + 1
        tur_say[e.get("k")] = tur_say.get(e.get("k"), 0) + 1
        secilen.append(kayit)

    # 1) Elle seçilenler: bitene kadar kalır
    for s in eski.get("secilenler", []):
        if not s.get("elle"):
            continue
        e = kimlik.get(s["id"])
        if e and not uygun(e):
            e = next((x for x in tr if x["il"] == e["il"] and x["b"] == e["b"] and uygun(x)), None)
        if e:
            ekle(e, {**s, "id": e["id"]})

    # 2) Kalan yerler puanla
    def puan(e):
        gun = max(0, (dt.date.fromisoformat(e["t"]) - bugun).days)
        return PUAN.get(e.get("k"), 0) * 10 - gun * 2 + (3 if e.get("u") else 0)

    for e in sorted((x for x in tr if uygun(x) and PUAN.get(x.get("k"))), key=puan, reverse=True):
        if len(secilen) >= TOPLAM:
            break
        if il_say.get(e["il"], 0) >= 2 or tur_say.get(e.get("k"), 0) >= 3:
            continue
        ekle(e, {"id": e["id"], "not": NOTLAR.get(e.get("k"), "").format(il_de=de(e["il"]))})

    veri = {
        "aciklama": eski.get("aciklama") or "Ana sayfa manşeti. toplayici/manset.py her gün yeniler.",
        "guncelleme": bugun_s,
        "secilenler": secilen[:TOPLAM],
    }
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=1)
    elle = sum(1 for s in veri["secilenler"] if s.get("elle"))
    print(f"Manşet: {len(veri['secilenler'])} etkinlik ({elle} elle seçilmiş)")
    return veri


if __name__ == "__main__":
    guncelle()
