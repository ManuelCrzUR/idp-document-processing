#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyze batch processing results.
Generates statistics, visualizations, and detailed reports.

Usage:
    python batch_analyze_results.py RESULTS_DIR

Example:
    python batch_analyze_results.py batch_results/20260525_143022
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt

def load_summary(results_dir):
    """Load summary.json from results directory."""
    summary_file = Path(results_dir) / "summary.json"
    if not summary_file.exists():
        print(f"[ERROR] summary.json not found: {summary_file}")
        return None

    with open(summary_file, encoding="utf-8") as f:
        return json.load(f)


def analyze_timing(summary):
    """Analyze timing statistics."""
    print("\n" + "="*70)
    print("TIMING ANALYSIS")
    print("="*70)

    image_timings = summary.get("image_timings", [])
    if not image_timings:
        print("No timing data available")
        return

    timings = [t["total_seconds"] for t in image_timings]
    sizes = [t["size_mb"] for t in image_timings]

    print(f"\n[EXECUTION TIME]")
    print(f"  Total time: {sum(timings):.1f}s ({sum(timings)/60:.1f} min)")
    print(f"  Average per image: {np.mean(timings):.2f}s")
    print(f"  Median per image: {np.median(timings):.2f}s")
    print(f"  Min: {np.min(timings):.2f}s")
    print(f"  Max: {np.max(timings):.2f}s")
    print(f"  Std deviation: {np.std(timings):.2f}s")

    print(f"\n[IMAGE SIZES]")
    print(f"  Average: {np.mean(sizes):.2f}MB")
    print(f"  Median: {np.median(sizes):.2f}MB")
    print(f"  Min: {np.min(sizes):.2f}MB")
    print(f"  Max: {np.max(sizes):.2f}MB")

    # Correlation
    correlation = np.corrcoef(sizes, timings)[0, 1]
    print(f"  Correlation (size ↔ time): {correlation:.3f}")

    # Phase breakdown
    print(f"\n[PHASE TIMING (averages)]")
    phases = summary.get("summary", {}).get("avg_phase_timing", {})
    for phase, timing in sorted(phases.items()):
        print(f"  {phase:20} {timing:6.2f}s")

    # Throughput
    throughput = summary.get("summary", {}).get("throughput_images_per_minute", 0)
    print(f"\n[THROUGHPUT]")
    print(f"  {throughput:.2f} images/minute")
    print(f"  {throughput*60:.0f} images/hour")


def analyze_ocr_quality(results_dir):
    """Analyze OCR quality metrics."""
    print("\n" + "="*70)
    print("OCR QUALITY ANALYSIS")
    print("="*70)

    logs_dir = Path(results_dir) / "logs"
    if not logs_dir.exists():
        print("No logs directory found")
        return

    # Collect metrics from all result files
    confidences = []
    block_counts = []
    char_counts = []
    word_counts = []
    success_images = []

    for result_file in sorted(logs_dir.glob("*_result.json")):
        try:
            with open(result_file, encoding="utf-8") as f:
                result = json.load(f)

            if result.get("success"):
                success_images.append(result["image_name"])
                if result.get("ocr_confidence"):
                    confidences.append(result["ocr_confidence"] * 100)
                if result.get("ocr_blocks"):
                    block_counts.append(result["ocr_blocks"])
                if result.get("metrics"):
                    m = result["metrics"]
                    if m.get("total_characters"):
                        char_counts.append(m["total_characters"])
                    if m.get("total_words"):
                        word_counts.append(m["total_words"])

        except Exception as e:
            pass

    if confidences:
        print(f"\n[OCR CONFIDENCE]")
        print(f"  Average: {np.mean(confidences):.2f}%")
        print(f"  Median: {np.median(confidences):.2f}%")
        print(f"  Min: {np.min(confidences):.2f}%")
        print(f"  Max: {np.max(confidences):.2f}%")
        print(f"  Std deviation: {np.std(confidences):.2f}%")

        # Confidence distribution
        high = sum(1 for c in confidences if c >= 80)
        medium = sum(1 for c in confidences if 50 <= c < 80)
        low = sum(1 for c in confidences if c < 50)
        print(f"\n  Distribution:")
        print(f"    High (≥80%):  {high:3} images ({high/len(confidences)*100:5.1f}%)")
        print(f"    Medium (50-80%): {medium:3} images ({medium/len(confidences)*100:5.1f}%)")
        print(f"    Low (<50%):   {low:3} images ({low/len(confidences)*100:5.1f}%)")

    if block_counts:
        print(f"\n[TEXT BLOCKS DETECTED]")
        print(f"  Average: {np.mean(block_counts):.1f} blocks per image")
        print(f"  Median: {np.median(block_counts):.1f} blocks")
        print(f"  Range: {np.min(block_counts):.0f} - {np.max(block_counts):.0f}")

    if char_counts:
        print(f"\n[TEXT EXTRACTION]")
        print(f"  Average chars: {np.mean(char_counts):.0f} per image")
        print(f"  Average words: {np.mean(word_counts):.0f} per image")
        print(f"  Total chars extracted: {sum(char_counts):,}")
        print(f"  Total words extracted: {sum(word_counts):,}")

    print(f"\n[SUCCESS RATE]")
    print(f"  Successful: {len(success_images)} images")


