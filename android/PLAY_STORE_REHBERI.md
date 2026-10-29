# Etkinlik Var — Android uygulamasını Google Play'de yayınlama rehberi

Uygulama, siteyi (etkinlik-var.netlify.app) telefonda tam ekran açan resmi Google yöntemiyle yapıldı
(**Trusted Web Activity**). Yani siteyi her güncellediğimizde uygulama da kendiliğinden güncellenir;
Play'e yeni sürüm yüklemek sadece simge/ad gibi şeyler değişince gerekir.

| Bilgi | Değer |
|---|---|
| Uygulama adı | Etkinlik Var |
| Paket adı (değiştirilemez!) | `com.etkinlikvar.app` |
| Uygulama dosyası | GitHub → Actions → "Android uygulamasi" → son çalıştırma → Artifacts → `etkinlik-var-android` (içinde `.aab` ve `.apk`) |
| İmza anahtarı | `C:\Users\HUAWEI\Documents\EtkinlikVar_imza\imza.jks` (şifre aynı klasörde `SIFRE_OKU.txt`) — **yedekle, kaybetme, kimseyle paylaşma** |
| Mağaza görselleri | `android/magaza/play-ikon-512.png`, `android/magaza/ozellik-gorseli-1024x500.png` |

## Adım 1 — İmza anahtarını GitHub'a ver (bir kez, Yunus)
GitHub'daki derleme, uygulamayı bu anahtarla imzalar. Anahtar depoya girmez, GitHub'ın "gizli değişken" kasasına girer.
Terminalde şu iki komutu çalıştır (05_ETKINLIK_MERKEZI klasöründe olman gerekmez):

```bash
base64 -w0 "C:/Users/HUAWEI/Documents/EtkinlikVar_imza/imza.jks" | gh secret set IMZA_JKS_BASE64 -R yunusbasyigit44-bot/etkinlik-var
```

```bash
sed -n 's/^Sifre: //p' "C:/Users/HUAWEI/Documents/EtkinlikVar_imza/SIFRE_OKU.txt" | tr -d '\r\n' | gh secret set IMZA_SIFRE -R yunusbasyigit44-bot/etkinlik-var
```

Sonra GitHub → Actions → "Android uygulamasi" → **Run workflow**. Bitince Artifacts'tan `app-release.aab` dosyasını indir
(imzalı olduğunu uyarı satırının KALKMASINDAN anlarsın: "IMZASIZ derlenecek" yazmamalı).

## Adım 2 — Google Play geliştirici hesabı (Yunus)
1. https://play.google.com/console → Google hesabınla gir → **25 ABD doları** tek seferlik ücret (kartı sen girersin).
2. Hesap türü: "Kişisel". Kimlik doğrulaması istenir (birkaç gün sürebilir).
3. Yeni kişisel hesaplarda Google, yayından önce **kapalı test** ister: en az **12 kişi 14 gün** boyunca uygulamayı test etmeli.
   Arkadaş/aile listesi hazırla (Gmail adresleri).

## Adım 3 — Uygulamayı oluştur
1. Play Console → **Uygulama oluştur** → Ad: `Etkinlik Var`, Dil: Türkçe, Tür: Uygulama, Ücretsiz.
2. **Uygulama imzalama**: "Google Play Uygulama İmzalama" açık kalsın (varsayılan). Bizim anahtar "yükleme anahtarı" olur.
3. **Test → Kapalı test** → yeni sürüm → `app-release.aab` dosyasını yükle → test kullanıcılarının e-postalarını ekle.

## Adım 4 — Site ile uygulamayı bağla (Claude yapar, sen değeri getir)
Google, uygulamayı kendi anahtarıyla yeniden imzalar. Uygulama adres çubuğu olmadan tam ekran açılsın diye
bu anahtarın parmak izi sitede olmalı:
1. Play Console → uygulama → **Test ve yayın → Kurulum → Uygulama bütünlüğü (App integrity) → Uygulama imzalama**.
2. "Uygulama imzalama anahtarı sertifikası" altındaki **SHA-256** değerini kopyala, Claude'a yapıştır.
3. Claude bunu `site/.well-known/assetlinks.json` dosyasına ikinci parmak izi olarak ekler ve yayınlar.
   (Şu an içinde sadece bizim yükleme anahtarının izi var.)

## Adım 5 — Mağaza sayfası (Claude metinleri hazırladı, sen yapıştır)
- **Kısa açıklama** (80 karakter): `81 ilde belediye, üniversite ve kültür etkinlikleri. Bugün ne yapsam?`
- **Tam açıklama**:

  > Etkinlik Var, Türkiye'nin 81 ilindeki belediye, üniversite, valilik, Devlet Tiyatroları, Devlet Opera ve Balesi
  > ve sivil toplum etkinliklerini tek yerde toplar. Her sabah güncellenir.
  >
  > • Bugün, yarın, hafta sonu: ilindeki tiyatro, konser, sergi, söyleşi ve çocuk etkinlikleri
  > • "Şu an sürenler" ve "az sonra başlayanlar"
  > • Türkiye geneli arama: etkinlik, mekân ya da sanatçı adıyla
  > • Online etkinlikler: evden katılabileceğin seminer ve atölyeler
  > • Takvime ekle, paylaş, yol tarifi al
  > • Etkinlik yoksa da gidilecek müze, park ve tarihi yerler
  >
  > Etkinlik Var bağımsız bir derlemedir; hiçbir kurumla resmî bağı yoktur. Her etkinlikte kaynağa bağlantı verilir.

- **Kategori**: Etkinlikler (Events). **İletişim e-postası**: kendi adresin.
- **Gizlilik politikası adresi** (zorunlu): `https://etkinlik-var.netlify.app/gizlilik.html`
- **İçerik derecelendirmesi** anketi: şiddet/kumar vb. hepsi "Hayır".
- **Veri güvenliği** formu: "Kişisel veri toplanmıyor" (Gidiyorum sayacı sadece rastgele cihaz numarası tutar;
  form gönderimi isteğe bağlı ve kişisel bilgi istemez).
- **Hedef kitle**: 13 yaş ve üzeri.
- Ekran görüntüleri: telefonda en az 2 adet (Claude önizlemeden çıkarabilir).

## Adım 6 — Üretime (herkese açık) geç
Kapalı test 14 günü doldurunca Play Console "Üretime erişim başvurusu" düğmesini açar → başvur → onaydan sonra
**Üretim → Yeni sürüm** → aynı `.aab` → yayınla. İnceleme genelde 1-7 gün sürer.

## Sonraki sürümler
`android/` klasöründe bir şey değişip GitHub'a gönderilince yeni `.aab` kendiliğinden derlenir (sürüm numarası otomatik artar).
İçerik (etkinlikler, manşet) için yeni sürüm GEREKMEZ — uygulama her açılışta siteyi gösterir.
