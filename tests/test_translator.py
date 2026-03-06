"""Tests for LibreTranslateClient using respx to mock httpx."""

import httpx
import pytest
import respx

from videotranslator.services.translator import LibreTranslateClient, TranslationError

HOST = "http://localhost:5000"


@respx.mock
def test_health_check_returns_true_on_200():
    respx.get(f"{HOST}/health").mock(return_value=httpx.Response(200))
    client = LibreTranslateClient(host=HOST)
    assert client.health_check() is True


@respx.mock
def test_health_check_returns_false_on_non_200():
    respx.get(f"{HOST}/health").mock(return_value=httpx.Response(503))
    client = LibreTranslateClient(host=HOST)
    assert client.health_check() is False


@respx.mock
def test_health_check_returns_false_on_connection_error():
    respx.get(f"{HOST}/health").mock(side_effect=httpx.ConnectError("refused"))
    client = LibreTranslateClient(host=HOST)
    assert client.health_check() is False


@respx.mock
def test_translate_sync_returns_translated_text():
    respx.post(f"{HOST}/translate").mock(
        return_value=httpx.Response(200, json={"translatedText": "Hola mundo"})
    )
    client = LibreTranslateClient(host=HOST)
    result = client.translate_sync("Hello world", source="en", target="es")
    assert result == "Hola mundo"


@respx.mock
def test_translate_sync_raises_on_http_error():
    respx.post(f"{HOST}/translate").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    client = LibreTranslateClient(host=HOST)
    with pytest.raises(TranslationError):
        client.translate_sync("Hello", source="en", target="es")


@respx.mock
def test_translate_sync_raises_on_invalid_response():
    respx.post(f"{HOST}/translate").mock(
        return_value=httpx.Response(200, json={"unexpected": "field"})
    )
    client = LibreTranslateClient(host=HOST)
    with pytest.raises(TranslationError):
        client.translate_sync("Hello", source="en", target="es")


def test_translate_sync_returns_empty_string_unchanged():
    client = LibreTranslateClient(host=HOST)
    assert client.translate_sync("", source="en", target="es") == ""
    assert client.translate_sync("   ", source="en", target="es") == "   "


@respx.mock
def test_detect_language_returns_detection_dict():
    respx.post(f"{HOST}/detect").mock(
        return_value=httpx.Response(
            200, json=[{"language": "en", "confidence": 0.99}]
        )
    )
    client = LibreTranslateClient(host=HOST)
    result = client.detect_language("Hello world")
    assert result["language"] == "en"
    assert result["confidence"] == 0.99


@respx.mock
def test_detect_language_raises_on_http_error():
    respx.post(f"{HOST}/detect").mock(
        return_value=httpx.Response(400, text="Bad Request")
    )
    client = LibreTranslateClient(host=HOST)
    with pytest.raises(TranslationError):
        client.detect_language("Hello")


@respx.mock
def test_translate_batch_sync_translates_all_items():
    respx.post(f"{HOST}/translate").mock(
        side_effect=[
            httpx.Response(200, json={"translatedText": "Hola"}),
            httpx.Response(200, json={"translatedText": "Mundo"}),
        ]
    )
    client = LibreTranslateClient(host=HOST)
    results = client.translate_batch_sync(["Hello", "World"], source="en", target="es")
    assert results == ["Hola", "Mundo"]


def test_translate_batch_sync_empty_list():
    client = LibreTranslateClient(host=HOST)
    assert client.translate_batch_sync([], source="en", target="es") == []
