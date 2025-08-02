import os
import difflib
import requests
import pdfplumber
from docx import Document

# -------- FILE READING FUNCTIONS -------- #

def read_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def read_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def read_file(path):
    ext = os.path.splitext(path)[1]
    if ext == '.txt':
        return read_txt(path)
    elif ext == '.pdf':
        return read_pdf(path)
    elif ext == '.docx':
        return read_docx(path)
    else:
        raise ValueError("Unsupported file type: " + ext)

# -------- TEXT COMPARISON -------- #

def compare_texts(text1, text2):
    d = difflib.unified_diff(
        text1.splitlines(),
        text2.splitlines(),
        lineterm='',
        n=0
    )
    return "\n".join(list(d))

# -------- GPT SUMMARIZATION -------- #

def summarize_differences(differences_text):
    prompt = (
        "You are a helpful assistant. The following is a line-by-line diff between two versions of a document. "
        "Summarize the key changes clearly and concisely in bullet points:\n\n"
        f"{differences_text}"
    )

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",  # Or "llama3", "phi3", etc.
        "prompt": prompt,
        "stream": False
    })

    return response.json()['response']

# -------- MAIN WORKFLOW -------- #

def main():
    file1 = 'files/doc1.pdf'  # Change to your actual file path
    file2 = 'files/doc2.pdf'  # Change to your actual file path

    print("[✓] Reading files...")
    text1 = read_file(file1)
    text2 = read_file(file2)

    print("[✓] Comparing documents...")
    diff = compare_texts(text1, text2)

    print("[✓] Summarizing differences using mistralAI...")
    summary = summarize_differences(diff)

    with open("comparison_summary.txt", "w", encoding='utf-8') as f:
        f.write(summary)

    print("[✓] Summary saved to 'comparison_summary.txt'.")

if __name__ == "__main__":
    main()
