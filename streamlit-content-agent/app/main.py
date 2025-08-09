import os
import re
import streamlit as st
from dotenv import load_dotenv

from app.llm import LLMClient, LLMConfig
from app.prompts import outline_prompt, draft_prompt, improve_prompt, seo_meta_prompt
from app.seo import seo_checklist, slugify

load_dotenv()  # load .env for local dev

st.set_page_config(page_title="AI Content Generator + Editor", layout="wide")
st.title("📝 AI Content Generator + Editor")

# --- Session state ---
for key, default in {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "outline": "",
    "draft": "",
    "seo_meta": {"Title": "", "Description": "", "Slug": ""},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Sidebar (professional controls) ---
with st.sidebar:
    st.header("⚙️ Settings")
    provider = st.selectbox("LLM Provider", ["openai", "ollama"], index=0)
    st.session_state["provider"] = provider

    if provider == "openai":
        openai_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
        model = st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"], index=0)
        cfg = LLMConfig(provider="openai", model=model, openai_api_key=openai_key)
    else:
        base = st.text_input("Ollama Base URL", value=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
        local_model = st.text_input("Ollama Model", value=os.getenv("OLLAMA_MODEL", "llama3"))
        cfg = LLMConfig(provider="ollama", model="N/A", ollama_base_url=base, ollama_model=local_model)

    temperature = st.slider("Temperature", 0.0, 1.0, 0.5, 0.05)
    target_words = st.slider("Target length (words)", min_value=400, max_value=2000, value=900, step=50)

    topic = st.text_input("Topic", value="How to start a habit of reading")
    audience = st.text_input("Audience", value="Busy professionals")
    tone = st.selectbox("Tone", ["Friendly", "Informative", "Persuasive", "Playful", "Academic"], index=1)
    keywords_str = st.text_input("Keywords (comma-separated)", value="reading habit, productivity, routines")
    keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

    colA, colB = st.columns(2)
    gen_outline = colA.button("✍️ Generate Outline")
    gen_draft = colB.button("🧠 Draft from Outline")
    improve_btn = colA.button("✨ Improve Draft")
    seo_btn = colB.button("🔎 Refresh SEO Meta")

client = LLMClient(cfg)

# --- Outline ---
st.subheader("1) Outline")
st.session_state["outline"] = st.text_area(
    "Edit the outline before drafting:", value=st.session_state["outline"], height=200
)
if gen_outline:
    with st.spinner("Generating outline..."):
        st.session_state["outline"] = client.generate(
            outline_prompt(topic, audience, tone, keywords), temperature=temperature
        )
    st.rerun()

# --- Draft ---
st.subheader("2) Draft")
st.session_state["draft"] = st.text_area(
    "Draft (Markdown):", value=st.session_state["draft"], height=380
)
if gen_draft:
    if not st.session_state["outline"].strip():
        st.warning("Please create or paste an outline first.")
    else:
        with st.spinner("Drafting article..."):
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
            st.session_state["draft"] = client.generate(
                improve_prompt(st.session_state["draft"], keywords), temperature=0.3
            )
        st.rerun()

# --- Suggestions ---
st.subheader("3) Suggestions")
if st.button("💡 Get Rewrite Suggestions"):
    with st.spinner("Finding micro-edits..."):
        suggestions = client.generate(
            f"Suggest 3 sentence-level improvements. Quote the original, then provide the improved version. "
            f"Keep each under 25 words.\n\nDraft:\n{st.session_state['draft'][:6000]}",
            temperature=0.4,
        )
    st.markdown(suggestions or "_No suggestions yet._")

# --- SEO Panel ---
st.subheader("4) SEO")
col1, col2 = st.columns([2, 1])
with col1:
    checks = seo_checklist(st.session_state["draft"], target_words, keywords)
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
    st.session_state["seo_meta"]["Description"] = st.text_area("Meta Description (≤155)", value=st.session_state["seo_meta"]["Description"], height=90)
    st.session_state["seo_meta"]["Slug"] = st.text_input("URL Slug", value=st.session_state["seo_meta"]["Slug"])

# --- Export ---
st.subheader("5) Export")
md_export = f"""# {st.session_state['seo_meta'].get('Title') or topic}

> Meta: {st.session_state['seo_meta'].get('Description','')}

<!-- slug: {st.session_state['seo_meta'].get('Slug','')} -->

{st.session_state['draft']}
"""
st.download_button(
    "⬇️ Download Markdown",
    data=md_export.encode("utf-8"),
    file_name=f"{slugify(st.session_state['seo_meta'].get('Title') or topic)}.md",
    mime="text/markdown",
)
st.caption("Tip: To export PDF, convert Markdown → HTML → PDF with markdown2 + wkhtmltopdf.")
