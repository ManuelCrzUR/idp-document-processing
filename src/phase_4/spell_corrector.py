# -*- coding: utf-8 -*-
"""
Spell Corrector: Levenshtein-based word correction
"""
import re
from typing import List, Dict, Set, Tuple
from pathlib import Path


class LevenshteinCalculator:
    """Calculate Levenshtein distance between strings"""

    @staticmethod
    def distance(s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance using dynamic programming.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Minimum edit distance
        """
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        return dp[m][n]


class SpellCorrector:
    """Spell correction using Levenshtein distance"""

    def __init__(
        self,
        levenshtein_threshold: int = 2,
        min_word_length: int = 3,
    ):
        """
        Args:
            levenshtein_threshold: Maximum distance to consider as correction candidate
            min_word_length: Minimum word length to attempt correction
        """
        self.threshold = levenshtein_threshold
        self.min_length = min_word_length
        self.calculator = LevenshteinCalculator()
        self.dictionary = self._load_dictionary()

    def _load_dictionary(self) -> Set[str]:
        """
        Load Spanish dictionary.
        Falls back to basic Spanish words if file not available.

        Returns:
            Set of valid Spanish words
        """
        dict_file = Path(__file__).parent.parent / "data" / "spanish_dict.txt"

        if dict_file.exists():
            try:
                with open(dict_file, 'r', encoding='utf-8') as f:
                    return set(word.strip().lower() for word in f if word.strip())
            except Exception:
                pass

        # Fallback: basic Spanish words
        return {
            'el', 'la', 'de', 'y', 'a', 'en', 'que', 'es', 'se', 'se',
            'no', 'por', 'con', 'para', 'una', 'sus', 'al', 'lo', 'como',
            'más', 'o', 'pero', 'sus', 'le', 'ya', 'o', 'fue', 'este',
            'sí', 'porque', 'esta', 'son', 'entre', 'está', 'cuando',
            'muy', 'sin', 'sobre', 'ser', 'tiene', 'también', 'me', 'hasta',
            'hay', 'donde', 'han', 'quien', 'están', 'estado', 'desde',
            'todo', 'nos', 'durante', 'estados', 'todos', 'uno', 'les',
            'ni', 'contra', 'otros', 'fueron', 'ese', 'eso', 'había',
            'ante', 'ellos', 'otro', 'otras', 'nuestra', 'esa', 'esos',
            'ahora', 'mismo', 'nuestro', 'durante', 'sea', 'ellas',
            'documento', 'número', 'fecha', 'persona', 'empresa', 'monto',
            'total', 'pago', 'banco', 'cuenta', 'concepto', 'descripción',
        }

    def correct_word(self, word: str) -> str:
        """
        Correct a single word if needed.

        Args:
            word: Word to correct

        Returns:
            Corrected word (original if no correction found)
        """
        word_lower = word.lower()

        # Don't correct short words, numbers, or already-correct words
        if len(word_lower) < self.min_length or word_lower.isdigit():
            return word

        if word_lower in self.dictionary:
            return word

        # Find candidates with Levenshtein distance <= threshold
        best_match = None
        best_distance = self.threshold + 1

        for dict_word in self.dictionary:
            if abs(len(dict_word) - len(word_lower)) > self.threshold:
                continue

            distance = self.calculator.distance(word_lower, dict_word)
            if distance <= self.threshold and distance < best_distance:
                best_match = dict_word
                best_distance = distance

        # Return match if found, otherwise original
        if best_match:
            return best_match if word.islower() else best_match.capitalize()
        return word

    def correct_text(self, text: str) -> str:
        """
        Correct text by correcting individual words.

        Args:
            text: Text to correct

        Returns:
            Corrected text
        """
        # Split preserving punctuation
        words = re.findall(r'\b\w+\b|\W+', text)

        corrected = []
        for token in words:
            if token and token[0].isalpha():
                corrected.append(self.correct_word(token))
            else:
                corrected.append(token)

        return ''.join(corrected)

    def correct_blocks(self, blocks: List[Dict]) -> List[Dict]:
        """
        Correct text in OCR blocks.

        Args:
            blocks: List of OCR blocks with 'texto' field

        Returns:
            Blocks with corrected text
        """
        corrected_blocks = []
        for block in blocks:
            corrected_block = block.copy()
            if 'texto' in block:
                corrected_block['texto'] = self.correct_text(block['texto'])
            corrected_blocks.append(corrected_block)

        return corrected_blocks