def analyze_errors(results_dir):
    """Analyze errors and failures."""
    print("\n" + "="*70)
    print("ERROR ANALYSIS")
    print("="*70)

    errors_file = Path(results_dir) / "ERRORS.txt"
    if not errors_file.exists():
        print("No errors file found (all images processed successfully!)")
        return

    with open(errors_file) as f:
        content = f.read()

    lines = [l for l in content.split("\n") if l.strip()]
    failed_images = sum(1 for l in lines if l.startswith(("synthetic_", "image_")))

    print(f"\nFailed images: {failed_images}")

    # Parse error types
    error_types = defaultdict(int)
    for line in lines:
        if "Phase 3A" in line:
            error_types["Phase 3A"] += 1
        elif "Phase 4" in line:
            error_types["Phase 4"] += 1
        elif "timeout" in line.lower():
            error_types["Timeout"] += 1
        elif "memory" in line.lower():
            error_types["Memory"] += 1
        elif "exception" in line.lower():
            error_types["Exception"] += 1

    if error_types:
        print("\nError types:")
        for error_type, count in sorted(error_types.items(), key=lambda x: -x[1]):
            print(f"  {error_type:15} {count:3} occurrences")


def generate_visualizations(results_dir):
    """Generate timing and confidence visualizations."""
    summary = load_summary(results_dir)
    if not summary:
        return

    image_timings = summary.get("image_timings", [])
    if not image_timings:
        return

    timings = [t["total_seconds"] for t in image_timings]
    sizes = [t["size_mb"] for t in image_timings]

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Batch Processing Analysis", fontsize=14, fontweight="bold")

    # Subplot 1: Timing histogram
    ax = axes[0, 0]
    ax.hist(timings, bins=20, color="skyblue", edgecolor="black", alpha=0.7)
    ax.axvline(np.mean(timings), color="red", linestyle="--", linewidth=2, label=f"Mean: {np.mean(timings):.2f}s")
    ax.axvline(np.median(timings), color="green", linestyle="--", linewidth=2, label=f"Median: {np.median(timings):.2f}s")
    ax.set_xlabel("Time per image (seconds)")
    ax.set_ylabel("Frequency")
    ax.set_title("Processing Time Distribution")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Subplot 2: Size vs Time scatter
    ax = axes[0, 1]
    ax.scatter(sizes, timings, alpha=0.6, s=30)
    # Add trend line
    z = np.polyfit(sizes, timings, 1)
    p = np.poly1d(z)
    ax.plot(sorted(sizes), p(sorted(sizes)), "r--", linewidth=2, label="Trend")
    ax.set_xlabel("Image size (MB)")
    ax.set_ylabel("Time (seconds)")
    ax.set_title("Size vs Processing Time")
    ax.legend()
    ax.grid(alpha=0.3)

    # Subplot 3: Cumulative time
    ax = axes[1, 0]
    cumulative = np.cumsum(timings)
    ax.plot(range(1, len(timings)+1), cumulative, linewidth=2, color="navy")
    ax.fill_between(range(1, len(timings)+1), cumulative, alpha=0.3, color="navy")
    ax.set_xlabel("Image number")
    ax.set_ylabel("Cumulative time (seconds)")
    ax.set_title("Cumulative Processing Time")
    ax.grid(alpha=0.3)

    # Subplot 4: Phase timing breakdown
    ax = axes[1, 1]
    phases = summary.get("summary", {}).get("avg_phase_timing", {})
    if phases:
        phase_names = list(phases.keys())
        phase_times = list(phases.values())
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]
        bars = ax.bar(phase_names, phase_times, color=colors[:len(phase_names)], edgecolor="black", alpha=0.7)
        ax.set_ylabel("Time (seconds)")
        ax.set_title("Average Time per Phase")
        ax.grid(axis="y", alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f"{height:.2f}s", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()

    # Save figure
    viz_file = Path(results_dir) / "analysis_visualization.png"
    plt.savefig(viz_file, dpi=150, bbox_inches="tight")
    print(f"\n[VISUALIZATION SAVED]")
    print(f"  {viz_file}")
    plt.close()


def generate_report(results_dir):
    """Generate a comprehensive text report."""
    summary = load_summary(results_dir)
    if not summary:
        return

    report_file = Path(results_dir) / "ANALYSIS_REPORT.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write("BATCH PROCESSING ANALYSIS REPORT\n")
        f.write("="*70 + "\n\n")

        # Summary stats
        f.write("SUMMARY\n")
        f.write("-"*70 + "\n")
        f.write(f"Start time: {summary.get('start_time', 'N/A')}\n")
        f.write(f"End time: {summary.get('end_time', 'N/A')}\n")
        f.write(f"Total images: {summary.get('total_images', 0)}\n")
        f.write(f"Processed: {summary.get('images_processed', 0)}\n")
        f.write(f"Failed: {summary.get('images_failed', 0)}\n")

        # Metrics
        f.write("\n" + "="*70 + "\n")
        f.write("METRICS\n")
        f.write("="*70 + "\n")
        metrics = summary.get("summary", {})
        f.write(f"Total time: {metrics.get('total_time_seconds', 0):.1f}s ({metrics.get('total_time_seconds', 0)/60:.1f} min)\n")
        f.write(f"Avg time/image: {metrics.get('avg_time_per_image_seconds', 0):.2f}s\n")
        f.write(f"Throughput: {metrics.get('throughput_images_per_minute', 0):.2f} images/min\n")
        f.write(f"Success rate: {metrics.get('success_rate_percent', 0):.1f}%\n")

        # Phase breakdown
        f.write("\nPhase timing (average):\n")
        for phase, timing in metrics.get("avg_phase_timing", {}).items():
            f.write(f"  {phase:20} {timing:6.2f}s\n")

    print(f"\n[REPORT GENERATED]")
    print(f"  {report_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_analyze_results.py RESULTS_DIR")
        print("\nExample:")
        print("  python batch_analyze_results.py batch_results/20260525_143022")
        print("\nOr analyze the most recent batch:")
        print("  ls -t batch_results/ | head -1 | xargs -I {} python batch_analyze_results.py batch_results/{}")
        return 1

    results_dir = Path(sys.argv[1])

    if not results_dir.exists():
        print(f"[ERROR] Directory not found: {results_dir}")
        return 1

    print("\n" + "="*70)
    print(f"ANALYZING BATCH RESULTS: {results_dir.name}")
    print("="*70)

    # Run analyses
    summary = load_summary(results_dir)
    if summary:
        analyze_timing(summary)
        analyze_ocr_quality(results_dir)
        analyze_errors(results_dir)
        generate_report(results_dir)
        generate_visualizations(results_dir)

        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70 + "\n")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
