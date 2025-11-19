from bs4 import BeautifulSoup
import json
from pathlib import Path
import re

def clean_text(text):
    """
    Normalizes whitespace in text.
    """
    return re.sub(r'\s+', ' ', text).strip()

def html_to_sections(html_path, out_json):
    """
    Parses HTML file and extracts sections (headings + text).
    Saves the result as a JSON list of {section, text} objects.
    """
    try:
        html = Path(html_path).read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")

        sections = []
        current_heading = "ROOT"
        
        # Find all relevant elements in order
        # We look for headings and content blocks
        # This is a heuristic approach; might need tuning for specific sites
        elements = soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "div"])
        
        for elem in elements:
            # If it's a heading, update current_heading
            if elem.name in ["h1", "h2", "h3", "h4"]:
                text = clean_text(elem.get_text())
                if text:
                    current_heading = text
            
            # If it's content, append to sections
            elif elem.name in ["p", "li"]:
                text = clean_text(elem.get_text())
                if text:
                    sections.append({
                        "section": current_heading,
                        "text": text
                    })
            
            # Divs are tricky, sometimes they contain text directly
            elif elem.name == "div":
                # Only take direct text or text if it doesn't have many children
                # This is to avoid duplicating text from parent divs
                if not elem.find_all(["p", "div", "h1", "h2", "h3", "h4"]):
                     text = clean_text(elem.get_text())
                     if text:
                        sections.append({
                            "section": current_heading,
                            "text": text
                        })

        # Ensure directory exists
        Path(out_json).parent.mkdir(parents=True, exist_ok=True)

        Path(out_json).write_text(json.dumps(sections, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Successfully parsed {html_path} to {out_json}")
        
    except Exception as e:
        print(f"Error parsing {html_path}: {e}")
        raise
