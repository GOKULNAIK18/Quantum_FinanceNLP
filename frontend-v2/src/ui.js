import { renderSentimentChart } from './charts.js'

const fmt = (n, d = 2) => Number(n).toFixed(d)
const CURRENCY_SYMBOLS = { USD: '$', INR: '₹', GBP: '£', AUD: 'A$', CAD: 'C$', HKD: 'HK$', CNY: '¥', EUR: '€' }
const sym = c => CURRENCY_SYMBOLS[c] || c + ' '

function fmtLarge(n, currency) {
  const s = sym(currency)
  if (n >= 1e12) return s + fmt(n / 1e12) + 'T'
  if (n >= 1e9)  return s + fmt(n / 1e9) + 'B'
  if (n >= 1e6)  return s + fmt(n / 1e6) + 'M'
  return s + Number(n).toLocaleString()
}

function progress(pct, cls = '') {
  return `<div class="progress-track"><div class="progress-fill ${cls}" style="width:${pct}%"></div></div>`
}

export function renderResults(container, d) {
  const s       = sym(d.currency)
  const isPos   = d.change >= 0
  const sign    = isPos ? '+' : ''
  const clr     = isPos ? 'pos' : 'neg'
  const changePct = (d.change_percent * 100).toFixed(2)

  const badgeMap  = { Bullish: 'badge-bullish', Bearish: 'badge-bearish', Neutral: 'badge-neutral' }
  const badgeDot  = { Bullish: '▲', Bearish: '▼', Neutral: '●' }
  const riskCls   = { High: 'risk-high', Medium: 'risk-medium', Low: 'risk-low' }
  const qLabels   = ['Price Chg', 'Volume', '52W Pos', 'Sentiment']

  // Peers sorted for bar chart
  const allPeers = [
    { ticker: d.ticker, score: d.sentiment.score, main: true },
    ...d.peers.map(p => ({ ticker: p.ticker, score: p.quantum_score, main: false }))
  ].sort((a, b) => b.score - a.score)
  const maxScore = Math.max(...allPeers.map(p => p.score), 1)

  container.innerHTML = `
    <div class="main">

      <!-- Stock header -->
      <div class="stock-header">
        <div class="stock-name-block">
          <div class="stock-ticker">${d.ticker}</div>
          <div class="stock-company">${d.company_name}</div>
          <div class="stock-meta">${d.sector} · ${d.industry}</div>
        </div>
        <div class="stock-price-block">
          <div class="stock-price ${clr}">${s}${fmt(d.price)}</div>
          <div class="stock-change ${clr}">${sign}${s}${fmt(Math.abs(d.change))} (${sign}${changePct}%) today</div>
        </div>
      </div>

      <!-- Stat strip -->
      <div class="stat-strip">
        <div class="stat-item">
          <div class="stat-label">52W High</div>
          <div class="stat-value">${s}${fmt(d.high_52w)}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">52W Low</div>
          <div class="stat-value">${s}${fmt(d.low_52w)}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Market Cap</div>
          <div class="stat-value">${fmtLarge(d.market_cap, d.currency)}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Volume</div>
          <div class="stat-value">${Number(d.volume).toLocaleString()}</div>
        </div>
      </div>

      <!-- Sentiment + Headlines -->
      <div class="two-col">

        <div class="panel">
          <div class="section-title">News Sentiment</div>
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <span class="badge ${badgeMap[d.sentiment.label] || 'badge-neutral'}">
              ${badgeDot[d.sentiment.label] || '●'} ${d.sentiment.label}
            </span>
            <span style="font-size:0.72rem;color:var(--muted);">FinBERT model</span>
          </div>
          <div class="score-display">
            <span class="score-num">${d.sentiment.score}</span>
            <span class="score-denom">/ 100</span>
          </div>
          ${progress(d.sentiment.score, d.sentiment.score >= 50 ? 'green' : '')}

          <div style="margin-top:1.25rem;display:grid;grid-template-columns:repeat(3,1fr);gap:0.5rem;text-align:center;">
            <div>
              <div style="font-size:1rem;font-weight:700;color:var(--green);">${d.sentiment.positive}%</div>
              <div style="font-size:0.68rem;color:var(--muted);margin-top:0.15rem;">Positive</div>
            </div>
            <div>
              <div style="font-size:1rem;font-weight:700;color:var(--red);">${d.sentiment.negative}%</div>
              <div style="font-size:0.68rem;color:var(--muted);margin-top:0.15rem;">Negative</div>
            </div>
            <div>
              <div style="font-size:1rem;font-weight:700;color:#8b8bff;">${d.sentiment.neutral}%</div>
              <div style="font-size:0.68rem;color:var(--muted);margin-top:0.15rem;">Neutral</div>
            </div>
          </div>

          <div style="margin-top:1.25rem;height:140px;">
            <canvas id="sentimentChart"></canvas>
          </div>
        </div>

        <div class="panel">
          <div class="section-title">Latest News</div>
          ${d.headlines.map(h => `
            <div class="headline-item">
              <div class="headline-dot"></div>
              <div class="headline-text">
                <a href="${h.link}" target="_blank" rel="noopener noreferrer">${h.title}</a>
                <div class="headline-pub">${h.publisher}</div>
              </div>
            </div>`).join('')}
        </div>

      </div>

      <!-- Quantum metrics -->
      <div class="section-title">Quantum Circuit Analysis <span style="font-size:0.65rem;color:var(--muted2);font-weight:400;text-transform:none;letter-spacing:0;">· RY gates · CNOT entanglement · Born rule</span></div>
      <div class="three-col">
        <div class="q-card">
          <div class="q-label">Entanglement Score</div>
          <div class="q-value">${d.quantum_metrics.entanglement_score}<span style="font-size:0.9rem;color:var(--muted);font-weight:400;"> / 100</span></div>
          ${progress(d.quantum_metrics.entanglement_score)}
          <div class="q-sub">Qubit correlation strength</div>
        </div>
        <div class="q-card">
          <div class="q-label">Superposition Stability</div>
          <div class="q-value">${d.quantum_metrics.superposition_stability}<span style="font-size:0.9rem;color:var(--muted);font-weight:400;">%</span></div>
          ${progress(d.quantum_metrics.superposition_stability)}
          <div class="q-sub">State coherence measure</div>
        </div>
        <div class="q-card">
          <div class="q-label">Decoherence Risk</div>
          <div class="q-value" style="margin-bottom:0.5rem;">
            <span class="risk-pill ${riskCls[d.quantum_metrics.decoherence_risk]}">${d.quantum_metrics.decoherence_risk}</span>
          </div>
          <div class="q-sub">Quantum state purity</div>
        </div>
      </div>

      <!-- Qubit states -->
      <div class="qubit-row">
        ${d.quantum_metrics.qubit_states.map((state, i) => `
          <div class="qubit-card">
            <div class="qubit-index">q[${i}] · ${qLabels[i]}</div>
            <div class="qubit-state">${state}</div>
            <div class="qubit-prob">P(|1⟩) = ${d.quantum_metrics.probabilities[i]}</div>
          </div>`).join('')}
      </div>

      <!-- Peers + Alternative -->
      <div class="col-2-1" style="margin-top:1.5rem;">

        <div class="panel">
          <div class="section-title">Peer Comparison</div>
          ${allPeers.map(p => `
            <div class="peer-row">
              <div class="peer-ticker">${p.ticker}</div>
              <div class="peer-bar-track">
                <div class="peer-bar-fill ${p.main ? 'main' : ''}" style="width:${(p.score / maxScore * 100).toFixed(1)}%"></div>
              </div>
              <div class="peer-score">${p.score}</div>
            </div>`).join('')}
        </div>

        <div class="alt-card">
          <div class="alt-label">AI Top Pick</div>
          <div class="alt-ticker">${d.top_alternative.ticker}</div>
          <div style="margin-top:0.4rem;">
            <span class="badge badge-bullish" style="font-size:0.68rem;">Recommended</span>
          </div>
          <div class="alt-reasoning">${d.top_alternative.reasoning}</div>
        </div>

      </div>

    </div>
  `

  renderSentimentChart(container.querySelector('#sentimentChart'), d.sentiment)
}
