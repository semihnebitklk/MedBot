"""MedBot'un beyni: gelen mesajı doğru katmana yönlendirir."""
import re
from pathlib import Path

from sohbet import Sohbet
from bilgi_tabani import BilgiTabani
from belirti_tahmin import BelirtiTahmin
from kalp_riski import KalpRiski

KOK = Path(__file__).resolve().parent.parent       # MedBot klasörü

ACIL = re.compile(r"heart attack|stroke|can'?t breathe|cannot breathe|unconscious|suicid|kill myself|severe chest pain", re.I)
KALP = re.compile(r"heart (disease )?risk|check my heart|heart test|kalp", re.I)

ACIL_CEVAP = ("🚨 This may be an emergency. Please call your local emergency number "
              "(112 in Türkiye) or go to the nearest emergency room right now.")
ANLAMADIM = ("I couldn't understand that. Please describe your symptoms in a full sentence, "
             "e.g. 'I have a fever, a headache and my body aches'. Type 'help' to see what I can do.")


class MedBot:
    def __init__(self):
        veri, modeller = KOK / "data" / "chatbot", KOK / "models"
        self.sohbet = Sohbet(veri / "intents.json")
        self.bilgi = BilgiTabani(veri / "hastalik_bilgileri.json", veri / "hastalik_belirtileri.json")
        self.belirti = BelirtiTahmin(modeller / "belirti_modeli.pkl", self.bilgi)
        self.kalp = KalpRiski(modeller / "kalp_modeli.pkl")

    def cevap(self, mesaj):
        mesaj = (mesaj or "").strip()
        if self.kalp.aktif:                      # kalp görüşmesi sürüyorsa cevap ona aittir
            return self.kalp.adim(mesaj)
        if not mesaj:
            return ANLAMADIM
        if ACIL.search(mesaj):                   # güvenlik: acil durum her şeyden önce gelir
            return ACIL_CEVAP
        if KALP.search(mesaj):
            self.belirti.sifirla()
            return self.kalp.baslat()
        if mesaj.lower() in {"reset", "start over"}:
            self.belirti.sifirla()
            return "OK, let's start over. Please describe your symptoms."
        hastalik = self.bilgi.soru_mu(mesaj)     # "what is malaria?" gibi hastalık soruları
        if hastalik:
            self.belirti.sifirla()
            return self.bilgi.hastalik_cevabi(hastalik)
        niyet = self.sohbet.bul(mesaj)           # 1. katman
        if niyet:
            self.belirti.sifirla()
            return self.sohbet.cevap(niyet)
        sonuc = self.belirti.cevap(mesaj)        # 2. katman
        return sonuc if sonuc else ANLAMADIM