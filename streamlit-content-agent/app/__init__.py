# app/__init__.py
"""
App package initializer for the Streamlit Content Generator + Editor.

Having this file ensures Python treats the `app/` directory as a package,
so imports like `from app.llm import LLMClient` work correctly.
"""

__version__ = "0.1.0"

# Optional: re-export common classes so you can `from app import LLMClient, LLMConfig`
# (Safe to keep; does not affect your current imports.)
try:
    from .llm import LLMClient, LLMConfig  # noqa: F401
except Exception:
    # Avoid import errors during certain tooling / partial installs.
    pass
