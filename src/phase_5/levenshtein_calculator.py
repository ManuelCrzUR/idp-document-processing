# -*- coding: utf-8 -*-
"""
Levenshtein Distance Calculator - From scratch implementation
No external dependencies for jiwer or similar libraries.
"""
import numpy as np
from typing import Tuple, List


class LevenshteinCalculator:
    """
    Calculate Levenshtein distance using dynamic programming.
    Supports both character-level and word-level distance.
    """

    @staticmethod
    def distance(s1, s2) -> Tuple[int, List[List[int]]]:
        """
        Calculate Levenshtein distance between two sequences.

        Args:
            s1: First sequence (string or list)
            s2: Second sequence (string or list)

        Returns:
            Tuple of (distance, dp_matrix)
            where distance is the minimum edit distance
            and dp_matrix is the DP table for analysis
        """
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # Initialize base cases
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],      # Deletion
                        dp[i][j - 1],      # Insertion
                        dp[i - 1][j - 1]   # Substitution
                    )

        return dp[m][n], dp

    @staticmethod
    def extract_operations(dp: List[List[int]], s1, s2) -> Tuple[int, int, int]:
        """
        Extract substitutions, deletions, and insertions from DP matrix.

        Args:
            dp: DP matrix from distance()
            s1: First sequence
            s2: Second sequence

        Returns:
            Tuple of (substitutions, deletions, insertions)
        """
        m, n = len(s1), len(s2)
        subs = dels = inserts = 0

        i, j = m, n
        while i > 0 or j > 0:
            if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
                i -= 1
                j -= 1
            elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
                subs += 1
                i -= 1
                j -= 1
            elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
                dels += 1
                i -= 1
            else:
                inserts += 1
                j -= 1

        return subs, dels, inserts
