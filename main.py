import json
import os
from pathlib import Path
from datetime import datetime
from utils.parser import extract_text_from_pdf  # Assumed to return a list of pages with "text" and "page_number"

# To run, just navigate to the correct directory 
# and run: docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none team_tech_pulse_solution_2:69

def load_json_config(config_path):
    """
    Load JSON configuration from a file.

    Args:
        config_path (str): Path to the JSON configuration file.

    Returns:
        dict: The loaded JSON configuration.
    """
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)

def colored_terminal_text(text, color_code):
    """
    Return colored text for terminal output.

    Args:
        text (str): Text to color.
        color_code (str): ANSI color code.

    Returns:
        str: Colored text.
    """
    return f"\033[{color_code}m{text}\033[0m"

def extract_sample_pages(pdf_path, num_pages=3):
    """
    Extract text from the first few pages of a PDF.

    Args:
        pdf_path (str): Path to the PDF file.
        num_pages (int): Number of pages to extract.

    Returns:
        list: List of pages with text and page number.
    """
    all_pages = extract_text_from_pdf(pdf_path)
    return all_pages[:num_pages]

def append_metadata(metadata, document_path):
    """
    Append filename to metadata.

    Args:
        metadata (dict): Metadata dictionary to update.
        document_path (str): Path to the document.
    """
    filename = os.path.basename(document_path)
    metadata["input_documents"].append(filename)

def add_extracted_section(sections, doc_path, rank, page_num, section_title):
    """
    Add extracted section details with section title from content.

    Args:
        sections (list): List to append the section details.
        doc_path (str): Path to the document.
        rank (int): Importance rank of the section.
        page_num (int): Page number.
        section_title (str): Title of the section.
    """
    filename = os.path.basename(doc_path)
    sections.append({
        "document": filename,
        "section_title": section_title,
        "importance_rank": rank,
        "page_number": page_num
    })

def add_subsection_analysis(analysis, doc_path, text, page_num):
    """
    Add subsection analysis details with filename only.

    Args:
        analysis (list): List to append the analysis details.
        doc_path (str): Path to the document.
        text (str): Text content of the subsection.
        page_num (int): Page number.
    """
    filename = os.path.basename(doc_path)
    analysis.append({
        "document": filename,
        "refined_text": text[:300],  # Trim text for preview
        "page_number": page_num
    })

def extract_section_title_from_text(text):
    """
    Extract the first non-empty line from page text to use as section title.

    Args:
        text (str): Text from which to extract the section title.

    Returns:
        str: The extracted section title.
    """
    lines = text.strip().splitlines()
    for line in lines:
        clean_line = line.strip()
        if clean_line:
            return clean_line
    return "Unknown Section"

def process_single_document(doc_path, output_data):
    """
    Process a single document using its full path.

    Args:
        doc_path (str): Path to the document.
        output_data (dict): Dictionary to store output data.
    """
    pdf_path = Path(doc_path)
    if not pdf_path.exists():
        print(colored_terminal_text(f"❌ File not found: {pdf_path}", "31"))
        return

    sample_pages = extract_sample_pages(str(pdf_path))
    append_metadata(output_data["metadata"], doc_path)

    for idx, page in enumerate(sample_pages):
        section_title = extract_section_title_from_text(page["text"])
        add_extracted_section(
            output_data["extracted_sections"],
            doc_path,
            idx + 1,
            page["page_number"],
            section_title
        )
        add_subsection_analysis(
            output_data["subsection_analysis"],
            doc_path,
            page["text"],
            page["page_number"]
        )

def process_input_spec(input_spec_path, output_dir_path):
    """
    Process documents as per input spec and write output JSON.

    Args:
        input_spec_path (str): Path to the input specification file.
        output_dir_path (str): Path to the output directory.
    """
    config = load_json_config(input_spec_path)
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()

    output_data = {
        "metadata": {
            "input_documents": [],
            "persona": config["persona"],
            "job_to_be_done": config["job_to_be_done"],
            "processing_timestamp": timestamp
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    for doc_path in config["documents"]:
        process_single_document(doc_path, output_data)

    output_file = output_dir / "challenge1b_output.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=2)

    print(colored_terminal_text(f"✅ Output written to {output_file}", "32"))

def main():
    """
    Main function to process input specification files.
    """
    input_spec_dir = Path("Input_specs")
    input_specs = sorted(input_spec_dir.glob("input_spec_*.json"))

    if not input_specs:
        print(colored_terminal_text("❌ No input spec files found in Input_specs/", "31"))
        return

    for idx, spec_file in enumerate(input_specs, start=1):
        output_dir = f"output_{idx}" if idx > 1 else "output"
        print(colored_terminal_text(f"\n📄 Processing {spec_file.name}", "34"))
        process_input_spec(spec_file, output_dir)

if __name__ == "__main__":
    main()
