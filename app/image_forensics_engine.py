import os
from pathlib import Path
from typing import List, Dict, Optional

from PIL import Image

try:
    from transformers import pipeline
except ImportError:
    pipeline = None


class ImageForensicsEngine:
    """
    Engine for locating and analyzing images from a loaded Facebook archive.
    Uses a pretrained Hugging Face image classification model for a simple
    authenticity / manipulation check.
    """

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or "prithivMLmods/Deepfake-Detect-Siglip2"
        self.classifier = None
        self.model_loaded = False

    def load_model(self) -> None:
        if self.model_loaded:
            return

        if pipeline is None:
            raise ImportError(
                "transformers is not installed. Run: pip install transformers torch pillow"
            )

        self.classifier = pipeline(
            "image-classification",
            model=self.model_name
        )
        self.model_loaded = True

    def is_supported_image(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def find_images_in_archive(self, archive_root: str, limit: Optional[int] = 50) -> List[str]:
        if not archive_root or not os.path.exists(archive_root):
            return []

        found_images = []

        for root, _, files in os.walk(archive_root):
            for file_name in files:
                full_path = os.path.join(root, file_name)
                if self.is_supported_image(full_path):
                    found_images.append(full_path)

                    if limit is not None and len(found_images) >= limit:
                        return found_images

        return found_images

    def classify_source(self, image_path: str) -> str:
        normalized = image_path.lower()

        if "profile" in normalized:
            return "Profile"
        if "message" in normalized or "messages" in normalized or "inbox" in normalized:
            return "Messages"
        if "photos" in normalized or "media" in normalized:
            return "Media"

        return "Other"

    def analyze_image(self, image_path: str) -> Dict:
        self.load_model()

        if not os.path.exists(image_path):
            return {
                "file_name": os.path.basename(image_path),
                "path": image_path,
                "source": "Unknown",
                "prediction": "Error",
                "confidence": 0.0,
                "status": "File not found"
            }

        try:
            image = Image.open(image_path).convert("RGB")
            results = self.classifier(image)

            if not results:
                return {
                    "file_name": os.path.basename(image_path),
                    "path": image_path,
                    "source": self.classify_source(image_path),
                    "prediction": "Unknown",
                    "confidence": 0.0,
                    "status": "No result"
                }

            top_result = results[0]
            label = top_result.get("label", "Unknown")
            score = float(top_result.get("score", 0.0))

            normalized_label = label.lower()

            if "fake" in normalized_label or "deepfake" in normalized_label or "ai" in normalized_label:
                prediction = "Potentially AI-generated"
                status = "Review suggested"
            else:
                prediction = "Likely authentic"
                status = "Low priority"

            return {
                "file_name": os.path.basename(image_path),
                "path": image_path,
                "source": self.classify_source(image_path),
                "prediction": prediction,
                "confidence": round(score * 100, 2),
                "status": status,
                "raw_label": label
            }

        except Exception as ex:
            return {
                "file_name": os.path.basename(image_path),
                "path": image_path,
                "source": self.classify_source(image_path),
                "prediction": "Error",
                "confidence": 0.0,
                "status": f"Error: {str(ex)}"
            }

    def analyze_images(self, image_paths: List[str]) -> List[Dict]:
        results = []
        for image_path in image_paths:
            results.append(self.analyze_image(image_path))
        return results