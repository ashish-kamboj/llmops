import base64
import os
from pathlib import Path
from typing import List

import requests
import streamlit as st
from bs4 import BeautifulSoup

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


st.set_page_config(page_title="Confluence", layout="wide")


def load_pages() -> List[dict]:
    resp = requests.get(f"{API_BASE_URL}/pages", timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_page(page_id: str) -> dict:
    resp = requests.get(f"{API_BASE_URL}/pages/{page_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_recommendations(page_id: str) -> List[dict]:
    resp = requests.get(f"{API_BASE_URL}/recommend/{page_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()["results"]


def inline_images(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        if src.startswith("http") or src.startswith("data:"):
            continue
        image_path = (DATA_DIR / "pages" / src).resolve()
        if not image_path.exists():
            continue
        mime = "image/svg+xml" if image_path.suffix == ".svg" else "image/png"
        b64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        img["src"] = f"data:{mime};base64,{b64}"
    return str(soup)


def confluence_header() -> None:
    st.markdown(
        """
        <style>
        :root { --c-bg: #F4F5F7; --c-text: #172B4D; --c-muted: #6B778C; --c-blue: #0052CC; }
        .app-shell { background: #FFFFFF; }
        .topbar {
            display: grid;
            grid-template-columns: 220px 1fr 220px;
            gap: 16px;
            align-items: center;
            padding: 10px 16px;
            border-bottom: 1px solid #DFE1E6;
        }
        .logo {
            display: flex; align-items: center; gap: 10px; font-weight: 700;
            color: var(--c-text); font-size: 16px;
        }
        .logo-mark {
            width: 24px; height: 24px; border-radius: 6px; background: var(--c-blue);
            display: inline-flex; align-items: center; justify-content: center; color: #FFFFFF; font-size: 14px;
        }
        .search-wrap { width: 100%; }
        .search-input {
            width: 100%; padding: 8px 12px; border: 1px solid #DFE1E6; border-radius: 6px;
            background: #FFFFFF; color: var(--c-text);
        }
        .top-actions { display: flex; justify-content: flex-end; gap: 10px; align-items: center; }
        .btn-primary {
            background: var(--c-blue); color: #FFFFFF; border: none; padding: 8px 12px; border-radius: 6px;
            font-weight: 600;
        }
        .icon-btn {
            width: 28px; height: 28px; border-radius: 50%; border: 1px solid #DFE1E6; background: #FFFFFF;
        }
        .sidebar-title { font-size: 14px; font-weight: 600; color: var(--c-text); margin: 4px 0 8px; }
        .sidebar-group { font-size: 12px; color: var(--c-muted); margin: 12px 0 6px; }
        .nav-item { padding: 6px 8px; border-radius: 6px; color: var(--c-text); }
        .nav-item.active { background: #E9F2FF; color: var(--c-blue); font-weight: 600; }
        .page-title { font-size: 28px; font-weight: 700; color: var(--c-text); margin: 10px 0 8px; }
        .related-title { font-size: 18px; font-weight: 600; color: var(--c-text); margin-top: 24px; }
        .card { border: 1px solid #DFE1E6; border-radius: 8px; padding: 12px; background: #FFFFFF; }
        .card-title { font-weight: 600; color: var(--c-blue); }
        .card-sub { font-size: 12px; color: var(--c-muted); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    confluence_header()
    st.markdown(
        """
        <div class="topbar">
            <div class="logo">
                <span class="logo-mark">C</span>
                <span>Confluence</span>
            </div>
            <div class="search-wrap">
                <input class="search-input" placeholder="Search" />
            </div>
            <div class="top-actions">
                <button class="btn-primary">Create</button>
                <button class="icon-btn" title="Notifications"></button>
                <button class="icon-btn" title="Help"></button>
                <button class="icon-btn" title="Profile"></button>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pages = load_pages()
    page_titles = {p["title"]: p["id"] for p in pages}

    with st.sidebar:
        st.markdown("<div class='sidebar-title'>Spaces</div>", unsafe_allow_html=True)
        st.markdown("<div class='nav-item active'>Technical Documentation</div>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-group'>Tech Document 2026</div>", unsafe_allow_html=True)
        selected_title = st.radio(
            "Pages",
            list(page_titles.keys()),
            index=0,
            label_visibility="collapsed",
        )
    page_id = page_titles[selected_title]

    page = get_page(page_id)
    html = inline_images(page["html"])

    #st.markdown(f"<div class='page-title'>{page['title']}</div>", unsafe_allow_html=True)
    st.components.v1.html(html, height=720, scrolling=True)

    st.markdown("<div class='related-title'>Related content</div>", unsafe_allow_html=True)
    recs = get_recommendations(page_id)

    cols = st.columns(3)
    for idx, rec in enumerate(recs):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">{rec['title']}</div>
                    <div class="card-sub">Similarity: {rec['similarity']:.3f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
