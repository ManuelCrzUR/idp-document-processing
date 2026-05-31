#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OPTIMIZED: Process 50 RANDOM images from synthetic dataset
with MAXIMUM parallelization (8 workers).

Usage:
    python batch_process_50_images.py
"""

import os
import sys
import json
import time
import gc
import psutil
import traceback
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import multiprocessing as mp
from functools import partial
from tqdm import tqdm
import cv2
import numpy as np

# Add repo to path
REPO_ROOT = Path(__file__).parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline import run_phase_3a, run_phase_4, consolidate_ocr_results

# ============================================================================
# CONFIGURATION - OPTIMIZED FOR 50 IMAGES + MAX PARALLELIZATION
# ============================================================================

IMAGES_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project\datos\synthetic_dataset\images")
OUTPUT_ROOT = Path(REPO_ROOT) / "batch_results" / f"batch_50_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
NUM_WORKERS = 8   # MAXIMUM parallelization
BATCH_SIZE = 4    # More frequent cleanup
NUM_IMAGES = 50   # Process only 50 random images

print(f"\n[CONFIG]")
print(f"  Images to process: {NUM_IMAGES} (random selection)")
print(f"  Parallel workers: {NUM_WORKERS}")
print(f"  Batch size: {BATCH_SIZE}")
print(f"  Output: {OUTPUT_ROOT}")

# Create output directories
(OUTPUT_ROOT / "phase_3a").mkdir(parents=True, exist_ok=True)
(OUTPUT_ROOT / "phase_4").mkdir(parents=True, exist_ok=True)
(OUTPUT_ROOT / "consolidated").mkdir(parents=True, exist_ok=True)
(OUTPUT_ROOT / "logs").mkdir(parents=True, exist_ok=True)

# ============================================================================
# WORKER FUNCTION
# ============================================================================

def process_single_image(image_path, output_root, image_index, total_images):
    """Process a single image through the full pipeline."""
    result = {
        "image_name": image_path.name,
        "image_index": image_index,
        "success": False,
        "phases_completed": [],
        "timing": {},
        "errors": [],
    }

    try:
        image_size_mb = image_path.stat().st_size / (1024 * 1024)
        start_total = time.time()
        start_mem = psutil.Process().memory_info().rss / (1024 * 1024)

        # ====== PHASE 3A ======
        try:
            phase_3a_output = str(output_root / "phase_3a" / image_path.stem)
            Path(phase_3a_output).mkdir(parents=True, exist_ok=True)

            start = time.time()
            result_3a = run_phase_3a(
                input_image_path=str(image_path),
                output_dir=phase_3a_output,
                block_size=20,
                inpainting_method="hybrid",
                save_intermediate=False,
            )
            result["timing"]["phase_3a"] = time.time() - start

            if result_3a["success"]:
                result["phases_completed"].append("3a")
                cleaned_image = result_3a["output_image"]
            else:
                result["errors"].append(f"Phase 3A failed: {result_3a.get('error', 'Unknown')}")
                cleaned_image = str(image_path)

        except Exception as e:
            result["errors"].append(f"Phase 3A exception: {str(e)}")
            cleaned_image = str(image_path)
            result["timing"]["phase_3a"] = time.time() - start

        # ====== PHASE 4 ======
        try:
            phase_4_output = str(output_root / "phase_4" / image_path.stem)
            Path(phase_4_output).mkdir(parents=True, exist_ok=True)

            start = time.time()
            result_4 = run_phase_4(
                input_image_path=cleaned_image,
                output_dir=phase_4_output,
                language="es",
                confidence_threshold=0.6,
                levenshtein_threshold=2,
            )
            result["timing"]["phase_4"] = time.time() - start

            if result_4["success"]:
                result["phases_completed"].append("4")
                ocr_json = result_4["output_json"]
                result["ocr_blocks"] = result_4.get("text_blocks", 0)
                result["ocr_confidence"] = result_4.get("confidence", 0)
                result["ocr_text_length"] = result_4.get("text_length", 0)
            else:
                result["errors"].append(f"Phase 4 failed: {result_4.get('error', 'Unknown')}")
                ocr_json = None

        except Exception as e:
            result["errors"].append(f"Phase 4 exception: {str(e)}")
            ocr_json = None
            result["timing"]["phase_4"] = time.time() - start

        # ====== CONSOLIDATE ======
        try:
            if ocr_json and Path(ocr_json).exists():
                consolidated_output = str(output_root / "consolidated" / image_path.stem)
                Path(consolidated_output).mkdir(parents=True, exist_ok=True)

                start = time.time()
                metrics = consolidate_ocr_results(
                    ocr_json_path=ocr_json,
                    output_dir=consolidated_output,
                )
                result["timing"]["consolidate"] = time.time() - start
                result["phases_completed"].append("consolidate")

                tm = metrics.get("text_metrics", {})
                cm = metrics.get("ocr_confidence_metrics", {})
                pm = metrics.get("post_processing_metrics", {})

                result["metrics"] = {
                    "total_characters": tm.get("total_characters", 0),
                    "total_words": tm.get("total_words", 0),
                    "total_blocks": tm.get("total_blocks", 0),
                    "avg_confidence": cm.get("average_percent", 0),
                    "words_corrected": pm.get("words_corrected", 0),
                    "entities_detected": pm.get("entities_detected", 0),
                }
        except Exception as e:
            result["errors"].append(f"Consolidation exception: {str(e)}")
            result["timing"]["consolidate"] = time.time() - start

        # ====== FINALIZE ======
        end_mem = psutil.Process().memory_info().rss / (1024 * 1024)
        result["timing"]["total"] = time.time() - start_total
        result["timing"]["image_size_mb"] = image_size_mb
        result["memory_delta_mb"] = end_mem - start_mem
        result["success"] = len(result["errors"]) == 0

    except Exception as e:
        result["errors"].append(f"Overall exception: {str(e)}\n{traceback.format_exc()}")

    return result


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main batch processing pipeline."""

    print("\n" + "="*80)
    print("BATCH PIPELINE PROCESSOR - 50 RANDOM SYNTHETIC IMAGES (MAX PARALLELIZATION)")
    print("="*80)

    # Discover all images
    all_images = sorted([
        f for f in IMAGES_DIR.glob("*")
        if f.suffix.lower() in [".png", ".jpg", ".jpeg"]
    ])

    print(f"\nFound {len(all_images)} total images in directory")

    if len(all_images) == 0:
        print("[ERROR] No images found!")
        return

    # Select 50 random images
    random.seed(42)  # For reproducibility
    selected_images = random.sample(all_images, min(NUM_IMAGES, len(all_images)))
    selected_images = sorted(selected_images)

    print(f"Selected {len(selected_images)} random images for processing")
    print(f"\nSample of selected images:")
    for img in selected_images[:5]:
        size_mb = img.stat().st_size / (1024 * 1024)
        print(f"  - {img.name} ({size_mb:.2f}MB)")
    print(f"  ... and {len(selected_images)-5} more")

    # Metrics
    metrics_summary = {
        "start_time": datetime.now().isoformat(),
        "total_images_in_dataset": len(all_images),
        "images_selected": len(selected_images),
        "images_processed": 0,
        "images_failed": 0,
        "phases_timing": defaultdict(float),
        "image_timings": [],
        "errors_log": [],
    }

    # ====== PROCESS IN BATCHES ======
    print(f"\n{'='*80}")
    print(f"Starting batch processing with {NUM_WORKERS} workers...")
    print(f"{'='*80}\n")

    with mp.Pool(processes=NUM_WORKERS) as pool:
        batch_idx = 0
        for batch_start in range(0, len(selected_images), BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, len(selected_images))
            batch_images = selected_images[batch_start:batch_end]
            batch_idx += 1

            print(f"[BATCH {batch_idx:2d}] Images {batch_start+1:2d}-{batch_end:2d}/{len(selected_images)}")

            # Process batch in parallel
            batch_results = list(tqdm(
                pool.starmap(
                    process_single_image,
                    [(img, OUTPUT_ROOT, idx+1, len(selected_images)) for idx, img in enumerate(batch_images, start=batch_start)]
                ),
                total=len(batch_images),
                desc="  Progress",
                unit="img",
                ncols=70
            ))

            # Save batch results
            for result in batch_results:
                result_file = OUTPUT_ROOT / "logs" / f"{Path(result['image_name']).stem}_result.json"
                with open(result_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)

                # Update metrics
                if result["success"]:
                    metrics_summary["images_processed"] += 1
                    metrics_summary["image_timings"].append({
                        "image": result["image_name"],
                        "total_seconds": result["timing"]["total"],
                        "size_mb": result["timing"]["image_size_mb"],
                        "throughput_mb_per_sec": result["timing"]["image_size_mb"] / max(result["timing"]["total"], 0.1),
                    })
                    for phase, timing in result["timing"].items():
                        if phase != "image_size_mb":
                            metrics_summary["phases_timing"][phase] += timing
                else:
                    metrics_summary["images_failed"] += 1
                    metrics_summary["errors_log"].append({
                        "image": result["image_name"],
                        "errors": result["errors"],
                    })

                # Print result
                status = "[OK]" if result["success"] else "[!]"
                timing = result["timing"]["total"]
                print(f"  {status} {result['image_name']:50} {timing:6.2f}s", end="")
                if result.get("metrics"):
                    m = result["metrics"]
                    print(f" | Conf: {m['avg_confidence']:.1f}% | Blocks: {m['total_blocks']}", end="")
                print()

            # Cleanup
            gc.collect()
            mem = psutil.virtual_memory()
            print(f"  [Mem] {mem.percent:.1f}% used ({mem.available/(1024**3):.1f}GB free)\n")

    # ====== FINAL METRICS ======
    metrics_summary["end_time"] = datetime.now().isoformat()

    total_time = sum(t["total_seconds"] for t in metrics_summary["image_timings"])
    avg_time_per_image = total_time / max(metrics_summary["images_processed"], 1)

    metrics_summary["summary"] = {
        "total_time_seconds": total_time,
        "avg_time_per_image_seconds": avg_time_per_image,
        "throughput_images_per_minute": 60 / max(avg_time_per_image, 0.1),
        "success_rate_percent": 100 * metrics_summary["images_processed"] / max(metrics_summary["images_selected"], 1),
        "avg_phase_timing": {
            phase: timing / max(metrics_summary["images_processed"], 1)
            for phase, timing in metrics_summary["phases_timing"].items()
        }
    }

    # Save summary
    summary_file = OUTPUT_ROOT / "summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        data = {k: v for k, v in metrics_summary.items()}
        data["phases_timing"] = dict(data["phases_timing"])
        json.dump(data, f, indent=2)

    # ====== PRINT REPORT ======
    print(f"\n{'='*80}")
    print("BATCH PROCESSING COMPLETE")
    print(f"{'='*80}\n")

    print(f"[RESULTS]")
    print(f"  Total images in dataset: {metrics_summary['total_images_in_dataset']}")
    print(f"  Images selected: {metrics_summary['images_selected']}")
    print(f"  Processed: {metrics_summary['images_processed']}")
    print(f"  Failed: {metrics_summary['images_failed']}")
    print(f"  Success rate: {metrics_summary['summary']['success_rate_percent']:.1f}%")

    print(f"\n[TIMING]")
    print(f"  Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"  Avg per image: {avg_time_per_image:.2f}s")
    print(f"  Throughput: {metrics_summary['summary']['throughput_images_per_minute']:.1f} images/min")

    print(f"\n[PHASE TIMINGS (average)]")
    for phase, timing in metrics_summary["summary"]["avg_phase_timing"].items():
        print(f"  {phase:20} {timing:6.2f}s")

    print(f"\n[OUTPUT DIRECTORY]")
    print(f"  {OUTPUT_ROOT}\n")

    print(f"[FILES GENERATED]")
    print(f"  - phase_3a/          ({len(list((OUTPUT_ROOT/'phase_3a').glob('*')))} folders)")
    print(f"  - phase_4/           ({len(list((OUTPUT_ROOT/'phase_4').glob('*')))} folders)")
    print(f"  - consolidated/      ({len(list((OUTPUT_ROOT/'consolidated').glob('*')))} folders)")
    print(f"  - logs/              ({len(list((OUTPUT_ROOT/'logs').glob('*')))} files)")
    print(f"  - summary.json       (batch statistics)")

    if metrics_summary["errors_log"]:
        errors_file = OUTPUT_ROOT / "ERRORS.txt"
        with open(errors_file, "w", encoding="utf-8") as f:
            for err in metrics_summary["errors_log"]:
                f.write(f"\n{err['image']}\n")
                for e in err["errors"]:
                    f.write(f"  - {e}\n")
        print(f"  - ERRORS.txt         ({len(metrics_summary['errors_log'])} failed images)")

    print(f"\n[NEXT STEPS]")
    print(f"  Analyze results:")
    print(f"    python batch_analyze_results.py {OUTPUT_ROOT}")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
