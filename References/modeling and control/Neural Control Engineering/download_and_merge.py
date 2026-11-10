"""Download public publisher PDFs and merge them with explicit coverage.

The MIT Direct book page currently returns HTTP 403. These public fallback
PDFs are a sample chapter and errata, not the complete book. The merged
filename and README deliberately retain that distinction.
"""

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import urllib.error
import urllib.request

import fitz


ROOT = Path(__file__).resolve().parent
BOOK_URL = (
    "https://direct.mit.edu/books/book/3723/"
    "Neural-Control-EngineeringThe-Emerging"
)
PUBLISHER_URL = "https://mitpress.mit.edu/9780262015370/neural-control-engineering/"
ASSET_ROOT = "https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/8436/"
SOURCES = [
    ("01 - Introduction - publisher sample.pdf", ASSET_ROOT + "9780262015370_sch_0001.pdf"),
    ("99 - Errata.pdf", ASSET_ROOT + "Neural_Control_Engineering_Errata_110911.pdf"),
]
MERGED_NAME = "Neural Control Engineering - available sample and errata.pdf"


def main():
    parts = ROOT / "individual_pdfs"
    parts.mkdir(parents=True, exist_ok=True)
    manifest = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "requested_page": BOOK_URL,
        "publisher_page": PUBLISHER_URL,
        "complete_book": False,
        "coverage": "Public publisher sample and errata only; full chapters not downloaded.",
        "sources": [],
    }
    try:
        with urllib.request.urlopen(BOOK_URL, timeout=30) as response:
            manifest["requested_page_status"] = response.status
            manifest["requested_page_final_url"] = response.url
    except urllib.error.HTTPError as error:
        manifest["requested_page_status"] = error.code
        manifest["requested_page_error"] = str(error)
    except urllib.error.URLError as error:
        manifest["requested_page_error"] = str(error)

    merged = fitz.open()
    bookmarks = []
    for name, url in SOURCES:
        with urllib.request.urlopen(url, timeout=45) as response:
            data = response.read()
            resolved_url = response.url
        if not data.startswith(b"%PDF-"):
            raise ValueError(f"Server did not return a PDF: {url}")
        with fitz.open(stream=data, filetype="pdf") as source:
            if source.needs_pass or len(source) == 0:
                raise ValueError(f"Unreadable PDF: {url}")
            path = parts / name
            path.write_bytes(data)
            first_page = len(merged) + 1
            merged.insert_pdf(source)
            bookmarks.append([1, path.stem, first_page])
            manifest["sources"].append({
                "file": path.relative_to(ROOT).as_posix(),
                "url": url,
                "resolved_url": resolved_url,
                "pages": len(source),
                "merged_first_page": first_page,
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            })
            print(f"Downloaded {name}: {len(source)} pages", flush=True)

    merged.set_toc(bookmarks)
    merged.set_metadata({
        "title": "Neural Control Engineering - public sample and errata (incomplete)",
        "author": "Steven J. Schiff",
        "subject": "Publisher sample and errata only. Not the complete book.",
    })
    output = ROOT / MERGED_NAME
    merged.save(output, garbage=4, deflate=True)
    page_count = len(merged)
    merged.close()
    with fitz.open(output) as check:
        assert len(check) == sum(item["pages"] for item in manifest["sources"])
        assert len(check.get_toc()) == len(SOURCES)
        assert all(page.get_text().strip() for page in check)
    manifest["merged_file"] = output.name
    manifest["merged_pages"] = page_count
    manifest["merged_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    (ROOT / "download_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Merged {page_count} pages into {output}", flush=True)
    print("INCOMPLETE: the full book chapters remain unavailable from MIT Direct.")


if __name__ == "__main__":
    main()
