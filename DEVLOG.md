# DEVLOG: AI Usage Data: Cleaning and Visualization

Durum: tamamlandı (Adım 1-10), 2026-10-30
Başlangıç: 2026-10-30

## Karar ve varsayımlar
- 2026-10-30 | Seviye 1, amaç temizleme ve görselleştirme | Veri sentetik (yazarın açıklaması), bulgu iddiası kurulmayacak, ML ve hipotez testi yok
- 2026-10-30 | Lisans CC0, veri repoya konmaz | Kural: veri `data/` altında, `.gitignore`'da
- 2026-10-30 | `Monthly_Income` para birimi bilinmiyor kabul edildi | Veride para birimi sütunu yok, sadece 6 değerde `$` var; tutarlar sadece aynı sütun içinde sıralama için kullanılır
- 2026-10-30 | Skor ölçekleri gözlenen aralık olarak raporlanır | Teorik ölçek veride belgelenmemiş
- 2026-10-30 | `Non-binary` (1 satır) -> `Other` | TASK Gender'ı Male/Female/Other olarak tanımlıyor
- 2026-10-30 | `Gemini` -> `Google Gemini`, `Copilot` -> `Microsoft Copilot` | Aynı ürünün kısa adı varsayıldı
- 2026-10-30 | `Undergraduate` ve `Bachelor's` ayrı bırakıldı | TASK kuralı; `undergrad` -> `Undergraduate`, `BA/BSc` -> `Bachelor's`. İkisi muhtemelen örtüşüyor, analizde birleştirilmiş gibi yorumlanmayacak
- 2026-10-30 | `Country` da standartlaştırıldı | TASK listesinde yoktu ama aynı türden basit yazım hatası (20 -> 12), ülke kıyaslaması yine yapılmayacak
- 2026-10-30 | Aykırı eşikleri: Age > 80, AI_Usage > 16 sa/gün, Work > 24, Time_Saved/hafta > AI_Usage x 7, Monthly_Income > 10 x Q3 | Sadece işaretleme için seçildi, silme kararı İbrahim'de
- 2026-10-30 | İbrahim'in kararı: 4 imkansız değer NaN, satırlar kalır | Age 97 x2, AI_Usage 23, Monthly_Income 250000; U0212 ve 23 usage>work satırı sadece işaretli
- 2026-10-30 | Ücretli = `Monthly_AI_Cost` > 0, eksik maliyet o analizden çıkar | TASK grafik önerisi 6'daki tanım

## Kayıtlar

### 2026-10-30 | Adım 1: Repo iskeleti
- Yapılan: `data/`, `notebooks/`, `figures/`, `src/`, `requirements.txt`, `.gitignore` (data/, .venv/ hariç tutuldu). Sistem Python'unda pandas yoktu, `.venv` oluşturuldu (Python 3.15.2, pandas 3.1.0, matplotlib 3.11.2, seaborn 0.13.2, numpy 2.5.4).
- Bulunan: Klasör git deposu değil. `.gitignore` hazır ama `git init` yapılmadı.
- Sorun: Yok.
- Süre: ~10 dk
- Sonraki: Veriyi indir.

### 2026-10-30 | Adım 2: Veriyi indir ve doğrula
- Yapılan: `kaggle datasets download ... -p data/ --unzip`. Kaggle lisansı CC0-1.0 olarak raporladı. `src/validate_raw.py` ham raporu üretir (`data/raw_report.csv`).
- Bulunan:
  - Şekil 300 x 19, doğrulandı.
  - pandas tipleri: sadece `Productivity_Score`, `Accuracy_Rating`, `Satisfaction_Score` sayısal (float64), diğer 16 sütun metin.
  - Sayısala çevrilemeyen (ek içeren) değer sayısı: `Age` 14 (`"28 yrs"`), `Monthly_Income` 6 (`"$1,884 "`), `AI_Usage_Hours_Per_Day` 22 (`"2 hrs"`), `Monthly_AI_Cost` 15 (`"$0 "`), `Time_Saved_Hours_Per_Week` 18, `Work_or_Study_Hours_Per_Day` 12. Hepsi ek temizliğiyle çevrilebilir görünüyor.
  - Eksik: toplam 204 hücre, 151 satırda en az bir eksik. Sütun bazında: Age 23, Tasks_Performed 18, Productivity_Score 16, Profession 15, Accuracy_Rating 15, Education_Level 13, AI_Purpose 13, Monthly_AI_Cost 12, AI_Tool 11, Gender 10, Country 10, Monthly_Income 10, Time_Saved 10, Work_or_Study 9, AI_Usage 7, Satisfaction 7, Would_Recommend 5, User_ID 0, User_Type 0.
  - Tekrar: 12 tam tekrar satır. 12 tekrarlı `User_ID` var ve bu ID'leri paylaşan 24 satırın hepsi tam tekrar (aynı ID'li ama farklı içerikli satır yok).
  - Benzersiz: Gender 11, Country 20, Education_Level 16, AI_Tool 16, AI_Purpose 8 (temiz), User_Type 2 (temiz), Would_Recommend 3 (temiz), Profession 126.
  - Skor ölçekleri: Productivity 1.6-10 (0.1 adım), Accuracy 2-5 tam sayı, Satisfaction 3-10 tam sayı.
  - Aykırı adaylar (tekrarlar silindikten sonra, ham sayısal çeviriyle): Age 97 (2 satır), AI_Usage 23 saat/gün (1 satır), Monthly_Income 250000 (1 satır, 17 yaşında öğrenci), AI_Usage > Work_or_Study (23 satır), Time_Saved/hafta > AI_Usage x 7 (1 satır). Work_or_Study > 24 yok (max 20).
