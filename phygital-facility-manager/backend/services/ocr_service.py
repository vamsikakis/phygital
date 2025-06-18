"""
OCR Service for extracting text from documents using OCR Space API
"""
import os
import requests
import logging
from typing import Dict, Any, Optional
from flask import current_app

class OCRService:
    def __init__(self):
        self.api_key = os.getenv('OCR_SPACE_API_KEY')
        self.api_url = "https://api.ocr.space/parse/image"
        
    def extract_text_from_file(self, file_path: str, language: str = 'eng') -> Dict[str, Any]:
        """
        Extract text from an image or PDF file using OCR Space API
        
        Args:
            file_path: Path to the file to process
            language: Language code for OCR (default: 'eng')
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            if not self.api_key:
                raise ValueError("OCR_SPACE_API_KEY not found in environment variables")
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Determine file type
            file_extension = os.path.splitext(file_path)[1].lower()
            supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
            
            if file_extension not in supported_formats:
                return {
                    "success": False,
                    "error": f"Unsupported file format: {file_extension}",
                    "text": "",
                    "confidence": 0
                }
            
            # Prepare the request
            with open(file_path, 'rb') as file:
                payload = {
                    'apikey': self.api_key,
                    'language': language,
                    'isOverlayRequired': False,
                    'detectOrientation': True,
                    'scale': True,
                    'isTable': True,
                    'OCREngine': 2  # Use OCR Engine 2 for better accuracy
                }
                
                files = {
                    'file': (os.path.basename(file_path), file, self._get_content_type(file_extension))
                }
                
                current_app.logger.info(f"Starting OCR processing for file: {file_path}")
                
                # Make the API request
                response = requests.post(self.api_url, data=payload, files=files, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                
                # Process the response
                return self._process_ocr_response(result, file_path)
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"OCR API request failed: {str(e)}")
            return {
                "success": False,
                "error": f"OCR API request failed: {str(e)}",
                "text": "",
                "confidence": 0
            }
        except Exception as e:
            current_app.logger.error(f"OCR processing failed: {str(e)}")
            return {
                "success": False,
                "error": f"OCR processing failed: {str(e)}",
                "text": "",
                "confidence": 0
            }
    
    def _process_ocr_response(self, response: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Process the OCR API response and extract relevant information"""
        try:
            if not response.get('IsErroredOnProcessing', True):
                parsed_results = response.get('ParsedResults', [])
                
                if parsed_results:
                    # Extract text from all parsed results
                    extracted_texts = []
                    total_confidence = 0
                    
                    for result in parsed_results:
                        text = result.get('ParsedText', '').strip()
                        if text:
                            extracted_texts.append(text)
                        
                        # Calculate average confidence if available
                        confidence = result.get('TextOverlay', {}).get('HasOverlay', 0)
                        if isinstance(confidence, (int, float)):
                            total_confidence += confidence
                    
                    combined_text = '\n\n'.join(extracted_texts)
                    avg_confidence = total_confidence / len(parsed_results) if parsed_results else 0
                    
                    current_app.logger.info(f"OCR completed successfully for {file_path}. Extracted {len(combined_text)} characters.")
                    
                    return {
                        "success": True,
                        "text": combined_text,
                        "confidence": avg_confidence,
                        "word_count": len(combined_text.split()),
                        "character_count": len(combined_text),
                        "pages_processed": len(parsed_results)
                    }
                else:
                    return {
                        "success": False,
                        "error": "No text found in the document",
                        "text": "",
                        "confidence": 0
                    }
            else:
                error_message = response.get('ErrorMessage', 'Unknown OCR error')
                current_app.logger.error(f"OCR processing error: {error_message}")
                return {
                    "success": False,
                    "error": error_message,
                    "text": "",
                    "confidence": 0
                }
                
        except Exception as e:
            current_app.logger.error(f"Error processing OCR response: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing OCR response: {str(e)}",
                "text": "",
                "confidence": 0
            }
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get the appropriate content type for the file extension"""
        content_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.gif': 'image/gif'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')
    
    def is_ocr_supported_file(self, file_path: str) -> bool:
        """Check if the file format is supported for OCR processing"""
        file_extension = os.path.splitext(file_path)[1].lower()
        supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        return file_extension in supported_formats

# Create a global instance
ocr_service = OCRService()
