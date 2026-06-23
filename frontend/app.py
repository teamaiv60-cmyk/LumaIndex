import streamlit as st
import requests
from markdown_it import MarkdownIt

BACKEND = "http://127.0.0.1:8000"

st.set_page_config(page_title="Local RAG Chat", layout="wide")

md = MarkdownIt()

st.markdown(
    """
    <style>
    .chat-container {
        border-radius: 24px;
        background: #0b1220;
        padding: 24px;
        color: #e2e8f0;
        min-height: 540px;
        max-height: calc(100vh - 220px);
        overflow-y: auto;
        box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.15);
    }
    .chat-bubble {
        border-radius: 18px;
        padding: 16px;
        margin: 8px 0;
        line-height: 1.6;
        max-width: 82%;
        word-wrap: break-word;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.12);
    }
    .chat-bubble.user {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        margin-left: auto;
    }
    .chat-bubble.assistant {
        background: #f8fafc;
        color: #111827;
        margin-right: auto;
    }
    .chat-role {
        font-size: 0.78rem;
        opacity: 0.75;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .sidebar-card {
        background: #111827;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 20px 40px rgba(15, 23, 42, 0.35);
    }
    .sidebar-card h2 {
        margin-top: 0;
    }
    .summary-box {
        background: #1f2937;
        border-radius: 16px;
        padding: 16px;
        color: #d1d5db;
        margin-top: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "summary_text" not in st.session_state:
    st.session_state.summary_text = None


def add_message(role: str, content: str) -> None:
    st.session_state.history.append({"role": role, "content": content})


def clear_chat() -> None:
    st.session_state.history = []
    st.session_state.summary_text = None


def render_markdown(text: str) -> str:
    return md.render(text)


def upload_pdf(file) -> None:
    files = {
        "file": (file.name, file, "application/pdf")
    }
    response = requests.post(f"{BACKEND}/upload", files=files)
    if response.status_code == 200:
        st.session_state.uploaded_file = file.name
        st.success("PDF uploaded successfully.")
        add_message("system", f"Uploaded '{file.name}'. Ask a question to explore the document.")
    else:
        st.error("Upload failed. Check the backend and try again.")


def ask_question(question: str) -> None:
    if not question.strip():
        return
    if not st.session_state.uploaded_file:
        st.warning("Upload a PDF first so the assistant can answer from the document.")
        return

    add_message("user", question)
    response = requests.get(f"{BACKEND}/ask", params={"question": question})
    if response.status_code == 200:
        assistant_answer = response.json().get("answer", "No answer returned.")
        add_message("assistant", assistant_answer)
    else:
        add_message("assistant", "Sorry, I could not reach the backend.")


def generate_summary() -> None:
    if not st.session_state.uploaded_file:
        st.warning("Upload a PDF before requesting a summary.")
        return
    response = requests.get(f"{BACKEND}/summary")
    if response.status_code == 200:
        st.session_state.summary_text = response.json().get("answer")
    else:
        st.session_state.summary_text = "Unable to retrieve summary from backend."


with st.sidebar:
    st.markdown("## 📄 Document Explorer")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key="file_uploader")
    if uploaded_file is not None:
        if st.button("Upload PDF", key="upload_button"):
            upload_pdf(uploaded_file)

    st.markdown("---")

    st.markdown("## ⚙️ Actions")
    if st.button("Generate Summary", key="summary_button"):
        generate_summary()
    if st.button("Clear chat", key="clear_button"):
        clear_chat()

    if st.session_state.uploaded_file:
        st.markdown(f"**Loaded:** {st.session_state.uploaded_file}")

    if st.session_state.summary_text:
        st.markdown("### Summary")
        st.markdown(f"<div class='summary-box'>{st.session_state.summary_text}</div>", unsafe_allow_html=True)


left, right = st.columns([3, 1])

with left:
    st.markdown("# 🤖 Local RAG Chat")
    st.markdown("Ask questions about your uploaded PDF and track the conversation history as you go.")

    if hasattr(st, "chat_input"):
        prompt = st.chat_input("Ask a question")
        if prompt:
            ask_question(prompt)
    else:
        with st.form("question_form", clear_on_submit=True):
            prompt = st.text_input("Ask a question", key="question_input")
            submitted = st.form_submit_button("Send")
            if submitted and prompt:
                ask_question(prompt)

    if st.session_state.history:
        history_html = ["<div class='chat-container'>"]
        for message in st.session_state.history:
            if message["role"] == "user":
                role_label = "You"
                bubble_class = "user"
                text = message["content"].replace("\n", "<br>")
            elif message["role"] == "assistant":
                role_label = "Assistant"
                bubble_class = "assistant"
                text = render_markdown(message["content"])
            else:
                role_label = "System"
                bubble_class = "assistant"
                text = message["content"].replace("\n", "<br>")

            history_html.append(
                f"<div class='chat-bubble {bubble_class}'><div class='chat-role'>{role_label}</div>{text}</div>"
            )
        history_html.append("</div>")
        st.markdown("".join(history_html), unsafe_allow_html=True)
    else:
        st.info("Your conversation will appear here once you ask the first question.")

with right:
    st.markdown("<div class='sidebar-card'><h2>Tips</h2><ul><li>Upload a PDF</li><li>Ask a question in the chat</li><li>Use summary for a quick overview</li></ul></div>", unsafe_allow_html=True)
