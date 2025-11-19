import spacy
import json
from pathlib import Path

# Load spaCy model once
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def split_into_clauses(in_json, out_json):
    """
    Splits text sections into individual clauses (sentences).
    """
    try:
        sections = json.loads(Path(in_json).read_text(encoding="utf-8"))
        clauses = []
        clause_id = 0

        for sec in sections:
            text = sec["text"]
            if not text:
                continue
                
            doc = nlp(text)
            for sent in doc.sents:
                sent_text = sent.text.strip()
                if not sent_text:
                    continue
                
                clauses.append({
                    "clause_id": clause_id,
                    "section": sec["section"],
                    "text": sent_text
                })
                clause_id += 1

        # Ensure directory exists
        Path(out_json).parent.mkdir(parents=True, exist_ok=True)
        
        Path(out_json).write_text(json.dumps(clauses, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Successfully split {in_json} into {len(clauses)} clauses at {out_json}")
        
    except Exception as e:
        print(f"Error splitting clauses for {in_json}: {e}")
        raise
