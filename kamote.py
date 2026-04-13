import html

import google.generativeai as genai
import requests
import streamlit as st
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
from pypdf import PdfReader


MAX_INPUT_CHARS = 15000
MODEL_NAME = "gemini-2.5-flash"
APP_ACCENT = "#b45309"
APP_BG = "#f7f1e3"
APP_PANEL = "#fffaf0"
APP_INK = "#2f241f"


st.set_page_config(
    page_title="Prof Elf's Kamote Critic",
    page_icon="K",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
    .stApp {{
        background:
            radial-gradient(circle at top left, rgba(245, 158, 11, 0.24), transparent 28%),
            radial-gradient(circle at top right, rgba(180, 83, 9, 0.18), transparent 24%),
            linear-gradient(180deg, #fff7ea 0%, {APP_BG} 55%, #efe0c8 100%);
        color: {APP_INK};
    }}
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1120px;
    }}
    .kamote-hero {{
        background: linear-gradient(135deg, rgba(255,250,240,0.96), rgba(247,237,214,0.92));
        border: 1px solid rgba(180, 83, 9, 0.18);
        border-radius: 24px;
        padding: 1.6rem 1.6rem 1.35rem 1.6rem;
        box-shadow: 0 20px 50px rgba(86, 56, 26, 0.12);
        margin-bottom: 1rem;
    }}
    .kamote-chip {{
        display: inline-block;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        background: rgba(180, 83, 9, 0.09);
        color: {APP_ACCENT};
        font-size: 0.86rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }}
    .kamote-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.9rem;
        margin: 1rem 0 1.25rem 0;
    }}
    .kamote-card {{
        background: rgba(255, 252, 245, 0.9);
        border: 1px solid rgba(180, 83, 9, 0.12);
        border-radius: 18px;
        padding: 0.95rem 1rem;
    }}
    .kamote-card strong {{
        display: block;
        margin-bottom: 0.3rem;
        color: {APP_ACCENT};
    }}
    .kamote-panel {{
        background: {APP_PANEL};
        border: 1px solid rgba(180, 83, 9, 0.14);
        border-radius: 22px;
        padding: 1.15rem;
        box-shadow: 0 14px 35px rgba(75, 47, 19, 0.08);
    }}
    .kamote-verdict {{
        background: linear-gradient(180deg, #fffdf8, #fff7ea);
        border: 1px solid rgba(180, 83, 9, 0.14);
        border-radius: 20px;
        padding: 1.25rem;
        margin-top: 1rem;
    }}
    .kamote-caption {{
        color: #6b4f39;
        font-size: 0.96rem;
    }}
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stButton"] button {{
        border-radius: 999px;
        border: 1px solid rgba(180, 83, 9, 0.18);
    }}
    @media (max-width: 900px) {{
        .kamote-grid {{
            grid-template-columns: 1fr;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="kamote-hero">
        <div class="kamote-chip">Academic Roast Lab</div>
        <h1 style="margin:0; font-size:2.6rem; line-height:1.05;">The Kamote Critic</h1>
        <p class="kamote-caption" style="margin:0.65rem 0 0 0;">
            Sharp feedback for articles, PDFs, and pasted drafts. The critic now digs
            harder into ideas, logic, weak arguments, and hidden bias, not just sentence polish.
        </p>
        <div class="kamote-grid">
            <div class="kamote-card">
                <strong>Three input modes</strong>
                URL articles, uploaded PDFs, or plain pasted text.
            </div>
            <div class="kamote-card">
                <strong>Argument-first verdicts</strong>
                The roast prioritizes claims, evidence, assumptions, fallacies, and blind spots.
            </div>
            <div class="kamote-card">
                <strong>Bilingual output</strong>
                Choose English or Filipino/Tagalog for the written verdict.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


BASE_SYSTEM_INSTRUCTION = """
You are The Kamote Critic, an academic writing reviewer.
Be specific, fair, and useful.
Prioritize depth of ideas, logic, evidence, assumptions, bias, and argumentative strength over surface writing style.
Avoid personal attacks, slurs, or humiliation.
Always end with practical revision advice.
""".strip()


def get_api_key():
    return st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")


@st.cache_resource
def load_model(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=BASE_SYSTEM_INSTRUCTION,
    )


def get_url_text(url):
    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "KamoteCritic/0.1"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    content = " ".join(text for text in paragraphs if text)
    if not content:
        raise ValueError("No readable paragraph text was found on that page.")
    return content


def get_pdf_text(uploaded_file):
    uploaded_file.seek(0)
    reader = PdfReader(uploaded_file)
    pages = [page.extract_text() or "" for page in reader.pages]
    content = " ".join(text.strip() for text in pages if text and text.strip())
    if not content:
        raise ValueError("This PDF does not contain extractable text.")
    return content


def get_target_content(option, url_input, pdf_input, text_input):
    if option == "Online Article (URL)":
        if not url_input.strip():
            raise ValueError("Paste an article URL first.")
        return get_url_text(url_input.strip())

    if option == "PDF Document":
        if pdf_input is None:
            raise ValueError("Upload a PDF first.")
        return get_pdf_text(pdf_input)

    if not text_input.strip():
        raise ValueError("Paste some text first.")
    return text_input.strip()


def truncate_for_model(text):
    if len(text) <= MAX_INPUT_CHARS:
        return text, False
    return text[:MAX_INPUT_CHARS], True


def build_prompt(content, roast_style, response_language):
    if response_language == "Filipino/Tagalog":
        language_rule = (
            "Write the entire response in natural Filipino/Tagalog. "
            "Do not answer in English except for unavoidable quoted phrases from the source text."
        )
    else:
        language_rule = "Write the entire response in English."

    return f"""
Review the following writing sample using the Kamote Critic persona.

Tone setting: {roast_style}
Response language: {response_language}

Return your answer in exactly these sections:
1. Strong Ideas Worth Keeping
2. Major Logical Problems
3. Hidden Assumptions, Bias, or Fallacies
4. What Evidence or Reasoning Is Missing
5. How to Fix the Argument
6. Quick Writing Notes

Rules:
- {language_rule}
- Focus much more on ideas and argument quality than on grammar or writing style.
- Call out weak logic, unsupported claims, false dilemmas, hasty generalizations, circular reasoning, and other fallacies when present.
- Point out ideological bias, untested assumptions, or one-sided framing when present.
- Use a witty but constructive Kamote tone.
- Make the advice concrete and revision-oriented.
- Keep "Quick Writing Notes" brief and secondary.

Writing sample:
{content}
""".strip()


def render_copy_button(text):
    safe_text = html.escape(text)
    components.html(
        f"""
        <div style="margin: 0.2rem 0 0.6rem 0;">
            <button
                onclick="navigator.clipboard.writeText(document.getElementById('kamote-copy-source').innerText)"
                style="
                    background:#fff7ea;
                    color:{APP_INK};
                    border:1px solid rgba(180, 83, 9, 0.18);
                    border-radius:999px;
                    padding:0.55rem 0.95rem;
                    cursor:pointer;
                    font-family:inherit;
                    font-size:0.95rem;
                ">
                Copy Verdict to Clipboard
            </button>
            <pre id="kamote-copy-source" style="display:none; white-space:pre-wrap;">{safe_text}</pre>
        </div>
        """,
        height=52,
    )


def build_download_name(option):
    if option == "Online Article (URL)":
        return "kamote_verdict_article.txt"
    if option == "PDF Document":
        return "kamote_verdict_pdf.txt"
    return "kamote_verdict_text.txt"


if "last_verdict" not in st.session_state:
    st.session_state.last_verdict = ""
if "last_trimmed" not in st.session_state:
    st.session_state.last_trimmed = False
if "last_input_chars" not in st.session_state:
    st.session_state.last_input_chars = 0


with st.sidebar:
    st.markdown("### Setup")
    st.caption("Core critique controls are now shown directly on the page for easier mobile use.")
    if not get_api_key():
        st.caption("Add your Gemini key in Streamlit secrets before running Kamote Mode.")
        with st.expander("Where do I put the API key?"):
            st.write(
                "Create or edit `.streamlit/secrets.toml` in this project folder and add your Gemini key there."
            )
            st.caption("The app reads the key automatically. The secret itself should not appear on the page.")


left_col, right_col = st.columns([1.08, 0.92], gap="large")

with left_col:
    st.markdown('<div class="kamote-panel">', unsafe_allow_html=True)
    controls_a, controls_b = st.columns(2)
    with controls_a:
        roast_style = st.selectbox(
            "Critique style",
            [
                "Playful but professional",
                "Brutal but still constructive",
                "Professor mode",
                "Friendly editor",
            ],
        )
    with controls_b:
        response_language = st.selectbox(
            "Written response language",
            ["English", "Filipino/Tagalog"],
        )

    st.caption(
        f"Very long inputs are trimmed to the first {MAX_INPUT_CHARS:,} characters before analysis."
    )
    option = st.radio(
        "Pick your victim:",
        ["Online Article (URL)", "PDF Document", "Plain Text"],
        horizontal=True,
    )

    url_input = ""
    pdf_input = None
    text_input = ""

    if option == "Online Article (URL)":
        url_input = st.text_input("Drop the link here:", placeholder="https://example.com/article")
    elif option == "PDF Document":
        pdf_input = st.file_uploader("Upload the PDF:", type="pdf")
    else:
        text_input = st.text_area(
            "Paste the text here:",
            height=280,
            placeholder="Paste the draft, essay, critique target, or suspiciously overcooked paragraph here.",
        )

    st.markdown(
        '<p class="kamote-caption">The critic checks ideas first: weak logic, shaky evidence, hidden bias, fallacies, and unsupported claims. Writing notes come last.</p>',
        unsafe_allow_html=True,
    )
    run_analysis = st.button("Initiate Kamote Mode", use_container_width=True, type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="kamote-panel">', unsafe_allow_html=True)
    st.markdown("### Before You Click")
    st.write(
        """
Use a clean article URL, a text-based PDF, or a draft you want challenged more deeply.
The best results come from argumentative writing where claims, evidence, assumptions,
and blind spots can be tested. Longer samples still work, but only the opening portion
is analyzed once the text passes the current limit.
"""
    )
    st.metric("Character Limit", f"{MAX_INPUT_CHARS:,}")
    st.metric("Critique Style", roast_style)
    st.metric("Response Language", response_language)
    st.markdown("</div>", unsafe_allow_html=True)


if run_analysis:
    api_key = get_api_key()
    if not api_key:
        st.error(
            "Add `GEMINI_API_KEY` or `GOOGLE_API_KEY` to Streamlit secrets before running Kamote Mode."
        )
    else:
        try:
            raw_content = get_target_content(option, url_input, pdf_input, text_input)
            st.session_state.last_input_chars = len(raw_content)
            target_content, was_trimmed = truncate_for_model(raw_content)
            model = load_model(api_key)
            prompt = build_prompt(target_content, roast_style, response_language)

            with st.spinner("Logic Hunter is analyzing..."):
                response = model.generate_content(prompt)
                roast_text = (response.text or "").strip()
                if not roast_text:
                    raise ValueError("The model returned an empty response.")

                st.session_state.last_verdict = roast_text
                st.session_state.last_trimmed = was_trimmed
        except requests.RequestException as exc:
            st.error(f"Couldn't fetch that URL: {exc}")
        except Exception as exc:
            st.error(str(exc))


if st.session_state.last_verdict:
    st.markdown('<div class="kamote-verdict">', unsafe_allow_html=True)
    st.markdown("### The Verdict")

    meta_a, meta_b, meta_c = st.columns(3)
    meta_a.metric("Input Size", f"{st.session_state.last_input_chars:,} chars")
    meta_b.metric("Trimmed", "Yes" if st.session_state.last_trimmed else "No")
    meta_c.metric("Verdict Size", f"{len(st.session_state.last_verdict):,} chars")

    if st.session_state.last_trimmed:
        st.info(
            f"The input was longer than {MAX_INPUT_CHARS:,} characters, so only the opening portion was analyzed."
        )

    render_copy_button(st.session_state.last_verdict)
    st.download_button(
        "Download Verdict as TXT",
        data=st.session_state.last_verdict.encode("utf-8"),
        file_name=build_download_name(option),
        mime="text/plain",
        use_container_width=False,
    )
    st.write(st.session_state.last_verdict)

    st.markdown("</div>", unsafe_allow_html=True)
