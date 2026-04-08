# Quantum Finance — Python

Full Python rebuild of the Quantum Finance app.

## Stack
- **Yahoo Finance** — real stock data, news, peers
- **FinBERT** (Hugging Face) — real NLP sentiment from headlines
- **Quantum Circuit Simulator** (NumPy) — real quantum math
- **Gemini 1.5 Flash** — peer scoring + top alternative
- **FastAPI** — backend API
- **Streamlit + Plotly** — frontend UI

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add your API keys to `.env`:
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
cd frontend
streamlit run app.py
```
Frontend runs at http://localhost:8501
