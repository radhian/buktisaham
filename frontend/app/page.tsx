'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';
import {
  TaskPayload,
  createTask,
  getDashboard,
  getRun,
  listRuns,
  listTasks,
  startRun,
} from '../lib/api';

type Run = {
  id: string;
  task_id: string;
  status: string;
  stage: string;
  progress: number;
  message: string;
  error?: string | null;
  result?: any;
  events?: Array<{ stage: string; progress: number; message: string; created_at: string }>;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
};

type Task = {
  id: string;
  name: string;
  thesis: string;
  ticker: string;
  tickers: string[];
  horizon_days: number;
  capital_idr: string;
  cadence: string;
  status: string;
  analysis_modules: string[];
  config_version: number;
  config_hash: string;
  latest_run?: Run | null;
  created_at: string;
};

const DEFAULT_FORM: TaskPayload = {
  name: 'IDX Quality Watchlist',
  thesis: 'Identify financially sound Indonesian equities with adequate liquidity, explainable upside, and explicit downside risk.',
  tickers: ['BBCA', 'BBRI', 'TLKM'],
  horizon_days: 90,
  capital_idr: '100000000',
  cadence: 'manual',
  analysis_modules: ['technical', 'fundamental', 'liquidity', 'scenario', 'evidence', 'ai_review'],
};

function idr(value: unknown, digits = 0) {
  return typeof value === 'number'
    ? `Rp ${value.toLocaleString('id-ID', { maximumFractionDigits: digits })}`
    : 'n/a';
}

function pct(value: unknown) {
  return typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : 'n/a';
}

function score(value: unknown) {
  return typeof value === 'number' ? value.toLocaleString('id-ID', { maximumFractionDigits: 1 }) : 'n/a';
}

function date(value?: string | null) {
  if (!value) return 'Not available';
  return new Date(value).toLocaleString('id-ID', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Asia/Jakarta',
  });
}

function shortId(value: string) {
  return value.slice(0, 8);
}

function isActive(status?: string) {
  return status === 'QUEUED' || status === 'RUNNING';
}

function statusTone(status?: string) {
  if (status === 'COMPLETED') return 'success';
  if (status === 'PARTIAL') return 'warning';
  if (status === 'FAILED') return 'danger';
  return 'active';
}

