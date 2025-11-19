import os
from pathlib import Path
from src.downloader import fetch_policy
from src.parser import html_to_sections
from src.clause_splitter import split_into_clauses
from src.tagger import run_tagging
from src.differ import diff_versions

def run_pipeline(url, product, doc_id, base_dir="data"):
    """
    Runs the full pipeline for a single policy version.
    """
    base = Path(base_dir)
    
    # Paths
    raw_path = base / "raw" / f"{doc_id}.html"
    clean_path = base / "clean" / f"{doc_id}.json"
    clauses_path = base / "clauses" / f"{doc_id}_clauses.json"
    claims_path = base / "claims" / f"{doc_id}_claims.json"
    
    print(f"--- Starting pipeline for {doc_id} ---")
    
    # Step 1a: Download
    if not raw_path.exists():
        fetch_policy(url, raw_path)
    else:
        print(f"Skipping download, {raw_path} exists.")
        
    # Step 1b: Parse
    html_to_sections(raw_path, clean_path)
    
    # Step 3: Split
    split_into_clauses(clean_path, clauses_path)
    
    # Step 4: Tag
    run_tagging(clauses_path, product, doc_id, claims_path)
    
    print(f"--- Pipeline finished for {doc_id} ---")
    return claims_path

def run_comparison(doc_id_1, doc_id_2, base_dir="data"):
    """
    Runs comparison between two processed policies.
    """
    base = Path(base_dir)
    claims_1 = base / "claims" / f"{doc_id_1}_claims.json"
    claims_2 = base / "claims" / f"{doc_id_2}_claims.json"
    diff_path = base / "diffs" / f"{doc_id_1}_vs_{doc_id_2}.json"
    
    if not claims_1.exists() or not claims_2.exists():
        print("Error: Claims files not found. Run pipeline for both versions first.")
        return
        
    print(f"--- Comparing {doc_id_1} vs {doc_id_2} ---")
    diff_versions(claims_1, claims_2, diff_path)
    print(f"--- Comparison finished ---")
