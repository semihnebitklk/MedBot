"""3. katman: Kalp hastalığı risk tahmini (Heart Failure Prediction ile eğitilmiş XGBoost)."""
import joblib
import numpy as np
import pandas as pd

# (sütun adı, soru, tip, kural)
#   sayi  → kural = (min, max)
#   secim → kural = {kullanıcı cevabı: veri setindeki değer}
SORULAR = [
    ("Age", "How old are you?", "sayi", (18, 100)),
    ("Sex", "What is your sex?\n  1) Male\n  2) Female", "secim", {"1": "M", "2": "F"}),
    ("ChestPainType", "Which describes your chest pain best?\n"
     "  1) Typical angina (chest pressure during effort, relieved by rest)\n"
     "  2) Atypical angina\n  3) Non-anginal pain (not related to the heart)\n  4) No chest pain",
     "secim", {"1": "TA", "2": "ATA", "3": "NAP", "4": "ASY"}),
    ("RestingBP", "What is your resting blood pressure (upper value, mm Hg)? e.g. 120", "sayi", (80, 220)),
    ("Cholesterol", "What is your cholesterol (mg/dl)? e.g. 200  (type 'unknown' if you don't know)", "sayi", (100, 650)),
    ("FastingBS", "Is your fasting blood sugar above 120 mg/dl?\n  1) Yes\n  2) No", "secim", {"1": 1, "2": 0}),
    ("RestingECG", "What was your resting ECG result?\n  1) Normal\n  2) ST-T wave abnormality\n  3) Left ventricular hypertrophy",
     "secim", {"1": "Normal", "2": "ST", "3": "LVH"}),
    ("MaxHR", "What is the maximum heart rate you reached during an exercise test? e.g. 150", "sayi", (60, 220)),
    ("ExerciseAngina", "Do you get chest pain during exercise?\n  1) Yes\n  2) No", "secim", {"1": "Y", "2": "N"}),
    ("Oldpeak", "ST depression during exercise (oldpeak)? e.g. 1.0", "sayi", (-3, 7)),
    ("ST_Slope", "Slope of the ST segment at peak exercise?\n  1) Up\n  2) Flat\n  3) Down",
     "secim", {"1": "Up", "2": "Flat", "3": "Down"}),
]

UYARI = ("\n\n⚠️ This is a statistical estimate from a model trained on 917 patients, "
         "not a medical diagnosis. Please consult a doctor.")


class KalpRiski:
    def __init__(self, model_yolu):
        paket = joblib.load(model_yolu)
        self.model, self.sutunlar = paket["model"], paket["sutunlar"]
        self.cevaplar = None          # None: görüşme yok, sözlük: görüşme sürüyor

    @property
    def aktif(self):
        return self.cevaplar is not None

    def baslat(self):
        self.cevaplar = {}
        return ("Let's estimate your heart disease risk. I'll ask 11 questions; "
                "the answers come from your medical check-up. Type 'cancel' to stop anytime.\n\n" + SORULAR[0][1])

    def adim(self, mesaj):
        """Kullanıcının cevabını işler, bir sonraki soruyu ya da sonucu döndürür."""
        mesaj = mesaj.strip().lower().replace(",", ".")
        if mesaj in {"cancel", "stop", "iptal"}:
            self.cevaplar = None
            return "Heart risk check cancelled. How else can I help you?"

        ad, soru, tip, kural = SORULAR[len(self.cevaplar)]
        deger = self._dogrula(ad, mesaj, tip, kural)
        if deger is None:
            ipucu = f"a number between {kural[0]} and {kural[1]}" if tip == "sayi" else "one of the numbered options"
            return f"Sorry, please enter {ipucu}.\n\n{soru}"

        self.cevaplar[ad] = deger
        if len(self.cevaplar) < len(SORULAR):
            return SORULAR[len(self.cevaplar)][1]
        sonuc = self.hesapla(self.cevaplar)
        self.cevaplar = None
        return sonuc

    @staticmethod
    def _dogrula(ad, metin, tip, kural):
        if tip == "secim":
            return kural.get(metin)
        if ad == "Cholesterol" and metin in {"unknown", "?", "bilmiyorum"}:
            return np.nan
        try:
            x = float(metin)
        except ValueError:
            return None
        return x if kural[0] <= x <= kural[1] else None

    def _satir_hazirla(self, c):
        """Kullanıcı cevaplarını modelin beklediği gold sütunlarına çevirir (One-Hot dahil)."""
        satir = dict.fromkeys(self.sutunlar, 0)
        for ad in ["Age", "RestingBP", "Cholesterol", "FastingBS", "MaxHR", "Oldpeak"]:
            satir[ad] = c[ad]
        satir["Cholesterol_eksik"] = int(pd.isna(c["Cholesterol"]))
        for ad in ["Sex", "ChestPainType", "RestingECG", "ExerciseAngina", "ST_Slope"]:
            satir[f"{ad}_{c[ad]}"] = 1
        return pd.DataFrame([satir])[self.sutunlar]

    def hesapla(self, cevaplar):
        p = float(self.model.predict_proba(self._satir_hazirla(cevaplar))[0, 1])
        if p < 0.3:
            seviye, oneri = "🟢 LOW", "Keep up a healthy lifestyle and have regular check-ups."
        elif p < 0.6:
            seviye, oneri = "🟡 MODERATE", "It would be wise to discuss these results with a cardiologist."
        else:
            seviye, oneri = "🔴 HIGH", "Please make an appointment with a cardiologist as soon as possible."
        return f"Estimated heart disease probability: {p * 100:.0f}%  →  {seviye} risk.\n{oneri}{UYARI}"