export default function Home() {
  const [view, setView] = useState<'dashboard' | 'tasks' | 'runs' | 'methodology' | 'settings'>('dashboard');
  const [dashboard, setDashboard] = useState<any>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [runDetail, setRunDetail] = useState<Run | null>(null);
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState<TaskPayload>(DEFAULT_FORM);
  const [tickerText, setTickerText] = useState(DEFAULT_FORM.tickers.join(', '));
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('Ready');

  const selectedTask = useMemo(
    () => tasks.find((task) => task.id === selectedTaskId) || null,
    [tasks, selectedTaskId],
  );

  async function refreshWorkspace() {
    try {
      const [dashboardData, taskData, runData] = await Promise.all([
        getDashboard(),
        listTasks(),
        listRuns(),
      ]);
      setDashboard(dashboardData);
      setTasks(taskData);
      setRuns(runData);
    } catch (error: any) {
      setNotice(`Unable to refresh workspace: ${error.message}`);
    }
  }

  useEffect(() => {
    refreshWorkspace();
    const timer = window.setInterval(refreshWorkspace, 5000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!selectedRunId) {
      setRunDetail(null);
      return;
    }
    let cancelled = false;
    async function loadRun() {
      try {
        const current = await getRun(selectedRunId as string);
        if (!cancelled) {
          setRunDetail(current);
          const analyses = current.result?.analyses || [];
          if (analyses.length && !analyses.some((item: any) => item.ticker === selectedTicker)) {
            setSelectedTicker(analyses[0].ticker);
          }
        }
      } catch (error: any) {
        if (!cancelled) setNotice(`Unable to load run: ${error.message}`);
      }
    }
    loadRun();
    const timer = window.setInterval(loadRun, 2500);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [selectedRunId, selectedTicker]);

  async function submitTask(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      const tickers = tickerText
        .split(/[\s,]+/)
        .map((item) => item.trim().toUpperCase())
        .filter(Boolean);
      const created = await createTask({ ...form, tickers });
      setNotice(`Created task “${created.name}”`);
      setShowCreate(false);
      setSelectedTaskId(created.id);
      setView('tasks');
      await refreshWorkspace();
    } catch (error: any) {
      setNotice(`Task creation failed: ${error.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function runTask(task: Task) {
    setBusy(true);
    try {
      setNotice(`Queueing ${task.name}...`);
      const run = await startRun(task.id);
      setSelectedTaskId(task.id);
      setSelectedRunId(run.id);
      setRunDetail(run);
      setView('runs');
      setNotice('Run queued. The worker is executing the saved task configuration.');
      await refreshWorkspace();
    } catch (error: any) {
      setNotice(`Unable to start run: ${error.message}`);
    } finally {
      setBusy(false);
    }
  }

  function openTask(task: Task) {
    setSelectedTaskId(task.id);
    setView('tasks');
  }

  function openRun(run: Run) {
    setSelectedRunId(run.id);
    setSelectedTaskId(run.task_id);
    setView('runs');
  }

  const analyses = runDetail?.result?.analyses || [];
  const analysis = analyses.find((item: any) => item.ticker === selectedTicker) || analyses[0] || null;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => setView('dashboard')}>
          <span className="brand-mark">BS</span>
          <span><strong>BuktiSaham</strong><small>IDX research orchestrator</small></span>
        </button>
        <nav>
          {[
            ['dashboard', 'Overview', '01'],
            ['tasks', 'Research tasks', '02'],
            ['runs', 'Run history', '03'],
            ['methodology', 'Methodology', '04'],
          ].map(([key, label, number]) => (
            <button
              key={key}
              className={view === key ? 'active' : ''}
              onClick={() => setView(key as any)}
            >
              <span>{number}</span>{label}
            </button>
          ))}
        </nav>
        <div className="sidebar-card">
          <span className="signal-dot" />
          <strong>Local-first stack</strong>
          <small>Free EOD data · Ollama review · deterministic policy</small>
        </div>
        <button className={`settings-link ${view === 'settings' ? 'active' : ''}`} onClick={() => setView('settings')}>
          <span>05</span>Settings
        </button>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">TASK-BASED INDONESIAN EQUITY RESEARCH</span>
            <h1>{view === 'dashboard' ? 'Research command center' : view === 'tasks' ? 'Research tasks' : view === 'runs' ? 'Run orchestration' : view === 'methodology' ? 'IDX methodology' : 'System settings'}</h1>
          </div>
          <div className="top-actions">
            <span className="policy-chip">FREE DATA ONLY</span>
            <button className="primary" onClick={() => setShowCreate(true)}>+ New task</button>
          </div>
        </header>

        <div className="notice"><span className="signal-dot" />{notice}</div>

        {view === 'dashboard' && (
          <>
            <section className="hero-banner">
              <div>
                <span className="eyebrow">REPEATABLE RESEARCH, NOT ONE-OFF CALCULATION</span>
                <h2>Create the method once. Run it whenever the evidence changes.</h2>
                <p>Each task preserves its thesis, ticker universe, horizon, capital context, methodology modules, and configuration hash. Every run produces a traceable evidence packet.</p>
                <div className="hero-actions">
                  <button className="primary" onClick={() => setShowCreate(true)}>Create research task</button>
                  <button className="secondary" onClick={() => setView('methodology')}>Review methodology</button>
                </div>
              </div>
              <div className="orchestration-mini">
                {['Task config', 'Queue', 'Free data', 'Quant engine', 'Ollama review', 'Evidence result'].map((stage, index) => (
                  <div key={stage}><span>{String(index + 1).padStart(2, '0')}</span><strong>{stage}</strong></div>
                ))}
              </div>
            </section>

            <section className="metric-grid">
              <Metric label="Active tasks" value={dashboard?.task_count ?? 0} detail="Reusable research mandates" />
              <Metric label="Runs in progress" value={dashboard?.active_run_count ?? 0} detail="Queued or executing" />
              <Metric label="Published runs" value={dashboard?.completed_run_count ?? 0} detail="Complete or partial packets" />
              <Metric label="Failed runs" value={dashboard?.failed_run_count ?? 0} detail="Visible, never silently hidden" />
            </section>

            <section className="section-block">
              <div className="section-heading">
                <div><span className="eyebrow">WORKSPACE</span><h2>Research tasks</h2></div>
                <button className="text-button" onClick={() => setView('tasks')}>View all →</button>
              </div>
              {tasks.length ? (
                <div className="task-grid">{tasks.slice(0, 4).map((task) => <TaskCard key={task.id} task={task} onOpen={openTask} onRun={runTask} busy={busy} />)}</div>
              ) : <EmptyState onCreate={() => setShowCreate(true)} />}
            </section>

            <section className="section-block">
              <div className="section-heading">
                <div><span className="eyebrow">AUDIT TRAIL</span><h2>Recent runs</h2></div>
                <button className="text-button" onClick={() => setView('runs')}>View history →</button>
              </div>
              <RunTable runs={runs.slice(0, 6)} tasks={tasks} onOpen={openRun} />
            </section>
          </>
        )}

        {view === 'tasks' && !selectedTask && (
          <section className="section-block">
            <div className="section-heading">
              <div><span className="eyebrow">VERSIONED MANDATES</span><h2>All research tasks</h2></div>
              <button className="primary" onClick={() => setShowCreate(true)}>+ New task</button>
            </div>
            {tasks.length ? (
              <div className="task-grid">{tasks.map((task) => <TaskCard key={task.id} task={task} onOpen={openTask} onRun={runTask} busy={busy} />)}</div>
            ) : <EmptyState onCreate={() => setShowCreate(true)} />}
          </section>
        )}

        {view === 'tasks' && selectedTask && (
          <TaskWorkspace
            task={selectedTask}
            runs={runs.filter((run) => run.task_id === selectedTask.id)}
            onBack={() => setSelectedTaskId(null)}
            onRun={runTask}
            onOpenRun={openRun}
            busy={busy}
          />
        )}

        {view === 'runs' && !selectedRunId && (
          <section className="section-block">
            <div className="section-heading">
              <div><span className="eyebrow">IMMUTABLE EXECUTION HISTORY</span><h2>All task runs</h2></div>
            </div>
            <RunTable runs={runs} tasks={tasks} onOpen={openRun} />
          </section>
        )}

        {view === 'runs' && selectedRunId && (
          <RunWorkspace
            run={runDetail}
            task={selectedTask}
            analyses={analyses}
            analysis={analysis}
            selectedTicker={selectedTicker}
            onTicker={setSelectedTicker}
            onBack={() => setSelectedRunId(null)}
          />
        )}

        {view === 'methodology' && <Methodology />}
        {view === 'settings' && <Settings />}
      </main>

      {showCreate && (
        <div className="modal-backdrop" role="presentation" onMouseDown={() => !busy && setShowCreate(false)}>
          <form className="task-modal" onSubmit={submitTask} onMouseDown={(event) => event.stopPropagation()}>
            <div className="modal-heading">
              <div><span className="eyebrow">NEW RESEARCH MANDATE</span><h2>Create research task</h2></div>
              <button type="button" className="close" onClick={() => setShowCreate(false)}>×</button>
            </div>
            <label>Task name<input required maxLength={100} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label>
            <label>Investment thesis<textarea required rows={4} maxLength={1200} value={form.thesis} onChange={(event) => setForm({ ...form, thesis: event.target.value })} /></label>
            <label>IDX tickers <small>Up to 10, separated by commas</small><input required value={tickerText} onChange={(event) => setTickerText(event.target.value.toUpperCase())} placeholder="BBCA, BBRI, TLKM" /></label>
            <div className="form-row">
              <label>Horizon (days)<input type="number" min={5} max={730} value={form.horizon_days} onChange={(event) => setForm({ ...form, horizon_days: Number(event.target.value) })} /></label>
              <label>Capital context (IDR)<input inputMode="numeric" value={form.capital_idr} onChange={(event) => setForm({ ...form, capital_idr: event.target.value })} /></label>
            </div>
            <div className="module-list">
              {['technical', 'fundamental', 'liquidity', 'scenario', 'evidence', 'ai_review'].map((module) => (
                <span key={module}>{module.replace('_', ' ')}</span>
              ))}
            </div>
            <p className="form-note">Runs are manual in v0.2.0. The task contract already preserves cadence metadata for a later scheduler without changing the analysis engine.</p>
            <div className="modal-actions">
              <button type="button" className="secondary" onClick={() => setShowCreate(false)}>Cancel</button>
              <button type="submit" className="primary" disabled={busy}>{busy ? 'Creating...' : 'Create task'}</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value, detail }: { label: string; value: number; detail: string }) {
  return <article className="metric-card"><small>{label}</small><strong>{value}</strong><span>{detail}</span></article>;
}

function EmptyState({ onCreate }: { onCreate: () => void }) {
  return <div className="empty"><strong>No research tasks yet</strong><p>Create a reusable IDX research mandate, then run it whenever you need a fresh evidence packet.</p><button className="primary" onClick={onCreate}>Create first task</button></div>;
}

function TaskCard({ task, onOpen, onRun, busy }: { task: Task; onOpen: (task: Task) => void; onRun: (task: Task) => void; busy: boolean }) {
  const latest = task.latest_run;
  return (
    <article className="task-card">
      <div className="task-card-top">
        <span className="config-badge">CONFIG v{task.config_version}</span>
        <span className={`status ${statusTone(latest?.status)}`}>{latest?.status || 'NOT RUN'}</span>
      </div>
      <button className="task-title" onClick={() => onOpen(task)}>{task.name}</button>
      <p>{task.thesis}</p>
      <div className="ticker-row">{task.tickers.map((ticker) => <span key={ticker}>{ticker.replace('.JK', '')}</span>)}</div>
      {latest && isActive(latest.status) && <Progress value={latest.progress} label={latest.message} />}
      <div className="task-meta"><span>{task.horizon_days} day horizon</span><span>{task.tickers.length} stocks</span><span>{date(task.created_at)}</span></div>
      <div className="card-actions">
        <button className="secondary" onClick={() => onOpen(task)}>Open task</button>
        <button className="primary" disabled={busy || isActive(latest?.status)} onClick={() => onRun(task)}>{isActive(latest?.status) ? 'Running...' : 'Run now'}</button>
      </div>
    </article>
  );
}

function Progress({ value, label }: { value: number; label: string }) {
  return <div className="progress-wrap"><div className="progress-label"><span>{label}</span><strong>{value}%</strong></div><div className="progress-track"><i style={{ width: `${value}%` }} /></div></div>;
}

function RunTable({ runs, tasks, onOpen }: { runs: Run[]; tasks: Task[]; onOpen: (run: Run) => void }) {
  if (!runs.length) return <div className="empty compact"><strong>No runs yet</strong><p>Run a research task to create the first immutable result.</p></div>;
  return (
    <div className="run-table">
      <div className="run-row header"><span>Run</span><span>Task</span><span>Status</span><span>Stage</span><span>Created</span><span /></div>
      {runs.map((run) => {
        const task = tasks.find((item) => item.id === run.task_id);
        return <div className="run-row" key={run.id}><code>{shortId(run.id)}</code><strong>{task?.name || shortId(run.task_id)}</strong><span className={`status ${statusTone(run.status)}`}>{run.status}</span><span>{run.stage} · {run.progress}%</span><span>{date(run.created_at)}</span><button className="text-button" onClick={() => onOpen(run)}>Inspect →</button></div>;
      })}
    </div>
  );
}

function TaskWorkspace({ task, runs, onBack, onRun, onOpenRun, busy }: { task: Task; runs: Run[]; onBack: () => void; onRun: (task: Task) => void; onOpenRun: (run: Run) => void; busy: boolean }) {
  return (
    <>
      <button className="back" onClick={onBack}>← All tasks</button>
      <section className="task-hero">
        <div><span className="eyebrow">RESEARCH TASK · CONFIG v{task.config_version}</span><h2>{task.name}</h2><p>{task.thesis}</p><div className="ticker-row">{task.tickers.map((ticker) => <span key={ticker}>{ticker}</span>)}</div></div>
        <button className="primary large" disabled={busy || isActive(task.latest_run?.status)} onClick={() => onRun(task)}>{isActive(task.latest_run?.status) ? 'Run in progress' : 'Run saved methodology'}</button>
      </section>
      <section className="task-detail-grid">
        <article className="panel"><span className="eyebrow">TASK CONTRACT</span><h3>Configuration</h3><dl><div><dt>Universe</dt><dd>{task.tickers.length} IDX ticker(s)</dd></div><div><dt>Horizon</dt><dd>{task.horizon_days} days</dd></div><div><dt>Capital context</dt><dd>Rp {Number(task.capital_idr).toLocaleString('id-ID')}</dd></div><div><dt>Cadence</dt><dd>{task.cadence}</dd></div><div><dt>Config hash</dt><dd><code>{task.config_hash.slice(0, 20)}…</code></dd></div></dl></article>
        <article className="panel"><span className="eyebrow">PIPELINE</span><h3>Enabled modules</h3><div className="module-list">{task.analysis_modules.map((module) => <span key={module}>{module.replace('_', ' ')}</span>)}</div><p className="small-copy">Numeric outputs and research actions come from deterministic code. Ollama only reviews and explains the evidence packet.</p></article>
      </section>
      <section className="section-block"><div className="section-heading"><div><span className="eyebrow">TASK HISTORY</span><h2>Runs for this task</h2></div></div><RunTable runs={runs} tasks={[task]} onOpen={onOpenRun} /></section>
    </>
  );
}

function RunWorkspace({ run, task, analyses, analysis, selectedTicker, onTicker, onBack }: { run: Run | null; task: Task | null; analyses: any[]; analysis: any; selectedTicker: string | null; onTicker: (ticker: string) => void; onBack: () => void }) {
  if (!run) return <div className="empty"><strong>Loading run...</strong></div>;
  return (
    <>
      <button className="back" onClick={onBack}>← Run history</button>
      <section className="run-hero">
        <div><span className="eyebrow">RUN {shortId(run.id)} · {task?.name || shortId(run.task_id)}</span><h2>{run.status}</h2><p>{run.message}</p></div>
        <span className={`status large-status ${statusTone(run.status)}`}>{run.stage}</span>
      </section>
      <Progress value={run.progress} label={run.message} />
      {isActive(run.status) && <EventTimeline events={run.events || []} />}
      {run.status === 'FAILED' && <div className="error-card"><strong>Run failed</strong><p>{run.error}</p></div>}
      {(run.status === 'COMPLETED' || run.status === 'PARTIAL') && (
        <>
          <section className="metric-grid three">
            <Metric label="Completed symbols" value={run.result?.summary?.completed_symbols || 0} detail={`of ${run.result?.summary?.requested_symbols || 0} requested`} />
            <Metric label="Average confidence" value={Math.round(run.result?.summary?.average_confidence || 0)} detail="Across completed analyses" />
            <Metric label="Evidence packet" value={analyses.reduce((total, item) => total + (item.evidence?.length || 0), 0)} detail="Traceable source records" />
          </section>
          <div className="ticker-tabs">{analyses.map((item) => <button key={item.ticker} className={selectedTicker === item.ticker ? 'active' : ''} onClick={() => onTicker(item.ticker)}>{item.ticker}<small>{item.research_action}</small></button>)}</div>
          {analysis && <AnalysisResult analysis={analysis} bundleHash={run.result?.bundle_hash} />}
          <EventTimeline events={run.events || []} />
        </>
      )}
    </>
  );
}

function EventTimeline({ events }: { events: Array<{ stage: string; progress: number; message: string; created_at: string }> }) {
  return <section className="timeline panel"><div className="section-heading"><div><span className="eyebrow">ORCHESTRATION TRACE</span><h3>Run events</h3></div></div><div className="event-list">{events.map((event, index) => <div className="event" key={`${event.created_at}-${index}`}><span>{event.progress}%</span><div><strong>{event.stage.replace('_', ' ')}</strong><p>{event.message}</p></div><small>{date(event.created_at)}</small></div>)}</div></section>;
}

function AnalysisResult({ analysis, bundleHash }: { analysis: any; bundleHash?: string }) {
  return (
    <div className="analysis-stack">
      <section className="result-grid">
        <article className="result-card accent"><span className="eyebrow">RESEARCH ACTION</span><h2>{analysis.research_action}</h2><strong className="ticker-big">{analysis.ticker}</strong><p>{analysis.policy_reasons?.join(' ')}</p></article>
        <article className="result-card"><span className="eyebrow">PRICE / RETURN</span><h2>{idr(analysis.technicals?.last_close)}</h2><div className="row-metric"><span>Expected return</span><strong>{pct(analysis.scenario_analysis?.expected_return)}</strong></div><div className="row-metric"><span>Bear downside</span><strong>{pct(analysis.scenario_analysis?.bear_downside)}</strong></div></article>
        <article className="result-card"><span className="eyebrow">CONFIDENCE</span><h2>{score(analysis.scores?.confidence)} / 100</h2><div className="row-metric"><span>Evidence</span><strong>{score(analysis.scores?.evidence_completeness)}%</strong></div><div className="row-metric"><span>Liquidity</span><strong>{score(analysis.scores?.liquidity)}</strong></div></article>
      </section>
      <section className="panel"><div className="section-heading"><div><span className="eyebrow">PROBABILITY-WEIGHTED OUTLOOK</span><h3>Bear · Base · Bull</h3></div></div><div className="scenario-grid">{analysis.scenario_analysis?.scenarios?.map((scenario: any) => <div className="scenario" key={scenario.name}><span>{scenario.name}</span><strong>{idr(scenario.target_price)}</strong><small>{pct(scenario.return)} return · {pct(scenario.probability)} probability</small></div>)}</div></section>
      <section className="task-detail-grid">
        <article className="panel"><span className="eyebrow">DETERMINISTIC ENGINE</span><h3>Scorecard</h3><dl><div><dt>Technical</dt><dd>{score(analysis.scores?.technical)}</dd></div><div><dt>Fundamental</dt><dd>{score(analysis.scores?.fundamental)}</dd></div><div><dt>RSI 14</dt><dd>{score(analysis.technicals?.rsi14)}</dd></div><div><dt>20-day return</dt><dd>{pct(analysis.technicals?.return_20d)}</dd></div><div><dt>1-year drawdown</dt><dd>{pct(analysis.technicals?.max_drawdown_1y)}</dd></div></dl></article>
        <article className="panel"><span className="eyebrow">LOCAL OLLAMA REVIEW</span><h3>{analysis.ai_review?.status || 'Unavailable'}</h3><p>{analysis.ai_review?.summary}</p><small>{analysis.ai_review?.provider} · {analysis.ai_review?.model}</small>{analysis.ai_review?.key_risks?.length ? <><h4>Key risks</h4><ul>{analysis.ai_review.key_risks.map((risk: string) => <li key={risk}>{risk}</li>)}</ul></> : null}</article>
      </section>
      <section className="panel"><div className="section-heading"><div><span className="eyebrow">SOURCE LINEAGE</span><h3>Evidence ledger</h3></div></div>{analysis.evidence?.map((item: any) => <div className="evidence-row" key={item.content_hash}><div><strong>{item.evidence_type}</strong><span>{item.source_name}</span></div><a href={item.source_uri} target="_blank" rel="noreferrer">Open source ↗</a><code>{item.content_hash}</code></div>)}<div className="hashes"><span>Analysis hash <code>{analysis.deterministic_hash}</code></span>{bundleHash && <span>Run bundle <code>{bundleHash}</code></span>}</div></section>
    </div>
  );
}

function Methodology() {
  return (
    <div className="method-grid">
      <section className="hero-banner compact-hero"><div><span className="eyebrow">INDONESIAN MARKET METHOD</span><h2>Evidence first, deterministic decision, local AI explanation.</h2><p>BuktiSaham applies the same saved method on every run so changes in results come from changed evidence, not an invisible prompt.</p></div></section>
      {[['1', 'IDX universe and free EOD data', 'Bare symbols such as BBCA are normalized to BBCA.JK. The MVP uses yfinance only and never falls back to a paid API.'], ['2', 'Deterministic quality checks', 'Freshness, history length, fundamental availability, liquidity, volatility, and drawdown are calculated before a recommendation can pass.'], ['3', 'Indonesia-oriented scorecard', 'Technical, fundamental, liquidity, and evidence-completeness scores feed explicit policy thresholds. Missing evidence lowers confidence.'], ['4', 'Bear, Base, and Bull scenarios', 'Scenario prices and probabilities are generated from the observed market record and the task horizon; they remain scenarios, not promises.'], ['5', 'Policy action', 'BUY_RESEARCH, HOLD_RESEARCH, SELL_RESEARCH, or WATCH is decided by code. Hard gates prevent a persuasive narrative from bypassing risk controls.'], ['6', 'Local Ollama evidence review', 'Ollama summarizes drivers, risks, contradictions, and review questions. It cannot alter prices, scores, scenarios, or the final action.']].map(([number, title, copy]) => <article className="method-card" key={number}><span>{number}</span><div><h3>{title}</h3><p>{copy}</p></div></article>)}
    </div>
  );
}

function Settings() {
  return <section className="settings-grid"><article className="panel"><span className="eyebrow">DATA POLICY</span><h3>Free-only market data</h3><dl><div><dt>Provider</dt><dd>yfinance</dd></div><div><dt>IDX suffix</dt><dd>.JK</dd></div><div><dt>Paid fallback</dt><dd>Disabled</dd></div><div><dt>Intended use</dt><dd>EOD research</dd></div></dl></article><article className="panel"><span className="eyebrow">AI POLICY</span><h3>Local review only</h3><dl><div><dt>Provider</dt><dd>Ollama</dd></div><div><dt>Authority</dt><dd>Explanation only</dd></div><div><dt>Default model</dt><dd>qwen3:8b</dd></div><div><dt>Cloud API key</dt><dd>Not required</dd></div></dl></article><article className="panel full"><span className="eyebrow">PRODUCT BOUNDARY</span><h3>Decision support, not trade execution</h3><p>BuktiSaham does not connect to a broker, place orders, guarantee outcomes, or provide individualized regulated financial advice. Every recommendation is a research action backed by a versioned task configuration and an auditable evidence packet.</p></article></section>;
}
