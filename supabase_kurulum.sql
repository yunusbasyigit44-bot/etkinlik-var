-- ============================================================
-- BUGÜN NE VAR? — "GİDİYORUM" SAYACI VE "ETKİNLİĞİNİ EKLE" FORMU
-- ------------------------------------------------------------
-- Yunus için: Bu kodun tamamını Supabase > SQL Editor'e yapıştırıp "Run" de.
-- Saha Kenarı ile aynı Supabase projesinde çalışır, onun tablolarına dokunmaz.
-- Bir kez çalıştırman yeterli; tekrar çalıştırırsan zarar vermez.
--
-- Ne kuruyor?
--   1) gidiyorum            : hangi cihaz hangi etkinliğe "gidiyorum" dedi
--   2) gidiyorum_sayilari   : etkinlik başına toplam sayı (sitede görünen rakam)
--   3) gidiyorum_ekle / gidiyorum_vazgec : sitenin çağırdığı iki küçük işlem
--   4) etkinlik_oneri       : "Etkinliğini ekle" formundan gelenler (onay bekler,
--                             site bunları OKUYAMAZ; sadece Claude/Yunus görür)
-- ============================================================

create table if not exists public.gidiyorum (
  etkinlik_id text not null check (char_length(etkinlik_id) between 6 and 40),
  cihaz       uuid not null,
  olusturma   timestamptz not null default now(),
  primary key (etkinlik_id, cihaz)
);

alter table public.gidiyorum enable row level security;
-- Tabloya doğrudan erişim yok; sadece aşağıdaki işlemler ve sayı görünümü kullanılır.
revoke all on public.gidiyorum from anon, authenticated;

create or replace view public.gidiyorum_sayilari as
  select etkinlik_id, count(*)::int as sayi from public.gidiyorum group by etkinlik_id;
grant select on public.gidiyorum_sayilari to anon, authenticated;

create or replace function public.gidiyorum_ekle(p_etkinlik text, p_cihaz uuid) returns void
language plpgsql security definer set search_path = public as $$
begin
  -- Hız sınırı: bir cihaz dakikada en fazla 20 işaret koyabilir
  if (select count(*) from public.gidiyorum where cihaz = p_cihaz and olusturma > now() - interval '1 minute') >= 20 then
    raise exception 'Cok hizli';
  end if;
  insert into public.gidiyorum (etkinlik_id, cihaz) values (p_etkinlik, p_cihaz)
  on conflict do nothing;
end $$;

create or replace function public.gidiyorum_vazgec(p_etkinlik text, p_cihaz uuid) returns void
language sql security definer set search_path = public as $$
  delete from public.gidiyorum where etkinlik_id = p_etkinlik and cihaz = p_cihaz;
$$;

grant execute on function public.gidiyorum_ekle(text, uuid) to anon, authenticated;
grant execute on function public.gidiyorum_vazgec(text, uuid) to anon, authenticated;

-- ------------------------------------------------------------
-- Etkinliğini ekle formu
-- ------------------------------------------------------------
create table if not exists public.etkinlik_oneri (
  id          bigint generated always as identity primary key,
  olusturma   timestamptz not null default now(),
  il          text not null check (char_length(il) <= 20),
  baslik      text not null check (char_length(btrim(baslik)) between 3 and 140),
  tarih       date not null,
  saat        time,
  ilce        text not null check (char_length(ilce) <= 40),
  mekan       text not null check (char_length(mekan) <= 120),
  kategori    text check (char_length(kategori) <= 30),
  ucretsiz    boolean,
  aciklama    text check (char_length(aciklama) <= 600),
  link        text check (link is null or (char_length(link) <= 300 and link ~ '^https?://')),
  duzenleyen  text not null check (char_length(duzenleyen) <= 120),
  cihaz       uuid not null,
  durum       text not null default 'beklemede' check (durum in ('beklemede', 'onaylandi', 'reddedildi'))
);

create or replace function public.oneri_kontrol() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.tarih < current_date - 1 or new.tarih > current_date + 365 then
    raise exception 'Gecersiz tarih';
  end if;
  -- Spam sınırı: bir cihaz günde en fazla 10 etkinlik gönderebilir
  if (select count(*) from public.etkinlik_oneri where cihaz = new.cihaz and olusturma > now() - interval '1 day') >= 10 then
    raise exception 'Gunluk sinir';
  end if;
  new.durum := 'beklemede';
  new.olusturma := now();
  return new;
end $$;

drop trigger if exists oneri_kontrol on public.etkinlik_oneri;
create trigger oneri_kontrol before insert on public.etkinlik_oneri
  for each row execute function public.oneri_kontrol();

alter table public.etkinlik_oneri enable row level security;
drop policy if exists "herkes gonderebilir" on public.etkinlik_oneri;
create policy "herkes gonderebilir" on public.etkinlik_oneri
  for insert to anon, authenticated with check (true);
-- Okuma kuralı YOK: gönderilenleri site ziyaretçileri göremez.
grant insert on public.etkinlik_oneri to anon, authenticated;
