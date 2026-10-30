# TASK: AI Usage Data: Cleaning and Visualization

## Bağlam
- Kaggle linki: https://www.kaggle.com/datasets/eishatuzzuhra/ai-usage-and-impact-on-students-and-professionals
- Lisans: CC0 1.0 (Public Domain), İbrahim teyit etti
- Seviye: 1 (temizleme ve görselleştirme ağırlıklı)
- Süre bütçesi: 2 hafta üst sınır, haftada 4-5 saat (tahmini toplam 8-10 saat)
- Veri SENTETİK. Yazarın açıklaması: eğitim amaçlı üretilmiş, eksik değer, tekrar kayıt, tutarsız kategori ve farklı sayı biçimleri bilerek eklenmiş, gerçek bir anketi temsil etmiyor. Bu bilgi README, grafik notları ve gönderide açıkça belirtilir.

## Ana soru
Kirli ve sentetik bir AI kullanım tablosu, belgelenmiş ve tekrarlanabilir adımlarla nasıl analize hazır hale getirilir ve temiz veri hangi dağılımları gösterir?

Yedek sorular:
1. Temizleme sonrası eksik veri hangi sütunlarda yoğunlaşıyor ve bu analizleri nasıl kısıtlıyor?
2. Kullanım süresi ve skorlar (`Productivity_Score`, `Satisfaction_Score`) öğrenci ve profesyonel gruplarında nasıl dağılıyor? (sadece tanımlayıcı)

## Veri bilgisi
- Satır/sütun: 300 x 19 (indirilen CSV ile doğrulandı, 2026-10-30)
- Dosya: `AI_Usage_and_Impact_on_Students_and_Professionals.csv`
- Sütunlar: User_ID, Age, Gender, Country, User_Type, Education_Level, Profession, Monthly_Income, AI_Tool, AI_Purpose, AI_Usage_Hours_Per_Day, Tasks_Performed, Monthly_AI_Cost, Productivity_Score, Accuracy_Rating, Satisfaction_Score, Time_Saved_Hours_Per_Week, Work_or_Study_Hours_Per_Day, Would_Recommend
- DOĞRULANDI (2026-10-30): skor ölçekleri veriden: `Productivity_Score` 1.6-10, 0.1 adımlı sürekli (73 benzersiz); `Accuracy_Rating` 2-5 tam sayı (4 benzersiz); `Satisfaction_Score` 3-10 tam sayı (8 benzersiz). Teorik ölçek (1-10 / 1-5) veride belgelenmemiş, gözlenen aralık bu.
- DOĞRULANAMAZ (2026-10-30): `Monthly_Income` para birimi veride yok. Sadece 6 değerde `$` öneki var, geri kalanı çıplak sayı. Para birimi bilinmiyor kabul edilir.
- Bilinen riskler (ön gözlem, ilk adımda doğrula):
  - Çoğu sayısal sütun metin: `"2 hrs"`, `"8.4 hrs"`, `"$0"` gibi ekler var.
  - `Gender` 11 benzersiz yazım (Male, male, MALE, M, Female, female, FEMALE, F, Other, other, Non-binary). Doğrulandı.
  - `Country` 20 benzersiz değer, büyük/küçük harf ve ad varyantları (`brazil`, `U.K.`, `United States of America`). Ön gözlemde yoktu.
  - `AI_Tool` 16 benzersiz değer (`ChatGPT` / `Chat GPT`).
  - `Education_Level` 16 benzersiz değer (`Masters` / `Master's`).
  - 12 tam tekrar satır ve 12 tekrarlı `User_ID`.
  - Eksik değer: `User_ID` ve `User_Type` 0, diğer 17 sütunda 5-23 arası (en çok `Age` 23). Toplam 204 hücre, 151 satırda en az bir eksik.
  - `Profession` çok dilli, 126 benzersiz değer. Gruplamak için `User_Type` kullan.
  - `Tasks_Performed` serbest metin, kapsam dışı.
  - Sentetik veri: görülen ilişkiler gerçek dünya hakkında bir şey söylemez.

