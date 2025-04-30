import streamlit as st
from pdf2image import convert_from_path
import pytesseract
from nltk.tokenize import word_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer
from collections import Counter
from itertools import tee, islice
import nltk
import tempfile
import os

# Set up and ensure punkt is downloaded
nltk_data_path = os.path.join(os.path.dirname(__file__), "nltk_data")
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", download_dir=nltk_data_path)

# N-gram helper
def ngrams(tokens, n):
    return zip(*[islice(seq, i, None) for i, seq in enumerate(tee(tokens, n))])

def find_frequent_sequences(tokens, min_length=2, max_length=3, min_freq=2):
    frequent_sequences = Counter()
    for n in range(min_length, max_length + 1):
        for seq in ngrams(tokens, n):
            frequent_sequences[seq] += 1
    return {seq: freq for seq, freq in frequent_sequences.items() if freq >= min_freq}

# OCR handler
def ocr_pdf(uploaded_pdf):
    with tempfile.TemporaryDirectory() as path:
        temp_pdf = os.path.join(path, "temp.pdf")
        with open(temp_pdf, "wb") as f:
            f.write(uploaded_pdf.read())
        images = convert_from_path(temp_pdf)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return text

# Streamlit UI
st.title("PDF Word Frequency Analyzer")
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    text = ocr_pdf(uploaded_file)

    # Tokenization
    sentence_tokenizer = PunktSentenceTokenizer()
    sentences = sentence_tokenizer.tokenize(text)

    tokens = []
    for sentence in sentences:
        tokens.extend(word_tokenize(sentence))

    tokens = [t.lower() for t in tokens if t.isalpha()]
    frequent_compounds = find_frequent_sequences(tokens)

    word_counts = Counter(tokens)
    for compound, freq in frequent_compounds.items():
        term = ' '.join(compound)
        word_counts[term] = freq
        for word in compound:
            if word_counts[word] > 0:
                word_counts[word] -= freq

    sorted_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    st.subheader("Word Frequencies")
    for word, count in sorted_counts:
        if count > 0:
            st.write(f"{word}: {count}")
