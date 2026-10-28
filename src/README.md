# src/

Chatbotun mantığı burada, arayüzler `app/` klasöründedir. Böylece arayüz değişse de beyin aynı kalır.

| Dosya               | Görevi                                                                                                               |
| ------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `medbot.py`         | Gelen mesajı sırayla kontrol edip doğru katmana yönlendirir                                                          |
| `sohbet.py`         | 1. katman: selamlaşma, teşekkür, yardım (kural tabanlı)                                                              |
| `belirti_tahmin.py` | 2. katman: belirtileri biriktirir, `belirti_modeli.pkl` ile tahmin yapar, emin değilse ayırt edici belirtileri sorar |
| `bilgi_tabani.py`   | Hastalık bilgilerini ve veriden çıkarılan belirtileri yönetir, "what is X?" sorularını cevaplar                      |
| `kalp_riski.py`     | 3. katman: 11 soru sorar, cevapları modelin sütunlarına çevirir, `kalp_modeli.pkl` ile risk hesaplar                 |
| `metin_isleme.py`   | Notebook'larda ve chatbotta ortak kullanılan metin temizleme fonksiyonu                                              |

## Bir mesajın yolculuğu (`medbot.py`)

1. Kalp anketi sürüyorsa → cevap ankete gider
2. Acil durum ifadesi varsa ("heart attack", "can't breathe") → 112 uyarısı
3. Kalp riski isteniyorsa → anket başlar
4. Bir hastalık soruluyorsa ("what is malaria?") → bilgi tabanı cevaplar
5. Sohbet kalıbına uyuyorsa ("hi", "thanks") → hazır cevap
6. Belirti anlatımıysa → hastalık tahmini (gerekirse takip sorusu)
7. Hiçbiri değilse → "anlamadım, daha detaylı anlatın"
