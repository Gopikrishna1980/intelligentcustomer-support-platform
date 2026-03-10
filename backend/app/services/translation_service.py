"""
Translation Service - Multi-language support
"""
from typing import Dict, Optional
from openai import OpenAI
import hashlib
import json

from app.core.config import settings

# Simple in-memory cache (in production, use Redis)
translation_cache: Dict[str, str] = {}


class TranslationService:
    """Multi-language translation using OpenAI GPT"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'nl': 'Dutch',
            'pl': 'Polish',
            'tr': 'Turkish',
            'vi': 'Vietnamese',
            'th': 'Thai',
            'id': 'Indonesian',
            'sv': 'Swedish',
            'no': 'Norwegian'
        }
    
    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'es', 'fr')
            source_language: Source language code (optional, will auto-detect)
        
        Returns:
            Dict with translated text and metadata
        """
        # Validate target language
        if target_language not in self.supported_languages:
            return {
                "translated_text": text,
                "error": f"Unsupported language: {target_language}",
                "from_cache": False
            }
        
        # Check cache
        cache_key = self._get_cache_key(text, target_language, source_language)
        if cache_key in translation_cache:
            return {
                "translated_text": translation_cache[cache_key],
                "source_language": source_language or "auto",
                "target_language": target_language,
                "from_cache": True
            }
        
        try:
            # Build prompt
            if source_language:
                prompt = f"""Translate the following text from {self.supported_languages.get(source_language, source_language)} to {self.supported_languages[target_language]}.
Maintain the tone and meaning. Respond with ONLY the translated text, no explanations.

Text: {text}"""
            else:
                prompt = f"""Translate the following text to {self.supported_languages[target_language]}.
Maintain the tone and meaning. Respond with ONLY the translated text, no explanations.

Text: {text}"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using 3.5 for cost efficiency
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3  # Lower temperature for consistent translation
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # Cache the translation
            translation_cache[cache_key] = translated_text
            
            return {
                "translated_text": translated_text,
                "source_language": source_language or "auto",
                "target_language": target_language,
                "from_cache": False,
                "tokens_used": response.usage.total_tokens
            }
        
        except Exception as e:
            return {
                "translated_text": text,
                "error": str(e),
                "from_cache": False
            }
    
    async def detect_language(self, text: str) -> Dict[str, str]:
        """
        Detect the language of text
        
        Returns:
            Dict with language code and confidence
        """
        try:
            prompt = f"""What language is this text written in? Respond with ONLY the two-letter ISO 639-1 language code (e.g., 'en', 'es', 'fr').

Text: {text[:200]}"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            detected_code = response.choices[0].message.content.strip().lower()
            
            return {
                "language_code": detected_code,
                "language_name": self.supported_languages.get(detected_code, "Unknown"),
                "confidence": "high" if detected_code in self.supported_languages else "low"
            }
        
        except Exception as e:
            return {
                "language_code": "en",
                "language_name": "English",
                "confidence": "unknown",
                "error": str(e)
            }
    
    async def batch_translate(
        self,
        texts: list[str],
        target_language: str,
        source_language: Optional[str] = None
    ) -> list[str]:
        """
        Translate multiple texts efficiently
        
        Returns:
            List of translated texts
        """
        if not texts:
            return []
        
        # For small batches, translate individually (better cache hit rate)
        if len(texts) <= 5:
            results = []
            for text in texts:
                result = await self.translate(text, target_language, source_language)
                results.append(result.get("translated_text", text))
            return results
        
        # For large batches, use batch translation
        try:
            texts_json = json.dumps(texts)
            
            prompt = f"""Translate the following JSON array of texts to {self.supported_languages[target_language]}.
Respond with ONLY a JSON array of translated texts, maintaining the same order.

{texts_json}"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            translated_texts = json.loads(response.choices[0].message.content)
            return translated_texts
        
        except Exception as e:
            print(f"Batch translation error: {str(e)}")
            # Fallback to individual translation
            results = []
            for text in texts:
                result = await self.translate(text, target_language, source_language)
                results.append(result.get("translated_text", text))
            return results
    
    def _get_cache_key(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str]
    ) -> str:
        """Generate cache key for translation"""
        key_string = f"{text}:{source_lang or 'auto'}:{target_lang}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages


# Global translation service instance
translation_service = TranslationService()
