import os
import csv
import google.generativeai as genai
from PyPDF2 import PdfReader

# Configure the Gemini API
genai.configure(api_key="AIzaSyD-cwTYMqme-AUG7TMWUxhgjLmChwpn0QE")
model = genai.GenerativeModel("gemini-pro")

def extract_text_from_pdf(pdf_path):
    """Extracts the title and abstract from the first page of a PDF."""
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return text
    except Exception as e:
        print(f"❌ Error reading {pdf_path}: {e}")
        return ""

def classify_paper(title, abstract):
    """Uses Gemini API to classify the research paper into predefined categories."""
    prompt = (
        f"Title: {title}\n"
        f"Abstract: {abstract}\n"
        "Categorize this paper into one of the following: Machine Learning, Computer Vision, Natural Language Processing, Reinforcement Learning, Theory."
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return "Uncategorized"

def process_pdfs(folder_path, output_csv, limit=100):
    """Processes PDFs in the folder, classifies them, and writes the results to a CSV file."""
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")][:limit]
    if not pdf_files:
        print("❌ No PDFs found in the given folder!")
        return
    
    print(f"📂 Processing {len(pdf_files)} PDFs...")
    
    results = []
    for pdf in pdf_files:
        pdf_path = os.path.join(folder_path, pdf)
        text = extract_text_from_pdf(pdf_path)
        if not text:
            continue
        
        title, abstract = text.split("\n", 1) if "\n" in text else (text, "")
        category = classify_paper(title, abstract)
        results.append([pdf, category])
        print(f"✅ {pdf} categorized as: {category}")
    
    with open(output_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Filename", "Category"])
        writer.writerows(results)
    print(f"📄 Results saved to {output_csv}")

# Set your folder path and output CSV file
folder_path = r"H:\Data_Scrapping_Assignment\NeurIPS_1988"
output_csv = r"H:\Data_Scrapping_Assignment\classified_papers.csv"

process_pdfs(folder_path, output_csv, limit=100)
