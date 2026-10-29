# 05 — Etkinlik Var (81 il etkinlik sitesi)

Slogan: **Bugün ne yapsam?** · Alan adı adayı: etkinlikvar.com.tr (2026-10-29 itibarıyla boş görünüyor; satın alma Yunus'ta)

"Bugün ne yapsam?" diyenler için il il etkinlik sitesi. Pilot il: **Adana** (başlangıç 2026-10-29). **81 ilin hepsi eklendi (2026-10-29).**

## Nasıl açılır?
- **Bilgisayarda deneme:** Claude uygulamasında "etkinlik-var" önizlemesini başlat (adres: http://localhost:8792).
- **Etkinlikleri elle güncelleme:** `BASLAT_TOPLA.bat` dosyasına çift tıkla.
- **İnternette yayın: https://etkinlik-var.netlify.app** (Netlify, 2026-10-29'dan beri yayında, herkese açık). Kod: https://github.com/yunusbasyigit44-bot/etkinlik-var
  - Her sabah 06:00'da GitHub etkinlikleri toplayıp depoya kaydeder (`.github/workflows/guncelle.yml`); Netlify yeni kaydı görünce siteyi kendiliğinden yeniden yayınlar (`netlify.toml`: "site" klasörü yayınlanır).
  - Bilgisayarda değişiklik yapınca: kaydet + `git push` → site 1 dakika içinde güncellenir.
  - Netlify paneli: https://app.netlify.com/projects/etkinlik-var (Yunus'un GitHub hesabıyla giriş).

## Klasörler
| Yol | Ne |
|---|---|
| `site/index.html` | Sitenin kendisi (tek sayfa) |
| `site/veri/adana.json` | Toplanan etkinlikler + kaynak durumu (otomatik üretilir, elle düzenlenmez) |
| `site/veri/adana_mekanlar.json` | Her gün açık yerler (müze, park, tarihi yer) — elle yazıldı |
| `toplayici/topla.py` | Ana program: kaynakları dolaşır, temizler, JSON yazar |
| `toplayici/ortak.py` | Ortak parçalar: Türkçe tarih/saat okuma, kategori tahmini, "olmuş etkinlik haberi" eleme |
| `toplayici/iller/adana.py` | Adana'ya özel kaynak listesi ve okuyucular. Yeni il = bu dosyanın bir kopyası |
| `supabase_kurulum.sql` | "Gidiyorum" sayacı ve "Etkinliğini ekle" formu için veritabanı kurulumu |

## Özellikler (örnek sitelerden alınanlar dahil)
- **Sol menü** (2026-10-29; telefonda "☰" ile soldan açılır): Türkiye geneli sayaç (toplam / bugün / şu an süren / hafta sonu, sayarak artar), "Bu hafta en hareketli iller" çubukları, tüm filtreler
- **Şu an** seçenekleri: Şu an sürenler · Az sonra (3 saat içinde) · Bugün başlayanlar · Devam eden (sergi, festival). Kartlarda canlı rozet: "● Şu an sürüyor", "⏳ 40 dk sonra başlıyor", "🔁 Devam ediyor · son gün …" — her dakika kendiliğinden güncellenir
- **24 tür, 8 sınıf** (Sahne, Müzik, Aile & Çocuk, Kültür & Sanat, Eğitim & Bilim, Spor & Doğa, Festival & Lezzet, Toplum). Tür kuralları `toplayici/ortak.py` → `KATEGORILER`; sınıflar `site/index.html` → `SINIFLAR` (yeni tür eklenince ikisine de ekle). Üstte sınıf düğmeleri, solda açılır sınıf + işaretli alt türler, sayılarıyla
- **Canlı şerit** (üstte kayan): Türkiye'de şu an süren / az sonra başlayan etkinlikler, il adına tıklayınca o ile gider. Fare üstüne gelince durur. Hareket istemeyenlerde (cihaz ayarı) animasyonlar kapanır
- Bugün / Yarın / Hafta sonu / 7 gün / 30 gün sekmeleri; ilçe, ücretsiz, arama; seçili filtreler üstte "✕" ile tek tek kaldırılır
- Hızlı seçim: Akşam (18:00+), İş çıkışı (hafta içi 17:30+), Aileyle gidilir
- Türkiye özeti `site/veri/turkiye.json` her toplamada `topla.py` tarafından yazılır
- Her etkinlikte afiş/görsel ve **Detaylar / Bilet** düğmesi (etkinliğin kendi sayfasına yönlendirir). Devlet Tiyatrosu afişleri 1 saatlik linkle geldiği için `site/veri/gorsel/` içine indirilir; eski afişler otomatik silinir
- Her gün açık yerlerde Vikipedi fotoğrafı ve "Hakkında" bağlantısı (`toplayici/mekan_gorsel.py` ile, yeni mekan eklenince bir kez çalıştır)
- **Gidiyorum** düğmesi ve kaç kişinin gittiği (sohbet yok — Yunus'un kararı)
- Takvime ekle (telefon takvimine), Paylaş (WhatsApp), Yol tarifi (Google Haritalar), Kaynağa git
- **Bana bir şey öner** düğmesi: bugünden rastgele bir etkinlik; yoksa her gün açık bir yer
- **Etkinliğini ekle** formu: kurum/kulüp/kafe kendi etkinliğini gönderir, onaydan sonra yayınlanır *(Eventfinda dersi)*
  - **Afiş/fotoğraf ekleme** (sürükle-bırak da olur). Güvenlik: sadece JPG/PNG/WEBP, en fazla 10 MB; fotoğraf tarayıcıda yeniden çizilip ≤1 MB JPEG'e çevrilir (konum/EXIF ve dosyaya gömülü her şey silinir; SVG ve sahte dosyalar reddedilir); "paylaşma hakkım var" onayı zorunlu; spam tuzağı alanı + 4 saniye kuralı; veritabanında gizli depo, ziyaretçi sadece yeni dosya ekleyebilir (okuyamaz/silemez/üzerine yazamaz), günde en fazla 200 fotoğraf, cihaz başına günde 10 etkinlik. Onaylanan afiş siteye elle kopyalanır
  - Sitenin güvenlik başlıkları `netlify.toml` içinde (başka sitelere gömülemez, sadece Supabase ile konuşur)
- Biletli konser ve gösteriler için bilet sitelerinin il sayfalarına bağlantı (içerik kopyalanmaz)
- "Bu listeyi nereden topluyoruz?" tablosu: her kaynağın çalışıp çalışmadığı açıkça görünür
- 81 il seçici; hazır olmayan il "yakında" der · koyu tema · telefona uygun

**Bilerek almadıklarımız:** üyelik zorunluluğu, bilet satışı/komisyon, reklam kalabalığı, çerez duvarı, sohbet.

## Adana — eksikler raporu (2026-10-29)

**Bugün:** 5 kaynak bağlı, 44 etkinlik (34'ü tiyatro/çocuk tiyatrosu). 17 kaynak tabloda.

| Durum | Kaynak | Not |
|---|---|---|
| ✅ Çalışıyor | Devlet Tiyatroları Adana | 22 seans; çocuk oyunları otomatik işaretleniyor |
| ✅ Çalışıyor | Adana Büyükşehir Şehir Tiyatrosu | 12 oyun |
| ✅ Çalışıyor | Adana Alparslan Türkeş BTÜ | 4 yaklaşan etkinlik |
| ✅ Çalışıyor | Çukurova Üniversitesi | 6 etkinlik; yer ve saat listede yok |
| ⚪ Bağlı, şu an boş | İl Kültür ve Turizm Müdürlüğü | Yeni duyuru gelince otomatik yakalanır |
| 🟡 Anahtar bekliyor | etkinlik.io | Resmî API hazır. Adana'da ~85 etkinlik var (konser, sahne, festival). **Yunus'un yayıncı başvurusu gerekiyor** |
| ❌ Takvim yok | Büyükşehir, Valilik, 15 kaymakamlık, ilçe belediyeleri, İl MEB | Sitelerde sadece haber/ihale/olmuş etkinlik var |
| ❌ Okunamıyor | Gençlik ve Spor İl Md., Saimbeyli Bld. | Bot koruması |
| ❌ Ulaşılamıyor | Altın Koza Festivali, İmamoğlu Bld., Halk Kütüphanesi | Site kapalı/bakımda |

### En büyük eksikler (öncelik sırasıyla)
1. **Belediyeler etkinliği sitede değil Instagram'da duyuruyor.** → Çözüm 1: "Etkinliğini ekle" formunu belediyelere/kulüplere tanıtmak. Çözüm 2 (ileride): Instagram'ı okumak resmî izin ister; şimdilik yapılmıyor.
2. **Konser ve festivaller eksik.** → etkinlik.io anahtarı gelince ~85 etkinlik eklenir.
3. **Spor etkinlikleri yok** (maraton, maçlar). → İleride: Adana Demirspor/Adanaspor maç takvimi, Adana Kebap ve Şalgam festivali gibi yıllık etkinlikler için elle "yıllık takvim" dosyası.
4. **Çukurova Üniversitesi etkinliklerinde saat/yer yok.** → Detay sayfasından okunabilir (sonraki adım).
5. **Sinema, müze sergileri, kütüphane etkinlikleri yok.**
6. **Gidiyorum sayacı ve form henüz veritabanına bağlı değil** → Yunus `supabase_kurulum.sql`'i bir kez çalıştırmalı. O zamana kadar Gidiyorum sadece kişinin kendi telefonunda hatırlanır.

## 02 Adıyaman — eksikler raporu (2026-10-29)

**Bugün:** 1 etkinlik, 10 gezilecek yer (8'i fotoğraflı). 12 kaynak tabloda.

| Durum | Kaynak | Not |
|---|---|---|
| ✅ Çalışıyor | Adıyaman Üniversitesi etkinlik takvimi | Bu ay + 2 ay okunuyor. Ekim'de 14 etkinlik vardı, Kasım–Aralık henüz boş; bahar döneminde yoğun (Mayıs 44) |
| ⚪ Bağlı, boş | İl Kültür ve Turizm, Devlet Tiyatroları | Adıyaman'da DT sahnesi yok (DT 15 ilde: Ankara, İstanbul, İzmir, Bursa, Adana, Trabzon, Diyarbakır, Antalya, Erzurum, Konya, Sivas, Van, Kayseri, Hatay, Batman) |
| 🟡 Anahtar bekliyor | etkinlik.io | |
| ❌ Takvim yok | Belediye (son kayıt Eylül 2025), Valilik, 8 kaymakamlık, ilçe belediyeleri, İl MEB | |
| ❌ Okunamıyor | Gençlik ve Spor İl Md. | Bot koruması |

### Adıyaman'dan çıkan ders: küçük illerde site boş kalacak
Büyükşehirlerde bile kurum siteleri az etkinlik veriyor; küçük illerde neredeyse hiç yok. Çözüm önerileri (öncelik sırasıyla):
1. **etkinlik.io anahtarı** — tüm illerde konser/sahne/festival getirir (en büyük kaldıraç).
2. **"Etkinliğini ekle" formunu yerelde tanıtmak** — belediye, üniversite kulüpleri, kafeler.
3. **Yıllık etkinlik takvimi** (elle): festivaller, bienaller, şenlikler — tarihi açıklanınca eklenir.
4. **Yakın illerde** bölümü: örn. Adıyaman sayfasında Diyarbakır/Batman tiyatro turneleri.

## 03 Afyonkarahisar — eksikler raporu (2026-10-29)

**Bugün:** 17 etkinlik (30 gün içinde 12), 10 gezilecek yer (7'si fotoğraflı). 16 kaynak tabloda.

| Durum | Kaynak | Not |
|---|---|---|
| ✅ Çalışıyor | Afyon Kocatepe Üniversitesi | 13 etkinlik; site ara sıra boş sayfa döndürüyor → yedek veri koruması devrede |
| ✅ Çalışıyor | Afyonkarahisar Belediyesi | Konser, koşu vb.; sayfaya gömülü veriden okunuyor (site yenilenirse bozulabilir) |
| ✅ Çalışıyor | Sağlık Bilimleri Üniversitesi (AFSÜ) | Tarih başlıkta yazanlar alınıyor; saat/yer yok |
| ⚪ Bağlı, boş | Emirdağ Belediyesi, İl Kültür ve Turizm, Devlet Tiyatroları (sahne yok) | |
| ❌ Takvim yok | Valilik, 17 kaymakamlık, Şehir Tiyatrosu (sadece arşiv), Sandıklı Bld., İl MEB | |
| ❌ Okunamıyor | Bolvadin Bld. (500 hatası), Gençlik ve Spor İl Md. (bot koruması), Dinar Bld. (serbest metin) | |

**Bu ilde eklenen genel iyileştirmeler (tüm illere işler):**
- Başka ilde yapılan etkinlikler elenir (ör. "Yer: Antalya").
- Kurul/senato/paydaş toplantısı gibi halka kapalı toplantılar elenir.
- Bir kaynak geçici olarak boş/bozuk dönerse bir kez daha denenir, olmazsa önceki günün geçerli verisi gösterilir.
- Vikipedi başka maddeye yönlendirirse fotoğraf alınmaz (Frig Vadisi için Göbekli Tepe fotoğrafı gelmişti).


## 81 il özeti (2026-10-29, otomatik)
Toplam: **990 etkinlik**, 81 il. Etkinliği 0 olan iller kurum sitelerinde takvim olmadığı içindir — etkinlik.io anahtarı ve 'Etkinliğini ekle' formu bunları dolduracak.

| Plaka | İl | Etkinlik | Gezilecek yer (fotoğraflı) | Çalışan kaynaklar |
|---|---|---|---|---|
| 01 | Adana | 44 | 14 (12) | Devlet Tiyatroları Adana (22), Adana Büyükşehir Şehir Tiyatrosu (12), Çukurova Üniversitesi (6), Adana Alparslan Türkeş BTÜ (4) |
| 02 | Adıyaman | 1 | 10 (8) | Adıyaman Üniversitesi (1) |
| 03 | Afyonkarahisar | 17 | 10 (7) | Afyon Kocatepe Üniversitesi (13), Afyonkarahisar Belediyesi (2), Afyonkarahisar Sağlık Bilimleri Üniversitesi (2) |
| 04 | Ağrı | 0 | 9 (3) | — |
| 05 | Amasya | 0 | 9 (1) | — |
| 06 | Ankara | 123 | 11 (8) | Devlet Tiyatroları (112), Devlet Opera ve Balesi (8), Hacettepe Üniversitesi (5), Çankaya Belediyesi (2) |
| 07 | Antalya | 33 | 12 (8) | Devlet Tiyatroları (22), Akdeniz Üniversitesi (5), Devlet Opera ve Balesi (5), Antalya Bilim Üniversitesi (1) |
| 08 | Artvin | 3 | 9 (2) | Artvin Çoruh Üniversitesi (3) |
| 09 | Aydın | 3 | 10 (6) | Aydın Adnan Menderes Üniversitesi (3) |
| 10 | Balıkesir | 11 | 10 (6) | Balıkesir Üniversitesi (11) |
| 11 | Bilecik | 0 | 8 (3) | — |
| 12 | Bingöl | 0 | 8 (2) | — |
| 13 | Bitlis | 0 | 8 (3) | — |
| 14 | Bolu | 0 | 9 (4) | — |
| 15 | Burdur | 6 | 10 (8) | Burdur Mehmet Akif Ersoy Üniversitesi (6) |
| 16 | Bursa | 53 | 12 (9) | Devlet Tiyatroları (26), Bursa Büyükşehir Belediyesi (kültür-sanat, sergiler) (11), Bursa Teknik Üniversitesi (9), Nilüfer Belediyesi (7) |
| 17 | Çanakkale | 0 | 10 (8) | — |
| 18 | Çankırı | 2 | 8 (3) | Çankırı Karatekin Üniversitesi (2) |
| 19 | Çorum | 0 | 9 (4) | — |
| 20 | Denizli | 1 | 10 (4) | Pamukkale Üniversitesi (1) |
| 21 | Diyarbakır | 37 | 10 (4) | Devlet Tiyatroları (21), Dicle Üniversitesi (12), Diyarbakır Büyükşehir Belediyesi (4) |
| 22 | Edirne | 0 | 10 (6) | — |
| 23 | Elazığ | 0 | 9 (4) | — |
| 24 | Erzincan | 4 | 10 (4) | Erzincan Binali Yıldırım Üniversitesi (3), Erzincan Belediyesi (1) |
| 25 | Erzurum | 31 | 10 (7) | Devlet Tiyatroları (18), Atatürk Üniversitesi (12), Erzurum Teknik Üniversitesi (1) |
| 26 | Eskişehir | 80 | 11 (7) | Anadolu Üniversitesi (45), Eskişehir Şehir Tiyatroları (35) |
| 27 | Gaziantep | 5 | 10 (4) | Gaziantep Üniversitesi (3), Gaziantep Büyükşehir Belediyesi (2) |
| 28 | Giresun | 0 | 8 (6) | — |
| 29 | Gümüşhane | 0 | 8 (4) | — |
| 30 | Hakkari | 5 | 8 (1) | Hakkari Üniversitesi (5) |
| 31 | Hatay | 3 | 9 (6) | Devlet Tiyatroları (3) |
| 32 | Isparta | 4 | 10 (6) | Süleyman Demirel Üniversitesi (3), Isparta Uygulamalı Bilimler Üniversitesi (1) |
| 33 | Mersin | 15 | 10 (8) | Devlet Opera ve Balesi (8), Mersin Üniversitesi (7) |
| 34 | İstanbul | 131 | 12 (9) | Devlet Tiyatroları (57), İBB Şehir Tiyatroları (53), Kadıköy Belediyesi Kültür Sanat (12), Devlet Opera ve Balesi (8), İstanbul Teknik Üniversitesi (2) |
| 35 | İzmir | 94 | 12 (11) | İzmir Büyükşehir Kültür Sanat (İzmir Sanat, Şehir Tiyatroları, AASSM, Elhamra) (43), Devlet Tiyatroları (40), Devlet Opera ve Balesi (8), Konak Belediyesi (3) |
| 36 | Kars | 0 | 8 (3) | — |
| 37 | Kastamonu | 3 | 10 (5) | Kastamonu Üniversitesi (2), Kastamonu Belediyesi (1) |
| 38 | Kayseri | 20 | 12 (8) | Devlet Tiyatroları (15), Erciyes Üniversitesi (5) |
| 39 | Kırklareli | 1 | 9 (5) | Lüleburgaz Belediyesi (1) |
| 40 | Kırşehir | 3 | 8 (3) | Kırşehir Belediyesi (3) |
| 41 | Kocaeli | 4 | 10 (6) | İzmit Belediyesi (3), Gebze Belediyesi (1) |
| 42 | Konya | 41 | 10 (6) | Devlet Tiyatroları (17), Konya Büyükşehir Belediyesi (Kültür Sanat Konya) (17), Necmettin Erbakan Üniversitesi (7) |
| 43 | Kütahya | 0 | 9 (3) | — |
| 44 | Malatya | 0 | 9 (5) | — |
| 45 | Manisa | 14 | 9 (4) | Manisa Büyükşehir Belediyesi Kültür (Şehir Tiyatrosu, konser, sergi) (9), Manisa Celal Bayar Üniversitesi (5) |
| 46 | Kahramanmaraş | 5 | 9 (3) | Kahramanmaraş Sütçü İmam Üniversitesi (4), Kahramanmaraş İl Kültür ve Turizm Müdürlüğü (2) |
| 47 | Mardin | 0 | 10 (6) | — |
| 48 | Muğla | 32 | 11 (4) | Bodrum Belediyesi (17), Muğla Sıtkı Koçman Üniversitesi (15) |
| 49 | Muş | 4 | 7 (1) | Muş Alparslan Üniversitesi (4) |
| 50 | Nevşehir | 3 | 10 (7) | Ürgüp Belediyesi (2), Nevşehir Hacı Bektaş Veli Üniversitesi (1) |
| 51 | Niğde | 4 | 9 (6) | Niğde Belediyesi Kültür Online (tiyatro, gösteri) (3), Niğde Ömer Halisdemir Üniversitesi (1) |
| 52 | Ordu | 0 | 8 (4) | — |
| 53 | Rize | 0 | 9 (6) | — |
| 54 | Sakarya | 0 | 8 (4) | — |
| 55 | Samsun | 12 | 9 (3) | Samsun Devlet Opera ve Balesi (8), Ondokuz Mayıs Üniversitesi (4) |
| 56 | Siirt | 0 | 9 (3) | — |
| 57 | Sinop | 15 | 10 (6) | Sinop Üniversitesi (15) |
| 58 | Sivas | 22 | 10 (6) | Devlet Tiyatroları (16), Sivas Cumhuriyet Üniversitesi (6) |
| 59 | Tekirdağ | 26 | 9 (2) | Tekirdağ Namık Kemal Üniversitesi (24), Tekirdağ Büyükşehir Belediyesi (2) |
| 60 | Tokat | 3 | 10 (3) | Tokat Belediyesi (3) |
| 61 | Trabzon | 32 | 10 (6) | Karadeniz Teknik Üniversitesi (15), Devlet Tiyatroları (13), Trabzon Üniversitesi (6) |
| 62 | Tunceli | 0 | 9 (2) | — |
| 63 | Şanlıurfa | 0 | 10 (7) | — |
| 64 | Uşak | 0 | 8 (7) | — |
| 65 | Van | 12 | 10 (6) | Devlet Tiyatroları (12) |
| 66 | Yozgat | 3 | 8 (4) | Yozgat Bozok Üniversitesi (3) |
| 67 | Zonguldak | 0 | 7 (2) | — |
| 68 | Aksaray | 6 | 8 (5) | Aksaray Üniversitesi (6) |
| 69 | Bayburt | 0 | 8 (4) | — |
| 70 | Karaman | 7 | 7 (6) | Karamanoğlu Mehmetbey Üniversitesi (7) |
| 71 | Kırıkkale | 0 | 8 (0) | — |
| 72 | Batman | 4 | 9 (6) | Devlet Tiyatroları (4) |
| 73 | Şırnak | 0 | 8 (3) | — |
| 74 | Bartın | 1 | 9 (2) | Bartın Üniversitesi (1) |
| 75 | Ardahan | 0 | 9 (1) | — |
| 76 | Iğdır | 2 | 7 (2) | Iğdır Üniversitesi (2) |
| 77 | Yalova | 1 | 8 (5) | Yalova Üniversitesi (1) |
| 78 | Karabük | 0 | 9 (2) | — |
| 79 | Kilis | 2 | 8 (1) | Kilis İl Kültür ve Turizm Müdürlüğü (2) |
| 80 | Osmaniye | 2 | 7 (2) | Osmaniye Korkut Ata Üniversitesi (2) |
| 81 | Düzce | 0 | 8 (2) | — |

## Yunus'un yapması gerekenler (sırayla)
1. Siteyi incele, beğenmediğini söyle.
2. Supabase > SQL Editor'de `supabase_kurulum.sql`'i çalıştır (Saha Kenarı'ndaki gibi).
3. https://etkinlik.io/yayinci-basvuru adresinden yayıncı başvurusu yap; gelen anahtarı Claude'a ver (anahtar koda yazılmaz, GitHub'da gizli değişken olarak saklanır).
4. ~~Yayın için onay ver~~ → Yapıldı: https://etkinlik-var.netlify.app (2026-10-29).
