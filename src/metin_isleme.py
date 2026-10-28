"""Metin ön işleme fonksiyonları. Hem notebook'larda hem chatbotta kullanılır."""
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

_lemmatizer = WordNetLemmatizer()

# "no", "not" gibi olumsuzluk kelimeleri tutulur: "no fever" ile "fever" farklı anlamdadır
_OLUMSUZ = {"no", "not", "nor", "without", "never"}
_STOPWORDS = set(stopwords.words("english")) - _OLUMSUZ


def temizle(metin):
    """Küçük harf → kelimelere ayırma → harf dışı karakterleri atma → stopword silme → kök bulma."""
    metin = str(metin).lower()
    kelimeler = nltk.word_tokenize(metin)
    kelimeler = [k for k in kelimeler if re.fullmatch(r"[a-z]+", k)]
    kelimeler = [k for k in kelimeler if k not in _STOPWORDS]
    kelimeler = [_lemmatizer.lemmatize(k) for k in kelimeler]
    return " ".join(kelimeler)


def toplu_temizle(metinler):
    """Bir metin listesini temizler (modelin pipeline'ında kullanılacak)."""
    return [temizle(m) for m in metinler]