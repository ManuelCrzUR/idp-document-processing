# -*- coding: utf-8 -*-
"""
Calculate accurate OCR evaluation metrics using the CORRECT ground truth file.
Ground truth file: train-00000_84.txt (matches the test document)
"""
import json
from pathlib import Path


def levenshtein_distance(s1, s2):
    """Calculate Levenshtein distance."""
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


def calculate_metrics(reference, hypothesis):
    """Calculate CER, WER, accuracy and detailed statistics."""
    ref = reference.lower().strip()
    hyp = hypothesis.lower().strip()

    ref_words = ref.split()
    hyp_words = hyp.split()

    # Character level
    cer_distance = levenshtein_distance(ref, hyp)
    cer = cer_distance / len(ref) if len(ref) > 0 else 0

    # Word level
    wer_distance = levenshtein_distance(ref_words, hyp_words)
    wer = wer_distance / len(ref_words) if len(ref_words) > 0 else 0

    # Accuracy
    char_accuracy = max(0, 1 - cer) * 100
    word_accuracy = max(0, 1 - wer) * 100

    # Character matching
    matching_chars = sum(1 for a, b in zip(ref, hyp) if a == b)

    # Word matching
    matching_words = sum(1 for a, b in zip(ref_words, hyp_words) if a == b)

    return {
        'cer': round(cer, 4),
        'cer_percent': round(cer * 100, 2),
        'char_accuracy': round(char_accuracy, 2),
        'wer': round(wer, 4),
        'wer_percent': round(wer * 100, 2),
        'word_accuracy': round(word_accuracy, 2),
        'reference_chars': len(ref),
        'hypothesis_chars': len(hyp),
        'char_difference': len(hyp) - len(ref),
        'matching_chars': matching_chars,
        'matching_chars_percent': round((matching_chars / len(ref) * 100) if len(ref) > 0 else 0, 2),
        'reference_words': len(ref_words),
        'hypothesis_words': len(hyp_words),
        'word_difference': len(hyp_words) - len(ref_words),
        'matching_words': matching_words,
        'matching_words_percent': round((matching_words / len(ref_words) * 100) if len(ref_words) > 0 else 0, 2),
    }


