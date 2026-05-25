# -*- coding: utf-8 -*-
"""
Text Normalizer: Preprocessing for consistent text comparison
"""
import re
from typing import Optional


class TextNormalizer:
    """Normalize text for consistent comparison"""

    @staticmethod
    def normalize(
        text: str,
        lowercase: bool = True,
        remove_punctuation: bool = False,
        remove_extra_spaces: bool = True,
        remove_newlines: bool = True,
    ) -> str:
        """
        Normalize text for analysis.

        Args:
            text: Text to normalize
            lowercase: Convert to lowercase
            remove_punctuation: Remove punctuation marks
            remove_extra_spaces: Remove extra/multiple spaces
            remove_newlines: Remove newline characters

        Returns:
            Normalized text
        """
        if not text:
            return ""

        result = text

        # Convert to lowercase
        if lowercase:
            result = result.lower()

        # Remove newlines
        if remove_newlines:
            result = re.sub(r'\n+', ' ', result)

        # Remove extra spaces
        if remove_extra_spaces:
            result = re.sub(r'\s+', ' ', result)

        # Remove punctuation (optional)
        if remove_punctuation:
            result = re.sub(r'[^\w\s]', '', result)

        # Final strip
        result = result.strip()

        return result

    @staticmethod
    def normalize_for_cer(text: str) -> str:
        """
        Normalize text for Character Error Rate calculation.
        Keeps more information than generic normalization.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        if not text:
            return ""

        result = text.lower()
        result = re.sub(r'\n+', ' ', result)
        result = re.sub(r'\s+', ' ', result)
        result = result.strip()

        return result

    @staticmethod
    def normalize_for_wer(text: str) -> str:
        """
        Normalize text for Word Error Rate calculation.
        Tokenizes into words.

        Args:
            text: Text to normalize

        Returns:
            Space-separated words
        """
        if not text:
            return ""

        result = text.lower()
        result = re.sub(r'\n+', ' ', result)
        result = re.sub(r'\s+', ' ', result)
        result = result.strip()

        return result

    @staticmethod
    def tokenize_words(text: str) -> list:
        """
        Tokenize text into words.

        Args:
            text: Text to tokenize

        Returns:
            List of words
        """
        return text.split()

    @staticmethod
    def tokenize_characters(text: str) -> list:
        """
        Tokenize text into characters.

        Args:
            text: Text to tokenize

        Returns:
            List of characters
        """
        return list(text)
