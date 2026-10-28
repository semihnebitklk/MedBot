"""1. katman: Sohbet (selamlaşma, teşekkür, veda...). Kural tabanlı eşleştirme."""
import json
import random
import re


class Sohbet:
    def __init__(self, intents_yolu):
        with open(intents_yolu, encoding="utf-8") as f:
            self.intents = json.load(f)["intents"]

    @staticmethod
    def _sadelestir(metin):
        """Küçük harfe çevirir, harf dışı karakterleri boşluk yapar."""
        return " ".join(re.sub(r"[^a-zçğıöşü' ]", " ", metin.lower()).split())

    def bul(self, mesaj):
        """Mesaj bir sohbet kalıbına uyuyorsa niyetin adını, uymuyorsa None döndürür."""
        m = self._sadelestir(mesaj)
        kisa = len(m.split()) <= 5          # uzun cümleler belirti anlatımı olabilir
        for niyet in self.intents:
            for kalip in niyet["patterns"]:
                if m == kalip or (kisa and re.search(rf"\b{re.escape(kalip)}\b", m)):
                    return niyet["tag"]
        return None

    def cevap(self, etiket):
        niyet = next(n for n in self.intents if n["tag"] == etiket)
        return random.choice(niyet["responses"])