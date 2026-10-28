# MedBot – Yapay Zekâ Destekli Sağlık Asistanı

MedBot, kullanıcının belirtilerini doğal dilde anlatarak olası hastalıkları öğrenebildiği ve klinik ölçümlerinden kalp hastalığı riskini tahmin ettirebildiği bir sağlık chatbotudur. İki ayrı makine öğrenmesi deneyine dayanır:

| Deney | Veri seti | Problem | Seçilen model | Sonuç (tekrarlı CV) |
|---|---|---|---|---|
| Kalp hastalığı riski | [Heart Failure Prediction](https://www.kaggle.com/datasets/fedesoriano/heart-failure-prediction) (918 hasta) | İkili sınıflandırma | XGBoost | ROC-AUC 0.936 ± 0.023 |
| Belirti → hastalık | [Symptom2Disease](https://www.kaggle.com/datasets/niyarrbarman/symptom2disease) (1200 metin, 24 hastalık) | 24 sınıflı metin sınıflandırma | Doğrusal SVM (TF-IDF) | macro-F1 0.982 ± 0.010 |

> ⚠️ MedBot bir eğitim projesidir, tıbbi teşhis koymaz. Sonuçlar istatistiksel tahmindir; sağlık kararları için mutlaka bir doktora başvurulmalıdır.

---

## Klasör yapısı

```
MedBot/
├── data/                          → Veri katmanları (bkz. data/README.md)
│   ├── raw/                       Kaggle'dan indirilen orijinal dosyalar
│   ├── bronze/                    Ham verinin değiştirilmeden alınmış kopyası
│   ├── silver/                    Temizlenmiş veri
│   ├── gold/                      Modele hazır veri (eğitim / test)
│   └── chatbot/                   Chatbotun bilgi dosyaları (JSON)
├── notebooks/                     → Analiz ve modelleme (bkz. notebooks/README.md)
│   ├── 01_kalp_veri_analizi.ipynb
│   ├── 02_kalp_modelleme.ipynb
│   ├── 03_belirti_veri_analizi.ipynb
│   ├── 04_belirti_modelleme.ipynb
│   └── 05_bilgi_tabani.ipynb
├── src/                           → Chatbotun beyni (bkz. src/README.md)
│   ├── medbot.py                  Mesajı doğru katmana yönlendirir
│   ├── sohbet.py                  1. katman: selamlaşma, yardım
│   ├── belirti_tahmin.py          2. katman: belirti → hastalık
│   ├── bilgi_tabani.py            Hastalık bilgileri ve ayırt edici belirtiler
│   ├── kalp_riski.py              3. katman: kalp hastalığı riski
│   └── metin_isleme.py            Ortak metin temizleme fonksiyonu
├── app/                           → Kullanıcı arayüzleri
│   ├── gui.py                     Pencereli arayüz (Tkinter)
│   └── konsol.py                  Terminal sürümü
├── models/                        → Eğitilmiş modeller
│   ├── kalp_modeli.pkl
│   └── belirti_modeli.pkl
├── results/                       → Rapor ve sunum çıktıları
│   ├── figures/                   Grafikler (.png)
│   └── tables/                    Sonuç tabloları (.csv)
├── requirements.txt
└── README.md
```

## Veri akışı

```
raw  ──►  bronze  ──►  silver  ──►  gold  ──►  model  ──►  chatbot
(Kaggle)  (ham kopya)  (temizlik)   (eğitim/test)  (.pkl)    (app/)
```

| Katman | Kalp verisi | Belirti verisi | Yapılan işlem |
|---|---|---|---|
| Raw / Bronze | 918 × 12 | 1200 × 3 | Değiştirilmeden saklanır |
| Silver | 917 × 13 | 1153 × 3 | Gizli eksik değerler, hatalı kayıt, tekrarlar, metin temizleme |
| Gold | 733 + 184 | 922 + 231 | One-Hot Encoding, %80 / %20 eğitim-test ayrımı |

---

## Kurulum

Python 3.10 – 3.12 önerilir.

```bash
cd MedBot
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -c "import nltk; [nltk.download(p) for p in ['punkt','punkt_tab','wordnet','stopwords']]"
```

macOS'ta XGBoost `libomp` hatası verirse: `brew install libomp`

Veri setleri Kaggle'dan indirilip `data/raw/` klasörüne konulmalıdır: `heart.csv`, `Symptom2Disease.csv`.

## Çalıştırma sırası

Notebook'lar sırayla çalıştırılmalıdır; her biri bir öncekinin ürettiği dosyayı kullanır.

| Sıra | Notebook | Ürettiği |
|---|---|---|
| 1 | `01_kalp_veri_analizi` | bronze dosyaları, `silver/heart_silver.csv` |
| 2 | `02_kalp_modelleme` | `gold/heart_*.csv`, `models/kalp_modeli.pkl` |
| 3 | `03_belirti_veri_analizi` | `silver/symptom_silver.csv` |
| 4 | `04_belirti_modelleme` | `gold/symptom_*.csv`, `models/belirti_modeli.pkl` |
| 5 | `05_bilgi_tabani` | `data/chatbot/hastalik_belirtileri.json` |

Ardından chatbot (MedBot klasöründen):

```bash
python app/gui.py        # pencereli arayüz
python app/konsol.py     # terminal sürümü
```

## Chatbotu kullanma

| Kullanıcı yazarsa | MedBot ne yapar? |
|---|---|
| `I have a fever, chills and my body aches` | Belirtilerden en olası 3 hastalığı tahmin eder |
| `I have a headache` | Emin değilse ayırt edici belirtileri sorar |
| `what is malaria?` | Hastalık bilgisi, veri setindeki tipik belirtiler, kaynak |
| `check my heart risk` | 11 soru sorar, kalp hastalığı riskini hesaplar |
| `I think I'm having a heart attack` | Acil durum uyarısı verir (112) |
| `help` | Neler yapabildiğini anlatır |

## Kullanılan yöntemler

- **Veri ön işleme:** gizli eksik değer tespiti (0 değerleri), eksiklik göstergesi, medyan ile doldurma, IQR aykırı değer analizi, One-Hot Encoding, StandardScaler, tekrar eden kayıtların silinmesi
- **Metin işleme:** küçük harf, tokenizasyon, stopword silme (olumsuzluk kelimeleri hariç), lemmatization, TF-IDF
- **Modeller:** Lojistik Regresyon, KNN, SVM, Karar Ağacı, Random Forest, XGBoost, Naive Bayes, Yapay Sinir Ağı (MLP)
- **Değerlendirme:** GridSearchCV, tabakalı k-katlı ve tekrarlı çapraz doğrulama, Accuracy, Precision, Recall, F1-Score, ROC-AUC, Wilcoxon testi, permütasyon önemi
- **Bilgi tabanı:** chi-kare testi ile hastalığa özgü belirtilerin çıkarılması

## Sınırlılıklar

- Kalp modelinde `Cholesterol_eksik` önemli bir özellik çıktı; model veri toplanan hastaneye dair bir izi öğrenmiş olabilir.
- Symptom2Disease metinleri düzgün ve belirti yoğun yazılmıştır; gerçek kullanıcı mesajlarında başarı daha düşük olabilir. Bazı hastalıkların (örn. Migraine) metinleri tipik klinik tabloyla tam örtüşmez.
- Bot olumsuzlukları anlamaz ("I don't have fever" cümlesinde "fever" belirti sayılır).
- Model İngilizce metinlerle eğitildiği için kullanıcı belirtilerini İngilizce yazmalıdır.

## Kaynaklar

- Veri setleri: Kaggle – fedesoriano, *Heart Failure Prediction Dataset*; Kaggle – niyarrbarman, *Symptom2Disease*
- Hastalık bilgileri: [MedlinePlus](https://medlineplus.gov/) (U.S. National Library of Medicine); her hastalığın kaynak sayfası `data/chatbot/hastalik_bilgileri.json` içinde
