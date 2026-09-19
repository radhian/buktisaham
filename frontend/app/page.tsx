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
import {
  Language,
  TranslationKey,
  localizeAction,
  localizeModule,
  localizeRunMessage,
  localizeStage,
  localizeStatus,
  translate,
} from '../lib/i18n';

type T = (key: TranslationKey, values?: Record<string, string | number>) => string;

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

function date(value: string | null | undefined, language: Language) {
  if (!value) return language === 'id' ? 'Tidak tersedia' : 'Not available';
  return new Date(value).toLocaleString(language === 'id' ? 'id-ID' : 'en-GB', {
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
  const [language, setLanguage] = useState<Language>('en');
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
  const [notice, setNotice] = useState('');
  const t: T = (key, values) => translate(language, key, values);

  const selectedTask = useMemo(
    () => tasks.find((task) => task.id === selectedTaskId) || null,
    [tasks, selectedTaskId],
  );

  useEffect(() => {
    const saved = window.localStorage.getItem('buktisaham-language');
    if (saved === 'en' || saved === 'id') setLanguage(saved);
  }, []);

  useEffect(() => {
    window.localStorage.setItem('buktisaham-language', language);
    document.documentElement.lang = language;
  }, [language]);

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
      setNotice(t('refreshError', { message: error.message }));
    }
  }

  useEffect(() => {
    refreshWorkspace();
    const timer = window.setInterval(refreshWorkspace, 5000);
    return () => window.clearInterval(timer);
  }, [language]);

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
        if (!cancelled) setNotice(t('loadRunError', { message: error.message }));
      }
    }
    loadRun();
    const timer = window.setInterval(loadRun, 2500);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [selectedRunId, selectedTicker, language]);

  async function submitTask(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      const tickers = tickerText
        .split(/[\s,]+/)
        .map((item) => item.trim().toUpperCase())
        .filter(Boolean);
      const created = await createTask({ ...form, tickers });
      setNotice(t('createdTask', { name: created.name }));
      setShowCreate(false);
      setSelectedTaskId(created.id);
      setView('tasks');
      await refreshWorkspace();
    } catch (error: any) {
      setNotice(t('createFailed', { message: error.message }));
    } finally {
      setBusy(false);
    }
  }

  async function runTask(task: Task) {
    setBusy(true);
    try {
      setNotice(t('queueing', { name: task.name }));
      const run = await startRun(task.id);
      setSelectedTaskId(task.id);
      setSelectedRunId(run.id);
      setRunDetail(run);
      setView('runs');
      setNotice(t('queuedNotice'));
      await refreshWorkspace();
    } catch (error: any) {
      setNotice(t('startFailed', { message: error.message }));
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
          <span><strong>BuktiSaham</strong><small>{t('brandSubtitle')}</small></span>
        </button>
        <nav>
          {[
            ['dashboard', t('overview'), '01'],
            ['tasks', t('researchTasks'), '02'],
            ['runs', t('runHistory'), '03'],
            ['methodology', t('methodology'), '04'],
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
          <strong>{t('localFirst')}</strong>
          <small>{t('localFirstCopy')}</small>
        </div>
        <button className={`settings-link ${view === 'settings' ? 'active' : ''}`} onClick={() => setView('settings')}>
          <span>05</span>{t('settings')}
        </button>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">{t('pageEyebrow')}</span>
            <h1>{view === 'dashboard' ? t('dashboardTitle') : view === 'tasks' ? t('tasksTitle') : view === 'runs' ? t('runsTitle') : view === 'methodology' ? t('methodologyTitle') : t('settingsTitle')}</h1>
          </div>
          <div className="top-actions">
            <span className="policy-chip">{t('freeDataOnly')}</span>
            <button className="primary" onClick={() => setShowCreate(true)}>{t('newTask')}</button>
          </div>
        </header>

        <div className="notice"><span className="signal-dot" />{notice || t('ready')}</div>

        {view === 'dashboard' && (
          <>
            <section className="hero-banner">
              <div>
                <span className="eyebrow">{t('repeatableEyebrow')}</span>
                <h2>{t('heroTitle')}</h2>
                <p>{t('heroCopy')}</p>
                <div className="hero-actions">
                  <button className="primary" onClick={() => setShowCreate(true)}>{t('createResearchTask')}</button>
                  <button className="secondary" onClick={() => setView('methodology')}>{t('reviewMethodology')}</button>
                </div>
              </div>
              <div className="orchestration-mini">
                {[t('taskConfig'), t('queue'), t('freeData'), t('quantEngine'), t('ollamaReview'), t('evidenceResult')].map((stage, index) => (
                  <div key={stage}><span>{String(index + 1).padStart(2, '0')}</span><strong>{stage}</strong></div>
                ))}
              </div>
            </section>

            <section className="metric-grid">
              <Metric label={t('activeTasks')} value={dashboard?.task_count ?? 0} detail={t('activeTasksDetail')} />
              <Metric label={t('runsInProgress')} value={dashboard?.active_run_count ?? 0} detail={t('runsInProgressDetail')} />
              <Metric label={t('publishedRuns')} value={dashboard?.completed_run_count ?? 0} detail={t('publishedRunsDetail')} />
              <Metric label={t('failedRuns')} value={dashboard?.failed_run_count ?? 0} detail={t('failedRunsDetail')} />
            </section>

            <section className="section-block">
              <div className="section-heading">
                <div><span className="eyebrow">{t('workspace')}</span><h2>{t('researchTasks')}</h2></div>
                <button className="text-button" onClick={() => setView('tasks')}>{t('viewAll')}</button>
              </div>
              {tasks.length ? (
                <div className="task-grid">{tasks.slice(0, 4).map((task) => <TaskCard key={task.id} task={task} onOpen={openTask} onRun={runTask} busy={busy} language={language} t={t} />)}</div>
              ) : <EmptyState onCreate={() => setShowCreate(true)} t={t} />}
            </section>

            <section className="section-block">
              <div className="section-heading">
                <div><span className="eyebrow">{t('auditTrail')}</span><h2>{t('recentRuns')}</h2></div>
                <button className="text-button" onClick={() => setView('runs')}>{t('viewHistory')}</button>
              </div>
              <RunTable runs={runs.slice(0, 6)} tasks={tasks} onOpen={openRun} language={language} t={t} />
            </section>
          </>
        )}

        {view === 'tasks' && !selectedTask && (
          <section className="section-block">
            <div className="section-heading">
              <div><span className="eyebrow">{t('versionedMandates')}</span><h2>{t('allResearchTasks')}</h2></div>
              <button className="primary" onClick={() => setShowCreate(true)}>{t('newTask')}</button>
            </div>
            {tasks.length ? (
              <div className="task-grid">{tasks.map((task) => <TaskCard key={task.id} task={task} onOpen={openTask} onRun={runTask} busy={busy} language={language} t={t} />)}</div>
            ) : <EmptyState onCreate={() => setShowCreate(true)} t={t} />}
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
            language={language}
            t={t}
          />
        )}

        {view === 'runs' && !selectedRunId && (
          <section className="section-block">
            <div className="section-heading">
              <div><span className="eyebrow">{t('immutableHistory')}</span><h2>{t('allTaskRuns')}</h2></div>
            </div>
            <RunTable runs={runs} tasks={tasks} onOpen={openRun} language={language} t={t} />
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
            language={language}
            t={t}
          />
        )}

        {view === 'methodology' && <Methodology t={t} />}
        {view === 'settings' && <Settings language={language} onLanguage={setLanguage} t={t} />}
      </main>

      {showCreate && (
        <div className="modal-backdrop" role="presentation" onMouseDown={() => !busy && setShowCreate(false)}>
          <form className="task-modal" onSubmit={submitTask} onMouseDown={(event) => event.stopPropagation()}>
            <div className="modal-heading">
              <div><span className="eyebrow">{t('newMandate')}</span><h2>{t('createResearchTask')}</h2></div>
              <button type="button" className="close" onClick={() => setShowCreate(false)}>×</button>
            </div>
            <label>{t('taskName')}<input required maxLength={100} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label>
            <label>{t('investmentThesis')}<textarea required rows={4} maxLength={1200} value={form.thesis} onChange={(event) => setForm({ ...form, thesis: event.target.value })} /></label>
            <label>{t('idxTickers')} <small>{t('upToTen')}</small><input required value={tickerText} onChange={(event) => setTickerText(event.target.value.toUpperCase())} placeholder="BBCA, BBRI, TLKM" /></label>
            <div className="form-row">
              <label>{t('horizonDays')}<input type="number" min={5} max={730} value={form.horizon_days} onChange={(event) => setForm({ ...form, horizon_days: Number(event.target.value) })} /></label>
              <label>{t('capitalIdr')}<input inputMode="numeric" value={form.capital_idr} onChange={(event) => setForm({ ...form, capital_idr: event.target.value })} /></label>
            </div>
            <div className="module-list">
              {['technical', 'fundamental', 'liquidity', 'scenario', 'evidence', 'ai_review'].map((module) => (
                <span key={module}>{localizeModule(module, language)}</span>
              ))}
            </div>
            <p className="form-note">{t('manualNote')}</p>
            <div className="modal-actions">
              <button type="button" className="secondary" onClick={() => setShowCreate(false)}>{t('cancel')}</button>
              <button type="submit" className="primary" disabled={busy}>{busy ? t('creating') : t('createTask')}</button>
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

function EmptyState({ onCreate, t }: { onCreate: () => void; t: T }) {
  return <div className="empty"><strong>{t('noTasks')}</strong><p>{t('noTasksCopy')}</p><button className="primary" onClick={onCreate}>{t('createFirstTask')}</button></div>;
}

function TaskCard({ task, onOpen, onRun, busy, language, t }: { task: Task; onOpen: (task: Task) => void; onRun: (task: Task) => void; busy: boolean; language: Language; t: T }) {
  const latest = task.latest_run;
  return (
    <article className="task-card">
      <div className="task-card-top">
        <span className="config-badge">{t('config')} v{task.config_version}</span>
        <span className={`status ${statusTone(latest?.status)}`}>{latest?.status ? localizeStatus(latest.status, language) : t('notRun')}</span>
      </div>
      <button className="task-title" onClick={() => onOpen(task)}>{task.name}</button>
      <p>{task.thesis}</p>
      <div className="ticker-row">{task.tickers.map((ticker) => <span key={ticker}>{ticker.replace('.JK', '')}</span>)}</div>
      {latest && isActive(latest.status) && <Progress value={latest.progress} label={localizeRunMessage(latest.message, language)} />}
      <div className="task-meta"><span>{t('dayHorizon', { count: task.horizon_days })}</span><span>{t('stocks', { count: task.tickers.length })}</span><span>{date(task.created_at, language)}</span></div>
      <div className="card-actions">
        <button className="secondary" onClick={() => onOpen(task)}>{t('openTask')}</button>
        <button className="primary" disabled={busy || isActive(latest?.status)} onClick={() => onRun(task)}>{isActive(latest?.status) ? t('running') : t('runNow')}</button>
      </div>
    </article>
  );
}

function Progress({ value, label }: { value: number; label: string }) {
  return <div className="progress-wrap"><div className="progress-label"><span>{label}</span><strong>{value}%</strong></div><div className="progress-track"><i style={{ width: `${value}%` }} /></div></div>;
}

function RunTable({ runs, tasks, onOpen, language, t }: { runs: Run[]; tasks: Task[]; onOpen: (run: Run) => void; language: Language; t: T }) {
  if (!runs.length) return <div className="empty compact"><strong>{t('noRuns')}</strong><p>{t('noRunsCopy')}</p></div>;
  return (
    <div className="run-table">
      <div className="run-row header"><span>{t('tableRun')}</span><span>{t('tableTask')}</span><span>{t('tableStatus')}</span><span>{t('tableStage')}</span><span>{t('tableCreated')}</span><span /></div>
      {runs.map((run) => {
        const task = tasks.find((item) => item.id === run.task_id);
        return <div className="run-row" key={run.id}><code>{shortId(run.id)}</code><strong>{task?.name || shortId(run.task_id)}</strong><span className={`status ${statusTone(run.status)}`}>{localizeStatus(run.status, language)}</span><span>{localizeStage(run.stage, language)} · {run.progress}%</span><span>{date(run.created_at, language)}</span><button className="text-button" onClick={() => onOpen(run)}>{t('inspect')}</button></div>;
      })}
    </div>
  );
}

function TaskWorkspace({ task, runs, onBack, onRun, onOpenRun, busy, language, t }: { task: Task; runs: Run[]; onBack: () => void; onRun: (task: Task) => void; onOpenRun: (run: Run) => void; busy: boolean; language: Language; t: T }) {
  return (
    <>
      <button className="back" onClick={onBack}>{t('allTasks')}</button>
      <section className="task-hero">
        <div><span className="eyebrow">{t('researchTaskConfig', { version: task.config_version })}</span><h2>{task.name}</h2><p>{task.thesis}</p><div className="ticker-row">{task.tickers.map((ticker) => <span key={ticker}>{ticker}</span>)}</div></div>
        <button className="primary large" disabled={busy || isActive(task.latest_run?.status)} onClick={() => onRun(task)}>{isActive(task.latest_run?.status) ? t('runInProgress') : t('runSavedMethod')}</button>
      </section>
      <section className="task-detail-grid">
        <article className="panel"><span className="eyebrow">{t('taskContract')}</span><h3>{t('configuration')}</h3><dl><div><dt>{t('universe')}</dt><dd>{t('idxTickerCount', { count: task.tickers.length })}</dd></div><div><dt>{t('horizon')}</dt><dd>{t('days', { count: task.horizon_days })}</dd></div><div><dt>{t('capitalContext')}</dt><dd>Rp {Number(task.capital_idr).toLocaleString('id-ID')}</dd></div><div><dt>{t('cadence')}</dt><dd>{task.cadence}</dd></div><div><dt>{t('configHash')}</dt><dd><code>{task.config_hash.slice(0, 20)}…</code></dd></div></dl></article>
        <article className="panel"><span className="eyebrow">{t('pipeline')}</span><h3>{t('enabledModules')}</h3><div className="module-list">{task.analysis_modules.map((module) => <span key={module}>{localizeModule(module, language)}</span>)}</div><p className="small-copy">{t('authorityCopy')}</p></article>
      </section>
      <section className="section-block"><div className="section-heading"><div><span className="eyebrow">{t('taskHistory')}</span><h2>{t('runsForTask')}</h2></div></div><RunTable runs={runs} tasks={[task]} onOpen={onOpenRun} language={language} t={t} /></section>
    </>
  );
}

function RunWorkspace({ run, task, analyses, analysis, selectedTicker, onTicker, onBack, language, t }: { run: Run | null; task: Task | null; analyses: any[]; analysis: any; selectedTicker: string | null; onTicker: (ticker: string) => void; onBack: () => void; language: Language; t: T }) {
  if (!run) return <div className="empty"><strong>{t('loadingRun')}</strong></div>;
  return (
    <>
      <button className="back" onClick={onBack}>{t('backRunHistory')}</button>
      <section className="run-hero">
        <div><span className="eyebrow">{t('tableRun').toUpperCase()} {shortId(run.id)} · {task?.name || shortId(run.task_id)}</span><h2>{localizeStatus(run.status, language)}</h2><p>{localizeRunMessage(run.message, language)}</p></div>
        <span className={`status large-status ${statusTone(run.status)}`}>{localizeStage(run.stage, language)}</span>
      </section>
      <Progress value={run.progress} label={localizeRunMessage(run.message, language)} />
      {isActive(run.status) && <EventTimeline events={run.events || []} language={language} t={t} />}
      {run.status === 'FAILED' && <div className="error-card"><strong>{t('runFailed')}</strong><p>{run.error}</p></div>}
      {(run.status === 'COMPLETED' || run.status === 'PARTIAL') && (
        <>
          <section className="metric-grid three">
            <Metric label={t('completedSymbols')} value={run.result?.summary?.completed_symbols || 0} detail={t('ofRequested', { count: run.result?.summary?.requested_symbols || 0 })} />
            <Metric label={t('averageConfidence')} value={Math.round(run.result?.summary?.average_confidence || 0)} detail={t('acrossAnalyses')} />
            <Metric label={t('evidencePacket')} value={analyses.reduce((total, item) => total + (item.evidence?.length || 0), 0)} detail={t('traceableRecords')} />
          </section>
          <div className="ticker-tabs">{analyses.map((item) => <button key={item.ticker} className={selectedTicker === item.ticker ? 'active' : ''} onClick={() => onTicker(item.ticker)}>{item.ticker}<small>{localizeAction(item.research_action, language)}</small></button>)}</div>
          {analysis && <AnalysisResult analysis={analysis} bundleHash={run.result?.bundle_hash} language={language} t={t} />}
          <EventTimeline events={run.events || []} language={language} t={t} />
        </>
      )}
    </>
  );
}

function EventTimeline({ events, language, t }: { events: Array<{ stage: string; progress: number; message: string; created_at: string }>; language: Language; t: T }) {
  return <section className="timeline panel"><div className="section-heading"><div><span className="eyebrow">{t('orchestrationTrace')}</span><h3>{t('runEvents')}</h3></div></div><div className="event-list">{events.map((event, index) => <div className="event" key={`${event.created_at}-${index}`}><span>{event.progress}%</span><div><strong>{localizeStage(event.stage, language)}</strong><p>{localizeRunMessage(event.message, language)}</p></div><small>{date(event.created_at, language)}</small></div>)}</div></section>;
}

function AnalysisResult({ analysis, bundleHash, language, t }: { analysis: any; bundleHash?: string; language: Language; t: T }) {
  return (
    <div className="analysis-stack">
      <section className="result-grid">
        <article className="result-card accent"><span className="eyebrow">{t('researchAction')}</span><h2>{localizeAction(analysis.research_action, language)}</h2><strong className="ticker-big">{analysis.ticker}</strong><p>{analysis.policy_reasons?.join(' ')}</p></article>
        <article className="result-card"><span className="eyebrow">{t('priceReturn')}</span><h2>{idr(analysis.technicals?.last_close)}</h2><div className="row-metric"><span>{t('expectedReturn')}</span><strong>{pct(analysis.scenario_analysis?.expected_return)}</strong></div><div className="row-metric"><span>{t('bearDownside')}</span><strong>{pct(analysis.scenario_analysis?.bear_downside)}</strong></div></article>
        <article className="result-card"><span className="eyebrow">{t('confidence')}</span><h2>{score(analysis.scores?.confidence)} / 100</h2><div className="row-metric"><span>{t('evidence')}</span><strong>{score(analysis.scores?.evidence_completeness)}%</strong></div><div className="row-metric"><span>{t('liquidity')}</span><strong>{score(analysis.scores?.liquidity)}</strong></div></article>
      </section>
      <section className="panel"><div className="section-heading"><div><span className="eyebrow">{t('probabilityOutlook')}</span><h3>{t('bearBaseBull')}</h3></div></div><div className="scenario-grid">{analysis.scenario_analysis?.scenarios?.map((scenario: any) => <div className="scenario" key={scenario.name}><span>{scenario.name}</span><strong>{idr(scenario.target_price)}</strong><small>{t('returnProbability', { returnValue: pct(scenario.return), probability: pct(scenario.probability) })}</small></div>)}</div></section>
      <section className="task-detail-grid">
        <article className="panel"><span className="eyebrow">{t('deterministicEngine')}</span><h3>{t('scorecard')}</h3><dl><div><dt>{t('technical')}</dt><dd>{score(analysis.scores?.technical)}</dd></div><div><dt>{t('fundamental')}</dt><dd>{score(analysis.scores?.fundamental)}</dd></div><div><dt>{t('rsi14')}</dt><dd>{score(analysis.technicals?.rsi14)}</dd></div><div><dt>{t('return20d')}</dt><dd>{pct(analysis.technicals?.return_20d)}</dd></div><div><dt>{t('drawdown1y')}</dt><dd>{pct(analysis.technicals?.max_drawdown_1y)}</dd></div></dl></article>
        <article className="panel"><span className="eyebrow">{t('localReview')}</span><h3>{analysis.ai_review?.status || t('unavailable')}</h3><p>{analysis.ai_review?.summary}</p><small>{analysis.ai_review?.provider} · {analysis.ai_review?.model}</small>{analysis.ai_review?.key_risks?.length ? <><h4>{t('keyRisks')}</h4><ul>{analysis.ai_review.key_risks.map((risk: string) => <li key={risk}>{risk}</li>)}</ul></> : null}</article>
      </section>
      <section className="panel"><div className="section-heading"><div><span className="eyebrow">{t('sourceLineage')}</span><h3>{t('evidenceLedger')}</h3></div></div>{analysis.evidence?.map((item: any) => <div className="evidence-row" key={item.content_hash}><div><strong>{item.evidence_type}</strong><span>{item.source_name}</span></div><a href={item.source_uri} target="_blank" rel="noreferrer">{t('openSource')}</a><code>{item.content_hash}</code></div>)}<div className="hashes"><span>{t('analysisHash')} <code>{analysis.deterministic_hash}</code></span>{bundleHash && <span>{t('runBundle')} <code>{bundleHash}</code></span>}</div></section>
    </div>
  );
}

function Methodology({ t }: { t: T }) {
  return (
    <div className="method-grid">
      <section className="hero-banner compact-hero"><div><span className="eyebrow">{t('methodEyebrow')}</span><h2>{t('methodTitle')}</h2><p>{t('methodCopy')}</p></div></section>
      {[
        ['1', t('method1Title'), t('method1Copy')],
        ['2', t('method2Title'), t('method2Copy')],
        ['3', t('method3Title'), t('method3Copy')],
        ['4', t('method4Title'), t('method4Copy')],
        ['5', t('method5Title'), t('method5Copy')],
        ['6', t('method6Title'), t('method6Copy')],
      ].map(([number, title, copy]) => <article className="method-card" key={number}><span>{number}</span><div><h3>{title}</h3><p>{copy}</p></div></article>)}
    </div>
  );
}

function Settings({ language, onLanguage, t }: { language: Language; onLanguage: (language: Language) => void; t: T }) {
  return (
    <section className="settings-grid">
      <article className="panel full language-panel">
        <span className="eyebrow">{t('languagePolicy')}</span>
        <h3>{t('interfaceLanguage')}</h3>
        <p>{t('languageCopy')}</p>
        <div className="language-picker" role="group" aria-label={t('interfaceLanguage')}>
          <button type="button" className={language === 'en' ? 'active' : ''} aria-pressed={language === 'en'} onClick={() => onLanguage('en')}>EN <span>{t('english')}</span></button>
          <button type="button" className={language === 'id' ? 'active' : ''} aria-pressed={language === 'id'} onClick={() => onLanguage('id')}>ID <span>{t('bahasaIndonesia')}</span></button>
        </div>
        <small className="language-status"><span className="signal-dot" />{t('languageActive', { language: language === 'id' ? t('bahasaIndonesia') : t('english') })}</small>
      </article>
      <article className="panel"><span className="eyebrow">{t('dataPolicy')}</span><h3>{t('freeOnlyMarketData')}</h3><dl><div><dt>{t('provider')}</dt><dd>yfinance</dd></div><div><dt>{t('idxSuffix')}</dt><dd>.JK</dd></div><div><dt>{t('paidFallback')}</dt><dd>{t('disabled')}</dd></div><div><dt>{t('intendedUse')}</dt><dd>{t('eodResearch')}</dd></div></dl></article>
      <article className="panel"><span className="eyebrow">{t('aiPolicy')}</span><h3>{t('localReviewOnly')}</h3><dl><div><dt>{t('provider')}</dt><dd>Ollama</dd></div><div><dt>{t('authority')}</dt><dd>{t('explanationOnly')}</dd></div><div><dt>{t('defaultModel')}</dt><dd>qwen3:8b</dd></div><div><dt>{t('cloudKey')}</dt><dd>{t('notRequired')}</dd></div></dl></article>
      <article className="panel full"><span className="eyebrow">{t('productBoundary')}</span><h3>{t('decisionSupport')}</h3><p>{t('boundaryCopy')}</p></article>
    </section>
  );
}
