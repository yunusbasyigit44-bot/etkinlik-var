# Etkinlik Var — Sosyal medya (Instagram, X, TikTok)

## Yunus'un yapacakları (bir kerelik)
1. Hesapları aç; mümkünse üçünde de **aynı ad**: Instagram `@etkinlikvar81` (açıldı, 2026-10-29) — X ve TikTok için de `@etkinlikvar81`. Hesap açma, şifre ve doğrulama senin işin, ben hesap açamam.
2. Instagram'ı **İşletme / Yaratıcı hesap** yap (istatistik, zamanlama ve bağlantı çıkartması için). Bir Facebook sayfasına bağlarsan **Meta Business Suite**'ten gönderi ve hikâye **zamanlanabilir**.
3. Hesap adlarını bana yaz → `sosyal/uret.py` içindeki `HESAP` satırını güncellerim.
4. Site yayına girince alan adı kesinleşir → `SITE` satırı güncellenir (şu an `etkinlikvar.com.tr` yazıyor).

### Profil metni (kopyala-yapıştır)
**Ad:** Etkinlik Var · Bugün ne yapsam?
**Biyografi:**
```
📅 81 ilde bugünün etkinlikleri
🎭 Konser · tiyatro · sergi · çocuk etkinlikleri
🆓 Ücretsiz olanlar dahil
👇 Şehrini seç
```
**Bağlantı:** site adresi

**Öne çıkanlar (Instagram):** her il için bir klasör ("Adana", "Adıyaman", …) + "Hafta sonu" + "Gezilecek yerler".

## Her gün ne üretiliyor?
Komut: `py -X utf8 -I sosyal/uret.py` → `sosyal/cikti/<tarih>/` klasörü. İçinde **PAYLASIM_PLANI.md** var; hangi dosya, hangi saatte, hangi metinle paylaşılacak.

| Platform | Ne | Saat (öneri) |
|---|---|---|
| Instagram hikâye | Türkiye özeti + etkinliği olan **her il** için "Bugün <il>'da" kartı (boş yerde o ilin gezilecek bir yeri) | 08:30'dan itibaren |
| Instagram gönderi | 1) Günün özeti 2) Gezilecek yer (fotoğraflı) 3) Yarın ne var / Perşembe-Cuma: Hafta sonu ne var | 09:00 · 13:00 · 19:00 |
| X (Twitter) | Aynı 3 görsel + 280 karakterlik metin | 09:00 · 13:00 · 19:00 |
| TikTok | ~18 sn dikey video: "Bugün Türkiye'de ne var?" (kendi ürettiğimiz telifsiz müzikle) | 18:00 |

## Paylaşım yolu (öneri)
- **Instagram:** Meta Business Suite'in kendi zamanlayıcısı (resmî yol, hesap güvenliği için en iyisi).
- **X:** x.com'un gönderi zamanlama özelliği.
- **TikTok:** tiktok.com web yükleme ekranındaki zamanlama.
- Sen giriş yaptıktan sonra bunları Claude in Chrome ile her gün ben doldurup zamanlayabilirim (YouTube kanalındaki gibi). Bot/otomatik beğeni-takip araçları **kullanılmaz**: hesap kapatılır.

## Kurallar
- **Kurum afişleri kullanılmaz** (telif). Kartlar bizim tasarımımız, sadece bilgi (ad, saat, yer) var.
- Mekân fotoğrafları Wikimedia Commons'tan; **fotoğrafçı + lisans satırı açıklamadan silinmez** (lisans şartı, X metninde de korunuyor).
- Yanlış bilgi riski: etkinlikler kurum duyurularından otomatik derleniyor. Paylaşım metinlerinde "Tüm ayrıntılar ve kaynak: site" yönlendirmesi var.
- Siyasi, dini, tartışmalı içerik paylaşılmaz; yorumlarda kavga varsa gizlenir.
