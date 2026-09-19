'use client';

import { useState } from 'react';
import { createTask, getRun, startRun } from '../lib/api';

function pct(value: unknown) {
  return typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : 'n/a';
}
function num(value: unknown, digits = 2) {
  return typeof value === 'number' ? value.toLocaleString('id-ID', { maximumFractionDigits: digits }) : 'n/a';
}

export default function Home() {
  const [ticker, setTicker] = useState('BBCA');
  const [horizon, setHorizon] = useState(90);
  const [capital, setCapital] = useState('100000000');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('Ready');
  const [result, setResult] = useState<any>(null);

  async function analyze() {
    setLoading(true);
    setResult(null);
    try {
      setMessage('Creating research task...');
      const task = await createTask(ticker, horizon, capital);
      setMessage('Queued. Waiting for deterministic analysis and local Ollama review...');
      const run = await startRun(task.id);
      for (let i = 0; i < 120; i++) {
        await new Promise((r) => setTimeout(r, 2000));
        const current = await getRun(run.id);
        setMessage(`Run status: ${current.status}`);
        if (current.status === 'COMPLETED') {
          setResult(current.result);
          setMessage('Completed');
          return;
        }
        if (current.status === 'FAILED') throw new Error(current.error || 'Run failed');
      }
      throw new Error('Timed out waiting for analysis');
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header>
        <div>
          <div className="eyebrow">LOCAL-FIRST INDONESIAN EQUITY RESEARCH</div>
          <h1>BuktiSaham</h1>
          <p>Deterministic research + evidence + local Ollama review. Stock data is free-only for this MVP.</p>
        </div>
        <div className="pill">No paid data fallback</div>
      </header>

      <section className="panel controls">
        <label>Ticker<input value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} placeholder="BBCA" /></label>
        <label>Horizon (days)<input type="number" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))} /></label>
        <label>Capital (IDR)<input value={capital} onChange={(e) => setCapital(e.target.value)} /></label>
        <button onClick={analyze} disabled={loading}>{loading ? 'Analyzing...' : 'Run analysis'}</button>
      </section>

      <div className="status">{message}</div>

      {result && (
        <>
          <section className="grid">
            <article className="panel hero-card">
              <div className="eyebrow">RESEARCH ACTION</div>
              <h2>{result.research_action}</h2>
              <div className="big">{result.ticker}</div>
              <p>{result.policy_reasons?.join(' ')}</p>
            </article>
            <article className="panel">
              <div className="eyebrow">PRICE / EXPECTED RETURN</div>
              <h2>Rp {num(result.technicals?.last_close, 0)}</h2>
              <div className="metric">Expected return <strong>{pct(result.scenario_analysis?.expected_return)}</strong></div>
              <div className="metric">Bear downside <strong>{pct(result.scenario_analysis?.bear_downside)}</strong></div>
            </article>
            <article className="panel">
              <div className="eyebrow">CONFIDENCE</div>
              <h2>{num(result.scores?.confidence, 1)} / 100</h2>
              <div className="metric">Evidence <strong>{num(result.scores?.evidence_completeness, 1)}%</strong></div>
              <div className="metric">Liquidity <strong>{num(result.scores?.liquidity, 1)}</strong></div>
            </article>
          </section>

          <section className="panel">
            <h3>Scenario analysis</h3>
            <div className="scenario-grid">
              {result.scenario_analysis?.scenarios?.map((s: any) => (
                <div className="scenario" key={s.name}>
                  <span>{s.name}</span>
                  <strong>Rp {num(s.target_price, 0)}</strong>
                  <small>{pct(s.return)} · p={pct(s.probability)}</small>
                </div>
              ))}
            </div>
          </section>

          <section className="two-col">
            <article className="panel">
              <h3>Deterministic metrics</h3>
              <div className="metric">Technical <strong>{num(result.scores?.technical, 1)}</strong></div>
              <div className="metric">Fundamental <strong>{num(result.scores?.fundamental, 1)}</strong></div>
              <div className="metric">RSI 14 <strong>{num(result.technicals?.rsi14, 1)}</strong></div>
              <div className="metric">20d return <strong>{pct(result.technicals?.return_20d)}</strong></div>
              <div className="metric">60d return <strong>{pct(result.technicals?.return_60d)}</strong></div>
              <div className="metric">1y max drawdown <strong>{pct(result.technicals?.max_drawdown_1y)}</strong></div>
            </article>
            <article className="panel">
              <h3>Local Ollama review</h3>
              <p className="subtle">{result.ai_review?.provider} · {result.ai_review?.model} · {result.ai_review?.status}</p>
              <p>{result.ai_review?.summary}</p>
              {result.ai_review?.key_risks?.length > 0 && <><h4>Risks</h4><ul>{result.ai_review.key_risks.map((x: string) => <li key={x}>{x}</li>)}</ul></>}
              {result.ai_review?.analyst_questions?.length > 0 && <><h4>Analyst questions</h4><ul>{result.ai_review.analyst_questions.map((x: string) => <li key={x}>{x}</li>)}</ul></>}
            </article>
          </section>

          <section className="panel">
            <h3>Evidence</h3>
            {result.evidence?.map((e: any) => (
              <div className="evidence" key={e.content_hash}>
                <div><strong>{e.evidence_type}</strong> · {e.source_name}</div>
                <a href={e.source_uri} target="_blank">source</a>
                <small>{e.rights_note}</small>
              </div>
            ))}
            <div className="hash">Deterministic hash: {result.deterministic_hash}</div>
          </section>
        </>
      )}
    </main>
  );
}
