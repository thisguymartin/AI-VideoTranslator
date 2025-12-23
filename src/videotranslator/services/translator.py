"""
LibreTranslate integration for subtitle translation.
"""

import httpx
from typing import Optional, List
from ..logger import get_logger

logger = get_logger(__name__)


class TranslationError(Exception):
    """Exception raised for translation errors."""
    pass


class LibreTranslateClient:
    """Client for LibreTranslate API."""

    def __init__(
        self,
        host: str = "http://localhost:5000",
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize LibreTranslate client.

        Args:
            host: LibreTranslate server URL (default: http://localhost:5000)
            api_key: API key if required by the server
            timeout: Request timeout in seconds
        """
        self.host = host.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        logger.info(f"Initialized LibreTranslate client: {self.host}")

    def _get_headers(self) -> dict:
        """Get request headers with API key if provided."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def translate(
        self,
        text: str,
        source: str = "auto",
        target: str = "en",
    ) -> str:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            source: Source language code (e.g., 'en', 'es', 'fr', or 'auto' for detection)
            target: Target language code (e.g., 'en', 'es', 'fr')

        Returns:
            Translated text

        Raises:
            TranslationError: If translation fails
        """
        if not text or not text.strip():
            return text

        url = f"{self.host}/translate"
        payload = {
            "q": text,
            "source": source,
            "target": target,
            "format": "text",
        }

        if self.api_key:
            payload["api_key"] = self.api_key

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                data = response.json()

                if "translatedText" not in data:
                    raise TranslationError(f"Invalid response format: {data}")

                translated_text = data["translatedText"]
                logger.debug(
                    f"Translated text ({source} -> {target}): "
                    f"{text[:50]}... -> {translated_text[:50]}..."
                )
                return translated_text

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise TranslationError(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            raise TranslationError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during translation: {str(e)}"
            logger.error(error_msg)
            raise TranslationError(error_msg) from e

    def translate_sync(
        self,
        text: str,
        source: str = "auto",
        target: str = "en",
    ) -> str:
        """
        Synchronous version of translate method.

        Args:
            text: Text to translate
            source: Source language code (e.g., 'en', 'es', 'fr', or 'auto' for detection)
            target: Target language code (e.g., 'en', 'es', 'fr')

        Returns:
            Translated text

        Raises:
            TranslationError: If translation fails
        """
        if not text or not text.strip():
            return text

        url = f"{self.host}/translate"
        payload = {
            "q": text,
            "source": source,
            "target": target,
            "format": "text",
        }

        if self.api_key:
            payload["api_key"] = self.api_key

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                data = response.json()

                if "translatedText" not in data:
                    raise TranslationError(f"Invalid response format: {data}")

                translated_text = data["translatedText"]
                logger.debug(
                    f"Translated text ({source} -> {target}): "
                    f"{text[:50]}... -> {translated_text[:50]}..."
                )
                return translated_text

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise TranslationError(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            raise TranslationError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during translation: {str(e)}"
            logger.error(error_msg)
            raise TranslationError(error_msg) from e

    async def translate_batch(
        self,
        texts: List[str],
        source: str = "auto",
        target: str = "en",
    ) -> List[str]:
        """
        Translate multiple texts in batch.

        Args:
            texts: List of texts to translate
            source: Source language code
            target: Target language code

        Returns:
            List of translated texts

        Raises:
            TranslationError: If translation fails
        """
        if not texts:
            return []

        # LibreTranslate doesn't have a native batch endpoint,
        # so we translate one by one (can be optimized with asyncio.gather)
        results = []
        for text in texts:
            translated = await self.translate(text, source, target)
            results.append(translated)

        return results

    def translate_batch_sync(
        self,
        texts: List[str],
        source: str = "auto",
        target: str = "en",
    ) -> List[str]:
        """
        Synchronous version of translate_batch.

        Args:
            texts: List of texts to translate
            source: Source language code
            target: Target language code

        Returns:
            List of translated texts

        Raises:
            TranslationError: If translation fails
        """
        if not texts:
            return []

        results = []
        for text in texts:
            translated = self.translate_sync(text, source, target)
            results.append(translated)

        return results

    def get_languages(self) -> List[dict]:
        """
        Get list of supported languages.

        Returns:
            List of language dictionaries with 'code' and 'name' keys

        Raises:
            TranslationError: If request fails
        """
        url = f"{self.host}/languages"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url)
                response.raise_for_status()
                languages = response.json()
                logger.info(f"Retrieved {len(languages)} supported languages")
                return languages

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise TranslationError(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            raise TranslationError(error_msg) from e

    def detect_language(self, text: str) -> dict:
        """
        Detect the language of given text.

        Args:
            text: Text to detect language for

        Returns:
            Dictionary with 'language' and 'confidence' keys

        Raises:
            TranslationError: If detection fails
        """
        url = f"{self.host}/detect"
        payload = {"q": text}

        if self.api_key:
            payload["api_key"] = self.api_key

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    detection = result[0]
                    logger.info(
                        f"Detected language: {detection.get('language')} "
                        f"(confidence: {detection.get('confidence', 0):.2f})"
                    )
                    return detection
                else:
                    raise TranslationError(f"Invalid detection response: {result}")

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise TranslationError(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            raise TranslationError(error_msg) from e

    def health_check(self) -> bool:
        """
        Check if LibreTranslate server is healthy.

        Returns:
            True if server is healthy, False otherwise
        """
        url = f"{self.host}/health"

        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(url)
                is_healthy = response.status_code == 200
                logger.info(f"LibreTranslate health check: {'OK' if is_healthy else 'FAILED'}")
                return is_healthy
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
