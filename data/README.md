# data/

Veriler bronze → silver → gold katman mantığıyla düzenlenmiştir. Her katman bir öncekinden kodla üretilir; ham veri hiçbir zaman değiştirilmez.

| Klasör | İçerik | Üreten |
|---|---|---|
| `raw/` | Kaggle'dan indirilen orijinal dosyalar (`heart.csv`, `Symptom2Disease.csv`) | Elle indirildi |
| `bronze/` | Ham verinin değiştirilmeden alınmış kopyası | `01_kalp_veri_analizi` |
| `silver/` | Temizlenmiş veri | `01` (kalp), `03` (belirti) |
| `gold/` | Modele hazır eğitim / test setleri | `02` (kalp), `04` (belirti) |
| `chatbot/` | Chatbotun kullandığı bilgi dosyaları | Aşağıya bakınız |

## Silver katmanında yapılanlar

**Kalp verisi (918 → 917 satır)**
- Kolesterolü 0 olan 171 kayıt: değer NaN yapıldı, `Cholesterol_eksik` sütunu eklendi (hasta silinmedi)
- Kan basıncı ve kolesterolü 0 olan 1 kayıt: güvenilmez kabul edilip silindi
- Negatif Oldpeak değerleri: klinik olarak mümkün olduğu için korundu

**Belirti verisi (1200 → 1153 satır)**
- 47 birebir tekrar eden metin silindi (eğitim/test sızıntısını önlemek için)
- Etiketlerdeki büyük/küçük harf tutarsızlığı giderildi
- `temiz_metin` sütunu eklendi (stopword, lemmatization)

## chatbot/

| Dosya | İçerik | Kaynak |
|---|---|---|
| `intents.json` | Sohbet kalıpları ve cevapları | Proje ekibi |
| `hastalik_bilgileri.json` | 24 hastalığın açıklaması, önerileri, acil belirtileri | MedlinePlus (her hastalıkta `source` alanı) |
| `hastalik_belirtileri.json` | Her hastalığın ayırt edici belirtileri | Symptom2Disease, chi-kare testi (`05_bilgi_tabani`) |
