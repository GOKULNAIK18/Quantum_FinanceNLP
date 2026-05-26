import './style.css'
import { analyzeTicket } from './api.js'
import { renderResults } from './ui.js'

const app = document.getElementById('app')

app.innerHTML = `
  <nav class="navbar">
    <div class="navbar-brand">⚛ <span>Quantum</span>Finance</div>
    <div class="navbar-tag">BETA</div>
  </nav>

  <div class="search-section">
    <div class="search-inner">
      <input id="tickerInput" type="text" placeholder="Search ticker — AAPL, BEL, RELIANCE…" maxlength="15" autocomplete="off" spellcheck="false" />
      <button id="analyseBtn">Analyse</button>
    </div>
  </div>

  <div id="spinner" class="spinner-wrap hidden" style="padding:2rem;">
    <div class="spinner"></div>
    <span id="spinnerText">Fetching data…</span>
  </div>
  <div id="errorBox" class="error-box hidden"></div>
  <div id="results"></div>
`

const tickerInput = document.getElementById('tickerInput')
const analyseBtn  = document.getElementById('analyseBtn')
const spinner     = document.getElementById('spinner')
const spinnerText = document.getElementById('spinnerText')
const errorBox    = document.getElementById('errorBox')
const results     = document.getElementById('results')

async function analyse() {
  const ticker = tickerInput.value.trim().toUpperCase()
  if (!ticker) return

  results.innerHTML = ''
  errorBox.classList.add('hidden')
  spinnerText.textContent = `Analysing ${ticker}…`
  spinner.classList.remove('hidden')
  analyseBtn.disabled = true

  try {
    const data = await analyzeTicket(ticker)
    renderResults(results, data)
  } catch (e) {
    const msg = e.message.includes('Failed to fetch')
      ? 'Cannot connect to backend. Make sure the Railway backend is running.'
      : `Analysis failed: ${e.message}`
    errorBox.textContent = msg
    errorBox.classList.remove('hidden')
  } finally {
    spinner.classList.add('hidden')
    analyseBtn.disabled = false
  }
}

analyseBtn.addEventListener('click', analyse)
tickerInput.addEventListener('keydown', e => { if (e.key === 'Enter') analyse() })
