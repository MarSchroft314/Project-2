#!/usr/bin/env python3
"""
Universal File Converter
=========================

A command-line tool that converts files between many common formats:

  Images:    png, jpg/jpeg, bmp, gif, webp, tiff, ico
  Documents: pdf, docx, txt, html, md
  Data:      csv, json, xlsx
  Audio:     mp3, wav, ogg, flac, m4a
  Video:     mp4, avi, mov, mkv, webm, gif (video->gif)

Usage:
    python file_converter.py input.ext output.ext
    python file_converter.py input.ext --to pdf

Requirements (install what you need):
    pip install pillow --break-system-packages              # images
    pip install pdf2image pillow img2pdf --break-system-packages  # pdf <-> image
    pip install python-docx docx2txt --break-system-packages       # docx
    pip install markdown --break-system-packages                   # md -> html
    pip install pandas openpyxl --break-system-packages            # csv/json/xlsx
    pip install moviepy --break-system-packages                    # video
    # Audio/video conversion also requires ffmpeg installed on the system.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Format groups
# ---------------------------------------------------------------------------

IMAGE_FORMATS = {"png", "jpg", "jpeg", "bmp", "gif", "webp", "tiff", "tif", "ico"}
AUDIO_FORMATS = {"mp3", "wav", "ogg", "flac", "m4a", "aac"}
VIDEO_FORMATS = {"mp4", "avi", "mov", "mkv", "webm"}
DATA_FORMATS = {"csv", "json", "xlsx"}
DOC_FORMATS = {"pdf", "docx", "txt", "html", "md"}


def ext_of(path: str) -> str:
    return Path(path).suffix.lower().lstrip(".")


# ---------------------------------------------------------------------------
# Image <-> Image / PDF
# ---------------------------------------------------------------------------

def convert_image(src: str, dst: str, src_ext: str, dst_ext: str):
    from PIL import Image

    img = Image.open(src)

    if dst_ext == "pdf":
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(dst, "PDF")
        return

    if dst_ext in ("jpg", "jpeg") and img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    if dst_ext == "ico":
        img.save(dst, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        return

    fmt = "JPEG" if dst_ext in ("jpg", "jpeg") else dst_ext.upper()
    if fmt == "TIF":
        fmt = "TIFF"
    img.save(dst, fmt)


# ---------------------------------------------------------------------------
# PDF <-> Image
# ---------------------------------------------------------------------------

def pdf_to_image(src: str, dst: str, dst_ext: str):
    from pdf2image import convert_from_path

    pages = convert_from_path(src, dpi=200)
    if len(pages) == 1:
        fmt = "JPEG" if dst_ext in ("jpg", "jpeg") else dst_ext.upper()
        pages[0].save(dst, fmt)
    else:
        # Multiple pages -> save as page-numbered files
        base, ext = os.path.splitext(dst)
        fmt = "JPEG" if dst_ext in ("jpg", "jpeg") else dst_ext.upper()
        for i, page in enumerate(pages, start=1):
            page.save(f"{base}_page{i}{ext}", fmt)
        print(f"PDF has {len(pages)} pages -> saved as {base}_page1{ext} .. {base}_page{len(pages)}{ext}")


def images_to_pdf(srcs, dst: str):
    import img2pdf

    with open(dst, "wb") as f:
        f.write(img2pdf.convert([str(s) for s in srcs]))


# ---------------------------------------------------------------------------
# Document conversions
# ---------------------------------------------------------------------------

def docx_to_txt(src: str, dst: str):
    import docx2txt

    text = docx2txt.process(src)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(text)


def txt_to_docx(src: str, dst: str):
    import docx

    with open(src, "r", encoding="utf-8") as f:
        content = f.read()

    document = docx.Document()
    for line in content.splitlines():
        document.add_paragraph(line)
    document.save(dst)


def md_to_html(src: str, dst: str):
    import markdown

    with open(src, "r", encoding="utf-8") as f:
        text = f.read()

    html_body = markdown.markdown(text, extensions=["extra", "tables", "fenced_code"])
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{Path(src).stem}</title>
</head>
<body>
{html_body}
</body>
</html>"""
    with open(dst, "w", encoding="utf-8") as f:
        f.write(html_doc)


