# 📚 Persona-Driven Document Intelligence
# Challenge 1B – Context-Aware PDF Analysis and Section Ranking

# # 🚀 Overview
This project enhances document understanding by applying persona-specific context to PDF analysis. It extracts text from PDF files, analyzes each section from a persona’s perspective (e.g., student, analyst), and ranks sections by relevance for a specific task (e.g., learning, reviewing).

# #🧭 Approach Summary

# # # Goal:
To analyze PDF documents through the lens of a user’s persona and task—enhancing document relevance, extracting insights, and ranking sections based on contextual importance.

# # # Step-by-Step Workflow:

# # # # Text Extraction (parser.py)
Use PyMuPDF to extract text from each non-empty page in the PDF.

Output: List of {page_number, text} dictionaries.

# # # # Document Sectioning
Simulate or parse document sections using headings or manual segmentation.

Structure: List of {section_title, content, position}.

# # # # Persona Processing (persona.py)
Classify user role (e.g., student, researcher) and task (e.g., review, learn) using keyword matching.

For each section:

Compute persona relevance score.

Extract persona-specific insights (e.g., "Findings presented").

Identify key concepts relevant to the persona.

Compute job alignment score.

Assign importance level: High / Medium / Low.

Output: Enhanced section data + metadata summary.

# # # # Section Ranking (ranks_section.py)
Compute final composite relevance score for each section based on:

Semantic relevance (TF-IDF-like scoring vs persona context).

Content length optimization (ideal length preferred).

Section position bonus (earlier sections are favored).

Rank sections in descending order of relevance.

# # # # Key Techniques:
Keyword-based classification for persona and task inference.

Relevance scoring via weighted components:

Role match, task match, direct task keyword match.

Context-aware insights extraction per role.

TF-IDF-inspired scoring without external corpus.

Heuristic-based length and position adjustments.

Output:
Ranked document sections with persona-aligned metadata.

Useful for personalized document summarization, review, and navigation.


# # 🔧 Modules Explained

# # #  1. utils/parser.py – PDF Text Extraction
Uses PyMuPDF (fitz) to extract text from each page.

Skips empty pages to optimize performance.

Output: A list of { page_number, text } dictionaries.


# # # # 2. src/persona.py – Persona Processor
Defines persona roles (e.g., researcher, student) and tasks (e.g., review, learn).

Enhances each document section with:

Persona relevance score

Key concepts

Persona-specific insights (e.g., "Methodology identified" for researchers)

Computes:

Job alignment score

Importance level: high, medium, low

Summary metadata for entire document

# # # # 3. src/ranks_section.py – Section Ranker
Ranks document sections based on:

Semantic relevance (TF-IDF-based)

Section length optimization

Position in document (earlier sections are prioritized)

Computes a composite score for each section.


# # 👤 Supported Personas and Tasks

# # # Roles:

Researcher

Student

Analyst

Teacher

Manager

Entrepreneur

# # # Tasks:
Review

Learn

Analyze

Prepare

Summarize

## Docker Configuration

### Base Image

- `python:3.10-slim` for minimal footprint
- AMD64 platform compatibility
- Offline operation (no network access)

### Container Specifications

- **Input**: Read-only mount at `/app/input`
- **Output**: Write mount at `/app/output`
- **Network**: Disabled (`--network none`)
- **Memory**: Optimized for 16GB constraint
- **CPU**: Utilizes 8 available cores

## Usage

### Building the Image

```bash
docker build --platform linux/amd64 -t none team_tech_pulse_solution_2:69 .
```

### Running the Container

```bash
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none team_tech_pulse_solution_2:69
```

### Input/Output

- **Input**: Place PDF files in `Input/input_#/` directory
- **Output**: JSON files generated in `output_#/` directory
- **Naming**: `document.pdf` → `document.json`