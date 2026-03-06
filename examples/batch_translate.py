#!/usr/bin/env python3
"""
Batch translate all SRT files in a directory to multiple target languages.

Usage:
    python examples/batch_translate.py ./subtitles --target es --target fr
    python examples/batch_translate.py ./subtitles --target de --source en --output ./translated
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from videotranslator.services.translator import LibreTranslateClient, TranslationError


def translate_srt_file(
    client: LibreTranslateClient,
    srt_path: Path,
    output_path: Path,
    source: str,
    target: str,
) -> None:
    """Translate a single SRT file in-place (block by block)."""
    content = srt_path.read_text(encoding="utf-8")
    blocks = content.strip().split("\n\n")
    translated_blocks = []

    for i, block in enumerate(blocks, 1):
        lines = block.split("\n")
        if len(lines) >= 3:
            number = lines[0]
            timestamp = lines[1]
            text = "\n".join(lines[2:])
            try:
                translated_text = client.translate_sync(text, source, target)
                translated_blocks.append(f"{number}\n{timestamp}\n{translated_text}")
            except TranslationError as e:
                print(f"  [WARN] block {i} failed: {e} — keeping original")
                translated_blocks.append(block)
        else:
            translated_blocks.append(block)

    output_path.write_text("\n\n".join(translated_blocks), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch translate SRT files to multiple languages."
    )
    parser.add_argument("input_dir", help="Directory containing .srt files")
    parser.add_argument(
        "--target", action="append", required=True, metavar="LANG",
        help="Target language code (can be specified multiple times)"
    )
    parser.add_argument("--source", default="auto", help="Source language code (default: auto)")
    parser.add_argument(
        "--output", default=None,
        help="Output directory (default: same as input_dir)"
    )
    parser.add_argument(
        "--host", default="http://localhost:5000", help="LibreTranslate server URL"
    )
    parser.add_argument("--api-key", default=None, help="LibreTranslate API key")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        print(f"Error: '{input_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output) if args.output else input_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    srt_files = sorted(input_dir.glob("*.srt"))
    if not srt_files:
        print(f"No .srt files found in '{input_dir}'.")
        sys.exit(0)

    client = LibreTranslateClient(host=args.host, api_key=args.api_key)
    if not client.health_check():
        print(f"Error: LibreTranslate server not reachable at {args.host}.", file=sys.stderr)
        print("Start it with: docker-compose up -d", file=sys.stderr)
        sys.exit(1)

    targets: list[str] = args.target
    print(f"Found {len(srt_files)} SRT file(s). Translating to: {', '.join(targets)}\n")

    for srt_path in srt_files:
        for target_lang in targets:
            out_name = f"{srt_path.stem}_{target_lang}.srt"
            out_path = output_dir / out_name
            print(f"  {srt_path.name} -> {out_name} ...", end=" ", flush=True)
            try:
                translate_srt_file(client, srt_path, out_path, args.source, target_lang)
                print("done")
            except Exception as e:
                print(f"FAILED: {e}")

    print("\nBatch translation complete.")


if __name__ == "__main__":
    main()
