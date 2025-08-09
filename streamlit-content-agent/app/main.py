# app/main.py
from __future__ import annotations

import os
import re
from typing import Dict, List

import streamlit as st
from dotenv import load_dotenv
from loguru import logger

# Local modules
from app.llm import LLMClient, LLMConfig
from app.prompts import (
    outline_prompt,
    draft_prompt,
    improve_prompt,
    seo_meta_prompt,
)
from app.seo import seo_checklist, slugify

# Optional (only needed for PDF export)
try:
    import markdown2  # type: ignore
    import pdfkit     # type: ignore
    _PDF_DEPS = True
except Exception:
    _PDF_DEPS = False


# -----------------------------
# App/bootstrap configuration
# -----------------------------
load_dotenv()  # load .env for local dev
st.set_page_config(page_title="AI Content Generator + Editor", layout="wide")

# Configure logger once (quiet, structured)
import sys
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | {level} | {message}",
)

st.title("📝 AI Content Generator + Editor")

# -----------------------------
# Session state defaults
# -----------------------------
# Make Ollama the default provider
st.session_state.setdefault("provider", "ollama")  # <-- default is ollama per your request
st.session_state.setdefault("model", "gpt-4o-mini")  # only used for OpenAI
st.session_state.setdefault("outline", "")
st.session_state.setdefault("draft", "")
st.session_state.setdefault("seo_meta", {"Title": "", "Description": "", "Slug": ""})

# -----------------------------
# Sidebar controls
# -----------------------------
with st.sidebar:
    st.image(
        "https://dummyimage.com/300x80/111827/ffffff&text=Your+Brand",
        use_container_width=True,
        caption="(Replace with your logo image or a local file path.)",
    )
    st.header("⚙️ Settings")

    provider = st.selectbox("LLM Provider", ["ollama", "openai"], index=0 if st.session_state["provider"] == "ollama" else 1)
    st.session_state["provider"] = provider

    if provider == "openai":
        # OpenAI configuration
        openai_key_default = os.getenv("OPENAI_API_KEY", "")
        openai_key = st.text_input("OpenAI API Key", value=openai_key_default, type="password")
        model = st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"], index=0)
        cfg = LLMConfig(provider="openai", model=model, openai_api_key=openai_key)
    else:
        # Ollama configuration (fully local)
        base_default = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model_default = os.getenv("OLLAMA_MODEL", "llama3")
        base = st.text_input("Ollama Base URL", value=base_default)
        local_model = st.text_input("Ollama Model", value=model_default)
        cfg = LLMConfig(provider="ollama", model="N/A", ollama_base_url=base, ollama_model=local_model)

    temperature = st.slider("Temperature", 0.0, 1.0, 0.5, 0.05)
    target_words = st.slider("Target length (words)", min_value=400, max_value=2000, value=900, step=50)

    topic = st.text_input("Topic", value="How to start a habit of reading")
    audience = st.text_input("Audience", value="Busy professionals")
    tone = st.selectbox("Tone", ["Friendly", "Informative", "Persuasive", "Playful", "Academic"], index=1)
    keywords_str = st.text_input("Keywords (comma-separated)", value="reading habit, productivity, routines")
    keywords: List[str] = [k.strip() for k in keywords_str.split(",") if k.strip()]

    colA, colB = st.columns(2)
    gen_outline = colA.button("✍️ Generate Outline")
    gen_draft = colB.button("🧠 Draft from Outline")
    improve_btn = colA.button("✨ Improve Draft")
    seo_btn = colB.button("🔎 Refresh SEO Meta")

# Build LLM client from sidebar config
client = LLMClient(cfg)
logger.info("Provider={}, OpenAIModel={}, OllamaModel={}", cfg.provider, cfg.model, cfg.ollama_model)

# -----------------------------
# 1) Outline
# -----------------------------
st.subheader("1) Outline")
st.session_state["outline"] = st.text_area(
    "Edit the outline before drafting:",
    value=st.session_state["outline"],
    height=200,
)

if gen_outline:
    with st.spinner("Generating outline..."):
        logger.info("Generating outline: topic='{}', audience='{}', tone='{}'", topic, audience, tone)
        st.session_state["outline"] = client.generate(
            outline_prompt(topic, audience, tone, keywords),
            temperature=temperature,
        )
    st.rerun()

# -----------------------------
# 2) Draft
# -----------------------------
st.subheader("2) Draft")
st.session_state["draft"] = st.text_area(
    "Draft (Markdown):",
    value=st.session_state["draft"],
    height=380,
)

if gen_draft:
    if not st.session_state["outline"].strip():
        st.warning("Please create or paste an outline first.")
    else:
        with st.spinner("Drafting article..."):
            logger.info(
                "Drafting with provider='{}', words={}, tone='{}', audience='{}'",
                cfg.provider, target_words, tone, audience
            )
            st.session_state["draft"] = client.generate(
                draft_prompt(st.session_state["outline"], tone, audience, target_words, keywords),
                temperature=min(0.8, max(0.2, temperature)),
            )
        st.rerun()

