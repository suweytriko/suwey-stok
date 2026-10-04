# SUWEY satış stok uygulaması (GitHub Pages)

Yayın adresi: https://suweytriko.github.io/suwey-stok/ (main dalı, kök klasör).
Satışçılar bu adresi telefonlarında ana ekrana ekli kullanır; Claude hesabı yok.

## Veri kaynağı
Yönetim uygulaması (sahibin özel artifact'ı): https://claude.ai/artifact/7PmjGKdh9H5WnJ8zhpsGnK
- db `stock/current`: Excel "STOK RAPORU" sayfasından gelen stok (rows: p, c, s, t, g, sat, bek, k, d; reportDate, kritik, dusuk)
- db `photos/<docid>`: {asset, product, color}; docid = ürün kodu + "__" + renk (veya KAPAK), Türkçe harfler ASCII'ye çevrili
- Fotoğraf dosyaları artifact'ın asset deposunda (asset id ile)

## "Satış uygulamasını güncelle" denince
Kullanıcı Excel'i sohbete eklediyse: önce Excel'in STOK RAPORU sayfasını (yönetim uygulamasındaki "Excel'den güncelle" ile aynı kurallarla: 'ÜRÜN ADI'/'RENK' başlık satırından TOPLAM'a kadar) okuyup `ArtifactData set` ile stock/current'a yaz (önce get ile version al), sonra aşağıdaki adımlara devam et.

1. `ArtifactData get` stock/current, `out_dir` ile kaydet.
2. `ArtifactData list` photos (limit 1000), `out_dir` ile kaydet.
3. Yalnızca `photos/` içinde henüz `<docid>-<assetid ilk 8>.jpg` dosyası olmayan fotoğraflar için (genelde hiçbiri; fotoğraflar sabit) her asset id'ye ayrı bir `Artifact read` (url + `path`=<asset id> + out_dir) çağrısı yap (`paths` asset id kabul etmez); çağrıları paralel gönder, hepsini tek klasöre koy.
4. `python3 tools/build_data.py <stock json> <photos klasörü> <asset klasörü>`
5. Çıktıdaki satır/ürün/fotoğraf sayısını kontrol et, `git fetch origin main`, commit, `git push origin HEAD:main`.
6. 1-2 dakika sonra https://suweytriko.github.io/suwey-stok/data.json adresinin yeni reportDate'i gösterdiğini doğrula.

Satış tutarları ve fiyatlar bu (herkese açık) depoya asla konmaz; yalnızca adetler.
index.html'de tasarım değişirse sw.js içindeki önbellek adını (suwey-vN) bir artır.
