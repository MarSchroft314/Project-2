#!/usr/bin/env python3
"""Universal File Converter - GUI"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

# Import only the pieces we need, not the whole module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_converter import (
    convert,
    IMAGE_FORMATS,
    AUDIO_FORMATS,
    VIDEO_FORMATS,
    DATA_FORMATS,
    DOC_FORMATS,
    ext_of,
)

ALL_FORMATS = sorted(IMAGE_FORMATS | AUDIO_FORMATS | VIDEO_FORMATS | DATA_FORMATS | DOC_FORMATS)


class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Universal File Converter")
        self.geometry("520x320")
        self.resizable(False, False)
        self.configure(padx=20, pady=20)

        self.input_path = tk.StringVar()
        self.output_format = tk.StringVar(value="pdf")
        self.output_dir = tk.StringVar()
        self.status_text = tk.StringVar(value="Pick a file to get started.")

        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Universal File Converter", font=("Segoe UI", 16, "bold")).pack(pady=(0, 15))

        frame1 = tk.Frame(self)
        frame1.pack(fill="x", pady=5)
        tk.Label(frame1, text="Input file:", width=12, anchor="w").pack(side="left")
        tk.Entry(frame1, textvariable=self.input_path).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(frame1, text="Browse...", command=self.browse_input).pack(side="left")

        frame2 = tk.Frame(self)
        frame2.pack(fill="x", pady=5)
        tk.Label(frame2, text="Convert to:", width=12, anchor="w").pack(side="left")
        ttk.Combobox(frame2, textvariable=self.output_format, values=ALL_FORMATS, state="readonly", width=15).pack(side="left", padx=5)

        frame3 = tk.Frame(self)
        frame3.pack(fill="x", pady=5)
        tk.Label(frame3, text="Save to:", width=12, anchor="w").pack(side="left")
        tk.Entry(frame3, textvariable=self.output_dir).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(frame3, text="Browse...", command=self.browse_output_dir).pack(side="left")

        self.convert_btn = tk.Button(
            self,
            text="Convert",
            font=("Segoe UI", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.start_conversion,
        )
        self.convert_btn.pack(pady=20, fill="x")

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 10))

        tk.Label(self, textvariable=self.status_text, fg="gray").pack()

        tk.Label(
            self,
            text=(
                "Supports: images (png, jpg, bmp, gif, webp, tiff, ico),\n"
                "pdf, docx, txt, md, html, csv, json, xlsx,\n"
                "and audio/video (requires ffmpeg)."
            ),
            fg="gray",
            font=("Segoe UI", 8),
            justify="center",
        ).pack(pady=(10, 0))

    def browse_input(self):
        path = filedialog.askopenfilename(title="Select a file to convert")
        if path:
            self.input_path.set(path)
            if not self.output_dir.get():
                self.output_dir.set(str(Path(path).parent))

    def browse_output_dir(self):
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.output_dir.set(path)

    def start_conversion(self):
        src = self.input_path.get().strip()
        dst_ext = self.output_format.get().strip().lower()
        out_dir = self.output_dir.get().strip()

        if not src:
            messagebox.showerror("Error", "Please select an input file.")
            return
        if not os.path.exists(src):
            messagebox.showerror("Error", "Input file does not exist.")
            return
        if not out_dir:
            out_dir = str(Path(src).parent)

        if ext_of(src) == dst_ext:
            messagebox.showerror("Error", "Input and output formats are the same.")
            return

        dst = str(Path(out_dir) / f"{Path(src).stem}.{dst_ext}")

        self.convert_btn.config(state="disabled")
        self.status_text.set("Converting...")
        self.progress.start(12)

        threading.Thread(target=self._run_conversion, args=(src, dst), daemon=True).start()

    def _run_conversion(self, src, dst):
        try:
            convert(src, dst)
            self.after(0, self._on_success, dst)
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _on_success(self, dst):
        self.progress.stop()
        self.convert_btn.config(state="normal")
        self.status_text.set(f"Done! Saved to: {dst}")
        messagebox.showinfo("Success", f"File converted successfully:\n{dst}")

    def _on_error(self, message):
        self.progress.stop()
        self.convert_btn.config(state="normal")
        self.status_text.set("Conversion failed.")
        messagebox.showerror("Conversion failed", message)


if __name__ == "__main__":
    ConverterApp().mainloop()
