"""2. katman: Belirti → hastalık tahmini (Symptom2Disease ile eğitilmiş model).

Bot belirtileri birkaç mesaj boyunca biriktirir. Model yeterince emin değilse,
aday hastalıkları birbirinden ayıran belirtileri (veri setinden çıkarılan) sorar.
"""
import joblib
from metin_isleme import temizle

ACILIYET = {"low": "🟢 Low", "medium": "🟡 Medium", "high": "🔴 High"}
BITTI = {"none", "no", "nope", "nothing", "nothing else", "no others", "that's all", "thats all", "no more"}


class BelirtiTahmin:
    def __init__(self, model_yolu, bilgi_tabani, guven_esigi=0.45, max_tur=3):
        self.model = joblib.load(model_yolu)["model"]
        self.sozluk = self.model.named_steps["tfidf"].vocabulary_   # modelin bildiği kelimeler
        self.bilgi = bilgi_tabani
        self.guven_esigi = guven_esigi      # en olası hastalığın olasılığı bunun altındaysa daha fazla belirti iste
        self.max_tur = max_tur              # en fazla kaç mesaj belirti toplanacak
        self.biriken = []                   # bu görüşmede şimdiye kadar anlatılan belirtiler

    @property
    def aktif(self):
        return bool(self.biriken)

    def sifirla(self):
        self.biriken = []

    def bilinen_kelimeler(self, mesaj):
        """Mesajdaki, modelin eğitimde gördüğü kelimeler."""
        return {k for k in temizle(mesaj).split() if k in self.sozluk}

    def tahmin(self, metin, n=3):
        """En olası n hastalığı (ad, olasılık) listesi olarak döndürür."""
        olasilik = self.model.predict_proba([metin])[0]
        sira = olasilik.argsort()[::-1][:n]
        return [(self.model.classes_[i], float(olasilik[i])) for i in sira]

    def cevap(self, mesaj):
        """Belirti anlatımıysa cevap metni, değilse None döndürür."""
        temiz = mesaj.strip().lower().rstrip(".!")
        if self.aktif and (temiz in BITTI or not self.bilinen_kelimeler(mesaj)):
            return self._bitir()                # kullanıcının ekleyecek belirtisi yok: eldekiyle sonuç ver
        if not self.bilinen_kelimeler(mesaj):
            return None

        self.biriken.append(mesaj)
        tum_metin = " ".join(self.biriken)      # tüm belirtiler birlikte değerlendirilir
        sonuc = self.tahmin(tum_metin)
        if sonuc[0][1] >= self.guven_esigi or len(self.biriken) >= self.max_tur:
            return self._bitir(sonuc)

        sorular = self.bilgi.ayirt_edici_sorular([ad for ad, _ in sonuc], temizle(tum_metin))
        return ("Your symptoms could match several conditions, so I need a bit more information.\n"
                "Do you also have any of these?\n" + "\n".join(f"  • {s}" for s in sorular) +
                "\nType the symptoms you have (or anything else you feel), or 'none'.")

    def _bitir(self, sonuc=None):
        sonuc = sonuc or self.tahmin(" ".join(self.biriken))
        self.sifirla()
        ad, olasilik = sonuc[0]
        h = self.bilgi.hastaliklar[ad]
        satirlar = []
        if olasilik < self.guven_esigi:
            satirlar.append("⚠️ I'm not very confident; your symptoms are common to several conditions.")
        satirlar.append("Based on your symptoms, the most likely conditions are:")
        satirlar += [f"  {i}. {a}  ({p * 100:.0f}%)" for i, (a, p) in enumerate(sonuc, 1)]
        satirlar += ["", f"About {ad}: {h['description']}", "What you can do:"]
        satirlar += [f"  • {t}" for t in h["advice"]]
        satirlar += ["⚠️ Seek urgent care if you have: " + "; ".join(h["red_flags"]),
                     f"Urgency: {ACILIYET[h['urgency']]}",
                     f"Source: {h['source']}",
                     f"(Type 'what is {ad.lower()}' to learn more.)"]
        return "\n".join(satirlar)