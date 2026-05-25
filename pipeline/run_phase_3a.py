# -*- coding: utf-8 -*-
"""
Phase 3A Runner: Stamp Removal with Progressive Filtering
Removes translucent stamps from document images using chromatic separation + intelligent filtering.

Pipeline steps:
1. Classify pixels (TEXTO, SELLO, MIXTO, FONDO, SELLO_TRANSLUCIDO)
2. Apply horizontal sweep filter (remove rows without text)
3. Apply block sweep filter (remove blocks without text)
4. Build final inpaint mask from surviving pixels
5. Apply inpainting to mask regions
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import numpy as np
from src.phase_3a import ChromaticSeparator, HybridInpainter


def create_pixel_map_overlay(pixel_map):
    """
    Create RGB visualization of pixel classification.
    Colors: 0=TEXTO(black), 1=SELLO(red), 2=MIXTO(yellow), 3=FONDO(white), 4=TRANS(blue)
    """
    h, w = pixel_map.shape
    overlay = np.zeros((h, w, 3), dtype=np.uint8)

    overlay[pixel_map == 0] = [0, 0, 0]        # TEXTO = black
    overlay[pixel_map == 1] = [0, 0, 255]      # SELLO_SATURADO = red
    overlay[pixel_map == 2] = [0, 255, 255]    # MIXTO = yellow
    overlay[pixel_map == 3] = [255, 255, 255]  # FONDO = white
    overlay[pixel_map == 4] = [255, 0, 0]      # SELLO_TRANSLUCIDO = blue

    return overlay


def create_mask_visualization(mask):
    """
    Create RGB visualization of inpaint mask.
    Red (255,0,0) = regions to inpaint, White = regions to preserve
    """
    h, w = mask.shape
    overlay = np.ones((h, w, 3), dtype=np.uint8) * 255  # White background

    # Red where mask is 255 (inpaint regions)
    red_regions = mask > 0
    overlay[red_regions] = [0, 0, 255]  # Red in BGR

    return overlay


def run_phase_3a(
    input_image_path: str,
    output_dir: str,
    stamp_bbox: tuple = None,
    block_size: int = 20,
    inpainting_method: str = "hybrid",
    save_intermediate: bool = True,
) -> dict:
    """
    Run Phase 3A: Stamp removal with intelligent filtering.

    Args:
        input_image_path: Path to input image
        output_dir: Output directory for results
        stamp_bbox: Optional stamp bounding box (x1, y1, x2, y2) or YOLO format (xc_norm, yc_norm, w_norm, h_norm)
        block_size: Block size for sweep filtering (pixels)
        inpainting_method: Method to use ("lama", "opencv", or "hybrid")
        save_intermediate: Save intermediate processing steps

    Returns:
        Dictionary with processing results
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load input image
    print(f"[*] Loading image: {input_image_path}")
    image = cv2.imread(input_image_path)
    if image is None:
        print(f"[ERROR] Could not load image: {input_image_path}")
        return {"success": False, "error": "Could not load image"}

    h, w = image.shape[:2]
    print(f"[*] Image size: {w}x{h}")

    # Initialize components
    separator = ChromaticSeparator()
    if inpainting_method == "hybrid":
        inpainter = HybridInpainter()
    else:
        from src.phase_3a.inpainter import OpenCVInpainter
        inpainter = OpenCVInpainter()

    print("\n" + "="*80)
    print("PHASE 3A: STAMP REMOVAL - INTELLIGENT FILTERING PIPELINE")
    print("="*80 + "\n")

    # Use whole image if no bbox provided
    if stamp_bbox is None:
        # YOLO format: normalized coordinates
        stamp_bbox = (0.5, 0.5, 1.0, 1.0)

    # PASO 1: Classify pixels
    print("[PASO 1/5] CLASIFICAR PÍXELES")
    print("-" * 80)

    roi_bgr, roi_coords = separator.extract_stamp_roi(image, stamp_bbox)
    x1, y1, x2, y2 = roi_coords
    roi_h, roi_w = roi_bgr.shape[:2]

    print(f"[*] ROI extracted: ({x1}, {y1}) to ({x2}, {y2}) = {roi_w}x{roi_h}")

    # Step 1: Classify pixels in ROI
    pixel_map = separator.classify_pixels(roi_bgr)

    # Count pixels in each category
    texto_count = np.sum(pixel_map == 0)
    sello_count = np.sum(pixel_map == 1)
    mixto_count = np.sum(pixel_map == 2)
    fondo_count = np.sum(pixel_map == 3)
    trans_count = np.sum(pixel_map == 4)

    print(f"\n[OK] Clasificacion completada:")
    print(f"    TEXTO (0):                {texto_count:8d} ({texto_count*100//pixel_map.size:3d}%)")
    print(f"    SELLO_SATURADO (1):       {sello_count:8d} ({sello_count*100//pixel_map.size:3d}%)")
    print(f"    MIXTO (2):                {mixto_count:8d} ({mixto_count*100//pixel_map.size:3d}%)")
    print(f"    FONDO (3):                {fondo_count:8d} ({fondo_count*100//pixel_map.size:3d}%)")
    print(f"    SELLO_TRANSLUCIDO (4):    {trans_count:8d} ({trans_count*100//pixel_map.size:3d}%)")

    # Save initial pixel map visualization
    if save_intermediate:
        overlay_initial = create_pixel_map_overlay(pixel_map)
        initial_mask = np.zeros_like(pixel_map, dtype=np.uint8)
        initial_mask[(pixel_map == 1) | (pixel_map == 2) | (pixel_map == 4)] = 255

        cv2.imwrite(str(output_dir / "01_pixel_classification.png"), overlay_initial)
        cv2.imwrite(str(output_dir / "01_initial_mask.png"), create_mask_visualization(initial_mask))
        print(f"[OK] Saved: 01_pixel_classification.png")
        print(f"[OK] Saved: 01_initial_mask.png")

    # PASO 2: Apply horizontal sweep filter
    print("\n[PASO 2/5] FILTRO DE BARRIDO HORIZONTAL")
    print("-" * 80)

    pixel_map_after_hsweep = separator.apply_horizontal_sweep_filter(pixel_map, roi_coords)

    # Count changes
    changed_hsweep = np.sum(pixel_map != pixel_map_after_hsweep)
    sello_count_after = np.sum(pixel_map_after_hsweep == 1)
    mixto_count_after = np.sum(pixel_map_after_hsweep == 2)
    trans_count_after = np.sum(pixel_map_after_hsweep == 4)

    print(f"[OK] Filtro horizontal completado:")
    print(f"    Píxeles reclasificados a FONDO: {changed_hsweep:8d}")
    print(f"    SELLO_SATURADO después:         {sello_count_after:8d} (antes: {sello_count:8d})")
    print(f"    MIXTO después:                  {mixto_count_after:8d} (antes: {mixto_count:8d})")
    print(f"    SELLO_TRANSLUCIDO después:      {trans_count_after:8d} (antes: {trans_count:8d})")

    if save_intermediate:
        overlay_hsweep = create_pixel_map_overlay(pixel_map_after_hsweep)
        mask_after_hsweep = np.zeros_like(pixel_map_after_hsweep, dtype=np.uint8)
        mask_after_hsweep[(pixel_map_after_hsweep == 1) | (pixel_map_after_hsweep == 2) | (pixel_map_after_hsweep == 4)] = 255

        cv2.imwrite(str(output_dir / "02_after_hsweep_classification.png"), overlay_hsweep)
        cv2.imwrite(str(output_dir / "02_after_hsweep_mask.png"), create_mask_visualization(mask_after_hsweep))
        print(f"[OK] Saved: 02_after_hsweep_classification.png")
        print(f"[OK] Saved: 02_after_hsweep_mask.png")

    # PASO 3: Apply block sweep filter
    print("\n[PASO 3/5] FILTRO DE BARRIDO POR BLOQUES")
    print("-" * 80)

    block_sweep_result = separator.apply_block_sweep_filter(pixel_map_after_hsweep, block_size=block_size)
    pixel_map_after_bsweep = block_sweep_result['pixel_map_filtered']
    blocks_info = block_sweep_result['blocks_info']
    grid_overlay = block_sweep_result['grid_overlay']

    # Count changes
    changed_bsweep = np.sum(pixel_map_after_hsweep != pixel_map_after_bsweep)
    sello_count_final = np.sum(pixel_map_after_bsweep == 1)
    mixto_count_final = np.sum(pixel_map_after_bsweep == 2)
    trans_count_final = np.sum(pixel_map_after_bsweep == 4)

    # Count blocks
    blocks_removed = sum(1 for b in blocks_info if not b['has_sufficient_text'])
    blocks_kept = sum(1 for b in blocks_info if b['has_sufficient_text'])

    print(f"[OK] Filtro de bloques completado:")
    print(f"    Tamaño de bloque: {block_size}x{block_size}")
    print(f"    Total bloques: {len(blocks_info)}")
    print(f"    Bloques mantenidos (con texto): {blocks_kept}")
    print(f"    Bloques limpiados (sin texto): {blocks_removed}")
    print(f"    Píxeles reclasificados a FONDO: {changed_bsweep:8d}")
    print(f"    SELLO_SATURADO final:           {sello_count_final:8d} (antes: {sello_count_after:8d})")
    print(f"    MIXTO final:                    {mixto_count_final:8d} (antes: {mixto_count_after:8d})")
    print(f"    SELLO_TRANSLUCIDO final:        {trans_count_final:8d} (antes: {trans_count_after:8d})")

    if save_intermediate:
        overlay_bsweep = create_pixel_map_overlay(pixel_map_after_bsweep)
        mask_after_bsweep = np.zeros_like(pixel_map_after_bsweep, dtype=np.uint8)
        mask_after_bsweep[(pixel_map_after_bsweep == 1) | (pixel_map_after_bsweep == 2) | (pixel_map_after_bsweep == 4)] = 255

        cv2.imwrite(str(output_dir / "03_after_bsweep_classification.png"), overlay_bsweep)
        cv2.imwrite(str(output_dir / "03_after_bsweep_mask.png"), create_mask_visualization(mask_after_bsweep))
        cv2.imwrite(str(output_dir / "03_block_grid_overlay.png"), grid_overlay)
        print(f"[OK] Saved: 03_after_bsweep_classification.png")
        print(f"[OK] Saved: 03_after_bsweep_mask.png")
        print(f"[OK] Saved: 03_block_grid_overlay.png (rojo=bloques limpiados, verde=mantenidos)")

    # PASO 4: Build final inpaint mask
    print("\n[PASO 4/5] CONSTRUIR MÁSCARA FINAL DE INPAINTING")
    print("-" * 80)

    # Create global mask (full image size)
    final_global_mask = np.zeros((h, w), dtype=np.uint8)

    # Fill in ROI region with final pixel map
    # Only pixels that are SELLO_SATURADO (1), MIXTO (2), or SELLO_TRANSLUCIDO (4)
    for yi in range(roi_h):
        for xi in range(roi_w):
            if pixel_map_after_bsweep[yi, xi] in [1, 2, 4]:
                final_global_mask[y1 + yi, x1 + xi] = 255

    inpaint_pixels = np.sum(final_global_mask > 0)
    print(f"[OK] Máscara final construida:")
    print(f"    Píxeles para inpainting: {inpaint_pixels:,}")
    print(f"    Porcentaje de imagen: {inpaint_pixels*100//(h*w)}%")

    if save_intermediate:
        mask_viz = create_mask_visualization(final_global_mask)
        cv2.imwrite(str(output_dir / "04_final_inpaint_mask.png"), mask_viz)
        print(f"[OK] Saved: 04_final_inpaint_mask.png")

    # PASO 5: Apply inpainting
    print("\n[PASO 5/5] APLICAR INPAINTING")
    print("-" * 80)

    cleaned_image = image.copy()

    if inpaint_pixels > 0:
        print(f"[*] Applying inpainting with method: {inpainting_method}")

        # Extract ROI for inpainting
        roi_mask = final_global_mask[y1:y2, x1:x2]

        # Apply inpainting to ROI only
        roi_inpainted, method_used = inpainter.inpaint(roi_bgr, roi_mask)
        cleaned_image[y1:y2, x1:x2] = roi_inpainted

        print(f"[OK] Inpainting completed with {method_used}")
    else:
        print("[*] No pixels to inpaint, skipping inpainting step")

    # Save final result
    print("\n" + "="*80)
    print("GUARDANDO RESULTADOS FINALES")
    print("="*80)

    output_image = output_dir / "cleaned_image.png"
    cv2.imwrite(str(output_image), cleaned_image)
    print(f"[OK] Saved: {output_image}")

    # Save comparison image (before and after side by side)
    if save_intermediate:
        h_img, w_img = image.shape[:2]
        comparison = np.hstack([image, cleaned_image])
        comparison_path = output_dir / "05_comparison_before_after.png"
        cv2.imwrite(str(comparison_path), comparison)
        print(f"[OK] Saved: 05_comparison_before_after.png")

    # Create summary statistics
    summary = {
        "input_image": input_image_path,
        "output_image": str(output_image),
        "stamp_roi": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
        "block_size": block_size,
        "inpainting_method": inpainting_method,
        "pixel_classification": {
            "initial": {
                "TEXTO": int(texto_count),
                "SELLO_SATURADO": int(sello_count),
                "MIXTO": int(mixto_count),
                "FONDO": int(fondo_count),
                "SELLO_TRANSLUCIDO": int(trans_count),
            },
            "after_horizontal_sweep": {
                "SELLO_SATURADO": int(sello_count_after),
                "MIXTO": int(mixto_count_after),
                "SELLO_TRANSLUCIDO": int(trans_count_after),
                "pixels_reclassified": int(changed_hsweep),
            },
            "after_block_sweep": {
                "SELLO_SATURADO": int(sello_count_final),
                "MIXTO": int(mixto_count_final),
                "SELLO_TRANSLUCIDO": int(trans_count_final),
                "pixels_reclassified": int(changed_bsweep),
            }
        },
        "block_filtering": {
            "total_blocks": len(blocks_info),
            "blocks_kept": int(blocks_kept),
            "blocks_removed": int(blocks_removed),
        },
        "final_mask": {
            "inpaint_pixels": int(inpaint_pixels),
            "percentage": f"{inpaint_pixels*100//(h*w)}%",
        }
    }

    return {
        "success": True,
        "output_image": str(output_image),
        "blocks_processed": roi_w * roi_h,
        "pixels_inpainted": int(inpaint_pixels),
        "inpainting_method": inpainting_method,
        "summary": summary,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Phase 3A: Stamp Removal"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input image path"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory"
    )
    parser.add_argument(
        "--block_size",
        type=int,
        default=20,
        help="Block size in pixels (default 20)"
    )
    parser.add_argument(
        "--inpainting_method",
        choices=["lama", "opencv", "hybrid"],
        default="hybrid",
        help="Inpainting method (default hybrid)"
    )

    args = parser.parse_args()

    result = run_phase_3a(
        input_image_path=args.input,
        output_dir=args.output,
        block_size=args.block_size,
        inpainting_method=args.inpainting_method,
    )

    if result["success"]:
        print("\n[OK] Phase 3A completed successfully")
        return 0
    else:
        print(f"\n[ERROR] {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
