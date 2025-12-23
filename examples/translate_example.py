#!/usr/bin/env python3
"""
Example script demonstrating LibreTranslate integration.

This script shows how to:
1. Check LibreTranslate server health
2. Get supported languages
3. Detect language
4. Translate text
5. Translate subtitle files (SRT)
"""

import asyncio
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from videotranslator.services.translator import LibreTranslateClient, TranslationError


def translate_srt_file(
    srt_path: str,
    output_path: str,
    source_lang: str = "auto",
    target_lang: str = "en",
    libretranslate_host: str = "http://localhost:5000",
):
    """
    Translate an SRT subtitle file to another language.

    Args:
        srt_path: Path to input SRT file
        output_path: Path to output translated SRT file
        source_lang: Source language code (or 'auto' for detection)
        target_lang: Target language code
        libretranslate_host: LibreTranslate server URL
    """
    client = LibreTranslateClient(host=libretranslate_host)

    # Read SRT file
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into subtitle blocks
    blocks = content.strip().split("\n\n")
    translated_blocks = []

    print(f"Translating {len(blocks)} subtitle blocks from {source_lang} to {target_lang}...")

    for i, block in enumerate(blocks, 1):
        lines = block.split("\n")

        if len(lines) >= 3:
            # Extract components: number, timestamp, text
            number = lines[0]
            timestamp = lines[1]
            text = "\n".join(lines[2:])

            # Translate the text
            try:
                translated_text = client.translate_sync(text, source_lang, target_lang)
                translated_block = f"{number}\n{timestamp}\n{translated_text}"
                translated_blocks.append(translated_block)
                print(f"  [{i}/{len(blocks)}] Translated: {text[:50]}...")
            except TranslationError as e:
                print(f"  [ERROR] Failed to translate block {i}: {e}")
                # Keep original on error
                translated_blocks.append(block)
        else:
            # Keep malformed blocks as-is
            translated_blocks.append(block)

    # Write translated SRT file
    output_content = "\n\n".join(translated_blocks)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"\nTranslated SRT saved to: {output_path}")


def main():
    """Run translation examples."""

    # Initialize client
    client = LibreTranslateClient(host="http://localhost:5000")

    print("=" * 70)
    print("LibreTranslate Integration Examples")
    print("=" * 70)

    # 1. Health Check
    print("\n1. Health Check")
    print("-" * 70)
    is_healthy = client.health_check()
    if not is_healthy:
        print("❌ LibreTranslate server is not running!")
        print("\nTo start LibreTranslate, run:")
        print("  docker-compose up -d")
        return

    print("✅ LibreTranslate server is healthy!")

    # 2. Get Supported Languages
    print("\n2. Supported Languages")
    print("-" * 70)
    try:
        languages = client.get_languages()
        print(f"Total languages supported: {len(languages)}\n")
        print("Sample languages:")
        for lang in languages[:10]:
            print(f"  - {lang['code']}: {lang['name']}")
        if len(languages) > 10:
            print(f"  ... and {len(languages) - 10} more")
    except TranslationError as e:
        print(f"❌ Error getting languages: {e}")

    # 3. Language Detection
    print("\n3. Language Detection")
    print("-" * 70)
    sample_texts = [
        "Hello, how are you?",
        "Hola, ¿cómo estás?",
        "Bonjour, comment allez-vous?",
        "Hallo, wie geht es dir?",
        "こんにちは、お元気ですか？",
    ]

    for text in sample_texts:
        try:
            detection = client.detect_language(text)
            print(f"Text: {text}")
            print(f"  → Language: {detection['language']} "
                  f"(confidence: {detection['confidence']:.2f})\n")
        except TranslationError as e:
            print(f"❌ Error detecting language: {e}")

    # 4. Simple Translation
    print("\n4. Simple Translation")
    print("-" * 70)
    test_cases = [
        ("Hello, world!", "auto", "es"),  # English to Spanish
        ("This is a test.", "en", "fr"),   # English to French
        ("Good morning!", "auto", "de"),   # English to German
    ]

    for text, source, target in test_cases:
        try:
            translated = client.translate_sync(text, source, target)
            print(f"Original ({source}): {text}")
            print(f"Translated ({target}): {translated}\n")
        except TranslationError as e:
            print(f"❌ Error translating '{text}': {e}\n")

    # 5. Batch Translation
    print("\n5. Batch Translation")
    print("-" * 70)
    batch_texts = [
        "The weather is nice today.",
        "I love learning new languages.",
        "Technology is amazing!",
    ]

    try:
        translated_batch = client.translate_batch_sync(batch_texts, "en", "es")
        for original, translated in zip(batch_texts, translated_batch):
            print(f"EN: {original}")
            print(f"ES: {translated}\n")
    except TranslationError as e:
        print(f"❌ Error in batch translation: {e}")

    # 6. SRT File Translation Example
    print("\n6. SRT File Translation")
    print("-" * 70)
    print("To translate an SRT file, use:")
    print("  python examples/translate_example.py --srt <input.srt> --output <output.srt> --target es")
    print("\nOr use the helper function in this script:")
    print("  from examples.translate_example import translate_srt_file")
    print("  translate_srt_file('input.srt', 'output.srt', source_lang='en', target_lang='es')")

    print("\n" + "=" * 70)
    print("✅ Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="LibreTranslate Examples and SRT Translation"
    )
    parser.add_argument(
        "--srt",
        type=str,
        help="Path to input SRT file to translate",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Path to output translated SRT file",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="auto",
        help="Source language code (default: auto)",
    )
    parser.add_argument(
        "--target",
        type=str,
        default="en",
        help="Target language code (default: en)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="http://localhost:5000",
        help="LibreTranslate server URL (default: http://localhost:5000)",
    )

    args = parser.parse_args()

    if args.srt and args.output:
        # Translate SRT file
        translate_srt_file(
            args.srt,
            args.output,
            args.source,
            args.target,
            args.host,
        )
    else:
        # Run examples
        main()
