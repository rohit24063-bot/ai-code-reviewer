import os

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 AI Code Reviewer")
st.caption("Analyze code, identify bugs, generate fixes, and create test cases with Gemini.")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("GEMINI_API_KEY is missing. Add it to your .env file (locally) "
              "or to your Streamlit Cloud app's Secrets (when deployed).")
    st.stop()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key
)

MODEL = "gemini-2.5-flash"

# ---------- Session state ----------
for key in ["review", "fixed_code", "tests", "last_code", "last_language"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ---------- LangChain call wrapper ----------
def call_gemini(prompt: str) -> str | None:
    try:
        response = llm.invoke(prompt)

        if not response or not getattr(response, "content", None):
            st.error("Gemini returned an empty response. Please try again.")
            return None

        content = response.content

        # LangChain may return content as a list of blocks
        if isinstance(content, list):
            text_parts = []

            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif isinstance(block, str):
                    text_parts.append(block)

            content = "\n".join(text_parts)

        return content

    except Exception as e:
        st.error("Unable to reach Gemini right now. Please check your API key "
                 "and connection, then try again.")

        with st.expander("Error details"):
            st.exception(e)

        return None


# ---------- Inputs ----------
language = st.selectbox(
    "Programming Language",
    ["Python", "C++", "Java", "JavaScript"]
)

code = st.text_area(
    "Paste your code",
    height=400,
    placeholder="Paste your code here..."
)

# If the code or language changes, stale results from a previous run are cleared
if code != st.session_state.last_code or language != st.session_state.last_language:
    st.session_state.review = None
    st.session_state.fixed_code = None
    st.session_state.tests = None

review_clicked = st.button("🔍 Review Code", type="primary")

if review_clicked:
    if not code.strip():
        st.warning("Please paste some code first.")
    else:
        review_prompt = f"""
You are an expert software engineer and code reviewer.

Analyze the following {language} code.

Identify:
1. Bugs and incorrect behavior
2. Potential runtime errors
3. Logic issues
4. Performance problems
5. Security issues if relevant
6. Code quality issues

For every issue provide:
- Severity: Critical, High, Medium, or Low
- Location/line number if possible
- Issue title
- Clear explanation
- Suggested fix

If the code is correct, explicitly say that no major issues were found.

Code:

```{language.lower()}
{code}```
"""

        with st.spinner("Analyzing your code..."):
            result = call_gemini(review_prompt)

        if result:
            st.session_state.review = result
            st.session_state.fixed_code = None
            st.session_state.tests = None
            st.session_state.last_code = code
            st.session_state.last_language = language


# ---------- Review results ----------
if st.session_state.review:
    st.divider()
    st.subheader("🐛 Code Review")
    st.markdown(st.session_state.review)

    col1, col2 = st.columns(2)

    fix_clicked = col1.button("✨ Fix Code")
    tests_clicked = col2.button("🧪 Generate Tests")

    if fix_clicked:
        fix_prompt = f"""
You are an expert software engineer.

Below is a piece of {language} code, followed by a code review of that code.

Rewrite the code so it:
- preserves the original functionality/intent
- fixes every issue identified in the review
- avoids unnecessary or unrelated changes
- is syntactically valid {language}

Return ONLY the corrected code in a single code block, with no extra commentary before or after it.

Original code:
```{language.lower()}
{st.session_state.last_code}```

Code review:
{st.session_state.review}
"""

        with st.spinner("Generating corrected code..."):
            result = call_gemini(fix_prompt)

        if result:
            st.session_state.fixed_code = result

    if tests_clicked:
        tests_prompt = f"""
You are an expert software engineer writing tests.

Below is a piece of {language} code, followed by a code review of that code.

Generate a set of test cases for this code, including:
- normal/typical inputs
- edge cases
- boundary conditions
- invalid inputs (if applicable)
- any test likely to expose the bugs mentioned in the review

For each test, give the input and the expected output/behavior. Present them clearly,
grouped and labeled (e.g. "Test 1", "Test 2", ...).

Original code:
```{language.lower()}
{st.session_state.last_code}```

Code review:
{st.session_state.review}
"""

        with st.spinner("Generating test cases..."):
            result = call_gemini(tests_prompt)

        if result:
            st.session_state.tests = result


# ---------- Fixed code ----------
if st.session_state.fixed_code:
    st.divider()
    st.subheader("✨ Recommended Corrected Code")
    st.markdown(st.session_state.fixed_code)


# ---------- Tests ----------
if st.session_state.tests:
    st.divider()
    st.subheader("🧪 Generated Test Cases")
    st.markdown(st.session_state.tests)