- Sorun: `Country` varyantları TASK ön gözleminde yoktu, TASK.md'ye eklendi. TASK.md'deki "DOĞRULANMADI" satırları güncellendi.
- Süre: ~25 dk
- Sonraki: `src/clean.py`.

### 2026-10-30 | Adım 3: Temizleme
- Yapılan: `src/clean.py` fonksiyonları: `drop_exact_duplicates`, `strip_units`, `standardize_categories`, `flag_outliers`, `clean` (hepsi `log` listesine kayıt ekler). Notebook (`notebooks/analysis.ipynb`) bunları çağırır. Çıktılar: `data/ai_usage_clean.csv`, `data/cleaning_log.csv`, `data/category_mappings.csv`.
- Bulunan:
  - 12 tam tekrar satır silindi (300 -> 288). Silmeden önce aynı `User_ID`'li ama farklı içerikli satır olmadığı kontrol edildi (fonksiyon bu durumda hata verir).
  - Ek temizliği (tekrar silindikten sonra): Age 12, Monthly_Income 6, AI_Usage 21, Monthly_AI_Cost 15, Time_Saved 15, Work_or_Study 12 değer. Çevrilemeyen değer: 0 (her sütunda).
  - Kategori: Gender 11 -> 3 (51 satır yeniden etiketlendi), AI_Tool 16 -> 8 (16 satır), Education_Level 16 -> 6 (16 satır), Country 20 -> 12 (14 satır).
  - Aykırı/tutarsız (sadece işaretlendi, silinmedi): Age > 80: 2 (U0248, U0210, ikisi de 97); AI_Usage > 16 sa/gün: 1 (U0046, 23 sa); Work_or_Study > 24: 0; AI_Usage > Work_or_Study: 23; Time_Saved/hafta > AI_Usage x 7: 1 (U0212); Monthly_Income > 10 x Q3: 1 (U0160, 17 yaşında öğrenci, 250000); negatif değer: 0. Toplam 27 satırda en az bir işaret.
- Sorun: Aykırı satırlar silinmedi, kural 9 gereği İbrahim'e soruldu.
- Süre: ~40 dk
- Sonraki: Doğrulama.

### 2026-10-30 | Adım 4: Temizleme doğrulaması
- Yapılan: `before_after_summary`, `run_checks`, eşleme tablosu notebook'ta. Notebook `jupyter nbconvert --execute` ile baştan sona hatasız çalıştı.
- Bulunan: 12 otomatik kontrolün 12'si geçti: tekrar satır yok, User_ID benzersiz, satır sayısı = 300 - 12, 9 sayısal sütun sayısal, ek temizliği yeni NaN üretmedi, Gender {Male, Female, Other}, AI_Tool 8, Education_Level 6, Country 12, User_Type 2, AI_Purpose 8, negatif değer yok.
- Sorun: Yok.
- Süre: ~20 dk
- Sonraki: Aykırı değer kararı gelince Adım 5 (keşifsel analiz).

### 2026-10-30 | Aykırı değer kararı (İbrahim)
- Karar: Sadece 4 imkansız değer NaN yapıldı, satırlar kaldı: Age 97 (U0248, U0210), AI_Usage 23 sa/gün (U0046), Monthly_Income 250000 (U0160). U0212 (Time_Saved > AI_Usage x 7) ve 23 AI_Usage > Work_or_Study satırı sadece işaretli kaldı.
- Uygulama: `clean.null_impossible_values`, `IMPOSSIBLE_VALUES` tablosu. Kontrol sayısı 13'e çıktı ("NaN only from raw + nulled impossible values", "no impossible values left").

