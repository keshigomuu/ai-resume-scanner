# AI Resume Checker

A full‐stack application that analyzes a user’s resume (PDF) against a given job description (plain text), computes a skill‐match percentage, identifies missing skills, and generates optimized, metric‐driven bullet rewrites and suggestions using OpenAI’s GPT. This tool combines Python/FastAPI, PDF parsing, lightweight NLP, and GPT prompts to deliver a polished, cost‐efficient resume‐review experience.

---

## Table of Contents

1. [Features](#features)  
2. [Tech Stack](#tech-stack)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
5. [Running the Application](#running-the-application)  

---

## Features

- **PDF Resume Parsing**  
  Automatically extracts text from a user‐uploaded PDF resume using PyPDF2.

- **Resume Summarization (Optional)**  
  Condenses lengthy résumés into concise bullet points via OpenAI GPT to reduce token usage.

- **Skill Extraction & Matching**  
  Uses a rule‐based, tokenized approach (against a curated `skill_patterns.json`) to identify which skills appear in both résumé and job description. Computes a “match percentage,” lists matched vs. missing skills.

- **GPT‐Driven Bullet Rewrites**  
  For each original résumé bullet, generates an improved, quantified version (strong verbs, metrics, aligned to JD) without hallucinating skills the candidate doesn’t have.

- **GPT‐Generated Suggestions**  
  For each missing skill, produces a concrete bullet explaining how to add or acquire that skill, plus 2–3 general tips on making the résumé more attention‐grabbing (strong verbs, mirroring keywords, quantifying results).

- **Modern Frontend UI**  
  Minimalist, responsive HTML/CSS/Vanilla JS interface with a drag‐and‐drop–style file upload and a CSS spinner to indicate “loading.”

- **Error Handling & Fallbacks**  
  Handles invalid inputs (non‐PDF uploads, missing JD skills) gracefully; provides generic fallback suggestions if GPT calls fail.

---

## Tech Stack

- **Frontend**  
  - HTML5, CSS3 (custom styles, responsive design)  
  - Vanilla JavaScript (Fetch API for REST calls, DOM manipulation)  

- **Backend**  
  - **FastAPI** (serving REST endpoints, request/response validation via Pydantic)  
  - **Uvicorn** (ASGI server)  
  - **Python 3.10+**  

- **PDF Parsing**  
  - **PyPDF2** (extract text from uploaded PDF)  

- **AI / NLP**  
  - **OpenAI GPT-3.5-Turbo** (via `openai` Python SDK) for summarization, rewriting bullets, and generating suggestions  
  - **spaCy** (installed as a dependency, available for future NLP enhancements but not used in the core flow)  

- **Other Libraries**  
  - `python-dotenv` (for managing environment variables, if desired)  

---

## Prerequisites

1. **Python 3.10+** installed on your system.  
2. **Node.js & npm** (if you plan to serve the frontend via an npm‐based static server).  
3. **OpenAI API Key** (obtain from [platform.openai.com](https://platform.openai.com/)).  
4. A modern web browser (Chrome, Firefox, Safari, Edge).

---

## Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-username/ai-resume-checker.git
   cd ai-resume-checker
   ```
2. **Backend Setup**
  ```bash
  cd backend
  python3 -m venv .venv
  source .venv/bin/activate         # macOS/Linux
  # .venv\Scripts\activate           # Windows
  pip install --upgrade pip
  pip install -r requirements.txt
  ```
3. **Environment Variables**
<br>Set up .env file in backend folder
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```
4. **Frontend Setup**
  <br> You can simply open frontend/index.html in your browser.

## Running the Application
1. **Starting the backend**
  ```bash
cd backend
source .venv/bin/activate       # (if not already)
uvicorn app:app --reload
```
3. **Starting the frontend**
   <br>Option A: Double‐click frontend/index.html in your file manager.<br>

Option B: If using live-server:
```bash
cd frontend
npm run dev
```