def text_like_to_pdf(src: str, dst: str):
    """Convert plain text / markdown / html (rendered as text) to PDF."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch

    with open(src, "r", encoding="utf-8") as f:
        text = f.read()

    c = canvas.Canvas(dst, pagesize=letter)
    width, height = letter
    margin = inch
    y = height - margin
    line_height = 14

    for raw_line in text.splitlines():
        # simple wrapping
        line = raw_line
        max_chars = 95
        while len(line) > max_chars:
            c.drawString(margin, y, line[:max_chars])
            line = line[max_chars:]
            y -= line_height
            if y < margin:
                c.showPage()
                y = height - margin
        c.drawString(margin, y, line)
        y -= line_height
        if y < margin:
            c.showPage()
            y = height - margin

    c.save()


# ---------------------------------------------------------------------------
# Data conversions (csv / json / xlsx)
# ---------------------------------------------------------------------------

def convert_data(src: str, dst: str, src_ext: str, dst_ext: str):
    import pandas as pd

    if src_ext == "csv":
        df = pd.read_csv(src)
    elif src_ext == "json":
        df = pd.read_json(src)
    elif src_ext == "xlsx":
        df = pd.read_excel(src)
    else:
        raise ValueError(f"Unsupported source data format: {src_ext}")

    if dst_ext == "csv":
        df.to_csv(dst, index=False)
    elif dst_ext == "json":
        df.to_json(dst, orient="records", indent=2)
    elif dst_ext == "xlsx":
        df.to_excel(dst, index=False)
    else:
        raise ValueError(f"Unsupported destination data format: {dst_ext}")


# ---------------------------------------------------------------------------
# Audio / Video conversions (via ffmpeg)
# ---------------------------------------------------------------------------

def convert_with_ffmpeg(src: str, dst: str):
    if subprocess.call(["which", "ffmpeg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        raise RuntimeError("ffmpeg is not installed. Install it with: sudo apt install ffmpeg")

    cmd = ["ffmpeg", "-y", "-i", src, dst]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-1000:]}")


# ---------------------------------------------------------------------------
# Main conversion dispatcher
# ---------------------------------------------------------------------------

def convert(src: str, dst: str):
    src_ext = ext_of(src)
    dst_ext = ext_of(dst)

    if src_ext == dst_ext:
        raise ValueError("Source and destination formats are the same.")

    print(f"Converting {src} ({src_ext}) -> {dst} ({dst_ext}) ...")

    # --- Image -> Image / PDF ---
    if src_ext in IMAGE_FORMATS and (dst_ext in IMAGE_FORMATS or dst_ext == "pdf"):
        convert_image(src, dst, src_ext, dst_ext)

    # --- PDF -> Image ---
    elif src_ext == "pdf" and dst_ext in IMAGE_FORMATS:
        pdf_to_image(src, dst, dst_ext)

    # --- Image -> PDF (alt path, multi-image not used here) ---
    elif src_ext in IMAGE_FORMATS and dst_ext == "pdf":
        images_to_pdf([src], dst)

    # --- Docx <-> Txt ---
    elif src_ext == "docx" and dst_ext == "txt":
        docx_to_txt(src, dst)
    elif src_ext == "txt" and dst_ext == "docx":
        txt_to_docx(src, dst)

    # --- Markdown -> HTML ---
    elif src_ext == "md" and dst_ext == "html":
        md_to_html(src, dst)

    # --- Text-like -> PDF ---
    elif src_ext in ("txt", "md", "html") and dst_ext == "pdf":
        text_like_to_pdf(src, dst)

    # --- Data formats ---
    elif src_ext in DATA_FORMATS and dst_ext in DATA_FORMATS:
        convert_data(src, dst, src_ext, dst_ext)

    # --- Audio / Video via ffmpeg ---
    elif src_ext in AUDIO_FORMATS | VIDEO_FORMATS and (
        dst_ext in AUDIO_FORMATS | VIDEO_FORMATS | {"gif"}
    ):
        convert_with_ffmpeg(src, dst)

    else:
        raise ValueError(
            f"Conversion from .{src_ext} to .{dst_ext} is not supported.\n"
            f"Supported groups:\n"
            f"  Images: {sorted(IMAGE_FORMATS)}\n"
            f"  Documents: {sorted(DOC_FORMATS)}\n"
            f"  Data: {sorted(DATA_FORMATS)}\n"
            f"  Audio: {sorted(AUDIO_FORMATS)}\n"
            f"  Video: {sorted(VIDEO_FORMATS)}"
        )

    print("Done.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Universal File Converter - convert files between many formats."
    )
    parser.add_argument("input", help="Path to the input file")
    parser.add_argument(
        "output",
        nargs="?",
        help="Path to the output file (or omit and use --to to auto-name it)",
    )
    parser.add_argument(
        "--to",
        dest="to_ext",
        help="Target format (e.g. pdf, png, mp3) - used if output path not given",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: input file '{args.input}' does not exist.")
        sys.exit(1)

    if args.output:
        output_path = args.output
    elif args.to_ext:
        stem = Path(args.input).with_suffix("")
        output_path = f"{stem}.{args.to_ext.lstrip('.')}"
    else:
        print("Error: provide an output file path or use --to <format>.")
        sys.exit(1)

    try:
        convert(args.input, output_path)
    except Exception as e:
        print(f"Conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
