# Ray-Ban Meta Smart Glasses Privacy Policy Analysis Project

## Project Overview

This project aims to develop an **explainable privacy policy analyzer** that automatically processes Meta's Ray-Ban smart glasses privacy policies, identifies data collection practices, and evaluates them against Canadian privacy standards (PIPEDA and PIPA). By combining human-guided thematic analysis with computational methods, we create a transparent, auditable system for privacy policy interpretation and compliance assessment.

---

## Project Objectives

1. **Systematic Framework Development**: Convert complex privacy policies into structured representations of data types, collection contexts, and legal compliance features.

2. **PIPEDA/PIPA Alignment**: Ensure analysis aligns with Canadian privacy frameworks, focusing on consent, transparency, and purpose limitation principles.

3. **Prototype Tool Implementation**: Build a system that ingests policy text and produces explainable outputs showing what personal data are collected, under what conditions, and how policies evolve over time.

---

## Methodology Overview

This project employs a **hybrid approach** combining qualitative and computational methods:

### Phase 1: Human-Guided Thematic Analysis
- **Framework**: Braun & Clarke's 6-step thematic analysis methodology
- **Approach**: Multiple independent coders manually analyze privacy text to identify patterns
- **Dimensions**: Data types (WHAT), Activity contexts (WHEN/HOW), and PIPEDA compliance (WHY)
- **Validation**: Inter-rater reliability measured using Cohen's Kappa (target ≥ 0.70)
- **Output**: Codebook defining data categories, activity patterns, and coding rules

### Phase 2: Automated Rule-Based Extraction
- Pattern matching and lexicon-based identification of data collection statements
- Negation and hedging detection (e.g., "may", "might")
- Section-aware processing to preserve context

### Phase 3: Machine Learning Classification
- Lightweight classifier (e.g., logistic regression) using TF-IDF features
- Assigns data type and activity context labels
- Probability calibration for meaningful confidence scores

### Phase 4: LLM Validation (Optional)
- Prompt-engineered LLM validator for low-confidence or ambiguous cases
- Strict JSON output format for reproducibility
- Full logging of LLM-assisted decisions

### Phase 5: Legal Evaluation
- Assessment against PIPEDA/PIPA principles
- Principle-based criteria: purpose & consent, limitation/minimization, transparency/access
- Heuristic checks for compliance signals

### Phase 6: Version Comparison & Change Analysis
- Alignment of comparable policy sections across versions
- Differential analysis at (data type, activity) pair level
- Tracking of added, removed, and modified data collection practices

---

## Project Phases & Timeline

### **Phase 1: Data Preparation & Team Setup (Week 1)**
**Duration**: 1-2 days  
**Activities**:
- [ ] Collect official privacy policy documents (current + prior versions)
- [ ] Establish coding team (3+ independent coders)
- [ ] Set up collaborative tools (Google Sheets, GitHub, communication channels)
- [ ] Create shared project repository structure
- [ ] Finalize coder agreements and commitment forms

**Deliverables**:
- Project folder with organized raw policy documents
- Google Sheets coding template
- Coder commitment agreements

---

### **Phase 2: Human-Guided Thematic Analysis (Week 1-2)**

#### **2.1 Coder Training & Pilot Coding (Days 2-3)**
- Train coders on data type classifications and activity context patterns
- Conduct pilot coding on 20% of policy text (independently)
- Achieve inter-rater reliability baseline

