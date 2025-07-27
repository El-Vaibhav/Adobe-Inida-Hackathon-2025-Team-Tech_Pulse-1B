# 📚 Persona-Driven Document Intelligence
# Challenge 1B – Context-Aware PDF Analysis and Section Ranking

## 🚀 Overview
This project enhances document understanding by applying persona-specific context to PDF analysis. It extracts text from PDF files, analyzes each section from a persona’s perspective (e.g., student, analyst), and ranks sections by relevance for a specific task (e.g., learning, reviewing).

## 🧭 Approach Summary

### 1. Goal:
To analyze PDF documents through the lens of a user’s persona and task—enhancing document relevance, extracting insights, and ranking sections based on contextual importance.

### 2.Step-by-Step Workflow:

#### 3.Text Extraction (parser.py)
1) Use PyMuPDF to extract text from each non-empty page in the PDF.

2) Output: List of {page_number, text} dictionaries.

#### 4.Document Sectioning
1)Simulate or parse document sections using headings or manual segmentation.

2) Structure: List of {section_title, content, position}.

#### 5.Persona Processing (persona.py)
Classify user role (e.g., student, researcher) and task (e.g., review, learn) using keyword matching.

For each section:

1) Compute persona relevance score.

2) Extract persona-specific insights (e.g., "Findings presented").

3) Identify key concepts relevant to the persona.

4) Compute job alignment score.

5) Assign importance level: High / Medium / Low.

6) Output: Enhanced section data + metadata summary.

#### 6.Section Ranking (ranks_section.py)
1) Compute final composite relevance score for each section based on:

2) Semantic relevance (TF-IDF-like scoring vs persona context).

3) Content length optimization (ideal length preferred).

4) Section position bonus (earlier sections are favored).

5) Rank sections in descending order of relevance.

#### 7.Key Techniques:
1) Keyword-based classification for persona and task inference.

2) Relevance scoring via weighted components:

3) Role match, task match, direct task keyword match.

4) Context-aware insights extraction per role.

5) TF-IDF-inspired scoring without external corpus.

6) Heuristic-based length and position adjustments.

Output:
Ranked document sections with persona-aligned metadata.
Useful for personalized document summarization, review, and navigation.

## Output format

``` json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Challenge 1B Output Schema",
  "description": "Schema for persona-driven document intelligence output",
  "required": ["metadata", "extracted_sections", "subsection_analysis"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": [
        "input_documents",
        "persona",
        "job_to_be_done",
        "processing_timestamp"
      ],
      "properties": {
        "input_documents": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "List of input PDF document filenames"
        },
        "persona": {
          "type": "string",
          "description": "Description of the user persona"
        },
        "job_to_be_done": {
          "type": "string",
          "description": "Specific task the persona needs to accomplish"
        },
        "processing_timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "Timestamp when processing was completed"
        }
      }
    },
    "extracted_sections": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "document",
          "section_title",
          "importance_rank",
          "page_number"
        ],
        "properties": {
          "document": {
            "type": "string",
            "description": "Source document filename"
          },
          "section_title": {
            "type": "string",
            "description": "Title of the extracted section"
          },
          "importance_rank": {
            "type": "integer",
            "minimum": 1,
            "description": "Importance ranking (1 = most important)"
          },
          "page_number": {
            "type": "integer",
            "minimum": 1,
            "description": "Page number where section is found"
          }
        }
      },
      "description": "Main sections ranked by relevance to persona and job"
    },
    "subsection_analysis": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["document", "refined_text", "page_number"],
        "properties": {
          "document": {
            "type": "string",
            "description": "Source document filename"
          },
          "refined_text": {
            "type": "string",
            "description": "Refined and extracted text content"
          },
          "page_number": {
            "type": "integer",
            "minimum": 1,
            "description": "Page number where content is found"
          }
        }
      },
      "description": "Granular subsection extraction with refined content"
    }
  }
}
```

## 🔧 Modules Explained

####  1. utils/parser.py – PDF Text Extraction

1) Uses PyMuPDF (fitz) to extract text from each page.

2) Skips empty pages to optimize performance.

3) Output: A list of { page_number, text } dictionaries.


#### 2. src/persona.py – Persona Processor

1) Defines persona roles (e.g., researcher, student) and tasks (e.g., review, learn).

##### Enhances each document section with:

1) Persona relevance score

2) Key concepts

3) Persona-specific insights (e.g., "Methodology identified" for researchers)

##### Computes:

1) Job alignment score

2) Importance level: high, medium, low

3) Summary metadata for entire document

#### 3. src/ranks_section.py – Section Ranker
##### Ranks document sections based on:

1) Semantic relevance (TF-IDF-based)

2) Section length optimization

3) Position in document (earlier sections are prioritized)

4) Computes a composite score for each section.

## 👥 Supported Personas and Tasks

### 🎭 Roles:

🧪 Researcher

🎓 Student

📊 Analyst

🧑‍🏫 Teacher

👔 Manager

🚀 Entrepreneur

### 📌 Tasks:
🧐 Review

📚 Learn

🧵 Analyze

🛠️ Prepare

✍️ Summarize



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
