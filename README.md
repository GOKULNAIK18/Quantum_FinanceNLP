# Quantum Finance — Python

Full Python + JavaScript rebuild of the Quantum Finance app.

## Stack
- **Yahoo Finance** — real stock data, news, peers (global + Indian exchanges)
- **FinBERT** (Hugging Face) — real NLP sentiment from headlines
- **Quantum Circuit Simulator** (NumPy) — real quantum math
- **Gemini 1.5 Flash** — peer scoring + top alternative
- **FastAPI** — backend API
- **Vite + Vanilla JS + Chart.js** — frontend UI

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend-v2
   npm install
   ```

3. Add your API keys to `.env`:
   ```
   GEMINI_API_KEY=your_gemini_key
   HUGGINGFACE_API_KEY=your_hf_key
   ```
   - Gemini key: https://aistudio.google.com/apikey
   - Hugging Face key: https://huggingface.co/settings/tokens

## Run

Open two terminals:

**Terminal 1 — Backend:**
```bash
cd backend
python main.py
```
Backend runs at http://localhost:8000

**Terminal 2 — Frontend:**
```bash
cd frontend-v2
npm run dev
```
Frontend runs at http://localhost:5173
