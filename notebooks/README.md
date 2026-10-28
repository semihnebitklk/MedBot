# notebooks/

Notebook'lar numara sırasıyla çalıştırılmalıdır. Hepsi `notebooks/` klasöründen çalışır ve dosya yollarında `../` kullanır.

| Notebook | Amaç | Girdi | Çıktı |
|---|---|---|---|
| `01_kalp_veri_analizi` | Kalp verisini tanıma, temizleme | `raw/` | `bronze/`, `silver/heart_silver.csv` |
| `02_kalp_modelleme` | 6 model, GridSearchCV, tekrarlı CV, ROC, özellik önemi | `silver/heart_silver.csv` | `gold/heart_*.csv`, `models/kalp_modeli.pkl` |
| `03_belirti_veri_analizi` | Metin verisini tanıma, temizleme | `bronze/symptom_bronze.csv` | `silver/symptom_silver.csv` |
| `04_belirti_modelleme` | TF-IDF, 6 model, GridSearchCV, tekrarlı CV | `silver/symptom_silver.csv` | `gold/symptom_*.csv`, `models/belirti_modeli.pkl` |
| `05_bilgi_tabani` | Chi-kare ile hastalığa özgü belirtiler | `silver/symptom_silver.csv` | `chatbot/hastalik_belirtileri.json` |

Grafikler `results/figures/`, tablolar `results/tables/` klasörüne kaydedilir. Dosya adlarındaki `kalp_` ve `belirti_` önekleri hangi deneye ait olduklarını gösterir.
