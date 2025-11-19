# Privacy Policy Analysis Pipeline

A transparent, rule-based tool for extracting and comparing privacy claims from policy documents.

---

## What This Tool Does

This pipeline analyzes privacy policies in **6 automated steps**:

1. **Download** → Fetches the HTML from a URL
2. **Parse** → Extracts clean text from HTML
3. **Split** → Breaks text into individual sentences (clauses)
4. **Tag** → Identifies privacy-related keywords (activities + data types)
5. **Extract** → Generates structured "claims" (e.g., "When you take photos, we collect location data")
6. **Compare** → Highlights differences between two policy versions

**Why use this tool?**
- ✅ **No AI/LLMs** - Fully deterministic and reproducible
- ✅ **Transparent** - All keywords defined in `src/lexicon.py`
- ✅ **Auditable** - Every step saves intermediate files for inspection

---

## Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Download spaCy language model (required for sentence splitting)
python -m spacy download en_core_web_sm
```

**Requirements:**
- Python 3.8+
- Chrome browser (for web scraping)

### 2. Analyze a Privacy Policy

```bash
python tools/run_analysis.py analyze \
  --url "https://www.ray-ban.com/uk/c/privacy-policy" \
  --product "rayban_glasses" \
  --id "rayban_2024"
```

**What happens:**
- Downloads HTML → `data/raw/rayban_2024.html`
- Parses sections → `data/clean/rayban_2024.json`
- Splits sentences → `data/clauses/rayban_2024_clauses.json`
- Extracts claims → `data/claims/rayban_2024_claims.json` ✨ **This is the final output**

### 3. Compare Two Versions

```bash
python tools/run_analysis.py compare \
  --old "rayban_2023" \
  --new "rayban_2024"
```

**Output:** `data/diffs/rayban_2023_vs_rayban_2024.json`
- `added` - New claims in the 2024 version
- `removed` - Claims that were deleted
- `kept` - Claims that stayed the same

---

## How to Customize (The Lexicon)

All privacy detection logic is in **`src/lexicon.py`**. You can edit it to match your specific needs.

### Example: Add a New Data Category

```python
# In src/lexicon.py
DATA_LEXICON = {
    "biometrics": [
        "face ID", "facial geometry", "fingerprint", "retinal scan"
    ],
    "health": [
        "medical records", "prescription data", "heart rate"
    ]
}
```

### Example: Add a New Activity

```python
ACTIVITY_LEXICON = {
    "use_voice_assistant": [
        "hey meta", "voice commands", "ask meta"
    ],
    "make_payment": [
        "purchase", "checkout", "buy", "transaction"
    ]
}
```

**After editing:** Just re-run the analysis. The tool will immediately use your new keywords.

---

## Project Structure

```
capestone/
├── data/                      # All output files (auto-generated)
│   ├── raw/                   # Downloaded HTML files
│   ├── clean/                 # Parsed JSON (sections + paragraphs)
│   ├── clauses/               # Split sentences
│   ├── claims/                # ✨ Final extracted claims
│   └── diffs/                 # Comparison results
│
├── src/                       # Source code
│   ├── lexicon.py            # ⚙️ Configuration (edit this!)
│   ├── downloader.py         # Selenium web scraper
│   ├── parser.py             # HTML → JSON converter
│   ├── clause_splitter.py    # Sentence segmentation
│   ├── tagger.py             # Keyword matching logic
│   ├── differ.py             # Version comparison
│   └── pipeline.py           # Orchestrates all steps
│
├── tools/
│   └── run_analysis.py       # 🎯 Main CLI entry point
│
├── tests/                     # Unit tests
└── requirements.txt           # Python dependencies
```

---

## Troubleshooting

### Problem: "403 Forbidden" or "Access Denied"

**Cause:** Some websites (like Ray-Ban) block automated scrapers.

**Solution:**
1. Manually save the page in your browser: `File → Save Page As → Webpage, Complete`
2. Place the `.html` file in `data/raw/your_id.html`
3. Run the analysis command - it will skip the download step automatically

### Problem: "No claims extracted" (0 results)

**Diagnosis:**
1. Check `data/clauses/xxx_clauses.json` - Does it contain text?
2. Check `src/lexicon.py` - Do your keywords match the policy's language?

**Fix:** Add more synonyms to `DATA_LEXICON` or `ACTIVITY_LEXICON` in `src/lexicon.py`.

### Problem: "ModuleNotFoundError: No module named 'spacy'"

**Fix:**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## Understanding the Output

### Claims File (`data/claims/xxx_claims.json`)

Each claim is a JSON object:

```json
{
  "doc_id": "rayban_2024",
  "product": "rayban_glasses",
  "section": "Data Collection",
  "clause_id": 42,
  "activity": ["take_photo_with_glasses"],
  "data_collected": ["location", "video_image"],
  "source_text": "When you capture photos, we may collect your location..."
}
```

**Fields:**
- `activity` - What the user is doing (from `ACTIVITY_LEXICON`)
- `data_collected` - What data is collected (from `DATA_LEXICON`)
- `source_text` - The original sentence from the policy

### Diff File (`data/diffs/xxx_vs_yyy.json`)

```json
{
  "added": [/* claims only in NEW version */],
  "removed": [/* claims only in OLD version */],
  "kept": [/* claims in BOTH versions */]
}
```

---

## Example Workflow

```bash
# Step 1: Analyze version 1
python tools/run_analysis.py analyze \
  --url "https://example.com/privacy-2023" \
  --product "smart_glasses" \
  --id "v1"

# Step 2: Analyze version 2
python tools/run_analysis.py analyze \
  --url "https://example.com/privacy-2024" \
  --product "smart_glasses" \
  --id "v2"

# Step 3: Compare
python tools/run_analysis.py compare --old "v1" --new "v2"

# Step 4: Review results
cat data/diffs/v1_vs_v2.json
```

---

## License

This project is for research and educational purposes.
