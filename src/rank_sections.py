"""
Section Ranker for Challenge 1B - Persona-Driven Document Intelligence
This script ranks document sections based on relevance and importance to a given persona and job context.
"""

import math
from typing import Dict, List, Any
from collections import Counter

class SectionRanker:
    """
    Ranks document sections based on relevance and importance.
    This class provides methods to rank sections of a document based on their relevance to a given persona and job context.
    """

    def __init__(self):
        """
        Initialize the SectionRanker.
        """
        pass

    def rank_sections(self, doc_sections: List[Dict[str, Any]], user_persona: Dict[str, str], job_details: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Rank sections by relevance to persona and job context.

        Args:
            doc_sections (List[Dict[str, Any]]): List of document sections to rank
            user_persona (Dict[str, str]): Dictionary containing user persona information
            job_details (Dict[str, str]): Dictionary containing job details

        Returns:
            List[Dict[str, Any]]: List of ranked document sections
        """
        if not doc_sections:
            return []

        # Create persona context from persona and job
        context_data = self._build_persona_context(user_persona, job_details)

        # Calculate scores for each section
        ranked_sections = []
        for doc_section in doc_sections:
            relevance_value = self._compute_final_score(doc_section, context_data)
            updated_section = doc_section.copy()
            updated_section['relevance_score'] = relevance_value
            updated_section['final_relevance_score'] = relevance_value
            ranked_sections.append(updated_section)

        # Sort by score descending
        ranked_sections.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return ranked_sections

    def _build_persona_context(self, user_persona: Dict[str, str], job_details: Dict[str, str]) -> Dict[str, Any]:
        """
        Build context dictionary from persona and job information.

        Args:
            user_persona (Dict[str, str]): Dictionary containing user persona information
            job_details (Dict[str, str]): Dictionary containing job details

        Returns:
            Dict[str, Any]: Dictionary containing combined persona context
        """
        return {
            "persona_role": user_persona.get("role", ""),
            "job_context": job_details.get("task", "")
        }

    def _compute_final_score(self, doc_section: Dict[str, Any], context_data: Dict[str, Any]) -> float:
        """
        Calculate composite relevance score for a document section.

        Args:
            doc_section (Dict[str, Any]): Dictionary containing document section information
            context_data (Dict[str, Any]): Dictionary containing persona context

        Returns:
            float: Composite relevance score
        """
        section_content = doc_section.get("content", "")
        if not section_content:
            return 0.0

        # TF-IDF based scoring
        semantic_score = self._compute_tfidf_relevance(section_content, context_data)

        # Length penalty (very short or very long sections get lower scores)
        length_weight = self._assess_content_length(section_content)

        # Position bonus (earlier sections might be more important)
        position_weight = self._compute_position_weight(doc_section)

        # Combine scores
        final_score = (0.6 * semantic_score + 0.3 * length_weight + 0.1 * position_weight)

        return min(final_score, 1.0)

    def _compute_tfidf_relevance(self, text_content: str, context_data: Dict[str, Any]) -> float:
        """
        Calculate TF-IDF based relevance score for a text content.

        Args:
            text_content (str): The text content to analyze
            context_data (Dict[str, Any]): Dictionary containing persona context

        Returns:
            float: TF-IDF based relevance score
        """
        role_keywords = self._extract_context_keywords(
            context_data.get("persona_role", ""),
            context_data.get("job_context", "")
        )

        if not role_keywords:
            return 0.5  # Default score if no context

        word_frequencies = self._calculate_word_frequencies(text_content)
        total_words = len(text_content.lower().split())

        relevance_sum = self._sum_keyword_scores(role_keywords, word_frequencies, total_words)

        return min(relevance_sum, 1.0)

    def _extract_context_keywords(self, role_info: str, task_info: str) -> set:
        """
        Extract relevant keywords from persona and job context.

        Args:
            role_info (str): Role information
            task_info (str): Task information

        Returns:
            set: Set of relevant keywords
        """
        combined_text = f"{role_info} {task_info}".lower()
        keyword_set = set(word for word in combined_text.split() if len(word) > 2)
        return keyword_set

    def _calculate_word_frequencies(self, text_content: str) -> Counter:
        """
        Calculate word frequency distribution for a text content.

        Args:
            text_content (str): The text content to analyze

        Returns:
            Counter: Word frequency distribution
        """
        word_list = text_content.lower().split()
        return Counter(word_list)

    def _sum_keyword_scores(self, keywords: set, word_freq: Counter, total_count: int) -> float:
        """
        Sum TF-IDF scores for all keywords.

        Args:
            keywords (set): Set of keywords
            word_freq (Counter): Word frequency distribution
            total_count (int): Total number of words

        Returns:
            float: Sum of TF-IDF scores
        """
        total_score = 0.0
        for keyword in keywords:
            if keyword in word_freq:
                term_frequency = word_freq[keyword] / total_count
                # Simple IDF approximation
                inverse_doc_freq = math.log(1 + 1 / max(1, word_freq[keyword]))
                total_score += term_frequency * inverse_doc_freq

        return total_score

    def _assess_content_length(self, text_content: str) -> float:
        """
        Calculate score based on content length.

        Args:
            text_content (str): The text content to analyze

        Returns:
            float: Score based on content length
        """
        word_count = len(text_content.split())

        if word_count < 10:
            return 0.3  # Too short
        elif word_count < 50:
            return 0.8  # Good length
        elif word_count < 200:
            return 1.0  # Ideal length
        elif word_count < 500:
            return 0.7  # Getting long
        else:
            return 0.4  # Too long

    def _compute_position_weight(self, doc_section: Dict[str, Any]) -> float:
        """
        Calculate score based on section position.

        Args:
            doc_section (Dict[str, Any]): Dictionary containing document section information

        Returns:
            float: Score based on section position
        """
        # Earlier sections get slight bonus
        idx = doc_section.get("position", 0)
        if idx < 3:
            return 1.0
        elif idx < 10:
            return 0.8
        else:
            return 0.6
