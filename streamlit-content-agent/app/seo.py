# app/seo.py
from __future__ import annotations

import re
from typing import Dict, List


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:70].strip("-")


def keyword_density(text: str, keywords: List[str]) -> Dict[str, float]:
    words = re.findall(r"\b\w+\b", text.lower())
    total = max(len(words), 1)
    joined = " ".join(words)
    densities: Dict[str, float] = {}
    for kw in keywords:
        k = kw.strip().lower()
        if not k:
            continue
        count = len(re.findall(rf"\b{re.escape(k)}\b", joined))
        densities[kw] = round(100 * count / total, 2)
    return densities


def seo_checklist(markdown_text: str, target_words: int, keywords: List[str]) -> Dict:
    h1 = re.findall(r"^# (.+)$", markdown_text, flags=re.MULTILINE)
    h2 = re.findall(r"^## (.+)$", markdown_text, flags=re.MULTILINE)
    word_count = len(re.findall(r"\b\w+\b", markdown_text))
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", markdown_text)
    images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", markdown_text)
    kd = keyword_density(markdown_text, keywords)
    return {
        "has_h1": bool(h1),
        "has_h2": len(h2) >= 2,
        "word_count": word_count,
        "meets_length": word_count >= int(0.9 * target_words),
        "has_links": len(links) > 0,
        "has_images_with_alt": all(alt.strip() for alt, _ in images) if images else True,
        "keyword_density": kd,
    }