### 2026-10-30 | Adım 5: Keşifsel analiz
- Yapılan: Notebook bölüm 4: describe, skor ölçekleri, kategori dağılımları, Spearman matrisi (sıralar üzerinde Pearson; pandas 3 `Series.corr(method="spearman")` scipy istiyor, bağımlılık eklememek için `figures.spearman` yazıldı ve `DataFrame.corr('spearman')` ile aynı sonucu verdiği kontrol edildi: 0.8095).
- Bulunan: n = 288. User_Type: Student 151, Professional 137. ChatGPT 119 / 278. Spearman: usage-productivity 0.81, usage-time_saved 0.83, productivity-satisfaction 0.63, accuracy-satisfaction 0.52, Monthly_AI_Cost tüm skorlarla |rho| <= 0.07. Monthly_Income medyanı: profesyonel 1884, öğrenci 122 (para birimi bilinmiyor).
- Sorun: Yok.
- Süre: ~30 dk
- Sonraki: Yedek sorular.

### 2026-10-30 | Adım 6: Yedek sorular
- Yapılan: Notebook bölüm 5.
- Bulunan:
  - Q1: Temizleme sonrası en çok eksik `Age` (25, %8.7; 2'si NaN yapılan 97'ler), sonra Tasks_Performed 17, Profession / Productivity / Accuracy 14'er. Tam satır sadece 138 / 288 (%47.9). Analiz bazında atınca n: kullanım-grup 280, kullanım-verimlilik 266, amaç-memnuniyet 268, ücretli-ücretsiz 269; 8 çekirdek sütun birlikte 216. Eksikler dağınık olduğu için global silme yarıdan fazla satırı atardı, analiz bazında silme bunu önlüyor.
  - Q2: Medyan kullanım öğrenci 2.00, profesyonel 2.05 sa/gün (Q1-Q3: 1.30-4.07 ve 1.40-3.90). Time_Saved medyanı 4.95 ve 5.15 sa/hafta. Productivity medyanı 4.9 ve 5.1. Satisfaction medyanı ikisinde de 6. Grup içi Spearman (usage-productivity): öğrenci 0.82 (n = 138), profesyonel 0.80 (n = 128).
- Sorun: Yok.
- Süre: ~20 dk
- Sonraki: Grafikler.

### 2026-10-30 | Adım 7: Grafikler
- Yapılan: `src/figures.py` içinde 6 fonksiyon, öneri listesinin 6'sı da: 01 eksik değer önce/sonra, 02 AI_Tool standartlaştırma, 03 kullanım dağılımı gruba göre, 04 kullanım-verimlilik scatter (Spearman notta), 05 amaca göre ortalama memnuniyet ve n, 06 ücretli/ücretsiz memnuniyet. Okuma notları koddaki sayılardan f-string ile üretiliyor. Renkler dataviz referans paletinden (mavi/turuncu, nötr gri).
- Bulunan: Görsel kontrolde fig 2'de etiket çakışması, fig 6'da lejant bar üstünde, fig 3/5'te not eksen adına yakındı; düzeltildi. Fig 3'te 2.05 medyanı `.1f` ile 2.0 görünüyordu, `.2f` yapıldı.
- Sorun: Yok.
- Süre: ~45 dk
- Sonraki: Gözlemler.

### 2026-10-30 | Adım 8-9: Gözlemler ve README
- Yapılan: Notebook bölüm 7 ve README'de 3 gözlem, sınırlamalar, ürün çıkarımı. Aşağıdaki Bulgular tablosu dolduruldu.
- Süre: ~25 dk

### 2026-10-30 | Adım 10: Kalite kontrol
- Yapılan: Üretilmiş dosyalar ve grafikler silinip notebook sıfırdan çalıştırıldı. Sonuç `05-kalite-kontrol.md`'de: 18/18 hücre, 0 hata, 13/13 kontrol, 6 grafik yeniden üretildi.
- Sorun: Klasör git deposu değil, commit yapılmadı.
- Süre: ~15 dk

## Veri kalite notları
- Satır/sütun: ham 300 x 19
- Eksik değerler: ham 204 hücre, 151 satır; sütun başına 0-23
- Tekrarlı satırlar: 12 tam tekrar (12 tekrarlı User_ID ile birebir aynı satırlar)
- Aykırı değerler: Age 97 (2), AI_Usage 23 sa/gün (1), Monthly_Income 250000 (1), AI_Usage > Work_or_Study (23), Time_Saved > AI_Usage x 7 (1). İlk 4'ü NaN yapıldı (İbrahim'in kararı), diğerleri sadece işaretli.
- Silinen/değiştirilen: 12 tam tekrar satır silindi (300 -> 288). 6 sütunda birim ekleri temizlendi. 4 kategori sütunu eşleme tablosuyla standartlaştırıldı. Aykırı satırlar sadece `flag_*` sütunlarıyla işaretli.

