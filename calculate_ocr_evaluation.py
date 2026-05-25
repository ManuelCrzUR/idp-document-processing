# -*- coding: utf-8 -*-
"""
Calculate OCR evaluation metrics: CER, WER, accuracy.
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
    """Calculate CER, WER, and other metrics."""

    ref = reference.lower().strip()
    hyp = hypothesis.lower().strip()

    ref_words = ref.split()
    hyp_words = hyp.split()

    # Character level
    cer = levenshtein_distance(ref, hyp) / len(ref) if len(ref) > 0 else 0

    # Word level
    wer = levenshtein_distance(ref_words, hyp_words) / len(ref_words) if len(ref_words) > 0 else 0

    # Accuracy
    char_accuracy = max(0, 1 - cer) * 100
    word_accuracy = max(0, 1 - wer) * 100

    return {
        'cer': round(cer, 4),
        'cer_percent': round(cer * 100, 2),
        'char_accuracy': round(char_accuracy, 2),
        'wer': round(wer, 4),
        'wer_percent': round(wer * 100, 2),
        'word_accuracy': round(word_accuracy, 2),
        'reference_chars': len(ref),
        'hypothesis_chars': len(hyp),
        'reference_words': len(ref_words),
        'hypothesis_words': len(hyp_words),
    }


def main():
    print("\n" + "=" * 100)
    print("OCR EVALUATION: CER, WER AND ACCURACY METRICS")
    print("=" * 100 + "\n")

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

    print(f"[OK] Loaded OCR text: {len(ocr_text):,} chars, {len(ocr_text.split()):,} words")

    # Find ground truth
    gt_dir = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project\datos\spanishocr\texts")
    gt_files = list(gt_dir.glob("*.txt"))

    if not gt_files:
        print(f"[ERROR] No ground truth files in {gt_dir}")
        return 1

    print(f"[OK] Found {len(gt_files)} ground truth files")
    print(f"[*] Using first file: {gt_files[0].name}\n")

    # Load ground truth
    with open(gt_files[0], 'r', encoding='utf-8') as f:
        gt_text = f.read().strip()

    print(f"[OK] Ground truth: {len(gt_text):,} chars, {len(gt_text.split()):,} words")

    # Calculate metrics
    print("\n[*] Calculating metrics...")
    metrics = calculate_metrics(gt_text, ocr_text)

    # Display results
    print("\n" + "=" * 100)
    print("RESULTS")
    print("=" * 100 + "\n")

    print("CHARACTER LEVEL METRICS:")
    print(f"  CER (Character Error Rate):     {metrics['cer_percent']:.2f}%")
    print(f"  Character Accuracy:             {metrics['char_accuracy']:.2f}%")
    print(f"  Reference characters:           {metrics['reference_chars']:,}")
    print(f"  Hypothesis characters:          {metrics['hypothesis_chars']:,}")
    print(f"  Character difference:           {metrics['hypothesis_chars'] - metrics['reference_chars']:+,}")

    print("\nWORD LEVEL METRICS:")
    print(f"  WER (Word Error Rate):          {metrics['wer_percent']:.2f}%")
    print(f"  Word Accuracy:                  {metrics['word_accuracy']:.2f}%")
    print(f"  Reference words:                {metrics['reference_words']:,}")
    print(f"  Hypothesis words:               {metrics['hypothesis_words']:,}")
    print(f"  Word difference:                {metrics['hypothesis_words'] - metrics['reference_words']:+,}")

    # Save to JSON
    output_json = Path("pipeline_results/consolidated/ocr_evaluation_metrics.json")
    output_json.parent.mkdir(parents=True, exist_ok=True)

    eval_metrics = {
        'ground_truth_file': gt_files[0].name,
        'character_level': {
            'cer': metrics['cer'],
            'cer_percent': metrics['cer_percent'],
            'accuracy': metrics['char_accuracy'],
            'reference_chars': metrics['reference_chars'],
            'hypothesis_chars': metrics['hypothesis_chars'],
        },
        'word_level': {
            'wer': metrics['wer'],
            'wer_percent': metrics['wer_percent'],
            'accuracy': metrics['word_accuracy'],
            'reference_words': metrics['reference_words'],
            'hypothesis_words': metrics['hypothesis_words'],
        },
        'summary': {
            'status': 'EVALUATION COMPLETE',
            'interpretation': get_interpretation(metrics['cer'], metrics['wer'])
        }
    }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(eval_metrics, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Metrics saved to: {output_json}")

    # Save text report
    output_txt = Path("pipeline_results/consolidated/ocr_evaluation_report.txt")
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("OCR EVALUATION REPORT\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"Ground Truth File: {gt_files[0].name}\n")
        f.write(f"Evaluation Date: {Path(__file__).stat().st_mtime}\n\n")

        f.write("CHARACTER LEVEL METRICS\n")
        f.write("-" * 100 + "\n")
        f.write(f"CER (Character Error Rate):     {metrics['cer_percent']:.2f}%\n")
        f.write(f"Character Accuracy:             {metrics['char_accuracy']:.2f}%\n")
        f.write(f"Reference Characters:           {metrics['reference_chars']:,}\n")
        f.write(f"Hypothesis Characters:          {metrics['hypothesis_chars']:,}\n\n")

        f.write("WORD LEVEL METRICS\n")
        f.write("-" * 100 + "\n")
        f.write(f"WER (Word Error Rate):          {metrics['wer_percent']:.2f}%\n")
        f.write(f"Word Accuracy:                  {metrics['word_accuracy']:.2f}%\n")
        f.write(f"Reference Words:                {metrics['reference_words']:,}\n")
        f.write(f"Hypothesis Words:               {metrics['hypothesis_words']:,}\n\n")

        f.write("INTERPRETATION\n")
        f.write("-" * 100 + "\n")
        f.write(get_interpretation(metrics['cer'], metrics['wer']))

    print(f"[OK] Report saved to: {output_txt}")

    print("\n" + "=" * 100 + "\n")
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
