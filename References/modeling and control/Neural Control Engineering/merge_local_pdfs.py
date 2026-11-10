"""Merge the user-provided book PDFs in reading order, preserving originals."""

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re

import fitz


ROOT = Path(__file__).resolve().parent
PARTS = ROOT / "individual_pdfs"
OUTPUT = ROOT / "Neural Control Engineering - merged.pdf"


def main():
    chapters = {}
    for path in PARTS.glob("*.pdf"):
        match = re.fullmatch(r"(\d{2}) - (.+)\.pdf", path.name)
        if match and 1 <= int(match[1]) <= 13:
            number = int(match[1])
            if number in chapters:
                raise ValueError(f"Duplicate chapter {number}: {path.name}")
            chapters[number] = path
    if set(chapters) != set(range(1, 14)):
        raise ValueError(f"Expected chapters 1--13; found {sorted(chapters)}")

    ordered = [PARTS / "Series Foreword.pdf", PARTS / "Preface.pdf"]
    ordered.extend(chapters[number] for number in range(1, 14))
    ordered.extend(PARTS / name for name in (
        "Bibliography.pdf", "Index.pdf", "99 - Errata.pdf"
    ))
    unexpected = set(PARTS.glob("*.pdf")) - set(ordered)
    if unexpected:
        raise ValueError("Unordered source PDFs: " + ", ".join(p.name for p in unexpected))

    manifest = {
        "assembled_at_utc": datetime.now(timezone.utc).isoformat(),
        "output": OUTPUT.name,
        "coverage": "All 13 chapters and all supplied front/back matter; errata appended.",
        "originals_preserved": True,
        "sources": [],
    }
    merged = fitz.open()
    bookmarks = []
    labels = []
    for path in ordered:
        data = path.read_bytes()
        with fitz.open(stream=data, filetype="pdf") as source:
            if source.needs_pass or not len(source):
                raise ValueError(f"Source is empty or requires a password: {path.name}")
            offset = len(merged)
            title = path.stem
            if path in chapters.values():
                number = int(path.name[:2])
                title = f"{number}. {path.stem[5:]}"
                first_text = source[0].get_text()
                if not re.match(rf"\s*{number}\s*\n", first_text):
                    raise ValueError(f"Chapter heading does not match filename: {path.name}")
            elif path.name == "99 - Errata.pdf":
                title = "Errata (publisher supplement)"
            bookmarks.append([1, title, offset + 1])
            merged.insert_pdf(source, links=True, annots=True)
            # Retain every page, including deliberate blank pages and plates.
            # Check extracted text and page dimensions before saving.
            for index, page in enumerate(source):
                inserted = merged[offset + index]
                assert inserted.get_text() == page.get_text(), (path.name, index + 1)
                assert inserted.rect == page.rect, (path.name, index + 1)

            if path.name == "Series Foreword.pdf":
                labels.append({"startpage": offset, "prefix": "Foreword-", "style": "D", "firstpagenum": 1})
            elif path.name == "Preface.pdf":
                labels.append({"startpage": offset, "prefix": "", "style": "r", "firstpagenum": 13})
            elif path == chapters[1]:
                labels.append({"startpage": offset, "prefix": "", "style": "D", "firstpagenum": 1})
            elif path.name == "Index.pdf":
                # The first six pages are the index (including its blank verso).
                # The remaining pages contain the book's colour plates.
                assert len(source) == 30 and "Plate" in source[6].get_text()
                bookmarks.append([2, "Colour plates", offset + 7])
                labels.append({"startpage": offset + 6, "prefix": "Plates-", "style": "D", "firstpagenum": 1})
            elif path.name == "99 - Errata.pdf":
                labels.append({"startpage": offset, "prefix": "Errata-", "style": "D", "firstpagenum": 1})

            text = "\n".join(page.get_text() for page in source)
            text = text.replace("\u200b", "")
            source_url = re.search(
                r"direct\.mit\.edu/books/book/chapter-pdf/\d+/[\w.-]+\.pdf", text
            )
            manifest["sources"].append({
                "file": path.relative_to(ROOT).as_posix(),
                "bookmark": title,
                "pages": len(source),
                "merged_first_page": offset + 1,
                "merged_last_page": len(merged),
                "sha256": hashlib.sha256(data).hexdigest(),
                "publisher_url_from_watermark": "https://" + source_url[0] if source_url else None,
            })
            print(f"{offset + 1:3d}--{len(merged):3d}: {path.name}", flush=True)

    merged.set_toc(bookmarks)
    merged.set_page_labels(labels)
    merged.set_metadata({
        "title": "Neural Control Engineering: The Emerging Intersection between Control Theory and Neuroscience",
        "author": "Steven J. Schiff",
        "subject": "User-provided book chapters and front/back matter, with publisher errata appended.",
        "keywords": "neural control engineering, neuroscience, control theory, Steven J. Schiff",
    })
    temporary = OUTPUT.with_suffix(".merging.pdf")
    merged.save(temporary, garbage=4, deflate=True)
    total = len(merged)
    merged.close()
    with fitz.open(temporary) as check:
        assert len(check) == sum(item["pages"] for item in manifest["sources"])
        assert check.get_toc() == bookmarks
        for item in manifest["sources"]:
            with fitz.open(ROOT / item["file"]) as source:
                for index, page in enumerate(source):
                    actual = check[item["merged_first_page"] - 1 + index]
                    assert actual.get_text() == page.get_text(), (item["file"], index + 1)
        assert check[6].get_label() == "1"
        assert check[-1].get_label() == "Errata-9"
    temporary.replace(OUTPUT)
    manifest["merged_pages"] = total
    manifest["merged_sha256"] = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    (ROOT / "merge_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Saved {total} pages with {len(bookmarks)} bookmarks: {OUTPUT}")


if __name__ == "__main__":
    main()
