import json
from pathlib import Path
from src.lexicon import DATA_LEXICON, ACTIVITY_LEXICON, COLLECTION_VERBS

def find_tags(text, lexicon):
    """
    Finds keys from the lexicon that appear in the text.
    """
    text_l = text.lower()
    tags = set()
    for tag, keywords in lexicon.items():
        for kw in keywords:
            if kw in text_l:
                tags.add(tag)
                break
    return sorted(list(tags))

def is_collection_clause(text):
    """
    Checks if the text contains any collection verbs.
    """
    t = text.lower()
    return any(phrase in t for phrase in COLLECTION_VERBS)

def tag_clause(clause, data_lex, activity_lex):
    """
    Tags a single clause with data and activity tags.
    """
    text = clause["text"]
    data_tags = find_tags(text, data_lex)
    activity_tags = find_tags(text, activity_lex)
    return {
        **clause,
        "data_tags": data_tags,
        "activity_tags": activity_tags
    }

def extract_claims(clauses, product, doc_id):
    """
    Filters and tags clauses to produce a list of claims.
    """
    claims = []
    for cl in clauses:
        # Filter: Must contain collection language
        if not is_collection_clause(cl["text"]):
            continue

        tagged = tag_clause(cl, DATA_LEXICON, ACTIVITY_LEXICON)
        
        # Filter: Must have at least one tag (data or activity)
        if not tagged["data_tags"] and not tagged["activity_tags"]:
            continue

        claims.append({
            "doc_id": doc_id,
            "product": product,
            "section": tagged["section"],
            "clause_id": tagged["clause_id"],
            "activity": tagged["activity_tags"],
            "data_collected": tagged["data_tags"],
            "source_text": tagged["text"]
        })
    return claims

def run_tagging(clause_json, product, doc_id, out_path):
    """
    Runs the tagging process on a file of clauses.
    """
    try:
        clauses = json.loads(Path(clause_json).read_text(encoding="utf-8"))
        claims = extract_claims(clauses, product, doc_id)
        
        # Ensure directory exists
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        
        Path(out_path).write_text(json.dumps(claims, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Successfully extracted {len(claims)} claims to {out_path}")
        
    except Exception as e:
        print(f"Error tagging clauses for {clause_json}: {e}")
        raise
