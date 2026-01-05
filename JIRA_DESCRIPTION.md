# Automated Evaluation Pipeline for Physician Segment Bot Responses

## Summary

Built an end-to-end automated pipeline that collects bot responses from VAPI and evaluates them against physician segment personas using LLM.

---

## Problem

We needed to evaluate how well our AI voice bots match their target physician personas (The Traditionalist, The Innovator, The Evidence Purist) across multiple questions.

---

## Solution

Developed a Python pipeline with two main processes:

### Process 1: VAPI Response Collection
- Reads questions from input Excel file
- Calls VAPI API for each question × segment combination
- Saves bot responses to output Excel (columns B, I, P)

### Process 2: LLM Evaluation
- Evaluates each response against segment persona description
- Uses OpenAI o4-mini reasoning model for accurate scoring
- Scores 0-5 with comments for low scores (≤3)
- Saves scores and comments to Excel (columns C, D, J, K, Q, R)

---

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PIPELINE                                    │
├─────────────────────────────────────────────────────────────────────┤
│  [1] VAPI RESPONSES          [2] LLM EVALUATION        [3] SAVE    │
│  ─────────────────           ────────────────          ────────    │
│  Questions → VAPI API        Responses → o4-mini       → Excel     │
│  Fill columns B, I, P        Score + Comment           output/     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Technical Implementation

| Component | Technology |
|-----------|------------|
| Language | Python 3.11 |
| VAPI Integration | REST API (chat endpoint) |
| LLM Evaluation | OpenAI o4-mini |
| Data Storage | Excel (openpyxl) |
| Architecture | OOP/SOLID principles |

---

## Project Structure

```
src/
├── config.py              # Configuration (API keys, Excel columns)
├── models.py              # Data classes (Segment, Response, Evaluation)
└── services/
    ├── vapi_service.py        # VAPI API integration
    ├── excel_service.py       # Excel read/write operations
    ├── segment_service.py     # Load segment personas from MD files
    └── evaluation_service.py  # LLM evaluation logic

scripts/
└── pipeline.py            # Main orchestrator

segments/
├── the_traditionalist.md  # Persona description
├── the_innovator.md       # Persona description
└── the_evidence_purist.md # Persona description
```

---

## Excel Output Structure

| Column | Header | Description |
|--------|--------|-------------|
| A | Question | The question asked |
| **The Traditionalist** |||
| B | The Traditionalist | Bot response |
| C | The Traditionalist Eval | LLM score (0-5) |
| D | The Traditionalist Comment | LLM comment |
| E-H | Eval/Comment_Aboubakr/Thomas | Human evaluator columns |
| **The Innovator** |||
| I | The Innovator | Bot response |
| J | The Innovator Eval | LLM score (0-5) |
| K | The Innovator Comment | LLM comment |
| L-O | Eval/Comment_Aboubakr/Thomas | Human evaluator columns |
| **The Evidence Purist** |||
| P | The Evidence Purist | Bot response |
| Q | The Evidence Purist Eval | LLM score (0-5) |
| R | The Evidence Purist Comment | LLM comment |
| S-V | Eval/Comment_Aboubakr/Thomas | Human evaluator columns |

---

## Scoring Scale (0-5)

| Score | Meaning |
|-------|---------|
| 0 | Not the segment at all |
| 1 | Mostly wrong, few weak hints |
| 2 | Mixed, clear drift into other segments |
| 3 | Acceptable but inconsistent / noticeable leaks |
| 4 | Strong match with minor issues |
| 5 | Perfect, no leaks |

---

## Usage

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run full pipeline
python scripts/pipeline.py --model o4-mini --delay 5

# Dry run (preview)
python scripts/pipeline.py --dry-run

# Skip VAPI, only evaluate existing responses
python scripts/pipeline.py --skip-responses

# Force re-evaluate
python scripts/pipeline.py --force
```

---

## Input/Output

- **Input:** `bot_evaluation_with_comments.xlsx` (questions only)
- **Output:** `output/evaluation_results.xlsx` (questions + responses + evaluations)

---

## Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...
VAPI_API_KEY=...

# VAPI Assistant IDs
VAPI_ASSISTANT_ID_1=...  # The Traditionalist
VAPI_ASSISTANT_ID_2=...  # The Innovator
VAPI_ASSISTANT_ID_5=...  # The Evidence Purist
```

---

## Acceptance Criteria

- [x] Pipeline reads questions from Excel
- [x] Pipeline fetches responses from VAPI for 3 segments
- [x] Pipeline evaluates responses with LLM (0-5 score)
- [x] Pipeline saves results to separate output file
- [x] Verbose logging during execution
- [x] Support for o4-mini reasoning model
- [x] Handles Unicode characters in responses
- [x] Rate limiting with configurable delay

---

## Dependencies

```
openai>=1.0.0
openpyxl>=3.1.0
requests>=2.31.0
python-dotenv>=1.0.0
mlflow>=2.0.0
```

---

## MLflow - Prompt Versioning

### Purpose
Track evaluation prompts in MLflow before making changes to enable:
- Version control for prompts
- Performance comparison between versions
- Rollback capability

### Commands

```bash
# Start MLflow UI
mlflow ui --port 5000

# Track current prompt before changes
python scripts/track_prompt.py --name "prompt_v1" --description "Initial prompt"

# List all tracked prompts
python scripts/track_prompt.py --list
```

### Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│  PROMPT VERSIONING WORKFLOW                                         │
├─────────────────────────────────────────────────────────────────────┤
│  1. Track Prompt  →  2. Make Changes  →  3. Run Pipeline  →  4. Compare │
│  ──────────────      ─────────────      ──────────────      ──────── │
│  MLflow save         Edit code          Evaluate            MLflow UI │
└─────────────────────────────────────────────────────────────────────┘
```

### MLflow UI
Access at: **http://localhost:5000**

