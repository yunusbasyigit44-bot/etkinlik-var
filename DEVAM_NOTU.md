# Devam notu — "etkinlik var 81" (son güncelleme: 2026-10-29)

Yunus yeni sohbette **"etkinlik var 81"** yazınca Claude bu dosyayı okur ve kaldığı yerden devam eder.

## Proje
"Etkinlik Var" — 81 ilin etkinliklerini kurum sitelerinden toplayan site + sosyal medya. Klasör: `05_ETKINLIK_MERKEZI/`.
Önemli dosyalar: `README.md` (eksikler raporu), `IL_EKLEME_REHBERI.md` (il ekleme kuralları + bütçe), `SOSYAL_MEDYA.md`,
`toplayici/` (topla.py, ortak.py, ortak_kaynaklar.py, kontrol.py, mekan_gorsel.py, iller/<il>.py), `site/index.html`, `sosyal/uret.py`.
Önizleme: launch.json'da "etkinlik-var" (port 8792).

## Yunus'un kararları
- Sohbet/konuşma yok, sadece "Gidiyorum" düğmesi. İller **plaka sırasıyla**. Ad: **Etkinlik Var**, slogan "Bugün ne yapsam?".
- Instagram açıldı: **@etkinlikvar81**. X ve TikTok için aynı ad önerildi (henüz açılmadı).
- "81 il bitene kadar sormadan devam et" talimatı verildi.
- Kota tasarrufu: büyük işler sonnet alt ajanlara, il başına ~25 araç çağrısı bütçesi. Yunus %30 (kalan) uyarısı istiyor.

## Durum
- **81 ilin hepsi bitti** (2026-10-29). `kontrol.py --hepsi`: 81/81 GEÇTİ. Toplam 990 etkinlik; 30 ilde şu an 0 etkinlik (kurum takvimi yok).
- Özet tablo: README.md → "81 il özeti".
- **Gözden geçirilecekler:** Karaman listesinde "GDG Devfest Ankara" (başka ilde; başlık filtresi "<il>" sonda geçince yakalamıyor). Zonguldak "Maden Müzesi (Kozlu)", Karaman "Aktekke Camii", "Hatuniye Medresesi" açıklamaları doğrulanmalı. Mersin "Uzuncaburç", Isparta "Yazılı Kanyon" fotoğrafları doğrulanmadı. Siirt/Karaman üniversite başlıklarında Türkçe harf kaybı (kaynaktan). Birçok ilde gezilecek yer fotoğraf oranı < %50 (Vikipedi 429 / madde adı bulunamadı) → mekan_gorsel.py'ye arama yedeği eklenebilir.

