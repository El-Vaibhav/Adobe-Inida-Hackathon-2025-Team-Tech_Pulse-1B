"""
Document Analyzer for Challenge 1B - Persona-Driven Document Intelligence
This script handles PDF text extraction and basic document structure analysis.
It is designed to extract and analyze content from PDF documents, detecting sections
based on headers, paragraphs, and lists.
"""

import fitz  # PyMuPDF library for handling PDF files
import re  # Regular expressions for text pattern matching
from pathlib import Path  # For handling file paths
from typing import Dict, List, Any, Tuple  # Type hints for better code clarity
from datetime import datetime  # For timestamping document processing

class DocumentAnalyzer:
    """
    Analyzes PDF documents and extracts structured content.
    This class provides methods to extract text, detect sections, and generate metadata from PDFs.
    """

    def __init__(self):
        # Initialize parameters for section detection
        self.min_section_length = 30  # Minimum length of a valid section
        self.max_section_length = 2000  # Maximum length of a valid section
        self.max_sections = 50  # Maximum number of sections to detect
        self.max_lookahead_lines = 5  # Maximum lines to look ahead for section content

    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """
        Extract and analyze content from a PDF document.

        Args:
            file_path (str): Path to the PDF file

        Returns:
            Dictionary containing document analysis results including metadata, full text,
            page contents, and detected sections.
        """
        try:
            # Open the PDF file
            doc = fitz.open(file_path)
            full_text, page_contents = self._extract_pdf_content(doc)
            doc.close()

            # Detect sections and generate metadata
            sections = self._detect_sections(full_text, Path(file_path).name, page_contents)
            metadata = self._generate_metadata(file_path, page_contents, full_text, sections)

            return {
                "metadata": metadata,
                "full_text": full_text,
                "pages": page_contents,
                "sections": sections
            }

        except Exception as e:
            # Handle any exceptions and return an error response
            return self._create_error_response(file_path, e)

    def _extract_pdf_content(self, doc) -> Tuple[str, List[Dict]]:
        """
        Extract text content from PDF document.

        Args:
            doc: The PDF document object

        Returns:
            Tuple containing the full text of the document and a list of page contents
        """
        full_text = ""
        page_contents = []

        # Iterate through each page in the document
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            full_text += page_text + "\n"

            # Store page content details
            page_contents.append({
                "page_number": page_num + 1,
                "text": page_text.strip(),
                "char_count": len(page_text)
            })

        return full_text, page_contents

    def _generate_metadata(self, file_path: str, pages: List[Dict],
                          full_text: str, sections: List[Dict]) -> Dict[str, Any]:
        """
        Generate document metadata.

        Args:
            file_path (str): Path to the PDF file
            pages (List[Dict]): List of page contents
            full_text (str): Full text of the document
            sections (List[Dict]): Detected sections in the document

        Returns:
            Dictionary containing metadata about the document
        """
        return {
            "filename": Path(file_path).name,
            "total_pages": len(pages),
            "total_characters": len(full_text),
            "total_sections": len(sections),
            "processing_timestamp": datetime.now().isoformat()
        }

    def _create_error_response(self, file_path: str, error: Exception) -> Dict[str, Any]:
        """
        Create error response for failed document processing.

        Args:
            file_path (str): Path to the PDF file
            error (Exception): The exception that occurred

        Returns:
            Dictionary containing error details
        """
        print(f"Error analyzing document {file_path}: {str(error)}")
        return {
            "metadata": {"filename": Path(file_path).name, "error": str(error)},
            "full_text": "",
            "pages": [],
            "sections": []
        }

    def _detect_sections(self, text: str, filename: str, pages: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detect logical sections within the document text.

        Args:
            text (str): Full text of the document
            filename (str): Name of the file
            pages (List[Dict]): List of page contents

        Returns:
            List of detected sections
        """
        sections = []

        # Apply different detection strategies
        sections.extend(self._detect_by_headers(text, pages))
        sections.extend(self._detect_by_paragraphs(text, pages))
        sections.extend(self._detect_by_lines(text, pages))

        # Process and deduplicate sections
        return self._process_detected_sections(sections, filename)

    def _process_detected_sections(self, sections: List[Dict], filename: str) -> List[Dict[str, Any]]:
        """
        Remove duplicates and add metadata to detected sections.

        Args:
            sections (List[Dict]): List of detected sections
            filename (str): Name of the file

        Returns:
            List of unique sections with added metadata
        """
        unique_sections = []
        seen_titles = set()

        for i, section in enumerate(sections):
            if self._is_valid_section(section, seen_titles):
                section.update({
                    "section_id": f"{filename}_section_{i+1}",
                    "word_count": len(section.get("content", "").split()),
                    "confidence_score": self._calculate_confidence(section)
                })
                unique_sections.append(section)
                seen_titles.add(section["section_title"])

        return unique_sections[:self.max_sections]

    def _is_valid_section(self, section: Dict[str, Any], seen_titles: set) -> bool:
        """
        Check if a section is valid and not a duplicate.

        Args:
            section (Dict[str, Any]): The section to validate
            seen_titles (set): Set of already seen section titles

        Returns:
            bool: True if the section is valid and not a duplicate
        """
        title = section.get("section_title", "")
        return title and title not in seen_titles and len(title) > 3

    def _detect_by_headers(self, text: str, pages: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detect heading-style sections.

        Args:
            text (str): Full text of the document
            pages (List[Dict]): List of page contents

        Returns:
            List of sections detected by headers
        """
        sections = []
        patterns = self._get_header_patterns()

        for page_info in pages:
            page_sections = self._find_headers_in_page(page_info, patterns)
            sections.extend(page_sections)

        return sections

    def _get_header_patterns(self) -> List[str]:
        """
        Get regex patterns for header detection.

        Returns:
            List of regex patterns for detecting headers
        """
        return [
            r'^([A-Z][A-Z\s]{5,40})$',  # ALL CAPS headers
            r'^(\d+\.?\s+[A-Z][^.!?]*?)(?:\n|$)',  # Numbered headers
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):',  # Title Case with colon
            r'(?:Chapter|Section)\s+\d+[:\-\s]*(.+)',  # Chapter/Section titles
        ]

    def _find_headers_in_page(self, page_info: Dict, patterns: List[str]) -> List[Dict[str, Any]]:
        """
        Find headers in a single page.

        Args:
            page_info (Dict): Information about the page
            patterns (List[str]): List of regex patterns for headers

        Returns:
            List of sections detected by headers in the page
        """
        sections = []
        page_num = page_info["page_number"]
        page_text = page_info["text"]
        lines = page_text.split('\n')

        for line in lines:
            line = line.strip()
            if not self._is_valid_line(line):
                continue

            header_match = self._match_header_patterns(line, patterns)
            if header_match:
                section = self._create_header_section(header_match, page_text, page_num)
                if section:
                    sections.append(section)

        return sections

    def _is_valid_line(self, line: str) -> bool:
        """
        Check if a line is valid for header detection.

        Args:
            line (str): The line to check

        Returns:
            bool: True if the line is valid
        """
        return bool(line and len(line) >= 5)

    def _match_header_patterns(self, line: str, patterns: List[str]) -> str:
        """
        Try to match line against header patterns.

        Args:
            line (str): The line to match
            patterns (List[str]): List of regex patterns

        Returns:
            str: The matched header title or None
        """
        for pattern in patterns:
            match = re.search(pattern, line, re.MULTILINE)
            if match:
                title = match.group(1).strip().rstrip(':')
                if 5 < len(title) < 80:
                    return title
        return None

    def _create_header_section(self, title: str, page_text: str, page_num: int) -> Dict[str, Any]:
        """
        Create a section from detected header.

        Args:
            title (str): The header title
            page_text (str): Text of the page
            page_num (int): Page number

        Returns:
            Dictionary representing the section or None if content extraction fails
        """
        content = self._extract_content_after_header(page_text, title)
        if content:
            return {
                "section_title": title,
                "page_number": page_num,
                "content": content,
                "detection_method": "header"
            }
        return None

    def _detect_by_paragraphs(self, text: str, pages: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detect paragraph-based sections.

        Args:
            text (str): Full text of the document
            pages (List[Dict]): List of page contents

        Returns:
            List of sections detected by paragraphs
        """
        sections = []

        for page_info in pages:
            page_sections = self._extract_paragraph_sections(page_info)
            sections.extend(page_sections)

        return sections

    def _extract_paragraph_sections(self, page_info: Dict) -> List[Dict[str, Any]]:
        """
        Extract sections from paragraphs in a page.

        Args:
            page_info (Dict): Information about the page

        Returns:
            List of sections detected by paragraphs in the page
        """
        sections = []
        page_num = page_info["page_number"]
        page_text = page_info["text"]

        paragraphs = [p.strip() for p in page_text.split('\n\n') if p.strip()]

        for paragraph in paragraphs:
            if self._is_valid_paragraph_length(paragraph):
                section = self._create_paragraph_section(paragraph, page_num)
                sections.append(section)

        return sections

    def _is_valid_paragraph_length(self, paragraph: str) -> bool:
        """
        Check if paragraph length is within valid range.

        Args:
            paragraph (str): The paragraph to check

        Returns:
            bool: True if the paragraph length is valid
        """
        return self.min_section_length <= len(paragraph) <= self.max_section_length

    def _create_paragraph_section(self, paragraph: str, page_num: int) -> Dict[str, Any]:
        """
        Create a section from a paragraph.

        Args:
            paragraph (str): The paragraph text
            page_num (int): Page number

        Returns:
            Dictionary representing the section
        """
        title = self._generate_paragraph_title(paragraph)
        return {
            "section_title": title,
            "page_number": page_num,
            "content": paragraph,
            "detection_method": "paragraph"
        }

    def _generate_paragraph_title(self, paragraph: str) -> str:
        """
        Generate title from paragraph's first sentence.

        Args:
            paragraph (str): The paragraph text

        Returns:
            str: Generated title from the first sentence
        """
        sentences = paragraph.split('. ')
        first_sentence = sentences[0]
        return first_sentence[:50] + "..." if len(first_sentence) > 50 else first_sentence

    def _detect_by_lines(self, text: str, pages: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detect line-based structured content.

        Args:
            text (str): Full text of the document
            pages (List[Dict]): List of page contents

        Returns:
            List of sections detected by lines
        """
        sections = []

        for page_info in pages:
            page_sections = self._extract_list_sections(page_info)
            sections.extend(page_sections)

        return sections

    def _extract_list_sections(self, page_info: Dict) -> List[Dict[str, Any]]:
        """
        Extract list-based sections from a page.

        Args:
            page_info (Dict): Information about the page

        Returns:
            List of sections detected by lists in the page
        """
        sections = []
        page_num = page_info["page_number"]
        page_text = page_info["text"]
        lines = page_text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            if self._is_list_item(line):
                section = self._create_list_section(lines, i, page_num)
                if section:
                    sections.append(section)

        return sections

    def _is_list_item(self, line: str) -> bool:
        """
        Check if line is a list item.

        Args:
            line (str): The line to check

        Returns:
            bool: True if the line is a list item
        """
        return bool(re.match(r'^[\•\-\*]\s+.+', line) or re.match(r'^\d+[\.\)]\s+.+', line))

    def _create_list_section(self, lines: List[str], start_index: int, page_num: int) -> Dict[str, Any]:
        """
        Create a section from list items.

        Args:
            lines (List[str]): List of lines in the page
            start_index (int): Starting index of the list
            page_num (int): Page number

        Returns:
            Dictionary representing the section or None if content is too short
        """
        line = lines[start_index].strip()
        title = line[:50] + "..." if len(line) > 50 else line
        content = self._gather_list_content(lines, start_index)

        if len(content) > self.min_section_length:
            return {
                "section_title": title,
                "page_number": page_num,
                "content": content,
                "detection_method": "list"
            }
        return None

    def _gather_list_content(self, lines: List[str], start_index: int) -> str:
        """
        Gather related list content starting from given index.

        Args:
            lines (List[str]): List of lines in the page
            start_index (int): Starting index of the list

        Returns:
            str: Gathered content
        """
        content = lines[start_index].strip()

        for j in range(start_index + 1, min(len(lines), start_index + self.max_lookahead_lines + 1)):
            next_line = lines[j].strip()
            if not next_line:
                continue

            if self._is_continuation_line(next_line):
                content += "\n" + next_line if self._is_list_item(next_line) else " " + next_line
            else:
                break

        return content

    def _is_continuation_line(self, line: str) -> bool:
        """
        Check if line continues the current list section.

        Args:
            line (str): The line to check

        Returns:
            bool: True if the line continues the current list section
        """
        return (self._is_list_item(line) or
                (line and not re.match(r'^[A-Z]', line)))

    def _extract_content_after_header(self, page_text: str, header_line: str) -> str:
        """
        Extract content that follows a detected header.

        Args:
            page_text (str): Text of the page
            header_line (str): The header line

        Returns:
            str: Extracted content following the header
        """
        lines = page_text.split('\n')
        content_lines = []
        found_header = False

        for line in lines:
            if self._is_header_line(line, header_line):
                found_header = True
                continue

            if found_header:
                if self._should_stop_content_extraction(line, content_lines):
                    break
                content_lines.append(line.strip())

        return ' '.join(content_lines)

    def _is_header_line(self, line: str, header_line: str) -> bool:
        """
        Check if current line matches the header.

        Args:
            line (str): The line to check
            header_line (str): The header line

        Returns:
            bool: True if the current line matches the header
        """
        return header_line.strip() in line.strip()

    def _should_stop_content_extraction(self, line: str, content_lines: List[str]) -> bool:
        """
        Determine if content extraction should stop.

        Args:
            line (str): The current line
            content_lines (List[str]): List of extracted content lines

        Returns:
            bool: True if content extraction should stop
        """
        line = line.strip()
        if not line:
            return False

        # Stop if we hit another header
        if (re.match(r'^[A-Z][A-Z\s]{5,}$', line) or
            re.match(r'^\d+\.?\s+[A-Z]', line)):
            return True

        # Stop if content is too long
        return len(' '.join(content_lines)) > self.max_section_length

    def _calculate_confidence(self, section: Dict[str, Any]) -> float:
        """
        Calculate confidence score for a detected section.

        Args:
            section (Dict[str, Any]): The section to calculate confidence for

        Returns:
            float: Confidence score
        """
        content = section.get("content", "")
        title = section.get("section_title", "")
        method = section.get("detection_method", "")

        score = self._get_base_confidence_score()
        score += self._get_method_score(method)
        score += self._get_content_quality_score(content, title)

        return min(score, 1.0)

    def _get_base_confidence_score(self) -> float:
        """
        Get base confidence score.

        Returns:
            float: Base confidence score
        """
        return 0.5

    def _get_method_score(self, method: str) -> float:
        """
        Get confidence score based on detection method.

        Args:
            method (str): The detection method

        Returns:
            float: Confidence score based on the method
        """
        method_scores = {
            "header": 0.3,
            "paragraph": 0.2,
            "list": 0.1
        }
        return method_scores.get(method, 0.0)

    def _get_content_quality_score(self, content: str, title: str) -> float:
        """
        Get confidence score based on content quality.

        Args:
            content (str): The section content
            title (str): The section title

        Returns:
            float: Confidence score based on content quality
        """
        score = 0.0
        if len(content) > 100:
            score += 0.1
        if len(title) > 10:
            score += 0.1
        return score
