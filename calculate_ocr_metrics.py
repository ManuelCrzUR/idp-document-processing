# -*- coding: utf-8 -*-
"""
Calculate OCR evaluation metrics: CER, WER, and related statistics.
Compare OCR output with ground truth text.
"""
import json
import sys
from pathlib import Path
from difflib import SequenceMatcher
from collections import Counter


def levenshtein_distance(s1, s2):
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def calculate_cer(reference, hypothesis):
    """Calculate Character Error Rate (CER)."""
    distance = levenshtein_distance(reference, hypothesis)
    if len(reference) == 0:
        return 0.0 if len(hypothesis) == 0 else 1.0
    return distance / len(reference)


def calculate_wer(reference_words, hypothesis_words):
    """Calculate Word Error Rate (WER)."""
    distance = levenshtein_distance(reference_words, hypothesis_words)
    if len(reference_words) == 0:
        return 0.0 if len(hypothesis_words) == 0 else 1.0
    return distance / len(reference_words)


def normalize_text(text):
    """Normalize text for comparison."""
    text = text.lower()
    text = text.strip()
    return text


def analyze_ocr_vs_ground_truth(ocr_text, ground_truth_text):
    """
    Comprehensive analysis of OCR vs ground truth.

    Args:
        ocr_text: Text extracted by OCR
        ground_truth_text: Reference/correct text

    Returns:
        Dictionary with all metrics
    """

    # Normalize texts
    ocr_norm = normalize_text(ocr_text)
    gt_norm = normalize_text(ground_truth_text)

    # Character level metrics
    cer = calculate_cer(gt_norm, ocr_norm)

    # Word level metrics
    gt_words = gt_norm.split()
    ocr_words = ocr_norm.split()
    wer = calculate_wer(gt_words, ocr_words)

    # String similarity
    matcher = SequenceMatcher(None, gt_norm, ocr_norm)
    similarity = matcher.ratio()

    # Character statistics
    gt_chars = len(gt_norm)
    ocr_chars = len(ocr_norm)
    char_diff = ocr_chars - gt_chars

    # Word statistics
    gt_word_count = len(gt_words)
    ocr_word_count = len(ocr_words)
    word_diff = ocr_word_count - gt_word_count

    # Matching characters
    matching_chars = sum(1 for a, b in zip(gt_norm, ocr_norm) if a == b)

    # Word-by-word analysis
    matching_words = 0
    for i in range(min(len(gt_words), len(ocr_words))):
        if gt_words[i] == ocr_words[i]:
            matching_words += 1

    # Common errors
    word_errors = []
    for i in range(min(len(gt_words), len(ocr_words))):
        if gt_words[i] != ocr_words[i]:
            word_errors.append({
                'position': i,
                'expected': gt_words[i],
                'got': ocr_words[i],
                'distance': levenshtein_distance(gt_words[i], ocr_words[i])
            })

    # Missing/Extra words
    if len(gt_words) != len(ocr_words):
        if len(gt_words) > len(ocr_words):
            missing_words = gt_words[len(ocr_words):]
            extra_words = []
        else:
            missing_words = []
            extra_words = ocr_words[len(gt_words):]
    else:
        missing_words = []
        extra_words = []

    # Build result dictionary
    metrics = {
        'timestamps': {
            'calculated': str(Path(__file__).stat().st_mtime)
        },

        'character_level_metrics': {
            'cer': round(cer, 4),
            'cer_percent': round(cer * 100, 2),
            'character_accuracy': round((1 - cer) * 100, 2),
            'ground_truth_chars': gt_chars,
            'ocr_chars': ocr_chars,
            'char_difference': char_diff,
            'matching_chars': matching_chars,
            'char_match_rate': round(matching_chars / gt_chars * 100, 2) if gt_chars > 0 else 0,
        },

        'word_level_metrics': {
            'wer': round(wer, 4),
            'wer_percent': round(wer * 100, 2),
            'word_accuracy': round((1 - wer) * 100, 2),
            'ground_truth_words': gt_word_count,
            'ocr_words': ocr_word_count,
            'word_difference': word_diff,
            'matching_words': matching_words,
            'word_match_rate': round(matching_words / gt_word_count * 100, 2) if gt_word_count > 0 else 0,
        },

        'string_similarity': {
            'similarity_ratio': round(similarity, 4),
            'similarity_percent': round(similarity * 100, 2),
        },

        'detailed_errors': {
            'total_word_errors': len(word_errors),
            'word_errors_sample': word_errors[:10],  # First 10 errors
            'missing_words_count': len(missing_words),
            'extra_words_count': len(extra_words),
            'missing_words_sample': missing_words[:5],
            'extra_words_sample': extra_words[:5],
        },

        'text_lengths': {
            'ground_truth_length': gt_chars,
            'ocr_length': ocr_chars,
            'ground_truth_word_count': gt_word_count,
            'ocr_word_count': ocr_word_count,
        }
    }

    return metrics


