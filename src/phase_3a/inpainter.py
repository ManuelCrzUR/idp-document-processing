# -*- coding: utf-8 -*-
"""
Inpainting implementations for stamp removal.
Provides both LaMa (if available) and OpenCV fallback.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Union, Tuple, Optional


class OpenCVInpainter:
    """OpenCV-based inpainting using Telea algorithm"""

    def __init__(self, radius: int = 3):
        """
        Args:
            radius: Inpainting radius (default 3)
        """
        self.radius = radius

    def inpaint(
        self,
        image: np.ndarray,
        mask: np.ndarray,
    ) -> np.ndarray:
        """
        Inpaint masked regions using OpenCV Telea algorithm.

        Args:
            image: Source image (BGR, uint8)
            mask: Binary mask (255 = inpaint, 0 = keep)

        Returns:
            Inpainted image (same shape as input)
        """
        if image.size == 0 or mask.size == 0:
            return image.copy()

        return cv2.inpaint(image, mask, self.radius, cv2.INPAINT_TELEA)


class LaMaInpainter:
    """LaMa inpainting (if library is available)"""

    def __init__(self, model_path: Optional[str] = None):
        """
        Args:
            model_path: Path to LaMa model (optional)
        """
        self.available = False
        self.model_path = model_path
        self._try_init()

    def _try_init(self):
        """Attempt to initialize LaMa"""
        try:
            import torch
            from lama_cleaner.model_manager import ModelManager
            from lama_cleaner.schema import Config

            self.torch = torch
            self.ModelManager = ModelManager
            self.Config = Config
            self.available = True
        except ImportError:
            self.available = False

    def inpaint(
        self,
        image: np.ndarray,
        mask: np.ndarray,
    ) -> np.ndarray:
        """
        Inpaint masked regions using LaMa.

        Args:
            image: Source image (BGR, uint8)
            mask: Binary mask (255 = inpaint, 0 = keep)

        Returns:
            Inpainted image (same shape as input)

        Raises:
            RuntimeError: If LaMa is not available
        """
        if not self.available:
            raise RuntimeError("LaMa is not available. Install lama-cleaner library.")

        if image.size == 0 or mask.size == 0:
            return image.copy()

        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Initialize LaMa model
        config = self.Config(
            hd_strategy="crop",
            ldm_steps=50,
        )
        model = self.ModelManager(name="lama", device="cpu", **config.dict())

        # Inpaint using LaMa
        inpainted_rgb = model(image_rgb, mask)

        # Convert back to BGR
        inpainted_bgr = cv2.cvtColor(inpainted_rgb, cv2.COLOR_RGB2BGR)

        return inpainted_bgr


class HybridInpainter:
    """
    Hybrid inpainting: tries LaMa first, falls back to OpenCV.
    """

    def __init__(self, opencv_radius: int = 3):
        """
        Args:
            opencv_radius: Radius for OpenCV inpainting (fallback)
        """
        self.lama = LaMaInpainter()
        self.opencv = OpenCVInpainter(radius=opencv_radius)

    def inpaint(
        self,
        image: np.ndarray,
        mask: np.ndarray,
    ) -> Tuple[np.ndarray, str]:
        """
        Inpaint using hybrid approach.

        Args:
            image: Source image (BGR, uint8)
            mask: Binary mask (255 = inpaint, 0 = keep)

        Returns:
            Tuple of (inpainted_image, method_used)
            where method_used is "lama" or "opencv"
        """
        if self.lama.available:
            try:
                result = self.lama.inpaint(image, mask)
                return result, "lama"
            except Exception as e:
                print(f"LaMa inpainting failed: {e}. Falling back to OpenCV.")
                result = self.opencv.inpaint(image, mask)
                return result, "opencv"
        else:
            result = self.opencv.inpaint(image, mask)
            return result, "opencv"
