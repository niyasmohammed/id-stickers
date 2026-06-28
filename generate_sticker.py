#!/usr/bin/env python3
"""
ID Sticker Generator
---------------------
For each person you add, this creates:
  1. output/stickers/<id>.pdf   -> a printable sticker with a QR code
  2. docs/people/<id>.html      -> a "digital ID" webpage with their details

Scanning the QR code opens the hosted webpage (once you push docs/ to
GitHub Pages -- see README.md).

USAGE:
    python3 generate_sticker.py

SETUP (do this FIRST):
    Edit the CONFIG block below with your GitHub username and the repo
    name you plan to create. That URL gets baked into every QR code, so
    changing it later means regenerating all stickers.
"""

import json
import secrets
from datetime import datetime
from pathlib import Path

import qrcode
from PIL import Image
from reportlab.lib.units import mm as MM
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ============== CONFIG -- EDIT THESE ==============
GITHUB_USERNAME = "niyasmohammed"   # e.g. "niyas123"
REPO_NAME = "id-stickers"                  # the repo you'll create on GitHub
PAGES_SUBFOLDER = "docs"                   # GitHub Pages serves from /docs
CARD_TITLE = "ID CARD"                     # printed at top of sticker & webpage
STICKER_WIDTH_MM = 80
STICKER_HEIGHT_MM = 50
# ====================================================

BASE_DIR = Path(__file__).parent.resolve()
DOCS_DIR = BASE_DIR / PAGES_SUBFOLDER / "people"
STICKERS_DIR = BASE_DIR / "output" / "stickers"
TEMPLATE_PATH = BASE_DIR / "template.html"

DOCS_DIR.mkdir(parents=True, exist_ok=True)
STICKERS_DIR.mkdir(parents=True, exist_ok=True)


def site_base_url() -> str:
    return f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}"


def person_url(person_id: str) -> str:
    return f"{site_base_url()}/people/{person_id}.html"


def make_qr_image(data: str) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def render_html_page(person_id: str, name: str, fields: dict) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    rows = "\n    ".join(
        f'<div class="row"><span class="label">{k}</span><span class="value">{v}</span></div>'
        for k, v in fields.items()
    )
    return (
        template
        .replace("{{TITLE}}", CARD_TITLE)
        .replace("{{NAME}}", name)
        .replace("{{ID}}", person_id)
        .replace("{{ROWS}}", rows)
        .replace("{{GENERATED}}", datetime.now().strftime("%d %b %Y"))
    )


def make_sticker_pdf(path: Path, person_id: str, name: str, fields: dict, qr_img: Image.Image):
    w, h = STICKER_WIDTH_MM * MM, STICKER_HEIGHT_MM * MM
    c = canvas.Canvas(str(path), pagesize=(w, h))

    # Border
    c.setLineWidth(0.6)
    c.rect(2, 2, w - 4, h - 4)

    # Title
    c.setFont("Helvetica-Bold", 10)
    c.drawString(6, h - 12, CARD_TITLE)

    # Name + ID
    c.setFont("Helvetica-Bold", 9)
    c.drawString(6, h - 24, name[:28])
    c.setFont("Helvetica", 7)
    c.drawString(6, h - 33, f"ID: {person_id}")

    # A couple of extra fields, kept compact
    y = h - 41
    c.setFont("Helvetica", 6.5)
    for k, v in list(fields.items())[:2]:
        c.drawString(6, y, f"{k}: {v}")
        y -= 7

    # QR code, right-aligned, full height
    qr_size = h - 10
    c.drawImage(ImageReader(qr_img), w - qr_size - 6, 5, width=qr_size, height=qr_size)

    c.showPage()
    c.save()


def add_person(name: str, fields: dict, person_id: str = None) -> dict:
    if not person_id:
        # Short, random, hard-to-guess ID (not sequential -> harder to enumerate)
        person_id = secrets.token_urlsafe(5).replace("_", "a").replace("-", "b")

    url = person_url(person_id)

    html = render_html_page(person_id, name, fields)
    (DOCS_DIR / f"{person_id}.html").write_text(html, encoding="utf-8")

    qr_img = make_qr_image(url)
    pdf_path = STICKERS_DIR / f"{person_id}.pdf"
    make_sticker_pdf(pdf_path, person_id, name, fields, qr_img)

    return {"id": person_id, "name": name, "url": url, "pdf": str(pdf_path)}


def interactive():
    print("=== Add a new person ===")
    print(f"(Pages will live at: {site_base_url()}/people/<id>.html)\n")
    people_log = []
    while True:
        name = input("Full name: ").strip()
        if not name:
            break
        fields = {}
        print("Add extra fields like 'Batch: Group A' (blank line to finish):")
        while True:
            line = input("  field: ").strip()
            if not line:
                break
            if ":" in line:
                k, v = line.split(":", 1)
                fields[k.strip()] = v.strip()
        result = add_person(name, fields)
        people_log.append(result)
        print(f"  -> sticker: {result['pdf']}")
        print(f"  -> QR opens: {result['url']}\n")

        if input("Add another person? (y/n): ").strip().lower() != "y":
            break

    log_path = BASE_DIR / "output" / "people_log.json"
    existing = json.loads(log_path.read_text()) if log_path.exists() else []
    existing.extend(people_log)
    log_path.write_text(json.dumps(existing, indent=2))
    print(f"\nDone. {len(people_log)} sticker(s) created in output/stickers/")
    print("Log saved to output/people_log.json")


if __name__ == "__main__":
    interactive()