def main():
    """Main function to calculate OCR metrics."""

    # Load OCR extracted text
    ocr_txt_path = "pipeline_results/consolidated/ocr_extracted_text.txt"

    print("\n" + "=" * 100)
    print("OCR METRICS CALCULATION: CER, WER AND ANALYSIS")
    print("=" * 100 + "\n")

    if not Path(ocr_txt_path).exists():
        print(f"[ERROR] OCR text file not found: {ocr_txt_path}")
        return 1

    # Load OCR text
    with open(ocr_txt_path, 'r', encoding='utf-8') as f:
        ocr_content = f.read()

    # Extract actual text (skip header/footer)
    lines = ocr_content.split('\n')

    # Find start and end of actual content
    start_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('====') and i > 0:
            start_idx = i + 1
            break

    end_idx = len(lines)
    for i in range(start_idx, len(lines)):
        if lines[i].startswith('===='):
            end_idx = i
            break

    ocr_text = '\n'.join(lines[start_idx:end_idx]).strip()

    print(f"[*] Loaded OCR text: {len(ocr_text)} characters")
    print(f"[*] OCR words: {len(ocr_text.split())}")

    # Search for ground truth
    print("\n[*] Searching for ground truth files...")

    ground_truth_dir = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project\datos\spanishocr\texts")

    if not ground_truth_dir.exists():
        print(f"[WARNING] Ground truth directory not found: {ground_truth_dir}")
        print("[*] Using first available ground truth file...")
        gt_files = list(Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project\datos\spanishocr\texts").glob("*.txt"))
        if not gt_files:
            print("[ERROR] No ground truth files found")
            return 1
        gt_file = gt_files[0]
    else:
        # Get first ground truth file
        gt_files = list(ground_truth_dir.glob("*.txt"))
        if not gt_files:
            print(f"[ERROR] No text files in {ground_truth_dir}")
            return 1
        gt_file = gt_files[0]

    print(f"[OK] Found: {gt_file.name}")

    # Load ground truth
    with open(gt_file, 'r', encoding='utf-8') as f:
        ground_truth_text = f.read().strip()

    print(f"[OK] Loaded ground truth: {len(ground_truth_text)} characters")
    print(f"[OK] Ground truth words: {len(ground_truth_text.split())}")

    # Calculate metrics
    print("\n[*] Calculating metrics...")
    metrics = analyze_ocr_vs_ground_truth(ocr_text, ground_truth_text)

    # Display results
    print("\n" + "=" * 100)
    print("METRICS RESULTS")
    print("=" * 100 + "\n")

    print("[CHARACTER LEVEL]")
    print("-" * 100)
    cer_metrics = metrics['character_level_metrics']
    print(f"  CER (Character Error Rate):    {cer_metrics['cer_percent']:.2f}%")
    print(f"  Character Accuracy:            {cer_metrics['char_accuracy']:.2f}%")
    print(f"  Ground Truth Chars:            {cer_metrics['ground_truth_chars']:,}")
    print(f"  OCR Chars:                     {cer_metrics['ocr_chars']:,}")
    print(f"  Character Difference:          {cer_metrics['char_difference']:+,}")
    print(f"  Matching Characters:           {cer_metrics['matching_chars']:,} ({cer_metrics['char_match_rate']:.2f}%)")

    print("\n[WORD LEVEL]")
    print("-" * 100)
    wer_metrics = metrics['word_level_metrics']
    print(f"  WER (Word Error Rate):         {wer_metrics['wer_percent']:.2f}%")
    print(f"  Word Accuracy:                 {wer_metrics['word_accuracy']:.2f}%")
    print(f"  Ground Truth Words:            {wer_metrics['ground_truth_words']:,}")
    print(f"  OCR Words:                     {wer_metrics['ocr_words']:,}")
    print(f"  Word Difference:               {wer_metrics['word_difference']:+,}")
    print(f"  Matching Words:                {wer_metrics['matching_words']:,} ({wer_metrics['word_match_rate']:.2f}%)")

    print("\n[STRING SIMILARITY]")
    print("-" * 100)
    sim = metrics['string_similarity']
    print(f"  Similarity Ratio:              {sim['similarity_percent']:.2f}%")

    print("\n[ERROR ANALYSIS]")
    print("-" * 100)
    errors = metrics['detailed_errors']
    print(f"  Total Word Errors:             {errors['total_word_errors']}")
    print(f"  Missing Words:                 {errors['missing_words_count']}")
    print(f"  Extra Words:                   {errors['extra_words_count']}")

    if errors['word_errors_sample']:
        print(f"\n  Sample Errors (first 5):")
        for i, err in enumerate(errors['word_errors_sample'][:5], 1):
            print(f"    {i}. Pos {err['position']}: '{err['expected']}' -> '{err['got']}' (dist: {err['distance']})")

    # Save metrics JSON
    metrics_output_path = Path("pipeline_results/consolidated") / "ocr_evaluation_metrics.json"
    metrics_output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(metrics_output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Metrics saved to: {metrics_output_path}")

    # Save detailed report
    report_path = Path("pipeline_results/consolidated") / "ocr_evaluation_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("OCR EVALUATION REPORT\n")
        f.write("=" * 100 + "\n\n")

        f.write("CHARACTER LEVEL METRICS\n")
        f.write("-" * 100 + "\n")
        f.write(f"CER (Character Error Rate):    {cer_metrics['cer_percent']:.2f}%\n")
        f.write(f"Character Accuracy:            {cer_metrics['char_accuracy']:.2f}%\n")
        f.write(f"Ground Truth Characters:       {cer_metrics['ground_truth_chars']:,}\n")
        f.write(f"OCR Characters:                {cer_metrics['ocr_chars']:,}\n")
        f.write(f"Character Difference:          {cer_metrics['char_difference']:+,}\n")
        f.write(f"Matching Characters:           {cer_metrics['matching_chars']:,} ({cer_metrics['char_match_rate']:.2f}%)\n\n")

        f.write("WORD LEVEL METRICS\n")
        f.write("-" * 100 + "\n")
        f.write(f"WER (Word Error Rate):         {wer_metrics['wer_percent']:.2f}%\n")
        f.write(f"Word Accuracy:                 {wer_metrics['word_accuracy']:.2f}%\n")
        f.write(f"Ground Truth Words:            {wer_metrics['ground_truth_words']:,}\n")
        f.write(f"OCR Words:                     {wer_metrics['ocr_words']:,}\n")
        f.write(f"Word Difference:               {wer_metrics['word_difference']:+,}\n")
        f.write(f"Matching Words:                {wer_metrics['matching_words']:,} ({wer_metrics['word_match_rate']:.2f}%)\n\n")

        f.write("STRING SIMILARITY\n")
        f.write("-" * 100 + "\n")
        f.write(f"Similarity Ratio:              {sim['similarity_percent']:.2f}%\n\n")

        f.write("ERROR ANALYSIS\n")
        f.write("-" * 100 + "\n")
        f.write(f"Total Word Errors:             {errors['total_word_errors']}\n")
        f.write(f"Missing Words:                 {errors['missing_words_count']}\n")
        f.write(f"Extra Words:                   {errors['extra_words_count']}\n\n")

        if errors['word_errors_sample']:
            f.write("Sample Errors:\n")
            for i, err in enumerate(errors['word_errors_sample'][:10], 1):
                f.write(f"{i:2d}. Pos {err['position']:3d}: '{err['expected']}' -> '{err['got']}' (distance: {err['distance']})\n")

    print(f"[OK] Report saved to: {report_path}")

    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"\nCER: {cer_metrics['cer_percent']:.2f}%  (lower is better)")
    print(f"WER: {wer_metrics['wer_percent']:.2f}%  (lower is better)")
    print(f"Similarity: {sim['similarity_percent']:.2f}%  (higher is better)")
    print(f"\nAccuracy:")
    print(f"  - Character level: {cer_metrics['char_accuracy']:.2f}%")
    print(f"  - Word level: {wer_metrics['word_accuracy']:.2f}%")

    print("\n" + "=" * 100 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
