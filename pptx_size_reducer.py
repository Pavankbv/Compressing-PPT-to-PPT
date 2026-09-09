# ============================================================
# PPTX SIZE REDUCER — Google Colab (local .ppt -> compressed .pptx)
# ============================================================

# Refresh package lists first, then install (fixes stale-mirror 404s)
!apt-get update -qq
!apt-get install -y libreoffice --fix-missing -qq

# 1) Install dependencies
!pip install python-pptx pillow -q
!apt-get update -qq
!apt-get install -y default-jre libreoffice-impress --fix-missing -qq

import os
import re
import shutil
import zipfile
from PIL import Image

INPUT_RAW = "/content/YOUR_INPUT_FILE.ppt"   # <-- set your input .ppt/.pptx path
INPUT_FILE = "input.pptx"
OUTPUT_FILE = "output_compressed.pptx"

MAX_IMAGE_WIDTH = 1280
JPEG_QUALITY = 70
CONVERT_PNG_TO_JPEG = True

# Verify libreoffice is actually installed
!which libreoffice || echo "libreoffice still not found - check errors above"

!libreoffice --headless --convert-to pptx --outdir /content "{INPUT_RAW}"

converted_name = os.path.splitext(os.path.basename(INPUT_RAW))[0] + ".pptx"
converted_path = f"/content/{converted_name}"

if not os.path.exists(converted_path):
    raise FileNotFoundError(f"Conversion failed - {converted_path} not found. Check the LibreOffice output above for errors.")

shutil.move(converted_path, INPUT_FILE)
print("Converted and ready:", INPUT_FILE, os.path.getsize(INPUT_FILE) / 1024, "KB")
print("Original .ppt size: ", os.path.getsize(INPUT_RAW) / (1024 * 1024), "MB")

# ------------------------------------------------------------
# Compress images inside the PPTX
# ------------------------------------------------------------
WORK_DIR = "pptx_extracted"
if os.path.exists(WORK_DIR):
    shutil.rmtree(WORK_DIR)
os.makedirs(WORK_DIR)

with zipfile.ZipFile(INPUT_FILE, "r") as z:
    z.extractall(WORK_DIR)

media_dir = os.path.join(WORK_DIR, "ppt", "media")
total_before, total_after = 0, 0

if os.path.exists(media_dir):
    for fname in os.listdir(media_dir):
        fpath = os.path.join(media_dir, fname)
        ext = fname.lower().split(".")[-1]

        if ext not in ("png", "jpg", "jpeg", "bmp", "tiff", "gif"):
            continue

        try:
            size_before = os.path.getsize(fpath)
            total_before += size_before

            img = Image.open(fpath)

            if img.width > MAX_IMAGE_WIDTH:
                ratio = MAX_IMAGE_WIDTH / float(img.width)
                new_size = (MAX_IMAGE_WIDTH, int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            if ext == "png" and CONVERT_PNG_TO_JPEG:
                if img.mode in ("RGBA", "P"):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    img = img.convert("RGBA")
                    bg.paste(img, mask=img.split()[-1])
                    img = bg
                new_fname = fname.rsplit(".", 1)[0] + ".jpg"
                new_fpath = os.path.join(media_dir, new_fname)
                img.save(new_fpath, "JPEG", quality=JPEG_QUALITY, optimize=True)
                if new_fpath != fpath:
                    os.remove(fpath)
                fpath = new_fpath
            elif ext in ("jpg", "jpeg"):
                img = img.convert("RGB")
                img.save(fpath, "JPEG", quality=JPEG_QUALITY, optimize=True)
            else:
                img.save(fpath, optimize=True)

            size_after = os.path.getsize(fpath)
            total_after += size_after

        except Exception as e:
            print(f"Skipped {fname}: {e}")

print(f"\nImages before: {total_before/1024:.1f} KB")
print(f"Images after:  {total_after/1024:.1f} KB")

# ------------------------------------------------------------
# Fix PNG->JPG references in relationship files
# ------------------------------------------------------------
rels_dir = os.path.join(WORK_DIR, "ppt", "slides", "_rels")

if os.path.exists(rels_dir):
    for relf in os.listdir(rels_dir):
        relpath = os.path.join(rels_dir, relf)
        with open(relpath, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = re.sub(r"(media/image\d+)\.png", r"\1.jpg", content)
        if new_content != content:
            with open(relpath, "w", encoding="utf-8") as f:
                f.write(new_content)

# ------------------------------------------------------------
# Re-zip everything into a new .pptx
# ------------------------------------------------------------
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

with zipfile.ZipFile(OUTPUT_FILE, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(WORK_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, WORK_DIR)
            zf.write(file_path, arcname)

print("\nOriginal .pptx size:  ", os.path.getsize(INPUT_FILE) / (1024 * 1024), "MB")
print("Compressed file size: ", os.path.getsize(OUTPUT_FILE) / (1024 * 1024), "MB")

# ------------------------------------------------------------
# Download the compressed file
# ------------------------------------------------------------
from google.colab import files
files.download(OUTPUT_FILE)
