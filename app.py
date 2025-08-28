# Written by Pejman --> Email: pejman.ebrahimi77@gmail.com
import os
import time
import gradio as gr
from datetime import datetime
from pathlib import Path

# Ensure folders exist
BASE_DIR = Path.cwd()
IMAGES_DIR = BASE_DIR / "Images"
FILES_DIR = BASE_DIR / "Files"
AUDIOS_DIR = BASE_DIR / "Audios"
VIDEOS_DIR = BASE_DIR / "Videos"
for d in [IMAGES_DIR, FILES_DIR, AUDIOS_DIR, VIDEOS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def sanitize_name(name: str):
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in (name or "")).strip("_") or "file"

def meaningful_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# -------- Image Utilities --------
from PIL import Image, UnidentifiedImageError

IMAGE_FORMATS = ["jpg", "jpeg", "png", "webp", "bmp", "tiff"]

def safe_open_image(path_str: str, force_rgb: bool):
    p = Path(path_str)
    with open(p, "rb") as fh:
        img = Image.open(fh)
        img.load()
    if force_rgb:
        img = img.convert("RGB")
    return img

def image_convert(files, target_format, base_name):
    if not files:
        return "No images provided."
    target_format = (target_format or "").lower()
    if target_format == "jpg":
        target_format = "jpeg"
    base_name = sanitize_name(base_name) if base_name else "converted"
    logs = []
    for idx, f in enumerate(files, start=1):
        try:
            src_path = Path(f)
            ext = src_path.suffix.lower().lstrip(".")
            if ext not in IMAGE_FORMATS:
                logs.append(f"Skipped (not an image type): {src_path.name}")
                continue
            force_rgb = target_format in ["jpeg", "jpg"]
            img = safe_open_image(str(src_path), force_rgb=force_rgb)
            src_name = src_path.stem
            out_name = f"{base_name}_{sanitize_name(src_name)}_{idx}_{meaningful_timestamp()}.{target_format}"
            out_path = IMAGES_DIR / out_name
            save_kwargs = {}
            if target_format == "webp":
                save_kwargs["quality"] = 90
                save_kwargs["method"] = 6
            img.save(out_path, format=target_format.upper(), **save_kwargs)
            logs.append(f"Saved: {out_path.name}")
        except UnidentifiedImageError:
            logs.append(f"Skipped (unrecognized image): {Path(f).name}")
        except Exception as e:
            logs.append(f"Error for {Path(f).name}: {e}")
    return "\n".join(logs) or "Done."

# -------- PDF Utilities --------
import pikepdf
from pypdf import PdfWriter, PdfReader
import shutil
import subprocess

