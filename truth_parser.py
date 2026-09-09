from __future__ import annotations
import json, re
from pathlib import Path

MARKERS = ("（已分流）", "(已分流)")
MISSING = re.compile(r"^缺失（[^）]+）\s*(?P<name>.+)$")
HEADERS = re.compile(r"^【(?P<category>[^】]+)】$")

def parse(path: str | Path, issue: int) -> list[dict]:
    path = Path(path); category = None; out = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        text = raw.strip()
        if not text: continue
        h = HEADERS.match(text)
        if h: category = h.group("category"); continue
        for marker in MARKERS:
            text = text.replace(marker, "").strip()
        missing = MISSING.match(text)
        if missing:
            out.append({"category": category, "material_name": missing["name"], "status": "missing", "source_line": line_no, "source_text": raw}); continue
        if not category: continue
        parts = text.split(maxsplit=1)
        if len(parts) != 2: continue
        answer, name = parts
        out.append({"category": category, "answer_raw": answer, "answer_canonical": answer, "material_name": name, "status": "valid", "source_line": line_no, "source_text": raw, "issue": issue})
    return out

if __name__ == "__main__":
    import sys
    rows = parse(sys.argv[1], int(sys.argv[2])); print(json.dumps(rows, ensure_ascii=False, indent=2))