### Kategori eşleme tablosu (sadece değişen yazımlar; tam tablo `data/category_mappings.csv`)
| Sütun | Ham | Standart | Satır |
|---|---|---|---|
| Gender | male / MALE / M | Male | 12 / 6 / 11 |
| Gender | female / FEMALE / F | Female | 3 / 5 / 10 |
| Gender | other / Non-binary | Other | 3 / 1 |
| AI_Tool | chatgpt / Chat GPT / Chatgpt | ChatGPT | 4 / 3 / 2 |
| AI_Tool | Gemini / gemini | Google Gemini | 1 / 1 |
| AI_Tool | Copilot / copilot | Microsoft Copilot | 2 / 1 |
| AI_Tool | claude | Claude | 2 |
| Education_Level | high school / HS | High School | 1 / 1 |
| Education_Level | undergrad | Undergraduate | 3 |
| Education_Level | Bachelors / bachelor's degree / BA/BSc | Bachelor's | 2 / 1 / 2 |
| Education_Level | Masters / master's degree / MA/MSc | Master's | 2 / 1 / 1 |
| Education_Level | Ph.D. | PhD | 2 |
| Country | india / brazil / canada / france / philippines / australia | Büyük harfli ad | 3 / 4 / 2 / 1 / 1 / 1 |
| Country | U.K. | United Kingdom | 1 |
| Country | United States of America | United States | 1 |

Satır sayıları tekrarlar silindikten sonraki tablodan.

## Bulgular (analiz bittikten sonra doldurulur)
| # | Gözlem (bu veri setinde) | Kanıt (sayı/grafik) | Sınırlama |
|---|--------------------------|---------------------|-----------|
| 1 | Bu veri setinde temizlenmiş 288 satırın sadece 138'i tam, ama analiz bazında silme ile her analiz n = 266-280 tutuyor | Notebook bölüm 5 Q1; fig 01, 02 | Eşlemelerin bir kısmı varsayım (Gemini, Copilot, Non-binary); Undergraduate / Bachelor's ayrı tutuldu ama muhtemelen örtüşüyor |
| 2 | Bu veri setinde günlük AI kullanımı ile Productivity_Score sıralamada birlikte artıyor: Spearman 0.81 (n = 266), öğrenci 0.82, profesyonel 0.80 | Bölüm 4-5; fig 04 | Sadece monoton ilişki, nedensellik değil; 23 satırda AI saati çalışma saatini aşıyor ve tutuldu |
| 3 | Bu veri setinde Satisfaction_Score gruplar arasında neredeyse değişmiyor: amaç ortalamaları 5.82-6.41, tüm medyanlar 6; ücretli 5.98 vs ücretsiz 6.24, ikisinin medyanı 6 | fig 05, 06 | Tam sayı skor (8 seviye), küçük gruplar (Office Work n = 11), test yok; küçük farklar yorumlanmadı |

Her bulgu için ortak sınırlama: veri sentetik.

## Ürün çıkarımı
Temizleme işinin çoğu (51 Gender, 16 AI_Tool yeniden etiketleme, birim içeren 81 sayısal hücre) serbest metin girişinden geliyor. Kategoriler için sabit seçim listeleri ve birimi etikette olan sadece sayı kabul eden alanlar bu işi veri toplanırken ortadan kaldırır.

## Ne öğrendim
- Analiz bazında eksik silme, global silmeye göre çok daha fazla veri tutuyor (138 yerine 266-280)
- Açık eşleme tablosu + eşlenmemiş değerde hata vermek, yeni bir yazımın sessizce geçmesini önlüyor
- Grafik notlarını koddan üretmek, rakam ile not arasındaki uyumsuzluğu engelliyor (fig 3'te 2.05'in 2.0'a yuvarlanması böyle yakalandı)

## Sonraki adımlar (kapsam dışı kalanlar)
- `Tasks_Performed` serbest metin, kapsam dışı bırakıldı
- `Profession` (126 çok dilli değer) gruplanmadı, `User_Type` kullanıldı
- 23 "AI_Usage > Work_or_Study" satırının çıkarılması durumunda duyarlılık kontrolü yapılmadı
- (yapıldı) Repo: https://github.com/ibrahimbinbuga/ai-usage-data

## LinkedIn için ham notlar
- Açılış cümlesi (temizleme sonucu veya gözlem ile başla): "300 satırlık kasıtlı kirli bir tabloda AI_Tool sütununda 16 farklı yazım vardı; temizleyince 8 araç kaldı." (veri sentetik olduğu belirtilmeli)
- Öne çıkan grafik: `figures/02_ai_tool_standardization.png` (temizleme hikayesi) veya `figures/01_missing_values.png`
- Tek cümlelik ders: Eksik veriyi her analizde ayrı ele almak, 288 satırdan 138'e düşmek yerine 266-280 satırla çalışmayı sağladı.
- Diğer ham notlar: 12 tam tekrar, 13 otomatik kontrol, 4 imkansız değer (97 yaş, günde 23 saat AI); "synthetic data" ve "nedensellik yok" uyarıları gönderide olmalı