def pdf_compress(file, base_name, quality):
    if file is None:
        return "No PDF provided."
    base_name = sanitize_name(base_name) if base_name else "compressed"
    in_path = Path(file)
    out_name = f"{base_name}_{meaningful_timestamp()}.pdf"
    out_path = FILES_DIR / out_name
    try:
        level = (quality or "medium").lower()
        # Use only widely supported save args
        with pikepdf.open(in_path) as pdf:
            pdf.save(
                out_path,
                linearize=True,
                compress_streams=True,
                recompress_flate=True if level in ["medium", "low"] else False,
            )
        # Optional qpdf pass
        if shutil.which("qpdf"):
            tmp = out_path.with_suffix(".tmp.pdf")
            subprocess.run(["qpdf", "--linearize", str(out_path), str(tmp)], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if tmp.exists() and tmp.stat().st_size <= out_path.stat().st_size:
                out_path.unlink(missing_ok=True)
                tmp.rename(out_path)
            else:
                tmp.unlink(missing_ok=True)
        return f"Saved: {out_path.name}"
    except Exception as e:
        return f"Compression failed: {e}"

def pdf_merge(files, base_name):
    if not files or len(files) < 2:
        return "Provide at least two PDFs."
    base_name = sanitize_name(base_name) if base_name else "merged"
    out_name = f"{base_name}_{meaningful_timestamp()}.pdf"
    out_path = FILES_DIR / out_name
    try:
        writer = PdfWriter()
        for f in files:
            src = Path(f)
            reader = PdfReader(str(src))
            for page in reader.pages:
                writer.add_page(page)
        with open(out_path, "wb") as fp:
            writer.write(fp)
        return f"Saved: {out_path.name}"
    except Exception as e:
        return f"Merge failed: {e}"

# -------- Audio: STT and TTS --------
import torch
import soundfile as sf
import numpy as np

import whisper
from kokoro import KPipeline

# STT language hint
LANG_CODE_MAP = {"English": "en", "Spanish": "es", "Deutsch": "de"}

whisper_model_cache = {}
kokoro_pipeline_en = None

def get_whisper_model(size="base"):
    if size not in whisper_model_cache:
        whisper_model_cache[size] = whisper.load_model(size)
    return whisper_model_cache[size]

def stt_transcribe(audio_file, language_ui, base_name, whisper_size):
    if audio_file is None:
        return "No audio provided."
    lang = LANG_CODE_MAP.get(language_ui, "en")
    base_name = sanitize_name(base_name) if base_name else "transcript"
    out_name = f"{base_name}_{lang}_{meaningful_timestamp()}.txt"
    out_path = AUDIOS_DIR / out_name
    try:
        model = get_whisper_model(whisper_size)
        result = model.transcribe(audio_file, language=None if lang == "en" else lang)
        text = (result.get("text") or "").strip()
        if not text:
            return "No transcription produced."
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        return f"Saved: {out_path.name}"
    except Exception as e:
        return f"STT failed: {e}"

def get_kokoro_pipeline_en():
    global kokoro_pipeline_en
    if kokoro_pipeline_en is None:
        kokoro_pipeline_en = KPipeline(lang_code="a")  # English only
    return kokoro_pipeline_en

def tts_synthesize(text, voice_name, base_name, merge_segments):
    text = (text or "").strip()
    if not text:
        return "Empty text."
    base_name = sanitize_name(base_name) if base_name else "tts"
    try:
        pipeline = get_kokoro_pipeline_en()
        voice = (voice_name or "").strip() or "af_heart"  # default English voice
        generator = pipeline(text, voice=voice)
        rates = []
        chunks = []
        for _, __, audio in generator:
            chunks.append(np.asarray(audio, dtype=np.float32))
            rates.append(24000)
        if not chunks:
            return "No audio produced."
        if merge_segments:
            merged = np.concatenate(chunks, axis=0)
            out_name = f"{base_name}_en_{meaningful_timestamp()}.wav"
            out_path = AUDIOS_DIR / out_name
            sf.write(out_path, merged, rates[0])
            return f"Saved: {out_path.name}"
        else:
            outputs = []
            for i, audio in enumerate(chunks):
                out_name = f"{base_name}_en_{i}_{meaningful_timestamp()}.wav"
                out_path = AUDIOS_DIR / out_name
                sf.write(out_path, audio, rates[i])
                outputs.append(out_path.name)
            return "Saved:\n" + "\n".join(outputs)
    except Exception as e:
        return f"TTS failed: {e}"

# -------- YouTube -> Text --------
def ensure_ytdlp():
    try:
        import yt_dlp  # noqa
        return True
    except Exception:
        return False

def ytdlp_download_audio(url, tmp_dir: Path):
    import yt_dlp
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(tmp_dir / "%(title).200s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", f"video_{int(time.time())}")
        for ext in ["mp3", "m4a", "webm", "wav"]:
            candidate = tmp_dir / f"{title}.{ext}"
            if candidate.exists():
                return candidate, title
        files = sorted(tmp_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        return (files[0], title) if files else (None, title)

def youtube_to_text(url, base_name, whisper_size):
    url = (url or "").strip()
    if not url:
        return "Empty URL."
    if not ensure_ytdlp():
        return "yt-dlp not found. Please install per requirements."
    base_name = sanitize_name(base_name) if base_name else "youtube_transcript"
    tmp_dir = VIDEOS_DIR / f"_tmp_{int(time.time())}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    try:
        audio_path, title = ytdlp_download_audio(url, tmp_dir)
        if not audio_path or not audio_path.exists():
            return "Download failed."
        model = get_whisper_model(whisper_size)
        result = model.transcribe(str(audio_path))
        text = (result.get("text") or "").strip()
        if not text:
            return "No transcription produced."
        clean_title = sanitize_name(title)[:80] or "video"
        out_name = f"{base_name}_{clean_title}_{meaningful_timestamp()}.txt"
        out_path = VIDEOS_DIR / out_name
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        return f"Saved: {out_path.name}"
    except Exception as e:
        return f"YouTube transcription failed: {e}"
    finally:
        try:
            for p in tmp_dir.glob("*"):
                p.unlink(missing_ok=True)
            tmp_dir.rmdir()
        except Exception:
            pass

# --------- Gradio UI ---------
with gr.Blocks(title="Local Media Utility", theme=gr.themes.Soft()) as demo:
    gr.Markdown("### Local Media Utility • Private, local processing")

    with gr.Tab("Images"):
        with gr.Row():
            img_files = gr.File(
                label="Select images",
                file_count="multiple",
                file_types=[".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"],
                type="filepath",
            )
        with gr.Row():
            img_format = gr.Dropdown(choices=["jpg", "png", "webp", "bmp", "tiff"], value="webp", label="Target format")
            img_basename = gr.Textbox(label="Base name (optional)", placeholder="e.g., holiday_photos")
            img_run = gr.Button("Convert")
        img_out = gr.Textbox(label="Logs", lines=10)
        img_run.click(image_convert, inputs=[img_files, img_format, img_basename], outputs=img_out)

    with gr.Tab("PDFs"):
        with gr.Group():
            gr.Markdown("#### Compress PDF")
            pdf_file = gr.File(label="Select a PDF", file_types=[".pdf"], type="filepath")
            pdf_quality = gr.Radio(choices=["high", "medium", "low"], value="medium", label="Compression level")
            pdf_basename = gr.Textbox(label="Base name (optional)", placeholder="e.g., report_compressed")
            pdf_compress_btn = gr.Button("Compress")
            pdf_compress_out = gr.Textbox(label="Result", lines=4)
            pdf_compress_btn.click(pdf_compress, inputs=[pdf_file, pdf_basename, pdf_quality], outputs=pdf_compress_out)

        with gr.Group():
            gr.Markdown("#### Merge PDFs")
            pdf_files_merge = gr.File(label="Select PDFs (2+)", file_count="multiple", file_types=[".pdf"], type="filepath")
            pdf_merge_basename = gr.Textbox(label="Base name (optional)", placeholder="e.g., combined_docs")
            pdf_merge_btn = gr.Button("Merge")
            pdf_merge_out = gr.Textbox(label="Result", lines=4)
            pdf_merge_btn.click(pdf_merge, inputs=[pdf_files_merge, pdf_merge_basename], outputs=pdf_merge_out)

    with gr.Tab("Audio"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Speech to Text (STT)")
                stt_audio = gr.File(label="Select audio", file_types=[".wav", ".mp3", ".m4a", ".flac", ".ogg"], type="filepath")
                stt_lang = gr.Dropdown(choices=list(LANG_CODE_MAP.keys()), value="English", label="Language (hint)")
                stt_model = gr.Dropdown(choices=["base", "small", "medium"], value="base", label="Whisper model")
                stt_basename = gr.Textbox(label="Base name (optional)", placeholder="e.g., meeting_notes")
                stt_btn = gr.Button("Transcribe")
                stt_out = gr.Textbox(label="Result", lines=6)
                stt_btn.click(stt_transcribe, inputs=[stt_audio, stt_lang, stt_basename, stt_model], outputs=stt_out)
            with gr.Column():
                gr.Markdown("#### Text to Speech (TTS) — English Only")
                tts_text = gr.Textbox(label="Text", lines=6, placeholder="Enter English text...")
                tts_voice = gr.Textbox(label="Voice (optional)", placeholder="e.g., af_heart")
                merge_segments = gr.Checkbox(label="Merge segments into a single file", value=True)
                tts_basename = gr.Textbox(label="Base name (optional)", placeholder="e.g., narration")
                tts_btn = gr.Button("Synthesize")
                tts_out = gr.Textbox(label="Result", lines=6)
                tts_btn.click(tts_synthesize, inputs=[tts_text, tts_voice, tts_basename, merge_segments], outputs=tts_out)

    with gr.Tab("YouTube → Text"):
        yt_url = gr.Textbox(label="YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        yt_model = gr.Dropdown(choices=["base", "small", "medium"], value="base", label="Whisper model")
        yt_basename = gr.Textbox(label="Base name (optional)", placeholder="e.g., lecture_transcript")
        yt_btn = gr.Button("Transcribe")
        yt_out = gr.Textbox(label="Result", lines=6)
        yt_btn.click(youtube_to_text, inputs=[yt_url, yt_basename, yt_model], outputs=yt_out)

if __name__ == "__main__":
    demo.launch()