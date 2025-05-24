import os
import pdfplumber
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer

# ------------------ SRP: FileReader Interface ------------------
class FileReader:
    def can_read(self, file_path: str) -> bool:
        raise NotImplementedError

    def extract_text(self, file_path: str) -> str:
        raise NotImplementedError

# ------------------ PDF Reader ------------------
class PDFReader(FileReader):
    def can_read(self, file_path: str) -> bool:
        return file_path.lower().endswith(".pdf")

    def extract_text(self, file_path: str) -> str:
        with pdfplumber.open(file_path) as pdf:
            texts = [page.extract_text() for page in pdf.pages if page.extract_text()]
            return "\n".join(texts) if texts else ""

# ------------------ TXT Reader ------------------
class TXTReader(FileReader):
    def can_read(self, file_path: str) -> bool:
        return file_path.lower().endswith(".txt")

    def extract_text(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

# ------------------ SRP: TextCleaner ------------------
class TextCleaner:
    def __init__(self):
        self._ensure_nltk_resources()
        self.stop_words = set(stopwords.words("portuguese"))
        self.stemmer = RSLPStemmer()

    def _ensure_nltk_resources(self):
        for resource in ["punkt", "stopwords", "rslp"]:
            try:
                nltk.data.find(f"tokenizers/{resource}" if resource == "punkt" else f"corpora/{resource}")
            except LookupError:
                nltk.download(resource)

    def clean(self, text: str) -> str:
        tokens = nltk.word_tokenize(text, language="portuguese")
        stemmed = [
            self.stemmer.stem(token.lower())
            for token in tokens
            if token.isalpha() and token.lower() not in self.stop_words
        ]
        return " ".join(stemmed)

# ------------------ OCP: FileProcessor ------------------
class FileProcessor:
    def __init__(self, readers: list[FileReader], cleaner: TextCleaner):
        self.readers = readers
        self.cleaner = cleaner

    def process(self, file_path: str) -> str:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        reader = next((r for r in self.readers if r.can_read(file_path)), None)
        if not reader:
            raise ValueError(f"Formato de arquivo não suportado: {file_path}")

        text = reader.extract_text(file_path)
        return self.cleaner.clean(text) if text else ""
