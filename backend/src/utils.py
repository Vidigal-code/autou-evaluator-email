import pdfplumber
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer

def extract_text_from_file(file_path):
    if file_path.lower().endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            textos = [page.extract_text() for page in pdf.pages if page.extract_text()]
            return "\n".join(textos) if textos else ""
    elif file_path.lower().endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    return ""

def clean_text(text):
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    try:
        nltk.data.find('stemmers/rslp')
    except LookupError:
        nltk.download('rslp')
    tokens = nltk.word_tokenize(text, language='portuguese')
    stop_words = set(stopwords.words('portuguese'))
    stemmer = RSLPStemmer()
    tokens = [stemmer.stem(token.lower()) for token in tokens if token.isalpha() and token.lower() not in stop_words]
    return ' '.join(tokens)