"""Hastalık bilgi tabanı: kaynaklı hastalık bilgileri + veri setinden çıkarılan ayırt edici belirtiler."""
import json
import re

# Kullanıcının hastalıklara verebileceği farklı isimler → veri setindeki etiket
TAKMA_ADLAR = {
    "acne": "Acne", "pimples": "Acne",
    "allergy": "Allergy", "allergies": "Allergy",
    "arthritis": "Arthritis",
    "asthma": "Bronchial Asthma", "bronchial asthma": "Bronchial Asthma",
    "cervical spondylosis": "Cervical Spondylosis", "spondylosis": "Cervical Spondylosis",
    "chicken pox": "Chicken Pox", "chickenpox": "Chicken Pox",
    "common cold": "Common Cold", "a cold": "Common Cold",
    "dengue": "Dengue",
    "diabetes": "Diabetes",
    "hemorrhoids": "Dimorphic Hemorrhoids", "haemorrhoids": "Dimorphic Hemorrhoids", "piles": "Dimorphic Hemorrhoids",
    "drug reaction": "Drug Reaction", "drug allergy": "Drug Reaction",
    "fungal infection": "Fungal Infection", "fungal": "Fungal Infection",
    "gerd": "Gastroesophageal Reflux Disease", "reflux": "Gastroesophageal Reflux Disease",
    "gastroesophageal reflux disease": "Gastroesophageal Reflux Disease",
    "hypertension": "Hypertension", "high blood pressure": "Hypertension",
    "impetigo": "Impetigo",
    "jaundice": "Jaundice",
    "malaria": "Malaria",
    "migraine": "Migraine",
    "peptic ulcer": "Peptic Ulcer Disease", "ulcer": "Peptic Ulcer Disease",
    "pneumonia": "Pneumonia",
    "psoriasis": "Psoriasis",
    "typhoid": "Typhoid",
    "uti": "Urinary Tract Infection", "urinary tract infection": "Urinary Tract Infection",
    "bladder infection": "Urinary Tract Infection",
    "varicose veins": "Varicose Veins", "varicose": "Varicose Veins",
}
SORU = re.compile(r"\b(what is|what's|what are|tell me about|symptoms? of|signs of|prevent|treat|treatment|"
                  r"cure|explain|information|info|about)\b", re.I)


class BilgiTabani:
    def __init__(self, bilgi_yolu, belirti_yolu):
        with open(bilgi_yolu, encoding="utf-8") as f:
            self.hastaliklar = {h["name"]: h for h in json.load(f)["diseases"]}
        with open(belirti_yolu, encoding="utf-8") as f:
            self.belirtiler = json.load(f)

    def tipik_belirtiler(self, hastalik):
        """Veri setinden çıkarılan, okunabilir adı olan ayırt edici belirtiler."""
        return [b for b in self.belirtiler.get(hastalik, []) if b["belirti"]]

    def soru_mu(self, mesaj):
        """Mesaj bir hastalık hakkında soruysa hastalığın adını döndürür (örn. 'what is malaria?')."""
        m = mesaj.lower()
        bulunan = None
        for takma, ad in sorted(TAKMA_ADLAR.items(), key=lambda x: -len(x[0])):   # uzun isimler önce
            if re.search(rf"\b{re.escape(takma)}\b", m):
                bulunan = ad
                break
        if bulunan and (SORU.search(m) or len(m.split()) <= 3):
            return bulunan
        return None

    def ayirt_edici_sorular(self, adaylar, anlatilan, n=2):
        """Aday hastalıkları birbirinden ayıran, kullanıcının henüz söylemediği belirtiler."""
        anlatilan = set(anlatilan.split())
        secilen = []
        for hastalik in adaylar:
            yeni = [b["belirti"] for b in self.tipik_belirtiler(hastalik)
                    if not set(b["terim"].split()) & anlatilan and b["belirti"] not in secilen]
            secilen += yeni[:n]                 # her aday hastalıktan en fazla n belirti
        return secilen

    def hastalik_cevabi(self, ad):
        h = self.hastaliklar[ad]
        tipik = self.tipik_belirtiler(ad)
        satirlar = [f"📘 {ad}", h["description"], ""]
        if tipik:
            satirlar.append("Most characteristic symptoms in our dataset:")
            satirlar += [f"  • {b['belirti']} (in {b['oran'] * 100:.0f}% of {ad} descriptions)" for b in tipik[:4]]
        satirlar += ["What you can do:"] + [f"  • {t}" for t in h["advice"]]
        satirlar += ["⚠️ Seek urgent care if you have:"] + [f"  • {t}" for t in h["red_flags"]]
        satirlar += [f"When to see a doctor: {h['see_doctor']}", f"Source: {h['source']}"]
        return "\n".join(satirlar)