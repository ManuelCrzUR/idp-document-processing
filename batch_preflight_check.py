#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pre-flight check before batch processing 201 images.
Verifies: images exist, pipeline works, RAM available, dependencies installed.
"""

import sys
import os
import psutil
from pathlib import Path
from datetime import datetime

# Add repo to path
REPO_ROOT = Path(__file__).parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

IMAGES_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project\datos\synthetic_dataset\images")

def check_images():
    """Verify images directory and count files."""
    print("\n[CHECK 1/6] Image Directory")
    print("─" * 60)

    if not IMAGES_DIR.exists():
        print(f"❌ Images directory not found: {IMAGES_DIR}")
        return False

    image_files = sorted([
        f for f in IMAGES_DIR.glob("*")
        if f.suffix.lower() in [".png", ".jpg", ".jpeg"]
    ])

    print(f"✓ Directory exists: {IMAGES_DIR}")
    print(f"✓ Found {len(image_files)} images")

    if len(image_files) == 0:
        print("❌ No images found!")
        return False

    # Check sizes
    total_size = sum(f.stat().st_size for f in image_files)
    avg_size = total_size / len(image_files)
    min_size = min(f.stat().st_size for f in image_files)
    max_size = max(f.stat().st_size for f in image_files)

    print(f"✓ Total size: {total_size / (1024**2):.1f}MB")
    print(f"✓ Average size: {avg_size / (1024**2):.2f}MB per image")
    print(f"✓ Size range: {min_size / (1024**2):.2f}MB - {max_size / (1024**2):.2f}MB")

    # Show sample images
    print(f"\n  Sample images:")
    for img in image_files[:3]:
        size_mb = img.stat().st_size / (1024**2)
        print(f"    - {img.name} ({size_mb:.2f}MB)")

    return True


def check_dependencies():
    """Verify required Python packages."""
    print("\n[CHECK 2/6] Dependencies")
    print("─" * 60)

    required = [
        ("cv2", "opencv-python-headless"),
        ("numpy", "numpy"),
        ("PIL", "Pillow"),
        ("yaml", "PyYAML"),
        ("easyocr", "easyocr"),
        ("spacy", "spacy"),
        ("tqdm", "tqdm"),
        ("psutil", "psutil"),
    ]

    all_ok = True
    for module, package in required:
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING (run: pip install {package})")
            all_ok = False

    return all_ok


def check_pipeline():
    """Test pipeline imports and basic functions."""
    print("\n[CHECK 3/6] Pipeline Functions")
    print("─" * 60)

    try:
        from pipeline import (
            run_phase_3a, run_phase_4,
            consolidate_ocr_results, run_evaluation
        )
        print("✓ run_phase_3a imported")
        print("✓ run_phase_4 imported")
        print("✓ consolidate_ocr_results imported")
        print("✓ run_evaluation imported")
        return True
    except Exception as e:
        print(f"❌ Failed to import pipeline: {e}")
        return False


def check_ram():
    """Check available RAM."""
    print("\n[CHECK 4/6] System Memory")
    print("─" * 60)

    mem = psutil.virtual_memory()

    print(f"Total RAM: {mem.total / (1024**3):.1f}GB")
    print(f"Available: {mem.available / (1024**3):.1f}GB ({mem.percent}% used)")
    print(f"In use: {mem.used / (1024**3):.1f}GB")

    # Check if enough for batch processing
    recommended_free = 4  # GB

    if mem.available / (1024**3) < recommended_free:
        print(f"\n⚠️  Only {mem.available / (1024**3):.1f}GB available")
        print(f"   Recommended: {recommended_free}GB free minimum")
        print(f"   Recommendation: Reduce NUM_WORKERS to 2-3")
        return False

    print(f"\n✓ Sufficient RAM available ({mem.available / (1024**3):.1f}GB > {recommended_free}GB)")
    return True


def check_output_dir():
    """Check if output directory is writable."""
    print("\n[CHECK 5/6] Output Directory")
    print("─" * 60)

    output_root = REPO_ROOT / "batch_results"

    try:
        output_root.mkdir(parents=True, exist_ok=True)
        test_file = output_root / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        print(f"✓ Output directory writable: {output_root}")
        return True
    except Exception as e:
        print(f"❌ Cannot write to output directory: {e}")
        return False


def check_disk_space():
    """Check disk space."""
    print("\n[CHECK 6/6] Disk Space")
    print("─" * 60)

    # Check disk at REPO_ROOT
    disk = psutil.disk_usage(str(REPO_ROOT))

    print(f"Total disk: {disk.total / (1024**3):.1f}GB")
    print(f"Used: {disk.used / (1024**3):.1f}GB")
    print(f"Free: {disk.free / (1024**3):.1f}GB ({100-disk.percent}% available)")

    # Estimate needed space
    # Original images: 381MB
    # Phase 3A output: ~381MB (cleaned images)
    # Phase 4 output: ~150MB (JSON)
    # Consolidated: ~50MB (txt+metrics)
    estimated_needed = 600  # MB

    free_mb = disk.free / (1024**2)

    if free_mb < estimated_needed:
        print(f"\n❌ Only {free_mb:.0f}MB free, need ~{estimated_needed}MB for results")
        return False

    print(f"\n✓ Sufficient disk space ({free_mb:.0f}MB > {estimated_needed}MB)")
    return True


def main():
    print("="*60)
    print("BATCH PROCESSING PRE-FLIGHT CHECK")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    checks = [
        ("Image Directory", check_images),
        ("Dependencies", check_dependencies),
        ("Pipeline Functions", check_pipeline),
        ("System Memory", check_ram),
        ("Output Directory", check_output_dir),
        ("Disk Space", check_disk_space),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Exception in {name}: {e}")
            results.append((name, False))

    # ====== SUMMARY ======
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status:8} {name}")

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("\n✅ ALL CHECKS PASSED - Ready to run batch_process_pipeline.py")
        print("\nNext steps:")
        print("  1. (Optional) Edit batch_process_pipeline.py to adjust NUM_WORKERS or BATCH_SIZE")
        print("  2. Run: python batch_process_pipeline.py")
        print("  3. Estimated time: 45-60 minutes for 201 images")
        return 0
    else:
        print("\n❌ SOME CHECKS FAILED - See above for details")
        print("\nFix the issues and re-run this script.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
