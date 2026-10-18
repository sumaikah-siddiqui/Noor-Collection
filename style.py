"""
style.py
--------
One function, called at the top of every page, that injects custom CSS.
This is what stops the app from looking like a default "vibe-coded" Streamlit app.
"""

import streamlit as st

CUSTOM_CSS = """
<style>
    /* ---------- Palette ---------- */
    :root {
        --cream: #FAF6F0;
        --panel: #FFFFFF;
        --maroon: #7B1E3A;
        --maroon-dark: #5E1729;
        --gold: #C9A34E;
        --text: #2B2620;
        --border: #E5DDD3;
    }

    /* Hide default Streamlit chrome for a cleaner, less "template" look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* App background */
    .stApp {
        background-color: var(--cream);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F1E7DA;
        border-right: 1px solid var(--border);
    }

    /* Headings */
    h1, h2, h3 {
        color: var(--maroon-dark);
        font-weight: 700;
        letter-spacing: 0.2px;
    }

    /* Buttons */
    .stButton > button, .stFormSubmitButton > button {
        background-color: var(--maroon);
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 0.5em 1.2em;
        font-weight: 600;
        transition: background-color 0.15s ease-in-out;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background-color: var(--maroon-dark);
        color: #FFFFFF;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: var(--panel);
        border: 1px solid var(--border);
        border-left: 5px solid var(--gold);
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetricLabel"] {
        color: var(--maroon-dark);
        font-weight: 600;
    }

    /* Dataframes / tables */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 10px;
        overflow: hidden;
    }

    /* Text inputs / selects */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 8px !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-weight: 600;
        color: var(--text);
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--maroon);
        border-bottom-color: var(--maroon) !important;
    }

    /* Divider gold accent */
    hr {
        border-top: 1px solid var(--gold);
    }

    /* Badges for status text */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.80em;
        font-weight: 600;
    }
    .badge-green  { background-color: #E4F0E5; color: #2E7D32; }
    .badge-amber  { background-color: #FBEFDD; color: #B8860B; }
    .badge-red    { background-color: #FBE4E4; color: #B03A2E; }
    .badge-grey   { background-color: #ECE7E0; color: #6b645a; }
</style>
"""


def apply_theme():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    """Returns an HTML badge span for a given order/shipping status."""
    status_l = (status or "").lower()
    if status_l in ("delivered", "confirmed"):
        css_class = "badge-green"
    elif status_l in ("pending", "preparing", "in transit", "dispatched", "shipped", "low stock"):
        css_class = "badge-amber"
    elif status_l in ("cancelled", "sold out"):
        css_class = "badge-red"
    else:
        css_class = "badge-grey"
    return f'<span class="badge {css_class}">{status}</span>'
