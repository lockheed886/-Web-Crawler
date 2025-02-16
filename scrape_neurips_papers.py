import requests, re, os, time, argparse
from bs4 import BeautifulSoup
from fpdf import FPDF

# Function to make filenames safe
def safe_filename(text):
    return re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '_')

# Function to download and save paper details as PDF
def save_paper_as_pdf(title, authors, abstract, year, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    filename = safe_filename(title) + ".pdf"
    pdf_path = os.path.join(out_dir, filename)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='', size=12)

    # Write title
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, title, ln=True, align='C')
    pdf.ln(10)

    # Write authors
    pdf.set_font("Arial", style='I', size=12)
    pdf.multi_cell(0, 8, f"Authors: {authors}")
    pdf.ln(5)

    # Write abstract
    pdf.set_font("Arial", style='', size=12)
    pdf.multi_cell(0, 8, f"Abstract: {abstract if abstract else 'No Abstract Available'}")

    pdf.output(pdf_path)
    print(f"Saved PDF: {pdf_path}")

# Function to scrape a single paper
def scrape_paper(url, out_dir, year):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        print(f"Failed {url}: {res.status_code}")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    title_elem = soup.find("h4")
    title = title_elem.get_text(strip=True) if title_elem else "Unknown_Title"

    # Extract authors
    authors_elem = soup.find("h4", string="Authors")
    authors = authors_elem.find_next("p").get_text(strip=True) if authors_elem else "Unknown Authors"

    # Extract abstract
    abstract_elem = soup.find("h4", string="Abstract")
    abstract = abstract_elem.find_next("p").get_text(strip=True) if abstract_elem else "No Abstract Available"

    # Save the paper details in a PDF
    save_paper_as_pdf(title, authors, abstract, year, out_dir)

# Function to get all paper links for a given year
def get_paper_links(year):
    base_url = f"https://papers.nips.cc/paper_files/paper/{year}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(base_url, headers=headers)

    if res.status_code != 200:
        print(f"Failed to fetch index for {year}: {res.status_code}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    return ["https://papers.nips.cc" + a["href"] for a in soup.find_all("a", href=True) if "hash" in a["href"]]

# Main script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape NeurIPS papers")
    parser.add_argument("--start", type=int, required=True, help="Start year")
    parser.add_argument("--end", type=int, required=True, help="End year")
    args = parser.parse_args()

    for year in range(args.start, args.end + 1):
        print(f"\n=== Scraping Year {year} ===")
        out_dir = os.path.join("H:/Data_Scrapping_Assignment", f"NeurIPS_{year}")
        links = get_paper_links(year)

        if not links:
            print(f"No papers found for {year}")
            continue

        for i, link in enumerate(links, 1):
            print(f"\nPaper {i}/{len(links)} for {year}: {link}")
            try:
                scrape_paper(link, out_dir, year)
            except Exception as e:
                print(f"Error processing {link}: {e}")

            time.sleep(1)  # Pause to avoid overloading the server
