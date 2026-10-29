# Yeni il ekleme rehberi (Etkinlik Var)

Bu rehber, bir ili siteye eklerken izlenecek adımlardır. Örnek dosyalar: `toplayici/iller/adana.py`, `adiyaman.py`, `afyonkarahisar.py`.

## Kesin kurallar (güvenlik ve dürüstlük)
- Sadece herkese açık sayfaları **okuma**. Giriş yapma, form gönderme, hesap açma yok.
- TLS/sertifika doğrulamasını kapatmaya, bot korumasını (TSPD, Cloudflare vb.) aşmaya **çalışma**. Korumalı site = "okunamıyor" notuyla listeye yaz, geç.
- Bilet sitelerini (bubilet, biletix, biletinial, passo, biletino) **kazıma**. Sitede zaten bağlantı veriliyor.
- Etkinlik uydurma, tahmin tarihle etkinlik ekleme. Sadece kaynağında tarihi yazan gerçek etkinlikler.
- Hiçbir paylaşılan dosyayı değiştirme: `ortak.py`, `ortak_kaynaklar.py`, `topla.py`, `kontrol.py`, `site/index.html`, diğer illerin dosyaları. Sadece kendi illerinin iki dosyasını oluştur. Ortak dosyada değişiklik gerekiyorsa raporunda öner.

## Bütçe (kotayı korumak için)
- İl başına toplam **~25 araç çağrısı**. En fazla 4-5 aday site dene; en iyi **2 kaynak** için özel okuyucu yaz (büyükşehirlerde en fazla 3). Gerisini `"not"` ile listele.
- Sadece ortak kaynaklar + gezilecek yerlerle biten il de kabul edilir; zorlamaya gerek yok.
- Her ili bitir (dosyalar + fotoğraflar + kontrol GEÇTİ), sonra diğerine geç; böylece yarıda kalırsa iş kaybolmaz.
- Geçici dosyaların için scratchpad içinde **kendi alt klasörünü** aç (ör. `scratchpad/ajan_30-33/`); başka ajanların dosyalarına dokunma.
- Dosyaları yazarken uzun heredoc yerine Write aracını kullan (tırnak sorunları çıkıyor).

## Ortak kodun yeni davranışları
- **Hazır Opera okuyucu:** `ortak_kaynaklar.devlet_opera` ("mudurluk": 1 Ankara, 2 İstanbul, 3 İzmir, 4 Mersin, 5 Antalya, 6 Samsun) — bu illerde zaten bağlı.
- `ortak.tarih_bul` artık "1 Ağustos - 30 Ekim" gibi ay aşan aralıkları da okur; kendi aralık fonksiyonunu yazma.
- `mekan_gorsel.py`: Vikipedi 429 verirse madde adını silmez ("sonra tekrar dene" yazar) → biraz bekleyip programı tekrar çalıştır. Anlam ayrımı sayfasında "X (İl)" biçimini dene.
- **Hazır iCal okuyucu:** `ortak_kaynaklar.ical` — WordPress "The Events Calendar" kullanan sitelerde (çoğu üniversite) `<site>/etkinlik/?ical=1` veya `/events/?ical=1` dene. Çalışıyorsa özel okuyucu yazma: `{"ad": ..., "tur": "universite", "url": "<akış>", "cek": ical, "mekan_varsayilan": "<Üniversite adı>", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"}`.
- `ortak.indir` sertifikası bozuk sitede **hata verir** (doğrulama kapatılmaz). Kaynağı "not" olarak yaz.
- Başlığı "<başka il>'da…" ya da "<başka il> Zirvesi/Fuarı/Kongresi/Festivali" olan etkinlikler otomatik elenir; sen ayrıca başlık filtresi yazma.
- `mekan_gorsel.py` artık: yönlendirilen madde ilin/ilçenin adını geçiriyorsa fotoğrafı kabul eder; harita, logo, .svg, uydu görüntüsü dosyalarını otomatik reddeder. Yine de dosya adlarına bir göz at.

## Her il için oluşturulacak 2 dosya
1. `toplayici/iller/<kod>.py` — kod: Türkçe harfsiz küçük harf (`agri`, `istanbul`, `sanliurfa`, `igdir`, `kirsehir`). `topla.il_kodu("Ağrı")` ile aynı olmalı.
2. `site/veri/<kod>_mekanlar.json` — 8-12 gezilecek yer.

İlin dosyası eklenince site ve toplayıcı onu **kendiliğinden** tanır (başka yere kayıt gerekmez).

