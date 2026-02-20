#!/usr/bin/env python3
"""
Validate that static frontend pages match the expected structure and,
optionally, that they match saved archive HTML.

Usage:
  # Validate our pages have required structure (header, nav, main, footer)
  python scripts/validate_archive_pages.py

  # Compare our pages to archive HTML you saved (e.g. "Save Page As" from Wayback)
  python scripts/validate_archive_pages.py --archive-dir path/to/saved/archive
"""

import argparse
import re
import sys
from pathlib import Path


# Project root = parent of script's parent
ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"

# Pages we expect (all must have header, nav, main, footer)
EXPECTED_PAGES = ["index", "about", "services", "contact", "register", "login", "dashboard"]

# Required elements (tag or class) that each page must have
REQUIRED = [
    ("header", "site-header"),
    ("nav", "main-nav"),
    ("main", None),  # tag only
    ("footer", "site-footer"),
    ("Scholarvalley", None),  # logo text
]


def get_text(html: str) -> str:
    """Strip tags and normalize whitespace for text comparison."""
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def check_required(html: str, path: Path) -> list[str]:
    """Return list of missing required elements."""
    missing = []
    for item, cls in REQUIRED:
        if cls:
            if cls not in html:
                missing.append(f"{item} (class={cls})")
        else:
            if item not in html:
                missing.append(item)
    return missing


def validate_our_pages() -> bool:
    """Ensure each static page has required structure."""
    ok = True
    for name in EXPECTED_PAGES:
        path = STATIC_DIR / "index.html" if name == "index" else STATIC_DIR / f"{name}.html"
        if not path.exists():
            print(f"  Missing: {path}")
            ok = False
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        missing = check_required(html, path)
        if missing:
            print(f"  {path.name}: missing {missing}")
            ok = False
        else:
            print(f"  OK {path.name}")
    return ok


def find_archive_files(archive_dir: Path) -> dict[str, Path]:
    """Map page name -> path for archive HTML files.
    Expects filenames like index.html, about.html, ... or scholarvalley.com.html etc.
    """
    mapping = {}
    for f in archive_dir.iterdir():
        if f.suffix.lower() not in (".html", ".htm"):
            continue
        stem = f.stem.lower()
        # Normalize: "scholarvalley.com" or "index" -> index; "about" -> about
        if "index" in stem or stem in ("scholarvalley", "scholarvalley.com", "home"):
            mapping["index"] = f
        elif "about" in stem:
            mapping["about"] = f
        elif "service" in stem:
            mapping["services"] = f
        elif "contact" in stem:
            mapping["contact"] = f
    return mapping


def compare_text(our_path: Path, archive_path: Path) -> tuple[bool, str]:
    """Compare main text content. Returns (match, message)."""
    our_html = our_path.read_text(encoding="utf-8", errors="replace")
    archive_html = archive_path.read_text(encoding="utf-8", errors="replace")
    our_text = get_text(our_html)
    archive_text = get_text(archive_html)
    # Archive often has wayback banner and extra links; so we check that most of
    # archive text appears in ours (we may have less if user hasn't pasted yet)
    our_words = set(our_text.lower().split())
    archive_words = set(archive_text.lower().split())
    # Remove very common words for a looser match
    skip = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "are", "be", "by", "with", "as", "at"}
    archive_significant = archive_words - skip
    our_significant = our_words - skip
    if not archive_significant:
        return True, "No significant text in archive to compare"
    overlap = len(archive_significant & our_significant) / len(archive_significant)
    if overlap >= 0.8:
        return True, f"Text overlap ~{overlap:.0%} (good match)"
    if overlap >= 0.4:
        return False, f"Text overlap ~{overlap:.0%} (partial - paste more content from archive)"
    return False, f"Text overlap ~{overlap:.0%} (low - ensure you copied archive body content)"


def validate_against_archive(archive_dir: Path) -> bool:
    """Compare our static pages to saved archive HTML."""
    mapping = find_archive_files(archive_dir)
    if not mapping:
        print(f"No HTML files found in {archive_dir}")
        return False
    print(f"Found archive files: {list(mapping)}")
    ok = True
    for name in EXPECTED_PAGES:
        our_path = STATIC_DIR / "index.html" if name == "index" else STATIC_DIR / f"{name}.html"
        if not our_path.exists():
            print(f"  Skip {name}: our page missing")
            continue
        arch_path = mapping.get(name)
        if not arch_path:
            print(f"  Skip {name}: no matching archive file")
            continue
        match, msg = compare_text(our_path, arch_path)
        if match:
            print(f"  {name}: {msg}")
        else:
            print(f"  {name}: {msg}")
            ok = False
    return ok


def main():
    parser = argparse.ArgumentParser(description="Validate static pages vs archive")
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=None,
        help="Directory containing saved archive HTML (e.g. from Save Page As)",
    )
    args = parser.parse_args()

    print("Structure check (required header/nav/main/footer):")
    if not validate_our_pages():
        sys.exit(1)

    if args.archive_dir:
        if not args.archive_dir.is_dir():
            print(f"Archive dir not found: {args.archive_dir}")
            sys.exit(1)
        print("\nComparison to saved archive HTML:")
        if not validate_against_archive(args.archive_dir):
            sys.exit(1)
    else:
        print("\nTip: save archive pages (Save Page As) into a folder and run with --archive-dir to compare text.")

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
