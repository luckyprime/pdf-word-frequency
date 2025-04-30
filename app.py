import streamlit as st
import nltk
import PyPDF2
from pdf2image import convert_from_bytes
import pytesseract
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter
import io

# --- NLTK Data Setup ---
@st.cache_resource
def download_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

download_nltk_data()
STOPWORDS = set(stopwords.words('english'))

# --- PDF Text Extraction using PyPDF2 ---
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.getvalue()))
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        st.warning(f"PyPDF2 error: {e}")
        return ""
    return text.strip()

# --- OCR Fallback using pytesseract ---
def ocr_pdf(pdf_file):
    try:
        images = convert_from_bytes(pdf_file.getvalue())
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        st.error(f"OCR failed: {e}")
        return ""

# --- Text Cleaning & Tokenization ---
def process_text(text):
    text = text.lower()
    sentences = sent_tokenize(text)
    all_tokens = []
    for sentence in sentences:
        tokens = word_tokenize(sentence)
        all_tokens.extend(tokens)
    return [word for word in all_tokens if word.isalpha() and word not in STOPWORDS]

# --- Streamlit UI ---
st.title("PDF Word Frequency Analyzer")
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    st.info("Extracting text from PDF...")
    text = extract_text_from_pdf(uploaded_file)

    if not text:
        st.warning("No text found via PyPDF2. Attempting OCR...")
        text = ocr_pdf(uploaded_file)

    if text:
        st.subheader("Extracted Text Preview")
        st.text(text[:1000] + ("..." if len(text) > 1000 else ""))

        st.info("Processing text...")
        tokens = process_text(text)

        if tokens:
            word_counts = Counter(tokens)
            num_display = st.slider("Number of top words to display", 10, 100, 20)

            st.subheader("Top Word Frequencies")
            st.dataframe([
                {"Word": word, "Frequency": freq}
                for word, freq in word_counts.most_common(num_display)
            ])

            st.write(f"Total unique words: {len(word_counts)}")
            st.write(f"Total words (after cleaning): {len(tokens)}")
        else:
            st.warning("No valid words found in the extracted text.")
    else:
        st.error("Failed to extract any text from the PDF.")

st.markdown("---")
st.markdown("App powered by Streamlit, NLTK, PyPDF2, pdf2image, and pytesseract.")
