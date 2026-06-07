"""
streamlit_app.py - Mines RAG Assistant frontend.

Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import chromadb
import ingest
from chunk import build_chunks
from embed import store
from generate import generate

# ---------------------------------------------------------------------------
# Build ChromaDB on first run if the collection doesn't exist
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Setting up knowledge base — this only runs once...")
def build_pipeline():
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_or_create_collection("mines_rag")
    if collection.count() == 0:
        ingest.main()
        store(build_chunks())

build_pipeline()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Mines Graduate Assistant",
    page_icon="⛏️",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* Clean background */
    .stApp { background-color: #f8f9fa; }

    /* Hide default Streamlit header */
    header[data-testid="stHeader"] { display: none; }

    /* Hero */
    .hero {
        text-align: center;
        padding: 2.5rem 0 1.5rem 0;
    }
    .hero h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.3rem;
    }
    .hero p {
        color: #6c757d;
        font-size: 1rem;
    }

    /* Suggestion cards */
    .suggestion-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
        margin-top: 1.5rem;
    }
    .suggestion-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        font-size: 0.9rem;
        color: #343a40;
        cursor: pointer;
        transition: box-shadow 0.15s;
    }
    .suggestion-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #c8d0d9;
    }

    /* Chat bubbles */
    .bubble-user {
        background: #1a1a2e;
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 16px 16px 4px 16px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
        font-size: 0.93rem;
    }
    .bubble-bot {
        background: white;
        color: #1a1a2e;
        padding: 0.75rem 1rem;
        border-radius: 16px 16px 16px 4px;
        margin: 0.5rem 0;
        max-width: 85%;
        border: 1px solid #e9ecef;
        font-size: 0.93rem;
    }

    /* Back button */
    .stButton > button {
        background: none;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        color: #495057;
        font-size: 0.85rem;
        padding: 0.3rem 0.9rem;
    }
    .stButton > button:hover {
        background: #f1f3f5;
        border-color: #adb5bd;
    }

    /* Chat input */
    .stChatInput > div { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Suggested questions
# ---------------------------------------------------------------------------

SUGGESTED_QUESTIONS = [
    "What happens if I receive an incomplete grade?",
    "What CS degree options are available at Mines?",
    "How do I apply for graduation?",
    "What is the tuition refund policy?",
    "What is the academic integrity policy?",
    "What is the full-time credit load for graduate students?",
]

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "view" not in st.session_state:
    st.session_state.view = "home"       # "home" | "chat"
if "messages" not in st.session_state:
    st.session_state.messages = []


def go_home():
    st.session_state.view = "home"
    st.session_state.messages = []


def open_chat(question: str = None):
    st.session_state.view = "chat"
    if question:
        st.session_state.messages = [{"role": "user", "content": question}]
        with st.spinner("Thinking..."):
            answer = generate(question)
        st.session_state.messages.append({"role": "assistant", "content": answer})


# ---------------------------------------------------------------------------
# Home view
# ---------------------------------------------------------------------------

if st.session_state.view == "home":
    st.markdown("""
    <div class="hero">
        <h1>⛏️ Mines Graduate Assistant</h1>
        <p>Ask anything about CS graduate programs, policies, grading, and more.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Suggested questions**")

    cols = st.columns(2)
    for i, question in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 2]:
            if st.button(question, key=f"q_{i}", use_container_width=True):
                open_chat(question)
                st.rerun()

    st.divider()
    st.markdown("<p style='color:#adb5bd; font-size:0.82rem; text-align:center;'>Or type your own question below</p>", unsafe_allow_html=True)

    custom = st.chat_input("Ask a question...")
    if custom:
        open_chat(custom)
        st.rerun()

# ---------------------------------------------------------------------------
# Chat view
# ---------------------------------------------------------------------------

else:
    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("← Back"):
            go_home()
            st.rerun()
    with col_title:
        st.markdown("<h3 style='margin:0; padding-top:0.2rem;'>⛏️ Mines Graduate Assistant</h3>", unsafe_allow_html=True)

    st.divider()

    # Render chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='bubble-user'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bubble-bot'>{msg['content']}</div>", unsafe_allow_html=True)

    # New message input
    user_input = st.chat_input("Ask a follow-up question...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            answer = generate(user_input)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
