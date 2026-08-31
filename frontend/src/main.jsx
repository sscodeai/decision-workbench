import React from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

const API = '/api'

const STANCE_LABELS = {
  architect: '🏛️ Architect',
  cost: '💰 Cost',
  security: '🛡️ Security',
  product: '📦 Product',
  red_team: '🔴 Red Team',
}

const NOVELTY_LABELS = {
  you_probably_didnt_know: '✨ you probably didn\'t know this',
  you_already_knew: '✓ you already knew this',
}

const CONSTRAINT_OPTIONS = [
  { id: 'budget', label: '💰 Budget is tight' },
  { id: 'team', label: '👥 Small / existing team skills' },
  { id: 'deadline', label: '⏰ Tight deadline (ship fast)' },
  { id: 'compliance', label: '🔒 Compliance / data residency matters' },
]

function App() {
  const [input, setInput] = React.useState('')
  const [loading, setLoading] = React.useState(false)
  const [result, setResult] = React.useState(null)
  const [selectedConstraints, setSelectedConstraints] = React.useState([])
  const [chosenOption, setChosenOption] = React.useState('')
  const [rationale, setRationale] = React.useState('')
  const [error, setError] = React.useState('')

  const runDecide = async (e) => {
    e?.preventDefault()
    if (!input.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    setSelectedConstraints([])
    setChosenOption('')
    setRationale('')
    try {
      const res = await fetch(`${API}/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input }),
      })
      if (!res.ok) throw new Error('Failed to run decision')
      setResult(await res.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const applyConstraints = async () => {
    if (!result) return
    try {
      const res = await fetch(`${API}/decide/constraints`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision_id: result.decision_id,
          constraints: selectedConstraints,
        }),
      })
      if (!res.ok) throw new Error('Failed to apply constraints')
      setResult(await res.json())
    } catch (err) {
      setError(err.message)
    }
  }

  const recordDecision = async () => {
    if (!result || !chosenOption) return
    try {
      const res = await fetch(`${API}/decide/human-decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision_id: result.decision_id,
          chosen_option: chosenOption,
          rationale,
        }),
      })
      if (!res.ok) throw new Error('Failed to record decision')
      setResult(await res.json())
    } catch (err) {
      setError(err.message)
    }
  }

  const map = result?.option_space_map
  const allOptions = [
    ...(map?.consensus_zone || []),
    ...(map?.true_divergence_zone || []),
    ...(map?.false_divergence_zone || []),
  ]

  return (
    <div className="app">
      <header>
        <h1>🧠 Decision Workbench</h1>
        <p className="tagline">
          Expand your cognition <em>before</em> you decide.
          <br />
          <small>Decision power = size of your option space, not the ability to pick.</small>
        </p>
      </header>

      <form onSubmit={runDecide} className="input-card">
        <label htmlFor="decision-input">
          Describe a decision you're about to make — including what you already know:
        </label>
        <textarea
          id="decision-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. I need to build a CRM. I only know Java Spring."
          rows={3}
        />
        <div className="demo-buttons">
          <span>Try a demo:</span>
          <button type="button" onClick={() => setInput('I need to build a CRM. I only know Java Spring.')}>📊 Tech stack</button>
          <button type="button" onClick={() => setInput('I want to sell report subscriptions. Only thought of Stripe.')}>💳 Business</button>
          <button type="button" onClick={() => setInput('I need to hire a full-stack engineer.')}>👥 Hiring</button>
        </div>
        <button type="submit" className="primary" disabled={loading || !input.trim()}>
          {loading ? 'Diverging options…' : '🚀 Expand my option space'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result">
          {/* Stage 1: Bias flags */}
          {result.bias_flags?.length > 0 && (
            <section className="card bias-card">
              <h2>⚠️ Locked-in bias detected</h2>
              {result.bias_flags.map((f, i) => (
                <div key={i} className="bias-flag">
                  <strong>{f.label}</strong>
                  <p>{f.detail}</p>
                </div>
              ))}
              <p className="hint">
                The system flags this so you know <em>why</em> your option space
                may be narrower than it should be.
              </p>
            </section>
          )}

          {/* Stage 2: Stance divergence */}
          <section className="card">
            <h2>🗣️ Independent perspectives</h2>
            <p className="hint">
              Five stances argue from different angles — the divergence is the product.
            </p>
            <div className="stance-grid">
              {result.stance_divergence.map((s) => (
                <details key={s.stance} className="stance">
                  <summary>{STANCE_LABELS[s.stance] || s.stance}</summary>
                  <pre>{s.response}</pre>
                </details>
              ))}
            </div>
          </section>

          {/* Stage 3: Probing questions */}
          <section className="card">
            <h2>❓ Cross-examination</h2>
            {result.probing_answers.map((a, i) => (
              <div key={i} className="probe">
                <strong>{a.question}</strong>
                <pre>{a.answer}</pre>
              </div>
            ))}
          </section>

          {/* Stage 4: Option-space map */}
          <section className="card">
            <h2>🗺️ Your expanded option space</h2>
            <div className="zone">
              <h3 className="zone-title consensus">✅ Consensus zone — safe to adopt</h3>
              {map.consensus_zone.map((o) => (
                <OptionRow key={o.canonical} o={o} />
              ))}
            </div>
            <div className="zone">
              <h3 className="zone-title true-div">⚡ True divergence — genuinely different paths</h3>
              {map.true_divergence_zone.map((o) => (
                <OptionRow key={o.canonical} o={o} />
              ))}
            </div>
            <div className="zone">
              <h3 className="zone-title false-div">🌀 False divergence — doesn't matter</h3>
              {map.false_divergence_zone.map((o) => (
                <OptionRow key={o.canonical} o={o} />
              ))}
            </div>
          </section>

          {/* Stage 5: Constraint backfill */}
          <section className="card">
            <h2>🎯 What are your real constraints?</h2>
            <div className="constraints">
              {CONSTRAINT_OPTIONS.map((c) => (
                <label key={c.id} className="constraint">
                  <input
                    type="checkbox"
                    checked={selectedConstraints.includes(c.id)}
                    onChange={(e) => {
                      const next = e.target.checked
                        ? [...selectedConstraints, c.id]
                        : selectedConstraints.filter((x) => x !== c.id)
                      setSelectedConstraints(next)
                    }}
                  />
                  {c.label}
                </label>
              ))}
            </div>
            <button onClick={applyConstraints} disabled={selectedConstraints.length === 0} className="secondary">
              Re-score against my constraints
            </button>
            {result.constraint_evaluation && (
              <div className="scored">
                <h4>Weighted evaluation (sorted):</h4>
                {result.constraint_evaluation.map((o) => (
                  <div key={o.canonical} className="scored-row">
                    <span>{o.canonical}</span>
                    <span className="score">{o.weighted_score ?? '—'}</span>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Stage 6: Human decision */}
          <section className="card decision-card">
            <h2>✋ The decision is yours</h2>
            <p className="hint">
              The system never picks a winner. You review the map and decide.
            </p>
            <select value={chosenOption} onChange={(e) => setChosenOption(e.target.value)}>
              <option value="">— choose an option —</option>
              {allOptions.map((o) => (
                <option key={o.canonical} value={o.canonical}>
                  {o.canonical}
                </option>
              ))}
            </select>
            <textarea
              value={rationale}
              onChange={(e) => setRationale(e.target.value)}
              placeholder="Your rationale (optional)"
              rows={2}
            />
            <button onClick={recordDecision} disabled={!chosenOption} className="primary">
              Record my decision
            </button>
            {result.human_decision?.status === 'decided' && (
              <div className="decision-recorded">
                ✅ Recorded: <strong>{result.human_decision.chosen_option}</strong>
                {result.human_decision.rationale && ` — ${result.human_decision.rationale}`}
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  )
}

function OptionRow({ o }) {
  return (
    <div className={`option-row ${o.novelty === 'you_probably_didnt_know' ? 'novel' : ''}`}>
      <div className="option-head">
        <strong>{o.canonical}</strong>
        <span className="novelty">{NOVELTY_LABELS[o.novelty] || o.novelty}</span>
        {o.support_count > 0 && <span className="support">({o.support_count} supports)</span>}
      </div>
      {o.reason && <p className="option-reason">{o.reason}</p>}
      {o.tradeoffs && <p className="option-tradeoffs">⚖️ {o.tradeoffs}</p>}
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
