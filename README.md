# Compressing PPT to PPT

A Google Colab script that reduces the file size of a PowerPoint presentation
by compressing and resizing its embedded images, and converts legacy `.ppt`
files to `.pptx` along the way.

## What it does

1. Converts `.ppt` to `.pptx` using LibreOffice (headless mode).
2. Extracts the `.pptx` (which is a ZIP archive) and locates all images
   inside `ppt/media/`.
3. Resizes images wider than a configurable max width.
4. Re-compresses images as JPEG at a configurable quality level
   (optionally converting PNG to JPEG for further savings).
5. Fixes internal file references after any PNG -> JPEG renames.
6. Re-zips everything into a new, smaller `.pptx` file.

## Requirements

- Google Colab (or any environment with `apt-get` and `pip` access)
- Python packages: `python-pptx`, `pillow`
- System package: `libreoffice` (for `.ppt` -> `.pptx` conversion)

## Usage

1. Open `pptx_size_reducer.py` in Google Colab (or copy its cells into a notebook).
2. Upload your `.ppt` or `.pptx` file to the Colab session (`/content/`).
3. Set `INPUT_RAW` to the path of your uploaded file.
4. Adjust these settings as needed:
   - `MAX_IMAGE_WIDTH` — resize images wider than this (pixels)
   - `JPEG_QUALITY` — JPEG compression quality (1-100, lower = smaller file)
   - `CONVERT_PNG_TO_JPEG` — convert PNG images to JPEG for extra savings
5. Run all cells. The compressed file (`output_compressed.pptx`) will be
   generated and automatically downloaded.

## Notes

- Works best on presentations where large/high-resolution images are the
  main contributor to file size.
- Does not compress embedded videos, fonts, or chart data.
- `.ppt` (legacy binary format) files are automatically converted to
  `.pptx` before compression, since `.pptx` is a ZIP-based format required
  for this compression method to work.

## License

For personal/internal use.
