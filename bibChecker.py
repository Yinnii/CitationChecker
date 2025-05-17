import bibtexparser
import requests
import time
import csv
import argparse


def load_bibtex_file(file_path):
    with open(file_path, 'r') as bib_file:
        return bibtexparser.load(bib_file)

def save_bibtex_file(bib_database, file_path):
    with open(file_path, 'w') as bib_file:
        bibtexparser.dump(bib_database, bib_file)

def check_paper(paper_title):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search/match?query={paper_title}&fields=title,publicationVenue,year,externalIds,journal,venue,publicationDate,url"
    results = requests.get(url).json()
    if results:
    # check if any paper does not contain arXiv in venue
      for paper in results["data"]: 
          try:
            journal_name = paper.get("journal").get("name", "")
          except AttributeError:
            journal_name = paper.get("venue")
          if ("arXiv" not in paper["venue"]) and ("ArXiv" not in journal_name) and ("arXiv" not in paper["externalIds"].get("DOI", "")):
              print(f"✅ Published version found in journal: {journal_name} with DOI: {paper['externalIds'].get('DOI', '')}")
              return paper
    else:
        print("Nothing found with semantic scholar.")
        return None

def process_bib_file(input_path, output_path, csv_path, delay):
    bib_data = load_bibtex_file(input_path)
    results = []

    for entry in bib_data.entries:
        if "doi" in entry and "arXiv" in entry["doi"]:
            title = entry.get("title", "")
            print(f"\n🔍 Processing entry: {title}")
            published = check_paper(title)
            r = {"title": title, "old_doi": entry.get("doi", "")}
            
            if published: 
                try: 
                    journal_name = published['journal'].get('name')
                except AttributeError:
                    journal_name = published.get('venue')

                # stick with old doi if new doi is not found
                # this sometimes happens when the paper is freshly published
                try:
                    doi = published['externalIds'].get('DOI')
                except AttributeError:
                    doi = entry.get('doi')

                entry['doi'] = str(doi)
                entry['url'] = published.get('publicationVenue').get('url', '')
                entry['publisher'] = journal_name
                entry['urldate'] = published.get('publicationDate', '')
                entry['year'] = str(published.get('year', ''))
                # if note exists remove it
                if 'note' in entry:
                    del entry['note']

                r.update({
                    "new_published": published.get('publicationDate', ''),
                    "new_venue": published.get('publicationVenue').get('name', ''),
                    "new_doi": published['externalIds'].get('DOI', ''),
                })
                results.append(r)
            else:
                print("❌ No published version found.")
            time.sleep(delay)

    save_bibtex_file(bib_data, output_path)
    print(f"\n💾 Updated BibTeX saved to {output_path}")

    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ["title", "old_doi", "new_published", "new_venue", "new_doi"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"📄 CSV summary saved to {csv_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for published versions of arXiv papers in a BibTeX file.")
    parser.add_argument("--input", "-i", required=True, help="Path to the input .bib file")
    parser.add_argument("--output", "-o", required=True, help="Path to save the updated .bib file")
    parser.add_argument("--csv", "-c", required=True, help="Path to save the CSV summary")
    parser.add_argument("--delay", "-d", type=float, default=1.0, help="Delay between API calls in seconds (default: 1.0)")

    args = parser.parse_args()
    process_bib_file(args.input, args.output, args.csv, args.delay)
