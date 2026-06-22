# -*- coding: utf-8 -*-
"""신청서 [원본] 이미지 파일명 변경 GUI.

카카오톡 등으로 받은 원본 신청서 이미지를 보면서
파일명을 `구좌수+이름` 형식으로 빠르게 바꾸는 도구입니다.

예)
    1홍길동.jpg
    2김영희.jpg
    5박철수.jpg

동일 파일명이 이미 있으면 덮어쓰지 않고 `(2)`, `(3)`을 자동으로 붙입니다.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import pandas as pd
from PIL import Image, ImageOps, ImageTk


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
INVALID_FILENAME_CHARS = r'<>:"/\|?*'
SMART_LOOKUP_SCRIPT = Path(r"E:\GoogleDrive\코드\전화번호추출\smart_lookup.py")
COMPLEMENT_REASONS = [
    "남녀구분미체크",
    "계좌보완",
    "타인계좌",
    "주소보완",
    "계약일보완",
    "가입동기보완",
    "화산미기입",
]
STATUS_FOLDERS = {
    "주말미등록": "주말미등록",
    "입력전 취소": "입력전 취소",
    "입력후 취소": "입력후 취소",
    "입력전 변경": "입력전 변경",
    "입력후 변경": "입력후 변경",
    "카드": "카드",
}
STATUS_TXT_SECTIONS = {
    "보완": "●보완",
    "주말미등록": "●주말미등록",
    "입력전 취소": "●입력전 취소",
    "입력후 취소": "●입력후 취소",
    "입력전 변경": "●입력전 변경",
    "입력후 변경": "●입력후 변경",
}
MANAGED_TXT_SECTIONS = set(STATUS_TXT_SECTIONS.values()) | {"●카드"}


if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def natural_key(path: Path):
    """파일명을 숫자 순서에 맞게 정렬하기 위한 키."""
    parts = re.split(r"(\d+)", path.name)
    return [int(p) if p.isdigit() else p.casefold() for p in parts]


def resolve_original_dir(target: Path) -> Path:
    """실행 위치 또는 인자로 받은 위치에서 실제 [원본] 폴더를 찾는다."""
    target = target.expanduser().resolve()

    candidates = []
    if target.name == "[원본]":
        candidates.append(target)
    candidates.append(target / "[원본]")
    candidates.append(target / "신청서" / "[원본]")

    for candidate in candidates:
        if candidate.is_dir():
            return candidate

    if target.is_dir():
        return target

    raise FileNotFoundError(f"대상 폴더를 찾지 못했습니다: {target}")


def list_images(original_dir: Path) -> list[Path]:
    """[원본] 폴더와 모든 하위 폴더의 이미지 파일을 불러온다."""
    files = [
        p for p in original_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS and not p.name.startswith("~$")
    ]
    return sorted(files, key=image_sort_key)


def image_sort_key(path: Path):
    quota, name = parse_quota_name(path)
    quota_num = int(quota) if quota.isdigit() else 9999
    folder_rank = 1 if any(part == "보완" for part in path.parts) else 0
    return (quota_num, name, folder_rank, natural_key(path))


def parse_quota_name(path: Path) -> tuple[str, str]:
    """이미 이름이 바뀐 파일이면 구좌수와 이름을 미리 채운다."""
    stem = path.stem.strip()
    stem = re.sub(r"\s+\(\d+\)$", "", stem)
    m = re.match(r"^(\d+)\s*(.+)$", stem)
    if not m:
        return "", ""
    quota = m.group(1).strip()
    name = m.group(2).strip()
    return quota, name


def parse_combined_input(value: str) -> tuple[str, str]:
    """`3홍길동` 또는 `3 홍길동` 형식의 빠른 입력값을 나눈다."""
    value = str(value or "").strip()
    m = re.match(r"^(\d+)\s*(.+)$", value)
    if not m:
        return "", ""
    return m.group(1).strip(), m.group(2).strip()


def sanitize_name(value: str) -> str:
    """Windows 파일명에 쓸 수 없는 문자를 제거한다."""
    value = str(value or "").strip()
    for ch in INVALID_FILENAME_CHARS:
        value = value.replace(ch, "")
    value = re.sub(r"\s+", "", value)
    value = value.rstrip(". ")
    return value


def same_path(a: Path, b: Path) -> bool:
    return os.path.normcase(os.path.abspath(str(a))) == os.path.normcase(os.path.abspath(str(b)))


def unique_target_path(current: Path, stem: str) -> Path:
    """덮어쓰지 않는 대상 파일 경로를 만든다."""
    suffix = current.suffix.lower()
    target = current.with_name(stem + suffix)
    if same_path(current, target):
        return target
    if not target.exists():
        return target

    n = 2
    while True:
        candidate = current.with_name(f"{stem} ({n}){suffix}")
        if same_path(current, candidate) or not candidate.exists():
            return candidate
        n += 1


def unique_path_in_dir(source: Path, target_dir: Path) -> Path:
    """다른 폴더로 옮길 때도 덮어쓰지 않는 대상 경로를 만든다."""
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    if same_path(source, target):
        return target
    if not target.exists():
        return target

    n = 2
    while True:
        candidate = target_dir / f"{source.stem} ({n}){source.suffix.lower()}"
        if not candidate.exists():
            return candidate
        n += 1


def find_event_txt(application_dir: Path) -> Path | None:
    """강연회 폴더명과 같은 TXT 파일을 찾는다."""
    event_dir = application_dir.parent
    preferred = event_dir / f"{event_dir.name}.txt"
    if preferred.exists():
        return preferred
    candidates = [p for p in event_dir.glob("*.txt") if not p.name.startswith("~$")]
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.stat().st_mtime)[-1]


def read_text_flexible(path: Path) -> tuple[str, str]:
    """대부분 UTF-8이지만, 깨진 구형 파일을 대비해 CP949도 시도한다."""
    for encoding in ("utf-8", "cp949"):
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace"), "utf-8"


def append_line_to_section(txt_path: Path, section_marker: str, line: str) -> None:
    """강연회 TXT의 지정 섹션에 내역을 추가한다."""
    text, encoding = read_text_flexible(txt_path)
    lines = text.splitlines()
    if line in lines:
        return

    marker_index = None
    for i, value in enumerate(lines):
        if value.strip() == section_marker:
            marker_index = i
            break

    if marker_index is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([section_marker, line])
    else:
        insert_at = marker_index + 1
        while insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
        lines.insert(insert_at, line)

    txt_path.write_text("\n".join(lines) + "\n", encoding=encoding)


def txt_line_matches_stem(line: str, stem: str) -> bool:
    value = line.strip()
    value = re.sub(r"^[ㆍ•\-\s]+", "", value)
    value = re.split(r"[-\t]", value, maxsplit=1)[0].strip()
    return value == stem


def update_txt_status(txt_path: Path, stem: str, status: str, reasons: list[str], change_from: str = "", change_to: str = "") -> None:
    """관리 대상 섹션에서 기존 파일 기록을 제거하고 현재 상태만 반영한다."""
    text, encoding = read_text_flexible(txt_path)
    lines = text.splitlines()
    new_lines = []
    current_section = ""

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("●"):
            current_section = stripped
            new_lines.append(line)
            continue
        if current_section in MANAGED_TXT_SECTIONS and txt_line_matches_stem(line, stem):
            continue
        new_lines.append(line)

    if status and status in STATUS_TXT_SECTIONS:
        marker = STATUS_TXT_SECTIONS[status]
        if status == "보완":
            line = f"{stem}\t{', '.join(reasons)}"
        elif status in {"입력전 변경", "입력후 변경"} and change_from and change_to:
            _old_quota, name = parse_quota_name(Path(stem))
            line = f"{name}\t{change_from}구좌-->{change_to}구좌"
        else:
            line = stem

        marker_index = None
        for i, value in enumerate(new_lines):
            if value.strip() == marker:
                marker_index = i
                break

        if marker_index is None:
            while new_lines and new_lines[-1].strip() == "":
                new_lines.pop()
            if new_lines:
                new_lines.append("")
            new_lines.extend([marker, line])
        else:
            insert_at = marker_index + 1
            while insert_at < len(new_lines) and new_lines[insert_at].strip() == "":
                new_lines.pop(insert_at)
            new_lines.insert(insert_at, line)

    normalized = normalize_section_layout(new_lines)
    txt_path.write_text("\n".join(normalized) + "\n", encoding=encoding)


def normalize_section_layout(lines: list[str]) -> list[str]:
    """섹션 위에는 빈 줄 1개, 섹션 바로 아래에는 빈 줄 0개로 정리한다."""
    out: list[str] = []
    current_marker = ""
    seen_section = False

    for raw in lines:
        stripped = raw.strip()

        if stripped.startswith("●"):
            seen_section = True
            current_marker = stripped
            if current_marker == "●카드":
                continue
            while out and out[-1].strip() == "":
                out.pop()
            if out:
                out.append("")
            out.append(current_marker)
            continue

        if current_marker == "●카드":
            continue

        if stripped == "":
            if not seen_section:
                out.append(raw)
            continue
        out.append(raw)

    while out and out[-1].strip() == "":
        out.pop()
    return out


def find_saved_complement_reasons(txt_path: Path | None, stem: str) -> list[str]:
    if not txt_path or not txt_path.exists():
        return []
    text, _encoding = read_text_flexible(txt_path)
    current_section = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("●"):
            current_section = stripped
            continue
        if current_section != STATUS_TXT_SECTIONS["보완"]:
            continue
        if not txt_line_matches_stem(line, stem):
            continue
        if "\t" in line:
            reason_text = line.split("\t", 1)[1].strip()
        elif "-" in line:
            reason_text = line.split("-", 1)[1].strip()
        else:
            return []
        return [reason.strip() for reason in reason_text.split(",") if reason.strip()]
    return []


class ImageCache:
    """이미지 재로드를 줄이기 위한 작은 캐시."""

    def __init__(self, max_items: int = 8):
        self.max_items = max_items
        self.cache: dict[str, Image.Image] = {}
        self.order: list[str] = []

    def get(self, path: Path) -> Image.Image:
        key = str(path)
        if key in self.cache:
            return self.cache[key]

        image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        self.cache[key] = image
        self.order.append(key)
        while len(self.order) > self.max_items:
            old = self.order.pop(0)
            self.cache.pop(old, None)
        return image

    def rename_key(self, old: Path, new: Path) -> None:
        old_key = str(old)
        new_key = str(new)
        if old_key in self.cache:
            self.cache[new_key] = self.cache.pop(old_key)
            self.order = [new_key if x == old_key else x for x in self.order]


class RenameTab(ttk.Frame):
    def __init__(self, master, original_dir: Path, app=None):
        super().__init__(master)
        self.app = app
        self.original_dir = original_dir
        self.application_dir = original_dir.parent if original_dir.name == "[\uc6d0\ubcf8]" else original_dir
        self.event_dir = self.application_dir.parent
        self.progress_path = original_dir / ".rename_progress.json"
        self.all_images = list_images(original_dir)
        self.images = list(self.all_images)
        self.idx = 0
        self.photo = None
        self.cache = ImageCache()
        self.view_zoom = 1.0
        self.view_offset_x_ratio = 0.0
        self.view_offset_y_ratio = 0.0
        self.view_locked = False
        self.drag_start = None

        self.quota_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.combined_var = tk.StringVar()
        self.preview_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.current_file_var = tk.StringVar()
        self.syncing_input = False
        self.space_save_pending = False
        self.lookup_running = False
        self.external_bat_running = False
        self.lookup_df = pd.DataFrame()
        self.lookup_search_var = tk.StringVar()
        self.filter_status_var = tk.StringVar(value="전체")
        self.filter_search_var = tk.StringVar()
        self.status_vars = {status: tk.BooleanVar(value=False) for status in STATUS_FOLDERS}
        self.reason_vars = {reason: tk.BooleanVar(value=False) for reason in COMPLEMENT_REASONS}
        self.change_quota_var = tk.StringVar()
        self.loading_status = False


        self.load_progress()
        self.build_ui()
        self.bind_keys()
        self.populate_list()
        self.show_item(self.idx)

    def load_progress(self) -> None:
        if not self.progress_path.exists():
            return
        try:
            data = json.loads(self.progress_path.read_text(encoding="utf-8"))
            self.idx = int(data.get("last_index", 0))
        except Exception:
            self.idx = 0

    def save_progress(self) -> None:
        data = {
            "last_index": self.idx,
            "updated_at": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.progress_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def build_ui(self) -> None:
        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)
        ttk.Label(top, textvariable=self.status_var).pack(side=tk.LEFT)
        ttk.Button(top, text="폴더 열기", command=self.open_folder).pack(side=tk.RIGHT, padx=3)
        ttk.Button(top, text="새로고침", command=self.reload_images).pack(side=tk.RIGHT, padx=3)

        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = ttk.Frame(paned)
        paned.add(left, weight=0)
        filter_bar = ttk.Frame(left)
        filter_bar.pack(side=tk.TOP, fill=tk.X, pady=(0, 4))
        ttk.Label(filter_bar, text="상태").grid(row=0, column=0, sticky="w", padx=(0, 3))
        self.filter_status_combo = ttk.Combobox(
            filter_bar,
            textvariable=self.filter_status_var,
            values=["전체", "CMS", "보완", "주말미등록", "입력전 취소", "입력후 취소", "입력전 변경", "입력후 변경", "카드"],
            state="readonly",
            width=12,
        )
        self.filter_status_combo.grid(row=0, column=1, sticky="ew", padx=(0, 3))
        self.filter_status_combo.bind("<<ComboboxSelected>>", lambda _e: self.apply_filter())
        ttk.Label(filter_bar, text="검색").grid(row=1, column=0, sticky="w", padx=(0, 3), pady=(3, 0))
        self.filter_search_entry = ttk.Entry(filter_bar, textvariable=self.filter_search_var, width=18)
        self.filter_search_entry.grid(row=1, column=1, sticky="ew", padx=(0, 3), pady=(3, 0))
        self.filter_search_entry.bind("<Return>", lambda _e: self.apply_filter())
        ttk.Button(filter_bar, text="적용", command=self.apply_filter).grid(row=0, column=2, rowspan=2, sticky="ns", padx=(2, 0))
        ttk.Button(filter_bar, text="초기화", command=self.clear_filter).grid(row=0, column=3, rowspan=2, sticky="ns", padx=(2, 0))
        filter_bar.columnconfigure(1, weight=1)
        self.listbox = tk.Listbox(left, width=42, font=("Malgun Gothic", 10), exportselection=False)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.listbox.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=sb.set)
        self.listbox.bind("<<ListboxSelect>>", self.on_list_select)
        self.listbox.bind("<Down>", lambda e: self.nav_and_stop(self.next_item))
        self.listbox.bind("<Up>", lambda e: self.nav_and_stop(self.prev_item))
        self.listbox.bind("<Prior>", lambda e: self.nav_and_stop(lambda: self.jump(-10)))
        self.listbox.bind("<Next>", lambda e: self.nav_and_stop(lambda: self.jump(10)))

        center = ttk.Frame(paned)
        paned.add(center, weight=3)
        self.canvas = tk.Canvas(center, bg="#202020", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda _e: self.render_image())
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Triple-Button-1>", self.reset_canvas_view)
        self.canvas.bind("<MouseWheel>", self.on_canvas_wheel)

        right = ttk.Frame(paned)
        paned.add(right, weight=1)

        ttk.Label(right, text="현재 파일", font=("Malgun Gothic", 11, "bold")).pack(anchor=tk.W)
        ttk.Label(right, textvariable=self.current_file_var, wraplength=360).pack(anchor=tk.W, fill=tk.X, pady=(2, 12))

        form = ttk.LabelFrame(right, text="파일명 입력")
        form.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(form, text="구좌수+이름").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.combined_entry = ttk.Entry(form, textvariable=self.combined_var, width=24, font=("Malgun Gothic", 18))
        self.combined_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=6)
        self.combined_entry.bind("<KeyRelease>", self.on_entry_key_release)
        self.combined_entry.bind("<Up>", lambda _e: self.event_and_stop(self.prev_item))
        self.combined_entry.bind("<Down>", lambda _e: self.event_and_stop(self.next_item))
        self.combined_entry.bind("<Prior>", lambda _e: self.event_and_stop(lambda: self.jump(-10)))
        self.combined_entry.bind("<Next>", lambda _e: self.event_and_stop(lambda: self.jump(10)))

        ttk.Label(form, text="구좌수").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.quota_entry = ttk.Entry(form, textvariable=self.quota_var, width=10, font=("Malgun Gothic", 14))
        self.quota_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=6)
        self.quota_entry.bind("<KeyRelease>", self.on_entry_key_release)
        self.quota_entry.bind("<Up>", lambda _e: self.event_and_stop(self.prev_item))
        self.quota_entry.bind("<Down>", lambda _e: self.event_and_stop(self.next_item))

        ttk.Label(form, text="이름").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.name_entry = ttk.Entry(form, textvariable=self.name_var, width=24, font=("Malgun Gothic", 14))
        self.name_entry.grid(row=2, column=1, sticky="ew", padx=8, pady=6)
        self.name_entry.bind("<KeyRelease>", self.on_entry_key_release)
        self.name_entry.bind("<Up>", lambda _e: self.event_and_stop(self.prev_item))
        self.name_entry.bind("<Down>", lambda _e: self.event_and_stop(self.next_item))

        ttk.Label(form, text="변경될 이름").grid(row=3, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(form, textvariable=self.preview_var, foreground="#0b5394", wraplength=320, font=("Malgun Gothic", 12, "bold")).grid(row=3, column=1, sticky="w", padx=8, pady=6)
        form.columnconfigure(1, weight=1)

        btns = ttk.Frame(right)
        btns.pack(fill=tk.X, pady=8)
        ttk.Button(btns, text="저장 후 다음 (Space)", command=self.rename_and_next).pack(fill=tk.X, pady=3)
        ttk.Button(btns, text="저장만 (Ctrl+S)", command=self.rename_current).pack(fill=tk.X, pady=3)
        ttk.Button(btns, text="건너뛰기 (↓)", command=self.next_item).pack(fill=tk.X, pady=3)
        ttk.Button(btns, text="이전", command=self.prev_item).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3), pady=3)
        ttk.Button(btns, text="다음", command=self.next_item).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0), pady=3)

        help_text = (
            "사용법\n"
            "1. 신청서 이미지를 보고 구좌수와 이름을 입력\n"
            "2. Space: 파일명 변경 후 다음 이미지\n"
            "3. ↓: 변경 없이 다음 이미지\n"
            "4. ↑: 이전 이미지\n"
            "5. PgUp/PgDn: 10개씩 이동\n\n"
            "덮어쓰기 방지\n"
            "같은 파일명이 있으면 자동으로 (2), (3)을 붙입니다."
        )
        ttk.Label(right, text=help_text, justify=tk.LEFT, wraplength=360).pack(anchor=tk.W, fill=tk.X, pady=12)

        lookup = ttk.LabelFrame(right, text="전화번호 매칭")
        lookup.pack(fill=tk.BOTH, expand=True, pady=(4, 8))
        lookup_btns = ttk.Frame(lookup)
        lookup_btns.pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(lookup_btns, text="조회 실행/재실행", command=self.run_smart_lookup_async).pack(side=tk.LEFT, padx=2)
        ttk.Button(lookup_btns, text="결과 새로고침", command=self.load_lookup_result).pack(side=tk.LEFT, padx=2)
        work_btns = ttk.Frame(lookup)
        work_btns.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(
            work_btns,
            text="2. 신청서정리 실행",
            command=lambda: self.run_local_bat_async("2.신청서정리.bat", "신청서정리"),
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            work_btns,
            text="3. 전체신청서대조 실행",
            command=lambda: self.run_local_bat_async("3.전화번호대조_전체신청서.bat", "전체신청서대조"),
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            work_btns,
            text="보고서생성 실행",
            command=lambda: self.run_local_bat_async("보고서생성.bat", "보고서생성", base_dir=self.event_dir, reload_after=False),
        ).pack(side=tk.LEFT, padx=2)
        open_btns = ttk.Frame(lookup)
        open_btns.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(open_btns, text="TXT 열기", command=self.open_event_txt).pack(side=tk.LEFT, padx=2)
        ttk.Button(open_btns, text="엑셀 열기", command=self.open_lookup_excel).pack(side=tk.LEFT, padx=2)
        ttk.Button(open_btns, text="보고서 열기", command=self.open_report_file).pack(side=tk.LEFT, padx=2)
        ttk.Entry(lookup, textvariable=self.lookup_search_var).pack(fill=tk.X, padx=6, pady=(2, 2))
        ttk.Button(lookup, text="이름/번호 검색", command=self.search_lookup_result).pack(fill=tk.X, padx=6, pady=(0, 4))
        self.lookup_text = tk.Text(lookup, height=8, wrap=tk.WORD, font=("Consolas", 9))
        self.lookup_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        complement = ttk.LabelFrame(right, text="상태 처리")
        complement.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(complement, text="보완 사유", font=("Malgun Gothic", 9, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=6, pady=(4, 2))
        for i, reason in enumerate(COMPLEMENT_REASONS):
            ttk.Checkbutton(complement, text=reason, variable=self.reason_vars[reason], command=self.on_reason_checked).grid(
                row=1 + (i // 2),
                column=i % 2,
                sticky="w",
                padx=6,
                pady=2,
            )
        ttk.Label(complement, text="기타 상태", font=("Malgun Gothic", 9, "bold")).grid(row=5, column=0, columnspan=4, sticky="w", padx=6, pady=(8, 2))
        for i, status in enumerate(STATUS_FOLDERS):
            ttk.Checkbutton(complement, text=status, variable=self.status_vars[status], command=lambda s=status: self.on_status_checked(s)).grid(
                row=6 + (i // 3),
                column=i % 3,
                sticky="w",
                padx=6,
                pady=2,
            )
        ttk.Label(complement, text="변경 구좌수").grid(row=8, column=0, sticky="w", padx=6, pady=(6, 2))
        self.change_quota_entry = ttk.Entry(complement, textvariable=self.change_quota_var, width=6)
        self.change_quota_entry.grid(row=8, column=1, sticky="w", padx=6, pady=(6, 2))
        ttk.Button(complement, text="다음 (Space)", command=self.next_item).grid(
            row=9,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=6,
            pady=6,
        )
        for col in range(4):
            complement.columnconfigure(col, weight=1)


    def bind_keys(self) -> None:
        self.bind("<Up>", lambda _e: self.prev_item())
        self.bind("<Down>", lambda _e: self.next_item())
        self.bind("<Control-s>", lambda _e: self.rename_current())
        self.bind("<Prior>", lambda _e: self.jump(-10))
        self.bind("<Next>", lambda _e: self.jump(10))
        self.bind("<Escape>", lambda _e: self.winfo_toplevel().destroy())

    def nav_and_stop(self, func):
        func()
        return "break"

    def event_and_stop(self, func):
        func()
        return "break"

    def on_entry_key_release(self, event) -> None:
        self.update_preview()
        # 한글 IME 조합 중에는 'ㅡ' 같은 입력이 Tkinter에서 keysym=space처럼
        # 들어오는 경우가 있다. 실제 물리 스페이스키는 Windows Tk 기준 keycode 32이므로
        # keycode로만 저장 단축키를 판정한다.
        if getattr(event, "keycode", None) == 32:
            self.schedule_space_save()

    def schedule_space_save(self) -> None:
        if self.space_save_pending:
            return
        self.space_save_pending = True
        self.after(120, self.run_space_save)

    def run_space_save(self) -> None:
        self.space_save_pending = False
        self.trim_entry_spaces()
        if self.rename_input_changed():
            self.rename_and_next(silent=True)
        else:
            self.next_item()

    def trim_entry_spaces(self) -> None:
        self.syncing_input = True
        try:
            self.combined_var.set(self.combined_var.get().strip())
            self.quota_var.set(self.quota_var.get().strip())
            self.name_var.set(self.name_var.get().strip())
        finally:
            self.syncing_input = False
        self.update_preview()

    def on_combined_changed(self) -> None:
        if self.syncing_input:
            return
        quota, name = parse_combined_input(self.combined_var.get())
        if not quota and not name:
            self.update_preview()
            return
        self.syncing_input = True
        try:
            self.quota_var.set(quota)
            self.name_var.set(name)
        finally:
            self.syncing_input = False
        self.update_preview()

    def on_split_changed(self) -> None:
        if self.syncing_input:
            return
        quota = self.quota_var.get().strip()
        name = self.name_var.get().strip()
        self.syncing_input = True
        try:
            self.combined_var.set(f"{quota}{name}" if quota or name else "")
        finally:
            self.syncing_input = False
        self.update_preview()

    def populate_list(self) -> None:
        self.listbox.delete(0, tk.END)
        for i, path in enumerate(self.images, 1):
            quota, name = parse_quota_name(path)
            mark = "✓ " if quota and name else "  "
            status = self.status_for_path(path)
            status_text = f" [{status}]" if status else ""
            self.listbox.insert(tk.END, f"{i:03d}. {mark}{path.name}{status_text}")
            if status == "보완":
                self.listbox.itemconfig(i - 1, bg="#ffe0b2", fg="#5d3300", selectbackground="#ffb74d", selectforeground="black")
            elif status == "주말미등록":
                self.listbox.itemconfig(i - 1, bg="#d6eaf8", fg="#154360", selectbackground="#85c1e9", selectforeground="black")
            elif "취소" in status:
                self.listbox.itemconfig(i - 1, bg="#f5b7b1", fg="#641e16", selectbackground="#ec7063", selectforeground="black")
            elif "변경" in status:
                self.listbox.itemconfig(i - 1, bg="#fcf3cf", fg="#7d6608", selectbackground="#f7dc6f", selectforeground="black")
            elif status == "카드":
                self.listbox.itemconfig(i - 1, bg="#d7bde2", fg="#4a235a", selectbackground="#bb8fce", selectforeground="black")
            elif quota and name:
                self.listbox.itemconfig(i - 1, bg="#e6f4ea", fg="#124116", selectbackground="#81c784", selectforeground="black")

    def on_list_select(self, _event=None) -> None:
        sel = self.listbox.curselection()
        if sel:
            self.show_item(sel[0])

    def status_for_path(self, path: Path) -> str:
        if not path.is_relative_to(self.original_dir):
            return ""
        parts = path.relative_to(self.original_dir).parts
        if "보완" in parts:
            return "보완"
        for status, folder in STATUS_FOLDERS.items():
            if folder in parts:
                return status
        return ""

    def apply_filter(self, keep_path: Path | None = None) -> None:
        status_filter = self.filter_status_var.get().strip() or "전체"
        query = self.filter_search_var.get().strip()
        query_key = re.sub(r"\s+", "", query).lower()

        filtered = []
        for path in self.all_images:
            status = self.status_for_path(path)
            if status_filter == "CMS":
                if status:
                    continue
            elif status_filter != "전체":
                if status != status_filter:
                    continue

            if query_key:
                rel = str(path.relative_to(self.original_dir)) if path.is_relative_to(self.original_dir) else path.name
                haystack = re.sub(r"\s+", "", f"{path.name} {rel} {status}").lower()
                if query_key not in haystack:
                    continue

            filtered.append(path)

        preferred = keep_path or self.current_path()
        self.images = filtered
        if preferred is not None:
            try:
                preferred_resolved = preferred.resolve()
                self.idx = next(
                    i for i, path in enumerate(self.images)
                    if path.resolve() == preferred_resolved
                )
            except Exception:
                self.idx = min(self.idx, max(0, len(self.images) - 1))
        else:
            self.idx = min(self.idx, max(0, len(self.images) - 1))

        self.populate_list()
        self.show_item(self.idx)

    def clear_filter(self) -> None:
        self.filter_status_var.set("전체")
        self.filter_search_var.set("")
        self.apply_filter()

    def load_status_for_current_path(self, path: Path) -> None:
        current_status = self.status_for_path(path)
        saved_reasons = find_saved_complement_reasons(find_event_txt(self.application_dir), path.stem) if current_status == "보완" else []
        self.loading_status = True
        try:
            for reason, reason_var in self.reason_vars.items():
                reason_var.set(reason in saved_reasons)
            for status, var in self.status_vars.items():
                var.set(status == current_status)
            self.change_quota_var.set("")
        finally:
            self.loading_status = False

    def has_any_status_selection(self) -> bool:
        return any(var.get() for var in self.status_vars.values()) or any(var.get() for var in self.reason_vars.values())

    def rename_input_changed(self) -> bool:
        path = self.current_path()
        if not path:
            return False
        combined_quota, combined_name = parse_combined_input(self.combined_var.get())
        quota = combined_quota or self.quota_var.get().strip()
        name = sanitize_name(combined_name or self.name_var.get())
        if not quota or not name or not re.fullmatch(r"\d+", quota):
            return False
        return f"{int(quota)}{name}" != path.stem

    def on_reason_checked(self) -> None:
        if self.loading_status:
            return
        if any(var.get() for var in self.reason_vars.values()):
            self.loading_status = True
            try:
                for var in self.status_vars.values():
                    var.set(False)
            finally:
                self.loading_status = False
        self.apply_current_status(move_next=False, silent=True)

    def on_status_checked(self, clicked_status: str) -> None:
        if self.loading_status:
            return
        self.loading_status = True
        try:
            if self.status_vars[clicked_status].get():
                for status, var in self.status_vars.items():
                    if status != clicked_status:
                        var.set(False)
                for var in self.reason_vars.values():
                    var.set(False)
                if clicked_status not in {"입력전 변경", "입력후 변경"}:
                    self.change_quota_var.set("")
        finally:
            self.loading_status = False
        if clicked_status in {"입력전 변경", "입력후 변경"} and not self.change_quota_var.get().strip():
            self.change_quota_entry.focus_set()
            return
        self.apply_current_status(move_next=False, silent=True)

    def show_item(self, index: int) -> None:
        if not self.images:
            self.status_var.set(f"이미지 없음: {self.original_dir}")
            self.current_file_var.set("")
            self.canvas.delete("all")
            return

        self.idx = max(0, min(index, len(self.images) - 1))
        path = self.images[self.idx]
        quota, name = parse_quota_name(path)
        self.syncing_input = True
        try:
            self.quota_var.set(quota)
            self.name_var.set(name)
            self.combined_var.set(f"{quota}{name}" if quota and name else "")
        finally:
            self.syncing_input = False
        self.current_file_var.set(str(path.relative_to(self.original_dir)) if path.is_relative_to(self.original_dir) else path.name)
        self.status_var.set(f"{self.idx + 1}/{len(self.images)} | 대상: {self.original_dir}")
        self.load_status_for_current_path(path)

        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.idx)
        self.listbox.see(self.idx)
        self.update_preview()
        self.render_image()
        self.combined_entry.focus_set()
        self.combined_entry.select_range(0, tk.END)
        self.save_progress()

    def current_path(self) -> Path | None:
        if not self.images:
            return None
        return self.images[self.idx]

    def update_preview(self) -> None:
        path = self.current_path()
        suffix = path.suffix.lower() if path else ".jpg"
        combined_quota, combined_name = parse_combined_input(self.combined_var.get())
        quota = combined_quota or self.quota_var.get().strip()
        name = sanitize_name(combined_name or self.name_var.get())
        if quota and name:
            self.preview_var.set(f"{quota}{name}{suffix}")
        else:
            self.preview_var.set("(구좌수와 이름을 입력)")

    def render_image(self) -> None:
        self.canvas.delete("all")
        path = self.current_path()
        if not path:
            return
        try:
            image = self.cache.get(path)
        except Exception as e:
            self.canvas.create_text(20, 20, anchor="nw", fill="white", text=f"이미지 열기 실패\n{e}", font=("Malgun Gothic", 16))
            return

        cw = max(100, self.canvas.winfo_width())
        ch = max(100, self.canvas.winfo_height())
        fit_scale = min(cw / image.width, ch / image.height) * 0.98
        if not self.view_locked:
            self.view_zoom = 1.0
            self.view_offset_x_ratio = 0.0
            self.view_offset_y_ratio = 0.0
        scale = fit_scale * self.view_zoom
        offset_x = int(self.view_offset_x_ratio * cw)
        offset_y = int(self.view_offset_y_ratio * ch)
        width = max(1, int(image.width * scale))
        height = max(1, int(image.height * scale))
        view = image.resize((width, height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(view)
        self.canvas.create_image(cw // 2 + offset_x, ch // 2 + offset_y, image=self.photo, anchor="center")

    def on_canvas_press(self, event) -> None:
        width = max(1, self.canvas.winfo_width())
        if event.x < width * 0.25:
            self.prev_item()
            self.drag_start = None
            return
        if event.x > width * 0.75:
            self.next_item()
            self.drag_start = None
            return
        self.drag_start = (event.x, event.y, self.view_offset_x_ratio, self.view_offset_y_ratio)

    def on_canvas_drag(self, event) -> None:
        if not self.drag_start:
            return
        sx, sy, ox, oy = self.drag_start
        cw = max(1, self.canvas.winfo_width())
        ch = max(1, self.canvas.winfo_height())
        self.view_locked = True
        self.view_offset_x_ratio = ox + ((event.x - sx) / cw)
        self.view_offset_y_ratio = oy + ((event.y - sy) / ch)
        self.render_image()

    def on_canvas_release(self, _event) -> None:
        self.drag_start = None

    def on_canvas_wheel(self, event) -> str:
        factor = 1.12 if event.delta > 0 else 1 / 1.12
        old_zoom = self.view_zoom
        new_zoom = max(0.1, min(8.0, old_zoom * factor))
        if abs(new_zoom - old_zoom) < 0.0001:
            return "break"

        cw = max(1, self.canvas.winfo_width())
        ch = max(1, self.canvas.winfo_height())
        offset_x = self.view_offset_x_ratio * cw
        offset_y = self.view_offset_y_ratio * ch
        center_x = cw / 2 + offset_x
        center_y = ch / 2 + offset_y
        rel_x = event.x - center_x
        rel_y = event.y - center_y
        ratio = new_zoom / old_zoom if old_zoom else 1

        self.view_zoom = new_zoom
        self.view_offset_x_ratio = (event.x - cw / 2 - rel_x * ratio) / cw
        self.view_offset_y_ratio = (event.y - ch / 2 - rel_y * ratio) / ch
        self.view_locked = True
        self.render_image()
        return "break"

    def reset_canvas_view(self, _event=None) -> str:
        self.view_locked = False
        self.view_zoom = 1.0
        self.view_offset_x_ratio = 0.0
        self.view_offset_y_ratio = 0.0
        self.render_image()
        return "break"

    def validate_input(self, silent: bool = False) -> tuple[str, str] | None:
        combined_quota, combined_name = parse_combined_input(self.combined_var.get())
        quota = combined_quota or self.quota_var.get().strip()
        name = sanitize_name(combined_name or self.name_var.get())
        if not re.fullmatch(r"\d+", quota):
            if not silent:
                messagebox.showwarning("입력 확인", "구좌수+이름 형식으로 입력해야 합니다. 예: 3홍길동")
            self.combined_entry.focus_set()
            return None
        if int(quota) <= 0:
            if not silent:
                messagebox.showwarning("입력 확인", "구좌수는 1 이상이어야 합니다.")
            self.combined_entry.focus_set()
            return None
        if not name:
            if not silent:
                messagebox.showwarning("입력 확인", "이름을 입력해야 합니다.")
            self.combined_entry.focus_set()
            return None
        return str(int(quota)), name

    def rename_current(self, silent: bool = False) -> bool:
        path = self.current_path()
        if not path:
            return False
        values = self.validate_input(silent=silent)
        if not values:
            return False

        quota, name = values
        target = unique_target_path(path, f"{quota}{name}")
        try:
            if not same_path(path, target):
                path.rename(target)
                self.cache.rename_key(path, target)
                self.images[self.idx] = target
            self.populate_list()
            self.listbox.selection_set(self.idx)
            self.listbox.see(self.idx)
            self.current_file_var.set(self.images[self.idx].name)
            self.update_preview()
            self.save_progress()
            return True
        except Exception as e:
            messagebox.showerror("? ?? ??", str(e))
            return False

    def rename_and_next(self, silent: bool = False) -> None:
        was_last = self.idx >= len(self.images) - 1
        if self.rename_current(silent=silent):
            if was_last:
                self.append_lookup_log("\n[INFO] 마지막 이미지까지 파일명 변경 완료. 전화번호 매칭을 실행합니다.\n")
                self.run_smart_lookup_async()
            else:
                self.next_item()

    def lookup_result_path(self) -> Path:
        return self.application_dir / f"전화번호_조회결과_{self.event_dir.name}.xlsx"

    def open_event_txt(self) -> None:
        txt_path = find_event_txt(self.application_dir)
        if not txt_path:
            self.append_lookup_log("[ERROR] 강연회 TXT 파일을 찾지 못했습니다.")
            return
        try:
            os.startfile(str(txt_path))
            self.append_lookup_log(f"[OPEN] TXT: {txt_path}")
        except Exception as e:
            self.append_lookup_log(f"[ERROR] TXT 열기 실패: {e}")

    def open_lookup_excel(self) -> None:
        path = self.lookup_result_path()
        if not path.exists():
            self.append_lookup_log(f"[ERROR] 전화번호 조회 결과 엑셀을 찾지 못했습니다: {path.name}")
            return
        try:
            os.startfile(str(path))
            self.append_lookup_log(f"[OPEN] Excel: {path}")
        except Exception as e:
            self.append_lookup_log(f"[ERROR] 엑셀 열기 실패: {e}")

    def find_report_file(self) -> Path | None:
        exact_names = [
            f"화산영업리포트_{self.event_dir.name}.txt",
            f"화산영업리포트_{self.event_dir.name}.xlsx",
        ]
        for name in exact_names:
            path = self.event_dir / name
            if path.exists():
                return path

        report_exts = {".txt", ".xlsx", ".xlsm", ".xls", ".docx", ".pdf"}
        candidates = []
        for path in self.event_dir.iterdir():
            if not path.is_file():
                continue
            if path.suffix.lower() not in report_exts:
                continue
            if path.name == "보고서생성.bat":
                continue
            if "화산영업리포트" in path.name or "보고서" in path.stem:
                candidates.append(path)
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.stat().st_mtime)

    def open_report_file(self) -> None:
        path = self.find_report_file()
        if not path:
            self.append_lookup_log("[ERROR] 열 수 있는 보고서 파일을 찾지 못했습니다.")
            return
        try:
            os.startfile(str(path))
            self.append_lookup_log(f"[OPEN] Report: {path}")
        except Exception as e:
            self.append_lookup_log(f"[ERROR] 보고서 열기 실패: {e}")

    def append_lookup_log(self, text: str) -> None:
        if not hasattr(self, "lookup_text"):
            return
        self.lookup_text.configure(state=tk.NORMAL)
        self.lookup_text.insert(tk.END, text)
        if not text.endswith("\n"):
            self.lookup_text.insert(tk.END, "\n")
        self.lookup_text.see(tk.END)
        self.lookup_text.configure(state=tk.DISABLED)

    def run_smart_lookup_async(self) -> None:
        if self.lookup_running:
            self.append_lookup_log("[INFO] 전화번호 매칭이 이미 실행 중입니다.")
            return
        if not SMART_LOOKUP_SCRIPT.exists():
            self.append_lookup_log(f"[ERROR] 조회 스크립트를 찾지 못했습니다: {SMART_LOOKUP_SCRIPT}")
            return
        self.lookup_running = True
        self.append_lookup_log("\n==========================================================")
        self.append_lookup_log("  전화번호 매칭 실행")
        self.append_lookup_log("==========================================================")
        self.append_lookup_log(f"[TARGET] {self.application_dir}")
        thread = threading.Thread(target=self._smart_lookup_worker, daemon=True)
        thread.start()

    def _smart_lookup_worker(self) -> None:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        cmd = [sys.executable, str(SMART_LOOKUP_SCRIPT), str(self.application_dir)]
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                creationflags=creationflags,
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                self.after(0, self.append_lookup_log, line.rstrip("\n"))
            exit_code = proc.wait()
            self.after(0, self._smart_lookup_done, exit_code)
        except Exception as e:
            self.after(0, self.append_lookup_log, f"[ERROR] {e}")
            self.after(0, self._smart_lookup_done, 1)

    def _smart_lookup_done(self, exit_code: int) -> None:
        self.lookup_running = False
        self.append_lookup_log(f"[DONE] exit={exit_code}")
        self.load_lookup_result()

    def run_local_bat_async(self, bat_name: str, label: str, base_dir: Path | None = None, reload_after: bool = True) -> None:
        if self.external_bat_running:
            self.append_lookup_log("[INFO] 다른 BAT 실행이 이미 진행 중입니다.")
            return

        run_dir = base_dir or self.application_dir
        bat_path = run_dir / bat_name
        if not bat_path.exists():
            self.append_lookup_log(f"[ERROR] BAT 파일을 찾지 못했습니다: {bat_path}")
            return

        self.external_bat_running = True
        self.append_lookup_log("\n==========================================================")
        self.append_lookup_log(f"  {label} 실행")
        self.append_lookup_log("==========================================================")
        self.append_lookup_log(f"[BAT] {bat_path}")
        self.append_lookup_log(f"[CWD] {run_dir}")

        thread = threading.Thread(target=self._local_bat_worker, args=(bat_path, label, run_dir, reload_after), daemon=True)
        thread.start()

    def _local_bat_worker(self, bat_path: Path, label: str, run_dir: Path, reload_after: bool) -> None:
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        cmd = ["cmd.exe", "/d", "/c", str(bat_path)]
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(run_dir),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=creationflags,
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                self.after(0, self.append_lookup_log, line.rstrip("\n"))
            exit_code = proc.wait()
            self.after(0, self._local_bat_done, label, exit_code, reload_after)
        except Exception as e:
            self.after(0, self.append_lookup_log, f"[ERROR] {label} 실행 실패: {e}")
            self.after(0, self._local_bat_done, label, 1, reload_after)

    def _local_bat_done(self, label: str, exit_code: int, reload_after: bool = True) -> None:
        self.external_bat_running = False
        self.append_lookup_log(f"[DONE] {label} exit={exit_code}")
        if reload_after:
            current = self.current_path()
            self.reload_images(keep_path=current)

    def load_lookup_result(self) -> None:
        path = self.lookup_result_path()
        if not path.exists():
            self.append_lookup_log(f"[INFO] 조회 결과 파일 없음: {path.name}")
            return
        try:
            self.lookup_df = pd.read_excel(path, dtype=str).fillna("")
        except Exception as e:
            self.append_lookup_log(f"[ERROR] 조회 결과 읽기 실패: {e}")
            return
        self.append_lookup_log(f"[OK] 조회 결과 로드: {path.name} / {len(self.lookup_df)}행")
        self.log_lookup_summary()
        self.show_lookup_rows(self.lookup_df.head(30))

    def log_lookup_summary(self) -> None:
        if self.lookup_df.empty:
            return
        phone_cols = [c for c in self.lookup_df.columns if "전화번호" in str(c)]
        if not phone_cols:
            self.append_lookup_log("[WARN] 조회 결과에 전화번호 열이 없습니다.")
            return

        rows = self.lookup_df.copy()
        name_col = "이름" if "이름" in rows.columns else None
        rows = rows[rows.apply(lambda r: any(str(v).strip() for v in r.values), axis=1)]
        total = len(rows)
        matched_mask = rows[phone_cols].apply(lambda r: any(str(v).strip() for v in r.values), axis=1)
        matched = int(matched_mask.sum())
        missing = total - matched
        self.append_lookup_log(f"[SUMMARY] 전화번호 매칭: {matched}/{total}명, 미매칭 {missing}명")

        if total and matched == 0:
            sample = []
            if name_col:
                sample = [str(x).strip() for x in rows[name_col].head(12).tolist() if str(x).strip()]
            self.append_lookup_log("[WARN] 참석자리스트는 읽혔지만 현재 파일명 이름과 일치하는 사람이 없습니다.")
            self.append_lookup_log("[WARN] 참석자리스트 파일이 다른 날짜/다른 강연회인지 확인하세요.")
            if sample:
                self.append_lookup_log("[WARN] 미매칭 예시: " + ", ".join(sample))

    def show_lookup_rows(self, df: pd.DataFrame) -> None:
        if df.empty:
            self.append_lookup_log("  검색 결과 없음")
            return
        text = df.to_string(index=False, max_rows=40)
        self.append_lookup_log("\n" + text + "\n")

    def search_lookup_result(self) -> None:
        if self.lookup_df.empty:
            self.load_lookup_result()
            if self.lookup_df.empty:
                return
        query = self.lookup_search_var.get().strip()
        if not query:
            self.show_lookup_rows(self.lookup_df.head(40))
            return
        query_digits = re.sub(r"\D+", "", query)

        def row_match(row) -> bool:
            values = [str(v) for v in row.values]
            joined = " ".join(values)
            if query in joined:
                return True
            if query_digits:
                digits = re.sub(r"\D+", "", joined)
                return query_digits in digits
            return False

        mask = self.lookup_df.apply(row_match, axis=1)
        result = self.lookup_df[mask]
        self.append_lookup_log(f"\n[SEARCH] {query} / {len(result)}건")
        self.show_lookup_rows(result.head(40))

    def selected_status(self) -> str:
        if any(var.get() for var in self.reason_vars.values()):
            return "보완"
        for status in STATUS_FOLDERS:
            if self.status_vars[status].get():
                return status
        return ""

    def apply_current_status(self, move_next: bool = False, silent: bool = False) -> None:
        path = self.current_path()
        if not path:
            return
        status = self.selected_status()
        reasons = [reason for reason, var in self.reason_vars.items() if var.get()]
        original_stem = path.stem
        current_quota, current_name = parse_quota_name(path)
        change_to = self.change_quota_var.get().strip()

        if status in {"입력전 변경", "입력후 변경"}:
            if not re.fullmatch(r"\d{1,2}", change_to) or int(change_to) <= 0:
                if not silent:
                    messagebox.showwarning("변경 구좌수", "변경 구좌수는 1~99 사이 숫자로 입력해야 합니다.")
                    self.change_quota_entry.focus_set()
                else:
                    self.append_lookup_log("[WARN] 변경 구좌수를 먼저 입력하세요.")
                return
            change_to = str(int(change_to))

        target_dir = self.original_dir / (STATUS_FOLDERS.get(status, "보완") if status else "")
        move_source = path
        if status == "입력전 변경" and current_name and change_to:
            renamed = unique_target_path(path, f"{change_to}{current_name}")
            if not same_path(path, renamed):
                path.rename(renamed)
                self.cache.rename_key(path, renamed)
                move_source = renamed
                path = renamed
        target = unique_path_in_dir(move_source, target_dir)

        if status == "보완":
            line = f"{path.stem}\t{', '.join(reasons)}"
        elif status in {"입력전 변경", "입력후 변경"} and current_quota and change_to:
            line = f"{current_name}\t{current_quota}구좌-->{change_to}구좌"
        elif status:
            line = path.stem
        else:
            line = ""
        txt_path = find_event_txt(self.application_dir)

        try:
            moved = False
            if not same_path(move_source, target):
                move_source.rename(target)
                moved = True
            if txt_path:
                update_txt_status(txt_path, original_stem, "", [], "", "")
                update_txt_status(txt_path, path.stem, status, reasons, current_quota, change_to)
            label = status or "원본복귀"
            if moved:
                self.append_lookup_log(f"[{label}] {move_source.name} -> {target}")
            else:
                self.append_lookup_log(f"[{label}] {path.name} 상태/TXT 업데이트")
            if txt_path:
                if status == "카드":
                    self.append_lookup_log(f"[TXT] {txt_path.name}: 카드 기록 없음 / 기존 관리항목 제거")
                else:
                    self.append_lookup_log(f"[TXT] {txt_path.name}: {status or '관리항목 제거'}")
            elif status:
                self.append_lookup_log("[WARN] 강연회 TXT 파일을 찾지 못해 TXT 기록은 생략했습니다.")
        except Exception as e:
            if not silent:
                messagebox.showerror("? ?? ??", str(e))
            else:
                self.append_lookup_log(f"[ERROR] 상태 처리 실패: {e}")
            return

        self.reload_images(keep_path=target)
        if move_next:
            self.next_item()

    def next_item(self) -> None:
        self.show_item(self.idx + 1)

    def prev_item(self) -> None:
        self.show_item(self.idx - 1)

    def jump(self, delta: int) -> None:
        self.show_item(self.idx + delta)

    def reload_images(self, keep_path: Path | None = None) -> None:
        self.all_images = list_images(self.original_dir)
        self.apply_filter(keep_path=keep_path)

    def open_folder(self) -> None:
        os.startfile(str(self.original_dir))


class RenameApp(tk.Tk):
    def __init__(self, original_dir: Path):
        super().__init__()
        self.title("신청서 전처리")
        self.geometry("1500x950")
        self.minsize(1100, 720)
        try:
            self.state("zoomed")
        except Exception:
            pass

        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=6, pady=4)
        ttk.Button(toolbar, text="+ 탭 추가", command=self.open_new_tab).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="현재 탭 닫기", command=self.close_active_tab).pack(side=tk.LEFT, padx=2)
        ttk.Label(toolbar, text="  각 탭은 별도 강연회/신청서 폴더입니다.").pack(side=tk.LEFT, padx=8)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.add_tab(original_dir)
        self.notebook.bind("<<NotebookTabChanged>>", lambda _e: self.focus_active_tab())

        self.bind("<Up>", lambda e: self.dispatch_to_active(e, "prev_item"))
        self.bind("<Down>", lambda e: self.dispatch_to_active(e, "next_item"))
        self.bind("<Prior>", lambda e: self.dispatch_to_active(e, "jump", -10))
        self.bind("<Next>", lambda e: self.dispatch_to_active(e, "jump", 10))
        self.bind("<Control-s>", lambda e: self.dispatch_to_active(e, "rename_current"))
        self.bind("<Escape>", lambda _e: self.destroy())

    def tab_title(self, original_dir: Path) -> str:
        application_dir = original_dir.parent if original_dir.name == "[원본]" else original_dir
        event_dir = application_dir.parent
        return event_dir.name or original_dir.name

    def add_tab(self, target: Path) -> None:
        try:
            original_dir = resolve_original_dir(Path(target))
        except Exception as e:
            messagebox.showerror("탭 추가 실패", str(e))
            return
        tab = RenameTab(self.notebook, original_dir, app=self)
        self.notebook.add(tab, text=self.tab_title(original_dir))
        self.notebook.select(tab)
        tab.combined_entry.focus_set()

    def open_new_tab(self) -> None:
        folder = filedialog.askdirectory(title="신청서 폴더 또는 [원본] 폴더 선택")
        if folder:
            self.add_tab(Path(folder))

    def active_tab(self):
        selected = self.notebook.select()
        if not selected:
            return None
        widget = self.nametowidget(selected)
        return widget if isinstance(widget, RenameTab) else None

    def focus_active_tab(self) -> None:
        tab = self.active_tab()
        if tab:
            tab.combined_entry.focus_set()

    def close_active_tab(self) -> None:
        selected = self.notebook.select()
        if not selected:
            return
        if len(self.notebook.tabs()) <= 1:
            return
        self.notebook.forget(selected)

    def dispatch_to_active(self, event, method_name: str, *args):
        focus = self.focus_get()
        if isinstance(focus, (tk.Entry, tk.Text, tk.Listbox)):
            return None
        tab = self.active_tab()
        if tab is None:
            return None
        getattr(tab, method_name)(*args)
        return "break"


def main() -> int:
    parser = argparse.ArgumentParser(description="Rename original application images by quota and name.")
    parser.add_argument("target", nargs="?", default=str(Path.cwd()))
    args = parser.parse_args()

    try:
        original_dir = resolve_original_dir(Path(args.target))
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    app = RenameApp(original_dir)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
