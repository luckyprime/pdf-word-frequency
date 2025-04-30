import streamlit as st
import nltk
import PyPDF2
import re
from collections import Counter
import io # To handle the uploaded file in memory

# --- NLTK Data Download Function ---
# Use st.cache_resource to download NLTK data only once per session.
# This is crucial for deployment platforms where NLTK data is not pre-installed.
@st.cache_resource
def download_nltk_data():
    """Downloads the NLTK 'punkt' tokenizer data and stopwords."""
    try:
        # Check if punkt is already available
        nltk.data.find('tokenizers/punkt')
        st.success("NLTK 'punkt' tokenizer data found.")
    except (nltk.downloader.DownloadError, LookupError):
        st.warning("NLTK 'punkt' tokenizer data not found. Downloading now...")
        nltk.download('punkt')
        st.success("NLTK 'punkt' tokenizer data downloaded.")

    try:
        # Check if stopwords are already available
        nltk.data.find('corpora/stopwords')
        st.success("NLTK stopwords data found.")
    except (nltk.downloader.DownloadError, LookupError):
        st.warning("NLTK stopwords data not found. Downloading now...")
        nltk.download('stopwords')
        st.success("NLTK stopwords data downloaded.")

# --- Call the download function before using NLTK ---
# This ensures the data is downloaded and available when needed.
download_nltk_data()

# Now you can safely import and use NLTK resources
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

# Get English stopwords
STOPWORDS = set(stopwords.words('english'))

# --- PDF Text Extraction Function ---
def extract_text_from_pdf(pdf_file):
    """
    Extracts text from an uploaded PDF file using PyPDF2.
    Returns the extracted text as a single string.
    """
    text = ""
    try:
        # Use io.BytesIO to read the file from memory
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.getvalue()))
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() or "" # Add extracted text, handle None case
    except Exception as e:
        st.error(f"Error processing PDF with PyPDF2: {e}")
        return None
    return text

# --- OCR Placeholder Function (Requires Tesseract Installation) ---
# Note: Implementing OCR requires installing Tesseract-OCR on the system
# where the Streamlit app is deployed. This is more complex than just
# adding a Python library. You'd also need a Python wrapper like 'pytesseract'.
# This function is a placeholder to show where OCR logic would go.
# If your PDFs are image-based, you'll need to implement this.
# def ocr_pdf(pdf_file):
#     """
#     Performs OCR on a PDF file (placeholder).
#     Requires Tesseract-OCR installation.
#     """
#     st.warning("OCR functionality requires Tesseract-OCR installation and implementation.")
#     return None # Return None as placeholder

# --- Text Cleaning and Tokenization Function ---
def process_text(text):
    """
    Cleans text, tokenizes into words, removes stopwords and punctuation.
    Returns a list of cleaned tokens.
    """
    if not text:
        return []

    # Lowercase the text
    text = text.lower()

    # Tokenize into sentences (using sent_tokenize which caused the error)
    # This should now work after the cached download
    sentences = sent_tokenize(text)

    all_tokens = []
    for sentence in sentences:
        # Tokenize into words
        tokens = word_tokenize(sentence)
        all_tokens.extend(tokens)

    # Clean tokens: remove punctuation and stopwords
    cleaned_tokens = [
        word for word in all_tokens
        if word.isalpha() and word not in STOPWORDS
    ]

    return cleaned_tokens

# --- Streamlit App Layout ---
st.title("PDF Word Frequency Counter")

st.write("Upload a PDF file to analyze the frequency of words.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Option to choose processing method (simple text extraction vs OCR)
    # For now, we only have simple text extraction implemented
    # processing_method = st.radio("Select Processing Method:", ("Simple Text Extraction", "OCR (Not Implemented)"))

    st.info("Extracting text from the PDF...")
    text = extract_text_from_pdf(uploaded_file)

    # If text extraction fails or returns empty, you might try OCR here
    # if not text and processing_method == "OCR (Not Implemented)":
    #     st.info("Attempting OCR...")
    #     text = ocr_pdf(uploaded_file) # Call OCR function

    if text:
        st.subheader("Extracted Text (Preview)")
        # Display a preview of the extracted text
        st.text(text[:1000] + ("..." if len(text) > 1000 else ""))

        st.info("Processing text and counting word frequency...")
        cleaned_tokens = process_text(text)

        if cleaned_tokens:
            # Count word frequencies
            word_counts = Counter(cleaned_tokens)

            st.subheader("Word Frequency")

            # Display the most common words
            num_words_to_display = st.slider("Number of top words to display", 10, 100, 20)

            st.write(f"Top {num_words_to_display} words:")
            # Convert Counter output to a list of dictionaries for better display
            word_count_list = [{"Word": word, "Frequency": count} for word, count in word_counts.most_common(num_words_to_display)]
            st.dataframe(word_count_list)

            # Optional: Display total unique words and total words
            st.write(f"Total unique words (after cleaning): {len(word_counts)}")
            st.write(f"Total words (after cleaning): {len(cleaned_tokens)}")

        else:
            st.warning("No meaningful words found after processing.")

    else:
        st.error("Failed to extract text from the PDF.")

# Add any footer or additional information
st.markdown("---")
st.markdown("App powered by Streamlit, NLTK, and PyPDF2.")