def main():
    print("\n" + "=" * 110)
    print("OCR EVALUATION: ACCURATE METRICS WITH CORRECT GROUND TRUTH")
    print("=" * 110 + "\n")

    # Load OCR text
    ocr_txt = "pipeline_results/consolidated/ocr_extracted_text.txt"
    if not Path(ocr_txt).exists():
        print(f"[ERROR] Not found: {ocr_txt}")
        return 1

    with open(ocr_txt, 'r', encoding='utf-8') as f:
        ocr_content = f.read()

    # Extract text (skip header/footer)
    lines = ocr_content.split('\n')
    ocr_text = '\n'.join([l for l in lines if not l.startswith('=') and l.strip()]).strip()

    # Remove total statistics lines
    ocr_text = '\n'.join([l for l in ocr_text.split('\n') if not l.startswith('Total ')]).strip()

    print(f"[OK] Loaded OCR text: {len(ocr_text):,} chars, {len(ocr_text.split()):,} words")

    # Use correct ground truth file: train-00000_84.txt
    gt_file = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project\datos\spanishocr\texts\train-00000_84.txt")

    if not gt_file.exists():
        print(f"[ERROR] Ground truth file not found: {gt_file}")
        return 1

    with open(gt_file, 'r', encoding='utf-8') as f:
        gt_text = f.read().strip()

    print(f"[OK] Ground truth (train-00000_84.txt): {len(gt_text):,} chars, {len(gt_text.split()):,} words")
    print(f"[OK] GROUND TRUTH IS CORRECTLY MATCHED TO THIS DOCUMENT\n")

    # Calculate metrics
    print("[*] Calculating metrics...")
    metrics = calculate_metrics(gt_text, ocr_text)

    # Display results
    print("\n" + "=" * 110)
    print("RESULTS - CHARACTER LEVEL METRICS")
    print("=" * 110 + "\n")

    print(f"  CER (Character Error Rate):          {metrics['cer_percent']:6.2f}%")
    print(f"  Character Accuracy:                  {metrics['char_accuracy']:6.2f}%")
    print(f"  Ground Truth Characters:             {metrics['reference_chars']:>7,}")
    print(f"  OCR Extracted Characters:            {metrics['hypothesis_chars']:>7,}")
    print(f"  Character Difference:                {metrics['char_difference']:>7,}")
    print(f"  Matching Characters:                 {metrics['matching_chars']:>7,} ({metrics['matching_chars_percent']:5.2f}%)")

    print("\n" + "=" * 110)
    print("RESULTS - WORD LEVEL METRICS")
    print("=" * 110 + "\n")

    print(f"  WER (Word Error Rate):               {metrics['wer_percent']:6.2f}%")
    print(f"  Word Accuracy:                       {metrics['word_accuracy']:6.2f}%")
    print(f"  Ground Truth Words:                  {metrics['reference_words']:>7,}")
    print(f"  OCR Extracted Words:                 {metrics['hypothesis_words']:>7,}")
    print(f"  Word Difference:                     {metrics['word_difference']:>7,}")
    print(f"  Matching Words:                      {metrics['matching_words']:>7,} ({metrics['matching_words_percent']:5.2f}%)")

    # Save to JSON
    output_json = Path("pipeline_results/consolidated/ocr_evaluation_metrics_CORRECT.json")
    output_json.parent.mkdir(parents=True, exist_ok=True)

    eval_metrics = {
        'ground_truth_file': 'train-00000_84.txt',
        'ground_truth_status': 'CORRECTLY MATCHED',
        'character_level': {
            'cer': metrics['cer'],
            'cer_percent': metrics['cer_percent'],
            'accuracy': metrics['char_accuracy'],
            'reference_chars': metrics['reference_chars'],
            'hypothesis_chars': metrics['hypothesis_chars'],
            'char_difference': metrics['char_difference'],
            'matching_chars': metrics['matching_chars'],
            'matching_chars_percent': metrics['matching_chars_percent'],
        },
        'word_level': {
            'wer': metrics['wer'],
            'wer_percent': metrics['wer_percent'],
            'accuracy': metrics['word_accuracy'],
            'reference_words': metrics['reference_words'],
            'hypothesis_words': metrics['hypothesis_words'],
            'word_difference': metrics['word_difference'],
            'matching_words': metrics['matching_words'],
            'matching_words_percent': metrics['matching_words_percent'],
        },
        'summary': {
            'status': 'EVALUATION COMPLETE WITH CORRECT GROUND TRUTH',
            'interpretation': get_interpretation(metrics['cer'], metrics['wer']),
            'document_type': 'SMV Document - Directores Independientes (BICENTENARIO)',
            'evaluation_date': '2026-05-25'
        }
    }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(eval_metrics, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Metrics saved to: {output_json}")

    # Save text report
    output_txt = Path("pipeline_results/consolidated/ocr_evaluation_report_CORRECT.txt")
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write("=" * 110 + "\n")
        f.write("OCR EVALUATION REPORT - ACCURATE METRICS WITH CORRECT GROUND TRUTH\n")
        f.write("=" * 110 + "\n\n")
        f.write(f"Ground Truth File: train-00000_84.txt (CORRECTLY MATCHED)\n")
        f.write(f"Document Type: SMV Document - Directores Independientes (Bicentenario)\n")
        f.write(f"Evaluation Date: 2026-05-25\n\n")

        f.write("CHARACTER LEVEL METRICS\n")
        f.write("-" * 110 + "\n")
        f.write(f"CER (Character Error Rate):          {metrics['cer_percent']:6.2f}%\n")
        f.write(f"Character Accuracy:                  {metrics['char_accuracy']:6.2f}%\n")
        f.write(f"Ground Truth Characters:             {metrics['reference_chars']:,}\n")
        f.write(f"OCR Extracted Characters:            {metrics['hypothesis_chars']:,}\n")
        f.write(f"Character Difference:                {metrics['char_difference']:+,}\n")
        f.write(f"Matching Characters:                 {metrics['matching_chars']:,} ({metrics['matching_chars_percent']:.2f}%)\n\n")

        f.write("WORD LEVEL METRICS\n")
        f.write("-" * 110 + "\n")
        f.write(f"WER (Word Error Rate):               {metrics['wer_percent']:6.2f}%\n")
        f.write(f"Word Accuracy:                       {metrics['word_accuracy']:6.2f}%\n")
        f.write(f"Ground Truth Words:                  {metrics['reference_words']:,}\n")
        f.write(f"OCR Extracted Words:                 {metrics['hypothesis_words']:,}\n")
        f.write(f"Word Difference:                     {metrics['word_difference']:+,}\n")
        f.write(f"Matching Words:                      {metrics['matching_words']:,} ({metrics['matching_words_percent']:.2f}%)\n\n")

        f.write("INTERPRETATION\n")
        f.write("-" * 110 + "\n")
        f.write(get_interpretation(metrics['cer'], metrics['wer']))

    print(f"[OK] Report saved to: {output_txt}")

    print("\n" + "=" * 110)
    print("SUMMARY")
    print("=" * 110)
    print(f"\nCER: {metrics['cer_percent']:.2f}%  (lower is better, <5% is excellent)")
    print(f"WER: {metrics['wer_percent']:.2f}%  (lower is better, <5% is excellent)")
    print(f"Character Accuracy: {metrics['char_accuracy']:.2f}%  (higher is better)")
    print(f"Word Accuracy: {metrics['word_accuracy']:.2f}%  (higher is better)")
    print(f"\nInterpretation: {get_interpretation(metrics['cer'], metrics['wer']).strip()}")

    print("\n" + "=" * 110 + "\n")
    return 0


def get_interpretation(cer, wer):
    """Get interpretation of metrics."""
    if cer < 0.05 and wer < 0.05:
        return "EXCELLENT: Near-perfect OCR quality\n"
    elif cer < 0.1 and wer < 0.1:
        return "VERY GOOD: High quality OCR, minor errors\n"
    elif cer < 0.2 and wer < 0.2:
        return "GOOD: Acceptable OCR quality\n"
    elif cer < 0.5 and wer < 0.5:
        return "FAIR: Significant errors present\n"
    else:
        return "POOR: High error rate, major issues\n"


if __name__ == "__main__":
    import sys
    sys.exit(main())
