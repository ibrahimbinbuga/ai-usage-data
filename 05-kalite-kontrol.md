# Kalite kontrol (2026-10-30)

Temiz çalıştırma: `data/` altındaki üretilmiş dosyalar (`ai_usage_clean.csv`, `cleaning_log.csv`, `category_mappings.csv`) ve `figures/*.png` silindi, ham CSV tutuldu, sonra `jupyter nbconvert --to notebook --execute --inplace notebooks/analysis.ipynb` çalıştırıldı.

## Notebook
- [x] Baştan sona hatasız çalışıyor: 18 kod hücresinin 18'i çalıştı, 0 hata, 0 stderr çıktısı
- [x] Çalışma sırası sıralı (1..18), elle çalıştırılmış eski hücre yok
- [x] Temizlenmiş CSV, log ve eşleme tablosu yeniden üretildi
- [x] 6 grafik `figures/` altında yeniden üretildi
- [x] Temizleme mantığı `src/clean.py` içinde, notebook sadece fonksiyonları çağırıyor

## Temizleme
- [x] 13 otomatik kontrolün hepsi geçiyor (`run_checks`, notebook'ta `assert` ile)
- [x] Tam tekrar silinmeden önce aynı ID'li farklı satır olmadığı doğrulandı (fonksiyon aksi halde hata verir)
- [x] Eşlenmemiş yeni bir kategori yazımı hata verir, sessizce geçmez
- [x] Doldurma (imputation) yok; her analiz kendi n'ini raporluyor (266-280)
- [x] Aykırı değerler işaretli; sadece İbrahim'in onayladığı 4 imkansız değer NaN yapıldı

## Grafikler (kural 5)
- [x] 6 grafiğin hepsinde başlık, eksen adı ve birim var
- [x] Her grafiğin altında tek cümlelik okuma notu ve "Synthetic data" ibaresi var
- [x] Okuma notundaki sayılar koddan geliyor (f-string), elle yazılmadı
- [x] Korelasyon grafiğinde nedensellik dili yok, notta açıkça "not evidence that usage causes" yazıyor
- [x] Görsel kontrol yapıldı: etiket çakışması yok (fig 2 ve fig 6 düzeltildi)

## Bulgu dili (kural 6, 10, 11)
- [x] Bulgu cümleleri "In this dataset..." ile başlıyor
- [x] Her bulgunun yanında bulguya özel bir sınırlama var
- [x] Makine öğrenmesi ve hipotez testi yok; sadece tanımlayıcı istatistik ve Spearman
- [x] Ülkeler arası gelir kıyaslaması yok; skorlar kendi ölçeklerinde yorumlandı

## Açık kalanlar
- [x] Repo: https://github.com/ibrahimbinbuga/ai-usage-data
- [ ] Notebook çıktıları gömülü görseller yüzünden ~840 KB; repoya koymadan önce çıktıları temizlemek isteyip istemediğine karar ver
