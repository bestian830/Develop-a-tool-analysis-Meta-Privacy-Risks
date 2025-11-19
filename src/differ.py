import json
from pathlib import Path

def load_claims(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def claim_key(c):
    """
    Generates a unique key for a claim for comparison purposes.
    Ignores clause_id and source_text, focuses on semantics.
    """
    return (
        tuple(sorted(c["activity"])),
        tuple(sorted(c["data_collected"])),
        c["section"]
    )

def diff_versions(v1_path, v2_path, out_path=None):
    """
    Compares two versions of claims and returns added, removed, and kept claims.
    """
    try:
        v1 = load_claims(v1_path)
        v2 = load_claims(v2_path)

        v1_map = {claim_key(c): c for c in v1}
        v2_map = {claim_key(c): c for c in v2}

        keys1, keys2 = set(v1_map.keys()), set(v2_map.keys())

        added = [v2_map[k] for k in keys2 - keys1]
        removed = [v1_map[k] for k in keys1 - keys2]
        kept = [v2_map[k] for k in keys1 & keys2]
        
        result = {
            "added_count": len(added),
            "removed_count": len(removed),
            "kept_count": len(kept),
            "added": added,
            "removed": removed,
            "kept": kept
        }

        if out_path:
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            Path(out_path).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"Diff saved to {out_path}")
            
        return result

    except Exception as e:
        print(f"Error diffing versions {v1_path} and {v2_path}: {e}")
        raise
