# -*- coding: utf-8 -*-
import io
import sys
from pathlib import Path

from PIL import Image, ImageOps

TARGET_WIDTH = 1040
MAX_FILE_SIZE = 300 * 1024  # 300KB
OUTPUT_FOLDER = "jpg"
IMAGE_EXTS = {".jpg", ".jpeg"}


def encode_jpeg(img, quality):
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()


def compress_to_target(img, max_bytes):
    data = encode_jpeg(img, 95)
    if len(data) <= max_bytes:
        return data

    data = encode_jpeg(img, 1)
    if len(data) > max_bytes:
        return None

    low = 1
    high = 95
    best_data = data

    while low <= high:
        mid = (low + high) // 2
        data = encode_jpeg(img, mid)
        if len(data) <= max_bytes:
            best_data = data
            low = mid + 1
        else:
            high = mid - 1

    return best_data


def process_single_file(dest_dir: Path, path: Path):
    try:
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size
        if w != TARGET_WIDTH:
            new_h = int(h * TARGET_WIDTH / w)
            img = img.resize((TARGET_WIDTH, new_h), Image.LANCZOS)

        jpeg_data = compress_to_target(img, MAX_FILE_SIZE)
        if jpeg_data is None:
            print(f"  [ERROR] {path.name} - cannot compress under 300KB")
            return "error"

        dest_path = dest_dir / path.name
        dest_path.write_bytes(jpeg_data)
        size_kb = len(jpeg_data) / 1024
        print(f"  [OK] {path.name} -> {OUTPUT_FOLDER}/ ({size_kb:.0f}KB)")
        return "success"
    except Exception as e:
        print(f"  [ERROR] {path.name} - {e}")
        return "error"


def process_folder(base_dir: Path):
    jpg_files = sorted(
        [p for p in base_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS],
        key=lambda p: p.name,
    )

    if not jpg_files:
        print("No JPG files found.")
        return

    dest_dir = base_dir / OUTPUT_FOLDER
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"JPG files: {len(jpg_files)}\n")
    success_count = 0
    error_count = 0

    for path in jpg_files:
        result = process_single_file(dest_dir, path)
        if result == "success":
            success_count += 1
        else:
            error_count += 1

    print("\n--- Result ---")
    print(f"Success: {success_count}")
    if error_count > 0:
        print(f"Error: {error_count}")


if __name__ == "__main__":
    try:
        if sys.platform == "win32":
            try:
                sys.stdout.reconfigure(encoding="utf-8")
                sys.stderr.reconfigure(encoding="utf-8")
            except Exception:
                pass

        base_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
        base_dir = base_dir.expanduser().resolve()
        print(f"Base folder: {base_dir}")
        print("=" * 60)
        process_folder(base_dir)
    except Exception as e:
        print(f"Script error: {e}")
