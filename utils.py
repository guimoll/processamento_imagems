import shutil
from pathlib import Path

# Supported image extensions (default)
EXTS = {".png", ".jpg", ".jpeg"}

def listar_imagens(pasta: Path, classes=None):
    """Return a sorted list of image Path objects in `pasta`.

    Args:
        pasta: Path to search for images.
        classes: kept for compatibility with previous calls (not used).
    """
    if not pasta.exists() or not pasta.is_dir():
        return []
    # Use a local fallback in case module-level EXTS is unavailable at runtime
    local_exts = globals().get('EXTS', {".png", ".jpg", ".jpeg"})
    return sorted([p for p in pasta.iterdir() if p.is_file() and p.suffix.lower() in local_exts])

def copiar(lista, destino: Path, classes=None):
    """Copy files from `lista` to `destino`, preserving a per-class subfolder when
    `classes` indicates multiple classes.

    If `classes` is None, behaviour assumes a single-class layout (files directly in source).
    """
    classes = classes or ["_"]
    for src_path in lista:
        if classes == ["_"]:
            dst_path = destino / src_path.name
        else:
            # Prefer using the immediate parent directory name as class folder.
            parent_name = src_path.parent.name
            dst_path = destino / parent_name / src_path.name
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if not dst_path.exists():
            shutil.copy2(src_path, dst_path)

def yoloLabels(txt_path: Path, W, H):
    boxes = []
    if not txt_path.exists():
        return boxes
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            c, cx, cy, w, h = map(float, parts)
            c = int(c)
            x1 = (cx - w/2.0) * W
            y1 = (cy - h/2.0) * H
            x2 = (cx + w/2.0) * W
            y2 = (cy + h/2.0) * H
            boxes.append([c, x1, y1, x2, y2])
    return boxes

def saveLabels(txt_path: Path, boxes, W, H):
    with open(txt_path, "w", encoding="utf-8") as f:
        for c, x1, y1, x2, y2 in boxes:
            x1, y1 = max(0, min(W-1, x1)), max(0, min(H-1, y1))
            x2, y2 = max(0, min(W-1, x2)), max(0, min(H-1, y2))
            w = (x2 - x1) / W
            h = (y2 - y1) / H
            cx = (x1 + x2) / (2*W)
            cy = (y1 + y2) / (2*H)
            f.write(f"{c} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")