**Key Resource**: 
📊 **[Thematic Analysis Spreadsheet](https://docs.google.com/spreadsheets/d/1k5vUOX3r5Ym9zIPVW74OkFlrVSZlwEJZMPFLFd1s5RU/edit?gid=0#gid=0)**
(Contains reference tables, coding examples, and pilot data entry interface)

#### **2.2 Inter-Rater Agreement Assessment (Day 4)**
- Calculate Cohen's Kappa for pairwise coder comparisons
- Target threshold: Kappa ≥ 0.70
- If below threshold, refine coding guidelines and iterate

#### **2.3 Full Text Coding (Days 5-10)**
- All coders independently code assigned policy sections
- Each statement labeled with: data type, activity context, confidence, and rationale
- Daily 15-minute sync meetings to surface issues
- Weekly full team alignment sessions

#### **2.4 Thematic Aggregation (Day 11-12)**
- Group coded statements by emerging themes
- Reconcile discrepancies through team discussion
- Define final themes with clear inclusion/exclusion criteria
- Document initial findings

**Deliverables**:
- Complete coded dataset (CSV/JSON format)
- Inter-rater agreement report (Kappa scores, agreement matrices)
- Thematic codebook (definitions, examples, decision rules)
- Initial thematic analysis report

**Output Metrics**:
- Final Cohen's Kappa score
- Distribution of data types and activity contexts
- High-risk compliance statements identified
- Theme frequency and prevalence statistics

---

### **Phase 3: Codebook Development & Refinement (Week 2)**

#### **3.1 Codebook Finalization**
Develop a comprehensive, standardized codebook including:

**Data Type Categories** (primary taxonomy):
- Biometric/Sensor Data (camera, audio, facial recognition, gesture recognition)
- Location Data (GPS, approximate location, movement patterns)
- Device & Network Information (device model, OS version, IP address, network type)
- Usage & Activity Logs (app usage, feature interactions, clickstream)
- Communications (message content, call logs, contacts, calendar)
- Financial/Transaction Data (payment information, purchase history, billing)
- Third-party Data (partner-sourced data, social media data)
- Inferred/Derived Data (interest profiles, behavioral predictions)

**Activity Context Categories**:
- User-initiated (when you activate, when you record, when you enable)
- Automatic/Always-on (continuous, background, real-time)
- Conditional (when app is running, if enabled, under circumstances)
- Optional (user can choose, based on consent)
- Required (necessary for feature, cannot be disabled)
- Third-party initiated (partners may, service providers may)
- Unclear (may, might, possibly)

**Confidence Scoring Rules**:
- 0.9-1.0: Very clear, no ambiguity
- 0.7-0.8: Relatively clear, minor uncertainties
- 0.5-0.6: Ambiguous, multiple concerns
- 0.3-0.4: Highly ambiguous, unclear intent
- 0.0-0.2: Cannot determine meaning

**PIPEDA Compliance Assessment**:
- Informed Consent: explicit description of data collection and purpose
- Purpose Limitation: scope and boundaries of intended use
- Clarity & Transparency: absence of legal hedging (may, might, could)
- Data Minimization: necessity and proportionality of collection
- Retention: explicit data retention periods and deletion policies
- Individual Rights: access, correction, deletion capabilities
- Security: description and specificity of protective measures

#### **3.2 Validation Against Prior Research**
- Cross-reference codebook with existing privacy analysis frameworks (CLEAR, PRISMe)
- Verify alignment with PIPEDA/PIPA guidance documents
- Document deviations and justifications

**Deliverables**:
- Finalized codebook document (>50 pages)
- Coded examples for each category
- Decision trees for ambiguous cases
- Updated coding protocol v2.0

---

### **Phase 4: Automated Extraction Pipeline Development (Week 3)**

#### **4.1 Rule-Based Content Analysis**
**Implementation**:
- Text preprocessing: PDF/HTML parsing, section segmentation, character offset preservation
- Pattern matching: keyword lexicons for each data type and activity context
- Negation/hedging detection: identify uncertainty qualifiers
- Output: candidate sentences with preliminary labels

**Tools**: Python (spaCy, NLTK, regex)  
**Code**: Available in `/src/rule_based_extractor.py`

#### **4.2 Simple Classifier Training**
**Implementation**:
- Feature extraction: TF-IDF vectorization of candidate sentences
- Model: Logistic Regression with calibrated probabilities
- Training data: human-annotated thematic analysis codes
- Cross-validation: 5-fold CV to assess generalization

**Performance Metrics**:
- Precision, Recall, F1 score (per data type and activity)
- Confidence calibration (ECE, MCE)
- Ablation: rules-only vs. ML-only vs. hybrid

**Tools**: Python (scikit-learn)  
**Code**: Available in `/src/ml_classifier.py`

#### **4.3 LLM Validator (Optional, Controlled)**
**Implementation**:
- Prompt engineering: strict JSON schema for outputs
- Invocation logic: triggered on low confidence or rule/ML disagreement
- Validation: quote span extraction, label assignment, rationale generation
- Logging: complete audit trail of LLM decisions

**Prompt Template**:
```
Decompose the following privacy policy statement into structured claims.

Statement: "{sentence}"

Return ONLY valid JSON (no markdown):
{
  "extracted": true/false,
  "quote": "exact extracted quote",
  "data_type": "category from codebook",
  "activity_context": "activity from codebook",
  "confidence": 0.0-1.0,
  "rationale": "brief explanation"
}
```

**Tools**: Python (anthropic/openai SDK)  
**Code**: Available in `/src/llm_validator.py`

**Deliverables**:
- Rule lexicon and pattern library
- Trained classifier model (serialized)
- LLM validation pipeline (if applicable)
- Extraction pipeline documentation
- Ablation study results

---

### **Phase 5: Legal Evaluation & Compliance Assessment (Week 3)**

#### **5.1 PIPEDA Principle Mapping**
For each extracted claim:
- Assess against 7 PIPEDA principles (Consent, Purpose Limitation, Clarity, Minimization, Retention, Individual Rights, Security)
- Assign risk level: High / Medium / Low
- Document rationale and evidence

#### **5.2 Compliance Heuristics**
**Examples**:
- ✅ High specificity + consent mention → Likely compliant
- ⚠️ Vague purpose + no opt-out → Medium risk
- 🔴 Background collection + no notice → High risk

#### **5.3 Longitudinal Compliance Tracking**
- Track compliance ratings across policy versions
- Identify improvements or deteriorations in practices
- Flag emerging privacy risks

**Deliverables**:
- PIPEDA compliance assessment report
- Risk-categorized statement inventory
- Comparative compliance timeline

---

### **Phase 6: Version Comparison & Change Analysis (Week 4)**

#### **6.1 Policy Alignment**
- Map equivalent sections across multiple policy versions
- Align extracted claims at the (data type, activity) pair level

#### **6.2 Differential Analysis**
**Change Types**:
- **Added**: New data-activity pair appears
- **Removed**: Previously mentioned pair disappears
- **Modified**: Wording or scope changes while maintaining core pair

**Example**:
```
v2023: "We collect camera data when you enable video recording"
v2024: "We collect audio and video data when you enable video 
       recording or voice commands"

Change Type: MODIFIED (video→audio+video, same activity)
Risk: Data collection scope expansion
```

#### **6.3 Trend Analysis**
- Quantify data collection practice evolution
- Identify patterns (e.g., gradual expansion of data sharing)
- Assess trajectory toward better or worse privacy practices

**Deliverables**:
- Version comparison report
- Change timeline visualization
- Trend analysis and risk trajectory

---

### **Phase 7: Reporting & Explainability (Week 4)**

#### **7.1 Report Generation**
The tool generates multiple output formats:

**1. HTML Interactive Report**
- Per-category tables with quotes, data types, activities, rationales
- Evidence badges (rules/ML/LLM source)
- Expandable sections for detailed exploration
- Color-coded PIPEDA risk levels

**2. JSON/CSV Exports**
- Structured claim dataset
- Diff analysis between versions
- Compliance assessment summary

**3. Audit Logs**
- Complete decision trail for reproducibility
- Timestamp, coder/system responsible, confidence score
- Rationale for every extraction and decision

#### **7.2 Explainability Features**
- **Quote Fidelity**: Every output traced back to exact policy text with character offsets
- **Rationale Transparency**: Clear explanation of why each data type and activity was assigned
- **Confidence Scores**: Calibrated probabilities indicate uncertainty
- **Source Attribution**: Identifies whether decision came from rules, ML, or LLM

**Deliverables**:
- Final HTML report
- JSON/CSV data exports
- Executive summary (1-2 pages)
- Full technical documentation

---

### **Phase 8: Benchmarking & Evaluation (Week 5)**

#### **8.1 System Performance Evaluation**

**Metrics**:
- **Precision / Recall / F1**: vs. human thematic analysis baseline
- **Cohen's Kappa**: inter-annotator agreement with human labels
- **Calibration**: confidence score reliability (Expected Calibration Error)
- **Qualitative Audits**: sample claims for quote fidelity and rationale validity

#### **8.2 Ablation Study**
Compare performance across system variants:
- Rules-only extraction
- ML classifier addition
- LLM validator inclusion
- Full hybrid pipeline

**Purpose**: Quantify contribution of each component

#### **8.3 Comparison with Baselines**
- Simple LLM summarization (no rules)
- Prior work baselines (if available)
- Manual expert analysis (gold standard)

**Deliverables**:
- Benchmarking report with tables and visualizations
- Ablation study results
- Baseline comparison analysis
- Error analysis and failure case documentation

---

## Project Deliverables Checklist

### Phase 1
- [x] Project repository structure
- [x] Policy documents (multiple versions)
- [ ] Coding team assembled and trained
- [ ] Google Sheets template operational

### Phase 2
- [ ] Coded dataset (complete)
- [ ] Inter-rater agreement report (Kappa ≥ 0.70)
- [ ] Thematic codebook (finalized)
- [ ] Initial findings report

### Phase 3
- [ ] Comprehensive codebook document
- [ ] Validated data type and activity taxonomies
- [ ] PIPEDA compliance assessment framework

### Phase 4
- [ ] Rule lexicon and pattern library
- [ ] Trained ML classifier
- [ ] LLM validator pipeline (if applicable)
- [ ] Extraction pipeline code

### Phase 5
- [ ] PIPEDA compliance evaluation tool
- [ ] Risk assessment report
- [ ] Compliance heuristics documentation

### Phase 6
- [ ] Version comparison analysis
- [ ] Change timeline visualization
- [ ] Trend analysis report

### Phase 7
- [ ] Interactive HTML report
- [ ] JSON/CSV data exports
- [ ] Complete audit logs
- [ ] Executive summary

### Phase 8
- [ ] Benchmarking report
- [ ] Ablation study results
- [ ] Error analysis
- [ ] Final paper (if applicable)

---

## Team & Responsibilities

| Role               | Responsibilities                                      | Time Commitment |
| ------------------ | ----------------------------------------------------- | --------------- |
| **Project Lead**   | Overall coordination, methodology design, integration | 50%             |
| **Coder 1**        | Human thematic analysis (independent)                 | 20%             |
| **Coder 2**        | Human thematic analysis (independent)                 | 20%             |
| **Coder 3**        | Human thematic analysis (independent)                 | 20%             |
| **ML Engineer**    | Automated pipeline development                        | 50%             |
| **Legal Reviewer** | PIPEDA compliance assessment oversight                | 20%             |

---

## Key Resources & Tools

### Collaboration & Data Management
- **Thematic Analysis Spreadsheet**: https://docs.google.com/spreadsheets/d/1k5vUOX3r5Ym9zIPVW74OkFlrVSZlwEJZMPFLFd1s5RU/edit?gid=0#gid=0
- **Version Control**: GitHub repository
- **Communication**: Slack / WeChat group for team sync

### Analysis & Computation
- **Text Processing**: Python (spaCy, NLTK, BeautifulSoup, pdfplumber)
- **Machine Learning**: scikit-learn (Logistic Regression, TF-IDF)
- **LLM Integration**: Claude API / OpenAI GPT-4
- **Statistics**: Python (nltk.metrics, statsmodels)

### Visualization & Reporting
- **Data Export**: Pandas (CSV, JSON)
- **Reporting**: Jinja2 (HTML templates)
- **Visualization**: Plotly, Matplotlib

---

## Success Criteria

✅ **Phase Completion**:
- Cohen's Kappa for human coding ≥ 0.70
- Complete coded dataset with >95% coverage
- Automated system achieves >85% precision/recall vs. human baseline

✅ **Quality Standards**:
- All extracted quotes verified against source policy
- Every extraction includes rationale and confidence score
- All PIPEDA assessments documented with evidence
- Complete audit trail maintained

✅ **Documentation**:
- Comprehensive methodology report
- Clear, reproducible codebook
- Technical documentation for automated pipeline
- Paper-ready results and findings

---

## References

1. Braun, V., & Clarke, V. (2006). Using thematic analysis in psychology. *Qualitative Research in Psychology*, 3(2), 77-101.

2. Han et al. (2024). Privacy policy compliance in miniapps: Automated assessment and real-time monitoring.

3. Chen et al. (2025). CLEAR: Compliant LLM-enabled Analysis for Regulatory contexts.

4. Kaya et al. (2025). PRISMe: Privacy Regulatory Impact Scoring and monitoring.

5. Office of the Privacy Commissioner of Canada (2023). PIPEDA Guidance Documents.

6. British Columbia Office of the Information and Privacy Commissioner (2021). PIPA: Private Sector Privacy Requirements.

---

## Contact & Support

For questions or issues related to:
- **Methodology**: [Project Lead Contact]
- **Coding & Thematic Analysis**: [Thematic Analysis Spreadsheet](https://docs.google.com/spreadsheets/d/1k5vUOX3r5Ym9zIPVW74OkFlrVSZlwEJZMPFLFd1s5RU/edit?gid=0#gid=0)
- **Technical Implementation**: [ML Engineer Contact]
- **PIPEDA Compliance**: [Legal Reviewer Contact]

---

## Project Status

**Current Phase**: Phase 2 - Human-Guided Thematic Analysis  
**Expected Completion**: [Date]  
**Last Updated**: [Today's Date]

---

*For the latest updates and resources, visit the [Project Repository]*