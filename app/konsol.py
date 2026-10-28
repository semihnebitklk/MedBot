"""MedBot – terminal sürümü (test için).  Çalıştırma:  python app/konsol.py"""
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from medbot import MedBot

bot = MedBot()
print("MedBot is ready. Type 'quit' to exit.\n")
while True:
    try:
        mesaj = input("You: ")
    except (EOFError, KeyboardInterrupt):
        break
    if mesaj.strip().lower() == "quit":
        break
    print("MedBot:", bot.cevap(mesaj), "\n")