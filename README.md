# Universal File Converter

Convert any file to another format right from your terminal. No online tools, no sign-ups — just Python.

---

## What can it convert?

| Type | Formats |
|------|---------|
| Images | png, jpg, jpeg, bmp, gif, webp, tiff, ico |
| Documents | pdf, docx, txt, md, html |
| Data | csv, json, xlsx |
| Audio | mp3, wav, ogg, flac, m4a |
| Video | mp4, avi, mov, mkv, webm |

---

## Setup (do this once)

**1. Install Python** (if you don't have it)
```
winget install Python.Python.3.12
```

**2. Install ffmpeg** (needed for audio/video)
```
winget install ffmpeg
```

**3. Install the required packages**
```
pip install pillow img2pdf pdf2image python-docx docx2txt markdown reportlab pandas openpyxl
```

**4. Download the files** and put them all in the same folder:
- `file_converter.py`
- `file_converter_gui.py`

---

## How to use it

Open a terminal, go to the folder where you saved the files:
```
cd "C:\Users\YourName\Desktop\converter"
```

Then run it like this:
```
py file_converter.py input.ext output.ext
```

Just replace `input.ext` with your file and `output.ext` with what you want it to become.

---

## Examples

```
# Turn a PNG image into a JPG
py file_converter.py photo.png photo.jpg

# Turn an image into a PDF
py file_converter.py photo.jpg photo.pdf

# Convert a Word document to plain text
py file_converter.py report.docx report.txt

# Convert a CSV spreadsheet to Excel
py file_converter.py data.csv data.xlsx

# Convert audio
py file_converter.py song.wav song.mp3
```

---

## GUI version (optional)

If you don't like typing commands, run this instead to open a window with buttons:
```
py file_converter_gui.py
```

Then just click **Browse**, pick your file, choose the format, and hit **Convert**.

---

## Something not working?

- Make sure the file you want to convert is in the same folder, or use the full path.
- Audio/video conversion needs `ffmpeg` installed (`winget install ffmpeg`).
- PDF to image needs `poppler` installed (`winget install poppler`).
