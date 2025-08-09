# app/prompts.py
from __future__ import annotations

import textwrap
from typing import List


def outline_prompt(topic: str, audience: str, tone: str, keywords: List[str]) -> str:
    return textwrap.dedent(f"""
    Create a detailed H2/H3 outline for a blog post.
    Topic: {topic}
    Audience: {audience}
    Tone: {tone}
    Include bullet talking points under each heading.
    Integrate keywords naturally: {", ".join(keywords)}.
    """)


def draft_prompt(outline: str, tone: str, audience: str, target_words: int, keywords: List[str]) -> str:
    return textwrap.dedent(f"""
    Write a {target_words}-word blog post using this outline:
    ---
    {outline}
    ---
    Requirements:
    - Use H2/H3 headings, short paragraphs, skimmable lists.
    - Tone: {tone} for audience: {audience}.
    - Include keywords naturally: {", ".join(keywords)}.
    - End with a clear conclusion and optional CTA.
    Return valid Markdown only.
    """)


def improve_prompt(draft: str, keywords: List[str], style_note: str = "clarity, concision, active voice") -> str:
    return textwrap.dedent(f"""
    Improve the following draft for {style_note}. Keep structure and facts.
    Ensure keywords remain: {", ".join(keywords)}.
    Return full revised Markdown only.
    ---
    {draft}
    """)


def seo_meta_prompt(draft: str, keywords: List[str]) -> str:
    return textwrap.dedent(f"""
    Propose:
    1) SEO title ≤ 60 chars
    2) Meta description ≤ 155 chars
    3) Short URL slug
    Consider keywords: {", ".join(keywords)}
    Format:
    Title: ...
    Description: ...
    Slug: ...
    ---
    {draft}
    """)
