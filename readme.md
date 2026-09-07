# AI Code Reviewer & Bug Fixing Agent

## Problem

Developers spend a lot of time manually identifying bugs, understanding why they happen, fixing them, and then writing test cases to confirm the fix. This is slow, especially when reviewing unfamiliar code or working under time pressure.

## Solution

An AI-powered assistant that:

- Reviews code and detects bugs, runtime errors, logic issues, performance problems, security issues, and code-quality concerns
- Explains each issue clearly (severity, location, explanation, suggested fix)
- Generates corrected code that preserves the original functionality
- Generates test cases (normal inputs, edge cases, boundaries, invalid inputs) to validate the fix

The user selects a programming language, pastes their code, and gets a structured review, a fixed version of the code, and a set of tests — all in one flow.

## Architecture

```
User
 ↓
Streamlit UI
 ↓
Python Application
 ↓
Gemini API
 ↓
AI Analysis
 ↓
Review / Fix / Tests
```

The app is a single-page Streamlit application. Each stage (Review, Fix, Tests) is a separate call to Gemini, and results are held in Streamlit session state so they persist across reruns as the user clicks through the flow.

## Tech Stack

- **Python** — application logic
- **Streamlit** — web UI (text input, dropdown, buttons, results display)
- **Google Gemini API** (`google-genai`) — reasoning engine for code review, fixing, and test generation
- **python-dotenv** — keeps the Gemini API key out of source control

## How to Run Locally

1. Clone the repository and move into the project folder.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with your Gemini API key:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```
5. Open the local URL Streamlit prints in the terminal (usually `http://localhost:8501`).

## Deployment

The app is deployed on Streamlit Community Cloud, built directly from this GitHub repository. The Gemini API key is configured in the deployed app's Secrets rather than committed to the repo.

**Live demo:** _[[Link](https://ai-code-reviewer-h95mmdcnylz8pmsvbfyur8.streamlit.app/)]_

## What's Not Included (by design)

This is an MVP built under a short time constraint, so the following were intentionally left out: login/authentication, a database, user accounts, RAG/vector search, a multi-agent architecture, GitHub repository scanning, CI/CD integration, actual compiler execution, and a custom ML model. These would strengthen a production version but aren't needed to demonstrate the core AI-assisted review/fix/test workflow.
