# Local Media Utility

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/pejman-ebrahimi-4a60151a7/)
[![HuggingFace](https://img.shields.io/badge/🤗_Hugging_Face-FFD21E?style=for-the-badge)](https://huggingface.co/arad1367)
[![Website](https://img.shields.io/badge/Website-008080?style=for-the-badge&logo=About.me&logoColor=white)](https://arad1367.github.io/pejman-ebrahimi/)
[![University](https://img.shields.io/badge/University-00205B?style=for-the-badge&logo=academia&logoColor=white)](https://www.uni.li/pejman.ebrahimi?set_language=en)

A private, local-first Gradio app to:
- Convert images between common formats
- Compress and merge PDFs
- Speech-to-text (STT) and Text-to-speech (TTS; English)
- Transcribe YouTube videos to text

All processing runs locally on your machine. Files never leave your system.

## Table of Contents
- [Features](#features)
- [Demo](#demo)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
  - [1) Clone](#1-clone)
  - [2) Create Virtual Environment](#2-create-virtual-environment)
  - [3) Activate Virtual Environment](#3-activate-virtual-environment)
  - [4) Install Dependencies](#4-install-dependencies)
  - [5) Run the App](#5-run-the-app)
- [Usage](#usage)
  - [Images Tab](#images-tab)
  - [PDFs Tab](#pdfs-tab)
  - [Audio Tab](#audio-tab)
  - [YouTube → Text Tab](#youtube--text-tab)
- [Performance Tips](#performance-tips)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)
- [Contact](#contact)

## Features
- Images: Convert between jpg/jpeg/png/webp/bmp/tiff, saved with meaningful, timestamped names to `Images/`
- PDFs: Compress and merge, outputs saved to `Files/`
- Audio:
  - STT via Whisper (local): English, Spanish, Deutsch
  - TTS via Kokoro (local): English (single-file output by default), saved to `Audios/`
- YouTube: Download audio locally via `yt-dlp` and transcribe with Whisper; transcripts saved to `Videos/`

## Demo
- Local app launches at http://127.0.0.1:7860
- No public links unless you explicitly enable them.

## Project Structure
```
.
├── app.py
├── requirements.txt
├── README.md/

```

Folders are auto-created on first run.

## Prerequisites
- Python 3.10+ (recommended)
- OS packages:
  - ffmpeg (required for YouTube audio extraction and some audio handling)
  - Optional: qpdf (can further optimize PDF linearization)
- Disk space (Whisper and Kokoro will download model weights on first use)

Install system packages:
- Ubuntu/Debian:
  - `sudo apt-get update && sudo apt-get install -y ffmpeg qpdf`
- macOS (Homebrew):
  - `brew install ffmpeg qpdf`
- Windows:
  - Install ffmpeg (add to PATH): https://ffmpeg.org/download.html
  - qpdf (optional): https://github.com/qpdf/qpdf/releases

## Quick Start

### 1) Clone
```bash
git clone https://github.com/arad1367/local-media-utility.git
cd local-media-utility
```

### 2) Create Virtual Environment
```bash
python -m venv venv
```

### 3) Activate Virtual Environment
- Windows (PowerShell):
  ```powershell
  venv\Scripts\Activate.ps1
  ```
- Windows (cmd):
  ```cmd
  venv\Scripts\activate.bat
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### 4) Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

First run may download Whisper/Kokoro models into your cache.

### 5) Run the App
```bash
python app.py
```
Open the URL shown in the console, typically:
- http://127.0.0.1:7860

To stop: Ctrl+C in the terminal.

## Usage

### Images Tab
- Upload one or more images (jpg/jpeg/png/webp/bmp/tiff).
- Choose target format (e.g., webp).
- Optionally set a base name.
- Click Convert. Outputs are saved in `Images/` with `base_originalname_index_timestamp.ext`.

### PDFs Tab
- Compress PDF:
  - Upload a PDF and choose compression level (high/medium/low).
  - Outputs saved in `Files/`.
- Merge PDFs:
  - Upload 2+ PDFs and click Merge.
  - Output saved in `Files/`.

### Audio Tab
- STT (Speech to Text):
  - Upload audio (`.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`).
  - Choose language hint (English/Spanish/Deutsch) and Whisper model (base/small/medium).
  - Transcript saved in `Audios/`.
- TTS (Text to Speech – English only):
  - Enter English text and optional voice (default: `af_heart`).
  - Merges segments into a single `.wav` file by default.
  - Output saved in `Audios/`.

### YouTube → Text Tab
- Paste a YouTube URL.
- Choose Whisper model (base/small/medium).
- Transcription saved in `Videos/`.

## Performance Tips
- Whisper:
  - Use `base` or `small` for CPU-only machines.
  - First run downloads models; subsequent runs are faster.
- TTS:
  - Merging segments reduces I/O overhead.
  - GPU (if available) speeds up both Whisper and Kokoro (PyTorch).
- PDFs:
  - Installing `qpdf` can slightly reduce output size after pikepdf save.

## Troubleshooting
- “Invalid file type” on image upload:
  - Ensure you select supported image formats. If a filename has unusual characters, try renaming or drag & drop again.
- PDF compression fails:
  - Ensure the input is a valid PDF. Optionally install `qpdf` to assist final linearization.
- ffmpeg not found:
  - Install ffmpeg and ensure it’s on your PATH; restart the terminal.
- Whisper FP16 warning on CPU:
  - Safe to ignore; it falls back to FP32 automatically.
- Windows Hugging Face cache warnings:
  - You can ignore them, or run terminal as Administrator, or enable Developer Mode for symlinks.

## Roadmap
- Image resize, EXIF preserve/strip, and batch renaming tools
- Optional OCR and PDF → image(s)
- Alternative multilingual local TTS (e.g., Coqui) for Spanish/Deutsch
- Optional summaries for long transcripts

## License
MIT

## Contact
- Author: arad1367 (Pejman Ebrahimi)
- Email: pejman.ebrahimi77@gmail.com
- LinkedIn: https://www.linkedin.com/in/pejman-ebrahimi-4a60151a7/
- Website: https://arad1367.github.io/pejman-ebrahimi/
- Hugging Face: https://huggingface.co/arad1367
- University: https://www.uni.li/pejman.ebrahimi?set_language=en