if improve_btn:
    if not st.session_state["draft"].strip():
        st.warning("Paste or generate a draft first.")
    else:
        with st.spinner("Improving draft..."):
            logger.info("Improving draft")
            st.session_state["draft"] = client.generate(
                improve_prompt(st.session_state["draft"], keywords),
                temperature=0.3,
            )
        st.rerun()

# -----------------------------
# 3) Suggestions (micro-edits)
# -----------------------------
st.subheader("3) Suggestions")
if st.button("💡 Get Rewrite Suggestions"):
    with st.spinner("Finding micro-edits..."):
        logger.info("Generating micro-suggestions")
        suggestions = client.generate(
            "Suggest 3 specific sentence-level improvements for clarity or punchiness. "
            "Quote the original, then provide the improved version. Keep each under 25 words.\n\n"
            f"Draft:\n{st.session_state['draft'][:6000]}",
            temperature=0.4,
        )
    st.markdown(suggestions or "_No suggestions yet._")

# -----------------------------
# 4) SEO Panel
# -----------------------------
st.subheader("4) SEO")
col1, col2 = st.columns([2, 1])

with col1:
    checks: Dict[str, object] = seo_checklist(st.session_state["draft"], target_words, keywords)
    st.write("**Checklist**")
    st.write({
        "Has H1": checks["has_h1"],
        "≥ 2 H2s": checks["has_h2"],
        "Word count": checks["word_count"],
        "Meets length": checks["meets_length"],
        "Has links": checks["has_links"],
        "Images have alt (if any)": checks["has_images_with_alt"],
        "Keyword density (%)": checks["keyword_density"],
    })

with col2:
    if seo_btn:
        with st.spinner("Refreshing SEO meta..."):
            logger.info("Generating SEO meta")
            meta_raw = client.generate(seo_meta_prompt(st.session_state["draft"], keywords), temperature=0.4)
            if meta_raw:
                title = re.search(r"Title:\s*(.+)", meta_raw)
                desc = re.search(r"Description:\s*(.+)", meta_raw)
                slug = re.search(r"Slug:\s*(.+)", meta_raw)
                st.session_state["seo_meta"] = {
                    "Title": (title.group(1).strip() if title else "")[:60],
                    "Description": (desc.group(1).strip() if desc else "")[:155],
                    "Slug": slugify(slug.group(1).strip() if slug else ""),
                }
        st.rerun()

    st.write("**Meta**")
    st.session_state["seo_meta"]["Title"] = st.text_input("SEO Title (≤60)", value=st.session_state["seo_meta"]["Title"])
    st.session_state["seo_meta"]["Description"] = st.text_area(
        "Meta Description (≤155)", value=st.session_state["seo_meta"]["Description"], height=90
    )
    st.session_state["seo_meta"]["Slug"] = st.text_input("URL Slug", value=st.session_state["seo_meta"]["Slug"])

# -----------------------------
# 5) Export
# -----------------------------
st.subheader("5) Export")

md_export = f"""# {st.session_state['seo_meta'].get('Title') or topic}

> Meta: {st.session_state['seo_meta'].get('Description','')}

<!-- slug: {st.session_state['seo_meta'].get('Slug','')} -->

{st.session_state['draft']}
"""

col_md, col_pdf = st.columns([1, 1], gap="small")

with col_md:
    st.download_button(
        "⬇️ Download Markdown",
        data=md_export.encode("utf-8"),
        file_name=f"{slugify(st.session_state['seo_meta'].get('Title') or topic)}.md",
        mime="text/markdown",
    )

with col_pdf:
    if not _PDF_DEPS:
        st.info("PDF export needs `markdown2` and `pdfkit` installed, plus system `wkhtmltopdf`.")
    else:
        if st.button("📄 Export PDF"):
            try:
                html = markdown2.markdown(md_export)
                # If wkhtmltopdf isn't on PATH, configure like:
                # config = pdfkit.configuration(wkhtmltopdf="/full/path/to/wkhtmltopdf")
                # pdf_bytes = pdfkit.from_string(html, False, configuration=config)
                pdf_bytes = pdfkit.from_string(html, False)
                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name=f"{slugify(st.session_state['seo_meta'].get('Title') or topic)}.pdf",
                    mime="application/pdf",
                    key="pdf_download_btn",
                )
            except Exception as e:
                logger.error("PDF export failed: {}", e)
                st.error(f"PDF export failed: {e}")

st.caption(
    "Tip: Tune temperature to control creativity. For fully local inference, keep Ollama running and use the 'llama3' model."
)
