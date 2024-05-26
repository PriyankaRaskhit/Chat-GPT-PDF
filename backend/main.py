# main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline, AutoTokenizer
import os
import PyPDF2
import re

app = FastAPI()

# Allow CORS for all origins (to be more restrictive, specify allowed origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the local model
generator = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad", tokenizer="bert-large-uncased-whole-word-masking-finetuned-squad")

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def preprocess_text(text):
    # Remove special characters and extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def get_answer_context(text, start_idx, end_idx, context_window=500):
    # Extract the context around the answer span
    start_context_idx = max(0, start_idx - context_window)
    end_context_idx = min(len(text), end_idx + context_window)
    return text[start_context_idx:end_context_idx]

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        with open("temp.pdf", "wb") as temp_pdf:
            temp_pdf.write(await file.read())
        return {"message": "PDF uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/ask_question/")
async def ask_question(file: UploadFile = File(...), question: str = Form(...)):
    try:
        # Save the uploaded file temporarily
        with open("temp.pdf", "wb") as temp_pdf:
            temp_pdf.write(await file.read())
        
        # Extract text from the uploaded PDF
        pdf_text = extract_text_from_pdf("temp.pdf")
        
        # Preprocess the text
        pdf_text = preprocess_text(pdf_text)
        
        # Ask a question about the text from the PDF
        response = generator(question=question, context=pdf_text)
        
        # Get the start and end indices of the answer
        start_idx = response["start"]
        end_idx = response["end"]
        
        # Get the context around the answer span
        answer_context = get_answer_context(pdf_text, start_idx, end_idx)
        
        # Delete the temporary PDF file
        os.remove("temp.pdf")

        return {"answer": answer_context}
    except Exception as e:
        return {"error": str(e)}
