#!/usr/bin/env python3
"""List the underlined words/phrases of a .docx, one per line, duplicates removed (first kept).

    python3 docx_underlined_words.py FILE.docx [-o OUT.txt]
"""
import argparse
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def underline_on(rpr):
    u = rpr.find(W + "u") if rpr is not None else None
    return None if u is None else u.get(W + "val", "single") != "none"


def underlined_styles(z):
    """Character styles that underline text (following basedOn)."""
    try:
        root = ET.fromstring(z.read("word/styles.xml"))
    except KeyError:
        return set()
    own, parent = {}, {}
    for s in root.iter(W + "style"):
        sid = s.get(W + "styleId")
        own[sid] = underline_on(s.find(W + "rPr"))
        based = s.find(W + "basedOn")
        parent[sid] = based.get(W + "val") if based is not None else None

    def resolve(sid, depth=0):
        if sid is None or depth > 20:
            return False
        return own.get(sid) if own.get(sid) is not None else resolve(parent.get(sid), depth + 1)

    return {sid for sid in own if resolve(sid)}


def run_underlined(r, styles):
    rpr = r.find(W + "rPr")
    direct = underline_on(rpr)
    if direct is not None:
        return direct
    rstyle = rpr.find(W + "rStyle") if rpr is not None else None
    return rstyle is not None and rstyle.get(W + "val") in styles


def clean(text):
    text = re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()
    return text.strip(" .,;:!?()[]\"'“”‘’…-–—")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()
    try:
        z = zipfile.ZipFile(args.docx)
    except (zipfile.BadZipFile, FileNotFoundError):
        sys.exit(f"Error: {args.docx} is not a readable .docx file (convert .doc first: textutil -convert docx FILE.doc)")
    styles = underlined_styles(z)
    body = ET.fromstring(z.read("word/document.xml"))

    items, current = [], []
    for p in body.iter(W + "p"):
        for r in p.iter(W + "r"):
            text = "".join(t.text or "" for t in r.iter(W + "t"))
            if run_underlined(r, styles) and text:
                current.append(text)  # adjacent underlined runs form one word/phrase
            elif text or r.find(W + "br") is not None:
                items.append("".join(current))
                current = []
        items.append("".join(current))
        current = []

    seen, unique = set(), []
    for item in map(clean, items):
        if item and item.casefold() not in seen:
            seen.add(item.casefold())
            unique.append(item)

    out = args.output or args.docx.with_name(args.docx.stem + "_gach_chan.txt")
    out.write_text("".join(u + "\n" for u in unique), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(unique))
    print(f"\n{len(unique)} mục -> {out}")


if __name__ == "__main__":
    main()
