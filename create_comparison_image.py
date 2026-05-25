# -*- coding: utf-8 -*-
"""
Create 3-column comparison image:
1. Original document with stamp
2. Cleaned document (Phase 3A)
3. Cleaned document with OCR blocks
"""
import cv2
import json
import numpy as np
from pathlib import Path

def draw_ocr_blocks(image, ocr_json_path, thickness=2, color=(0, 255, 0)):
    """
    Draw OCR text blocks on image.

    Args:
        image: Input image (BGR)
        ocr_json_path: Path to OCR results JSON
        thickness: Bounding box line thickness
        color: Color in BGR (default green)

    Returns:
        Image with OCR blocks drawn
    """
    image_with_blocks = image.copy()

    # Load OCR results
    with open(ocr_json_path, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)

    blocks = ocr_data.get('bloques', [])

    # Draw each block
    for block in blocks:
        if 'coordenadas' in block:
            coords = block['coordenadas']
            # coords = [[x1,y1], [x2,y1], [x2,y2], [x1,y2]] (corner points)
            pts = np.array(coords, dtype=np.int32)

            # Draw bounding box
            cv2.polylines(image_with_blocks, [pts], True, color, thickness)

            # Add confidence text in top-left corner of box
            x1 = min([c[0] for c in coords])
            y1 = min([c[1] for c in coords])
            confidence = block.get('confianza', 0)
            text = f"{confidence:.2f}"
            cv2.putText(image_with_blocks, text, (int(x1), int(y1)-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    return image_with_blocks

def create_comparison_image(original_path, cleaned_path, ocr_json_path, output_path):
    """
    Create 3-column comparison image.

    Args:
        original_path: Path to original image with stamp
        cleaned_path: Path to cleaned image (Phase 3A)
        ocr_json_path: Path to OCR results JSON
        output_path: Where to save the comparison image
    """
    # Load images
    print("[*] Loading images...")
    original = cv2.imread(str(original_path))
    cleaned = cv2.imread(str(cleaned_path))

    if original is None or cleaned is None:
        print("[ERROR] Could not load images")
        return False

    print(f"[*] Original size: {original.shape}")
    print(f"[*] Cleaned size: {cleaned.shape}")

    # Draw OCR blocks on cleaned image
    print("[*] Drawing OCR blocks...")
    with_blocks = draw_ocr_blocks(cleaned, ocr_json_path, thickness=2, color=(0, 255, 0))

    # Ensure all images have same height
    h = original.shape[0]
    w = original.shape[1]

    # Create white separator (10px)
    separator = np.ones((h, 10, 3), dtype=np.uint8) * 255

    # Stack horizontally: original | separator | cleaned | separator | with_blocks
    print("[*] Creating 3-column comparison...")
    comparison = np.hstack([original, separator, cleaned, separator, with_blocks])

    # Add labels at top
    label_height = 60
    label_img = np.ones((label_height, comparison.shape[1], 3), dtype=np.uint8) * 255

    # Add text labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2
    font_color = (0, 0, 0)
    thickness = 2

    # Label positions
    x_offset = w // 3
    y_pos = 40

    cv2.putText(label_img, "ORIGINAL CON SELLO", (x_offset - 100, y_pos),
               font, font_scale, font_color, thickness)
    cv2.putText(label_img, "DESPUES PHASE 3A", (w + 10 + x_offset - 100, y_pos),
               font, font_scale, font_color, thickness)
    cv2.putText(label_img, "CON BLOQUES OCR", (2*w + 20 + x_offset - 100, y_pos),
               font, font_scale, font_color, thickness)

    # Add label image on top
    final_comparison = np.vstack([label_img, comparison])

    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[*] Saving comparison image: {output_path}")
    cv2.imwrite(str(output_path), final_comparison)
    print(f"[OK] Saved: {output_path}")
    print(f"[*] Image size: {final_comparison.shape}")

    return True

if __name__ == "__main__":
    original_path = "output/prueba_completa/01_imagen_original.png"
    cleaned_path = "test_results_corrected/phase_3a/cleaned_image.png"
    ocr_json_path = "test_results_corrected/phase_4/ocr_results.json"
    output_path = "output/prueba_completa/RESULTADO_FINAL.png"

    print("="*80)
    print("CREATING 3-COLUMN COMPARISON IMAGE")
    print("="*80 + "\n")

    success = create_comparison_image(original_path, cleaned_path, ocr_json_path, output_path)

    if success:
        print("\n" + "="*80)
        print("[OK] COMPARISON IMAGE CREATED SUCCESSFULLY")
        print("="*80)
    else:
        print("\n[ERROR] Failed to create comparison image")
