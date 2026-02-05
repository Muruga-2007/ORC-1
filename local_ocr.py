"""
Local OCR Module using PaddleOCR and Tesseract
No external API dependencies - runs completely offline
"""

import os
import re
import json
from typing import Dict, Optional, Tuple
from paddleocr import PaddleOCR
import cv2
import numpy as np
from PIL import Image

class LocalOCR:
    """
    Local OCR engine using PaddleOCR for accurate text extraction
    """
    
    def __init__(self):
        """Initialize PaddleOCR with English language support"""
        try:
            # Initialize PaddleOCR with angle classification enabled
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
            print("✓ PaddleOCR initialized successfully")
        except Exception as e:
            print(f"⚠ PaddleOCR initialization error: {e}")
            self.ocr = None
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        - Convert to grayscale
        - Apply denoising
        - Enhance contrast
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Apply adaptive thresholding for better text detection
            thresh = cv2.adaptiveThreshold(
                enhanced, 255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            return thresh
        except Exception as e:
            print(f"Image preprocessing error: {e}")
            # Return original image if preprocessing fails
            return cv2.imread(image_path)
    
    def extract_text(self, image_path: str, preprocess: bool = True) -> str:
        """
        Extract text from image using PaddleOCR
        
        Args:
            image_path: Path to the image file
            preprocess: Whether to preprocess the image (default: True)
        
        Returns:
            Extracted text as a string
        """
        if not self.ocr:
            return ""
        
        try:
            # Optionally preprocess the image
            if preprocess:
                img = self.preprocess_image(image_path)
            else:
                img = image_path
            
            # Perform OCR
            result = self.ocr.ocr(img)
            
            # Extract text from results
            if result and result[0]:
                text_lines = []
                for line in result[0]:
                    if line and len(line) >= 2:
                        # line[1] contains (text, confidence)
                        text = line[1][0] if isinstance(line[1], tuple) else line[1]
                        text_lines.append(text)
                
                full_text = "\n".join(text_lines)
                print(f"✓ Extracted {len(text_lines)} lines of text")
                return full_text
            
            return ""
        
        except Exception as e:
            print(f"OCR extraction error: {e}")
            return ""
    
    def extract_document_details(self, image_path: str) -> Dict[str, str]:
        """
        Extract full content and specialized fields (Aadhaar: Name, Address, Phone)
        """
        # Extract text from image
        full_text = self.extract_text(image_path)
        
        if not full_text:
            print("⚠ No text extracted from image")
            return {"document_content": "", "metadata": "{}"}
        
        print(f"\n--- Extracted Content (Preview) ---\n{full_text[:500]}...\n-------------------\n")
        
        # Original Aadhaar extraction logic
        details = {
            "document_content": re.sub(r'\s+', ' ', full_text).strip(),
            "full_extracted_text": full_text,
            "name": "Unknown",
            "address": "Unknown",
            "phone": "Unknown",
            "document_title": "General Document"
        }

        # 1. Extract Name (Aadhaar specific)
        # Usually name is one of the first few lines
        name_match = re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", full_text)
        if name_match:
            details["name"] = name_match.group(1).strip()
            details["document_title"] = f"Aadhaar: {details['name']}"

        # 2. Extract Phone Number
        phone_match = re.search(r"(\b\d{10}\b|\b\d{4}\s\d{4}\s\d{4}\b)", full_text)
        if phone_match:
            details["phone"] = phone_match.group(1).strip()

        # 3. Extract Address (Look for keywords like Address, S/O, D/O, W/O)
        address_match = re.search(r"(?:Address:|Address|S/O|D/O|W/O)[\s:]+([\s\S]{10,200}?(?=\d{6}|$))", full_text, re.IGNORECASE)
        if address_match:
            details["address"] = re.sub(r'\s+', ' ', address_match.group(1)).strip()

        return details

    def _is_valid_name(self, candidate: str) -> bool:
        """Deprecated: System now uses full content"""
        return True


# Tesseract fallback (optional, requires tesseract installation)
class TesseractOCR:
    """
    Fallback OCR using Tesseract (requires system installation)
    """
    
    def __init__(self):
        try:
            import pytesseract
            self.tesseract = pytesseract
            print("✓ Tesseract OCR available")
        except ImportError:
            print("⚠ pytesseract not available")
            self.tesseract = None
    
    def extract_text(self, image_path: str) -> str:
        """Extract text using Tesseract"""
        if not self.tesseract:
            return ""
        
        try:
            img = Image.open(image_path)
            text = self.tesseract.image_to_string(img)
            return text
        except Exception as e:
            print(f"Tesseract error: {e}")
            return ""


# Main OCR interface
def extract_document_details(image_path: str) -> Dict[str, str]:
    """
    Main function to extract details from document image
    """
    paddle_ocr = LocalOCR()
    details = paddle_ocr.extract_document_details(image_path)
    
    # If extraction is empty, try Tesseract
    if not details.get("document_content"):
        print("Trying Tesseract fallback...")
        tesseract = TesseractOCR()
        text = tesseract.extract_text(image_path)
        if text:
            details["document_content"] = re.sub(r'\s+', ' ', text).strip()
            details["full_extracted_text"] = text
    
    return details


if __name__ == "__main__":
    # Test the OCR
    import sys
    
    if len(sys.argv) > 1:
        test_image = sys.argv[1]
        print(f"Testing OCR on: {test_image}")
        result = extract_document_details(test_image)
        print(f"\nResults:")
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python local_ocr.py <image_path>")