## 1) Kaynak taraması (her il için 10-20 dakikayı geçme)
Önceki illerden öğrenilenler: valilik/kaymakamlık sitelerinde (`<ad>.gov.tr/duyurular`) neredeyse hiç etkinlik yok — hızlıca 1-2 tanesine bak, not düş, geç. Asıl kaynaklar sırasıyla:
1. **Üniversiteler** (ilde kaç tane varsa): etkinlik takvimi/listesi, WordPress ise `/category/etkinlikler/feed/` veya `/feed/`, sayfanın JS'inin kullandığı JSON uçları.
2. **Büyükşehir / il belediyesi**: etkinlik, kültür-sanat, şehir tiyatrosu, kültür merkezi programı. Next.js sitelerde veri sayfaya gömülü olabilir (`self.__next_f.push`).
3. **Büyük ilçe belediyeleri** (büyükşehirlerde merkez ilçeler).
4. Şehir tiyatrosu / kültür merkezi / il kültür-turizm müdürlüğü (`<il>.ktb.gov.tr` — alan adı bazen kısaltmalı: `afyon.ktb.gov.tr`).
5. Ortak kaynaklar her ilde **mutlaka** listeye eklenir (çalışıp çalışmadığına bakmadan):
   - `ktb` (İl Kültür ve Turizm — doğru alan adıyla)
   - `devlet_tiyatrosu` (`"sehir": "<İl adı>"`) — DT sahnesi olan iller: Ankara, İstanbul, İzmir, Bursa, Adana, Trabzon, Diyarbakır, Antalya, Erzurum, Konya, Sivas, Van, Kayseri, Hatay, Batman
   - `etkinlik_io` (`"sehir": "<İl adı>"`, url `https://etkinlik.io/<kod>`)

Çalışmayan/etkinlik vermeyen kurumlar da `"not": "..."` ile listeye yazılır — eksikler sitede görünsün diye (valilik, kaymakamlıklar, belediyeler, GSB, MEB, yıllık festivaller, "STK'lar, öğrenci kulüpleri, kafeler").

## 2) Okuyucu (parser) yazma
- Sadece standart kütüphane: `ortak.indir(url)` (sayfa indirir, kibar bekler), `re`, `json`, `html`.
- Yardımcılar: `ortak.tarih_bul(metin, bugun)` → (başlangıç, bitiş); `ortak.saat_bul`, `ortak.temizle`, `ortak.kategori_tahmin`, `ortak.baska_il_mi(yer, "<İl>")`; `ortak_kaynaklar.basliklar` (TAMAMI BÜYÜK başlığı düzeltir), `ilce_bulucu(ILCELER, SALON_ILCE)`.
- Okuyucu fonksiyonu `def ad(kaynak, bugun):` ve `yield {...}` döner. Alanlar:
  `baslik` (zorunlu), `tarih` (datetime.date), `bitis` (çok günlükse), `saat` ("HH:MM"), `mekan`, `ilce` (ILCELER içinden), `kategori` (yoksa otomatik), `ucretsiz` (biliniyorsa), `gorsel` (tam URL; boşluk/Türkçe harf varsa encode et), `url` (etkinliğin kendi sayfası), `ozet`.
- Geçmiş tarihliler, "düzenlendi/gerçekleştirildi" haberleri, iç toplantılar toplayıcıda otomatik elenir; yine de sadece yaklaşan etkinlik veren sayfaları tercih et.
- Başka ilde yapılan etkinliği alma (`ortak.baska_il_mi`).
- Site ara sıra boş dönerse toplayıcı önceki veriyi kullanır; sen sadece doğru ayrıştır.
- `ILCELER`: ilin tüm ilçeleri (merkez ilçe adıyla: büyükşehirlerde gerçek ilçe adları, diğerlerinde "Merkez"). Vikipedi'den doğrula.

## 3) Gezilecek yerler (`<kod>_mekanlar.json`)
8-12 yer: tarihi yerler, müzeler, doğa, parklar, çarşılar. Alanlar:
`ad, ilce, tur, simge (tek emoji), ucretsiz (true/false), vikipedi (tam Vikipedi madde adı ya da null), aciklama (1-2 cümle, kendi cümlen)`.
Sonra fotoğrafları çek: `py -X utf8 -I toplayici/mekan_gorsel.py <kod>`.
**Fotoğraf doğrulama (zorunlu):** Program yönlendirmeleri zaten reddeder. Ayrıca her fotoğrafın dosya adına bak; şüpheliyse Commons açıklamasını kontrol et:
`https://commons.wikimedia.org/w/api.php?action=query&titles=File:<dosya>&prop=imageinfo&iiprop=extmetadata&format=json`
Yanlış yeri gösteriyorsa `gorsel`'i sil ve `"vikipedi": null` yap (simge görünür). Örnek hatalar: "Yumurtalık" → anatomi resmi, "Frig Vadisi" → Göbekli Tepe, "Besni" → başka köprü.
Vikipedi'ye çok hızlı istek atma (program zaten 2 sn bekler); 429 alırsan bekle.

## 4) Kontrol (zorunlu)
`py -X utf8 -I toplayici/kontrol.py <kod>` → **GEÇTİ** yazmalı. Hata varsa düzelt, tekrar çalıştır. Uyarıları mümkünse gider.
Ayrıca çıkan etkinlik listesine göz at (`site/veri/<kod>.json`): başlıklar anlamlı mı, tarihler doğru mu, iç toplantı/ihale sızmış mı?

## 5) Rapor
Her il için tek satır: `<plaka> <İl>: N etkinlik, M gezilecek yer (K fotoğraflı); çalışan kaynaklar: ...; sorunlar: ...`
