"""MedBot – pencereli arayüz.  Çalıştırma:  python app/gui.py"""
import sys
import tkinter as tk
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from medbot import MedBot

KARSILAMA = ("Hello! I'm MedBot, your AI health assistant.\n"
             "• Describe your symptoms in a sentence, e.g. 'I have a fever and my body aches'\n"
             "• Type 'check my heart risk' for a heart disease risk estimate\n"
             "I am not a doctor; always consult a professional for medical decisions.")


class MedBotArayuz:
    def __init__(self, pencere):
        self.bot = MedBot()
        pencere.title("MedBot – AI Health Assistant")
        pencere.geometry("620x680")

        self.sohbet = tk.Text(pencere, wrap="word", state="disabled", padx=10, pady=10,
                              font=("Helvetica", 13), bg="#FAFAFA", relief="flat")
        self.sohbet.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self.sohbet.tag_config("kullanici", foreground="#1F5FAD", font=("Helvetica", 13, "bold"))
        self.sohbet.tag_config("bot", foreground="#222222")

        alt = tk.Frame(pencere)
        alt.pack(fill="x", padx=8, pady=(4, 8))
        self.giris = tk.Entry(alt, font=("Helvetica", 13))
        self.giris.pack(side="left", fill="x", expand=True, ipady=6)
        self.giris.bind("<Return>", self.gonder)
        tk.Button(alt, text="Send", command=self.gonder, width=8).pack(side="left", padx=(6, 0))
        self.giris.focus()

        self.yaz("MedBot", KARSILAMA, "bot")

    def yaz(self, kim, metin, etiket):
        self.sohbet.config(state="normal")
        self.sohbet.insert("end", f"{kim}: ", etiket)
        self.sohbet.insert("end", metin + "\n\n", "bot")
        self.sohbet.config(state="disabled")
        self.sohbet.see("end")

    def gonder(self, _olay=None):
        mesaj = self.giris.get().strip()
        if not mesaj:
            return
        self.giris.delete(0, "end")
        self.yaz("You", mesaj, "kullanici")
        try:
            cevap = self.bot.cevap(mesaj)
        except Exception as hata:          # beklenmeyen bir hata arayüzü çökertmesin
            cevap = f"Sorry, something went wrong ({hata})."
        self.yaz("MedBot", cevap, "bot")


if __name__ == "__main__":
    pencere = tk.Tk()
    MedBotArayuz(pencere)
    pencere.mainloop()