## Kurallar
1. Önce `DEVLOG.md` ve bu dosyayı oku. Her adımın sonunda `DEVLOG.md`'ye kayıt ekle.
2. İlk adım veriyi doğrulamak: indir (`kaggle datasets download -d eishatuzzuhra/ai-usage-and-impact-on-students-and-professionals -p data/ --unzip`), şekli, sütun tiplerini, eksik değerleri, tekrarlı satırları raporla. Bu rapor bu dosyadaki "DOĞRULANMADI" ifadelerini düzeltir.
3. Veri `data/` altında kalır ve git'e girmez (`.gitignore`). Temizlenmiş çıktı da `data/` altına yazılır.
4. Sonuç uydurma. Her sayı kodun çıktısından gelsin. Çalıştırmadığın analizi bulgu diye yazma.
5. Her grafik: başlık, eksen adı, birim, tek cümle okuma notu. Her grafiğin notunda veya altyazısında "synthetic data" ibaresi olsun.
6. Her bulgunun yanına bir sınırlama yaz. Sentetik veri her bulgunun sınırlaması olarak geçerli, buna ek olarak bulguya özel bir sınırlama da yaz.
7. Varsayım yaptıysan `DEVLOG.md`'de "Karar ve varsayımlar" altına yaz.
8. Kapsamı büyütme. Ana soru dışında bir şeye 30 dakikadan fazla harcama, "Sonraki adımlar"a not düş.
9. Büyük bir karar gerekiyorsa (veri silme, soruyu değiştirme) dur ve İbrahim'e sor.
10. Seviye 1: makine öğrenmesi ve hipotez testi yok. Tanımlayıcı istatistik ve Spearman korelasyonu serbest. Korelasyon grafiklerinde nedensellik veya "gerçek dünyada böyle" dili kullanma.
11. Gerçek dünya iddiası kurma. Bulgu cümleleri "bu veri setinde..." diye başlasın.

## Adımlar
1. [x] Repo iskeleti: `data/`, `notebooks/`, `figures/`, `src/`, `requirements.txt`, `.gitignore`
2. [x] Veriyi indir ve doğrula (ham durum raporu: tipler, eksik, tekrar, benzersiz değer sayıları)
3. [x] Temizleme (`src/clean.py` içinde fonksiyonlar, notebook onları çağırır; her karar loglanır)
4. [x] Temizleme doğrulaması: önce/sonra özet tablosu, kategori eşleme tabloları, otomatik kontroller (tekrar satır kalmadı, sayısal sütunlar sayısal, kategori sayıları beklenen aralıkta)
5. [x] Keşifsel analiz (tanımlayıcı)
6. [x] Yedek sorulara kısa cevap
7. [x] 4-6 grafik `figures/` altına kaydet
8. [x] 3 gözlem + sınırlamalar + ürün çıkarımı
9. [x] README'yi doldur
10. [x] Kontrol listesi (`05-kalite-kontrol.md`): notebook baştan sona temiz çalışıyor mu?

## Seviyeye özel ek adımlar (Seviye 1: temizleme kuralları)
- Birim temizliği: `hrs`, `$` gibi ekleri at, sayısala çevir. Çevrilemeyen değeri say ve logla.
- Standartlaştır: `Gender` (Male / Female / Other), `AI_Tool` (yazım varyantlarını birleştir), `Education_Level`. Eşleme tablosunu `DEVLOG.md`'ye ve `data/` altında bir CSV olarak yaz. `Undergraduate` ile `Bachelor's` ayrı bırakılır, notu düşülür.
- Tekrarlı satır: önce tam aynı olup olmadığını doğrula, sonra sil. Kaç satır silindiğini yaz.
- Eksik değer: doldurma (imputation) yok. Her analizde o analizin kullandığı sütunlardaki eksik satırlar çıkarılır ve kalan n raporlanır.
- Aykırı/tutarsız değer kontrolü: `Age` aralığı, negatif değerler, `Time_Saved_Hours_Per_Week` ile `AI_Usage_Hours_Per_Day` tutarlılığı, `Work_or_Study_Hours_Per_Day` > 24. Silmeden önce İbrahim'e sor (kural 9).
- `Monthly_Income`: öğrenciler için çoğu 0 görünüyor, para birimi belirsiz. Ülkeler arası kıyaslama yapma.
- Skor sütunlarının ölçeği farklıysa doğrudan kıyaslama, her biri ayrı yorumlanır.

## Grafik önerisi (4-6 tanesini seç)
1. Eksik değer oranı, sütun bazında (temizleme öncesi/sonrası)
2. Kategori standartlaştırma etkisi: `AI_Tool` benzersiz değer sayısı öncesi ve sonrası, temizlenmiş araç dağılımı
3. `AI_Usage_Hours_Per_Day` dağılımı, `User_Type`'a göre
4. Kullanım süresi ve `Productivity_Score` dağılım grafiği (scatter), Spearman katsayısı altyazıda, "synthetic" notu ile
5. `AI_Purpose`'a göre ortalama `Satisfaction_Score` ve her grupta n
6. Ücretli ve ücretsiz kullanıcıların memnuniyet dağılımı (`Monthly_AI_Cost` > 0)

## Teslim
- Çalışır notebook, `src/clean.py`, `figures/`, doldurulmuş `README.md` ve `DEVLOG.md`
- Çıktının sonunda: 3 gözlem, 3 sınırlama, 1 ürün çıkarımı, LinkedIn taslağı için ham notlar
