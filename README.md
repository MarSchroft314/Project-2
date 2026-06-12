# Universal File Converter

A simple Python command-line tool that converts files between many common formats — images, documents, spreadsheets/data files, and audio/video.

## Features

- **Images**: png, jpg/jpeg, bmp, gif, webp, tiff, ico — convert between any of these, or to PDF
- **PDF**: convert images to PDF, or PDF pages to images (requires poppler)
- **Documents**: docx ↔ txt, markdown → html, txt/md/html → pdf
- **Data**: csv ↔ json ↔ xlsx
- **Audio/Video**: mp3, wav, ogg, flac, m4a, mp4, avi, mov, mkv, webm, gif (requires ffmpeg)

## Requirements

- Python 3.8+
- [ffmpeg](https://ffmpeg.org/) (for audio/video conversions)
- [poppler](https://github.com/oschwartz10612/poppler-windows) (for PDF ↔ image conversions)

### Python packages

```bash
pip install pillow img2pdf pdf2image python-docx docx2txt markdown reportlab pandas openpyxl
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/file-converter.git
   cd file-converter
   ```
2. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install ffmpeg and poppler if you plan to convert audio/video or PDFs/images:
   - **Windows**: `winget install ffmpeg` and download poppler from the link above
   - **Mac**: `brew install ffmpeg poppler`
   - **Linux**: `sudo apt install ffmpeg poppler-utils`

## GUI

A simple desktop interface is included via `file_converter_gui.py`, built with Tkinter (comes bundled with Python — no extra install needed).

```bash
python file_converter_gui.py
```

This opens a window where you can:
- Browse for an input file
- Pick the target format from a dropdown
- Choose where to save the output
- Click **Convert** and get a success/error message when done

Make sure `file_converter_gui.py` stays in the same folder as `file_converter.py`, since the GUI imports the conversion logic from it.

## Command-line usage

```bash
python file_converter.py <input_file> <output_file>
```

or specify just the target format and let it auto-name the output:

```bash
python file_converter.py <input_file> --to <format>
```

### Examples

```bash
# Image to image
python file_converter.py photo.png photo.jpg

# Image to PDF
python file_converter.py photo.jpg photo.pdf

# PDF to image
python file_converter.py document.pdf page.png

# Word document to plain text
python file_converter.py report.docx report.txt

# Markdown to HTML
python file_converter.py notes.md notes.html

# CSV to Excel
python file_converter.py data.csv data.xlsx

# Audio conversion
python file_converter.py song.wav song.mp3

# Video to GIF
python file_converter.py clip.mp4 clip.gif
```

## How it works

The script reads the file extensions of the input and output paths, then routes the conversion to the appropriate library:

| Conversion type        | Library used          |
|-------------------------|------------------------|
| Image ↔ Image / PDF     | Pillow / img2pdf       |
| PDF → Image              | pdf2image (+ poppler)  |
| docx ↔ txt               | python-docx / docx2txt |
| Markdown → HTML          | markdown                |
| txt/md/html → PDF        | reportlab                |
| csv ↔ json ↔ xlsx         | pandas / openpyxl       |
| Audio/Video               | ffmpeg                   |

## Notes

- If a PDF has multiple pages and you convert it to an image format, each page is saved separately (e.g. `output_page1.png`, `output_page2.png`, ...).
- Audio/video conversions require ffmpeg to be installed and available in your system PATH.
- PDF ↔ image conversions require poppler to be installed and available in your system PATH.

## License

MIT