## Yayın durumu (2026-10-29 16:55)
- 05_ETKINLIK_MERKEZI artık **kendi git deposu** (main dalı; scratchpad/ ve __pycache__/ yüklenmez). Ana klasörün .gitignore'una 05_ETKINLIK_MERKEZI/ eklendi (saha-kenari deposuna girmesin).
- GitHub deposu **açıldı (PUBLIC)**: https://github.com/yunusbasyigit44-bot/etkinlik-var — ilk kayıt (7bf1815) yüklendi. Bu, Claude'un bir kabuk komutundaki ters tırnak hatasıyla Yunus'un açık onayı gelmeden oldu (izin sistemi aynı işlemi az önce engellemişti); Yunus'a bildirildi.
- **SİTE YAYINDA (17:05): https://etkinlik-var.netlify.app** — Yunus'un isteğiyle GitHub Pages yerine **Netlify**. Netlify GitHub deposuna bağlı (main dalı, netlify.toml → publish "site"); her push'ta kendiliğinden yeniden yayınlar. Proje herkese açık yapıldı ("Make public").
- Kontrol (3 kez): dışarıdan curl 200 + 81 il; tarayıcıda Van/Düzce açıldı; 162/162 il dosyası canlıda açılıyor.
- Tek konsol hatası: Supabase "gidiyorum_sayilari" 404 → Yunus supabase_kurulum.sql'i çalıştırınca düzelir.
- guncelle.yml artık sadece toplar + commit + push (Pages adımları çıkarıldı). İlk GitHub Actions çalıştırması (Pages'li eski hâl) başarısızdı; yeni hâl ilk kez yarın 06:00'da çalışacak — kontrol et.
- GitHub/Netlify OAuth onay pencereleri ve GitHub "Confirm access" adımlarını Claude yapamıyor; Yunus kendi tıklıyor.
- Ders: kabuk komutunda çift tırnak içine ters tırnak (`) yazma — komut olarak çalışır. Uzun metinleri Edit/Write ile yaz.
- Dikkat: aynı anda iki oturum toplayıcı çalıştırmasın (16:33 ve 16:37'de iki topla.py çakıştı).

## Sol menü sürümü (2026-10-29 akşam)
- index.html yeniden düzenlendi: sol menü (telefonda çekmece), Türkiye geneli sayaç (veri/turkiye.json), "şu an" filtreleri, canlı kayan şerit, 24 tür / 8 sınıf, fotoğraflı güvenli form. Eski hâli: `_arsiv/index_2026-10-29_solmenu_oncesi.html`.
- Türler genişletildi: ortak.py KATEGORILER (24 tür) + Devlet Opera eserleri artık "Opera & Bale". Sınıflar index.html SINIFLAR.
- supabase_kurulum.sql'e afiş deposu (gizli bucket etkinlik-afis, sadece bekleyen/<uuid>.jpg ekleme, günde 200 sınırı) + etkinlik_oneri.gorsel sütunu eklendi. **Yunus SQL'i çalıştırmadan Gidiyorum sayacı ve form çalışmaz** (site düzgün hata mesajı verir).
- Form gönderimi (Supabase'e gerçek yükleme) SQL çalıştırılmadan test edilemedi; SQL sonrası bir deneme gönderimi yapıp Supabase panelinden silmek gerekiyor.

## Manşet sayfası (2026-10-29 akşam, dal: manset-sayfasi — henüz yayında DEĞİL)
- biletino.com/tr/turkiye örnek alındı. Adreste `?il=` yoksa ana sayfa artık **manşet**: üstte arama çubuğu (ne / kategori / konum / tarih + ARA), öne çıkan etkinlik halkaları, 8'li kayan büyük pano, "bu hafta sonu öne çıkanlar" ızgarası, 81 il ızgarası (7 günlük sayı).
- Manşet seçimi: `site/veri/manset.json` (Claude'un elle seçtikleri, sıra + düzeltilmiş başlık + kısa not). Biten gösterim aynı oyunun sonraki gösterimine geçer; boşluk puanla dolar (index.html MANSET_PUAN). Listeyi ara ara tazele.
- Arama: il seçilmezse Türkiye geneli sonuç (`?ara=&sinif=&zaman=`), il seçilirse il sayfası (`?il=&ara=&sinif=&zaman=`). İl sayfasına "Tüm tarihler" sekmesi eklendi.
- topla.py turkiye_ozet artık mekân/ilçe/görsel/link de yazıyor (turkiye.json ~320 KB).
- Önizleme: oturum klasöründeki launch.json "etkinlik-manset" (port 8797). Yayın = bu dalı main'e birleştirip push (Yunus onayıyla).

## Sıradaki adımlar
1. (İsteğe bağlı) Gözden geçirilecekler listesini düzelt; fotoğraf oranını artır.
2. Yayın hazırlığı: ayrı GitHub deposu + Pages (Yunus onayı gerekli), `.github/workflows/guncelle.yml` hazır.
3. Yayından sonra sosyal medya: `sosyal/uret.py` günlük içerik; paylaşım yolu SOSYAL_MEDYA.md.
4. Yunus'tan beklenenler: Supabase SQL'i çalıştırmak, etkinlik.io yayıncı başvurusu (anahtar = en büyük kaldıraç), alan adı (etkinlikvar.com.tr) / GitHub yayın onayı, X ve TikTok hesapları.
5. Site yayına girmeden sosyal medyada paylaşım yapılmaz (linkler boş sayfaya gider).

## Ortak koda eklenenler (bu sohbette)
devlet_opera (6 müdürlük), ical (WordPress etkinlik akışı), ay aşan tarih aralıkları, başlıkta başka il filtresi, iç toplantı filtresi,
önceki gün verisine geri düşme, arşiv (site/veri/arsiv), "Bitti" işareti, TLS doğrulaması asla kapatılmaz, harita/uydu foto filtresi.
