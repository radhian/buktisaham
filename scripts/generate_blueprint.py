#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = Path(__file__).resolve().parents[1] / "output" / "pdf" / "BuktiSaham_PRD_TRD_v2.0_Task_Orchestration.pdf"

NAVY = colors.HexColor("#071421")
NAVY_2 = colors.HexColor("#0D2438")
NAVY_3 = colors.HexColor("#143A52")
TEAL = colors.HexColor("#2CC8B7")
TEAL_LIGHT = colors.HexColor("#BFF8ED")
BLUE = colors.HexColor("#4C9FDB")
INK = colors.HexColor("#142638")
MUTED = colors.HexColor("#597187")
LIGHT = colors.HexColor("#F2F6F8")
LINE = colors.HexColor("#CBD9E2")
AMBER = colors.HexColor("#E5A83A")
RED = colors.HexColor("#D85D6C")
GREEN = colors.HexColor("#3F9D7C")
WHITE = colors.white


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverEyebrow", fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=TEAL, spaceAfter=8, tracking=1.4))
styles.add(ParagraphStyle(name="CoverTitle", fontName="Helvetica-Bold", fontSize=29, leading=33, textColor=WHITE, spaceAfter=14))
styles.add(ParagraphStyle(name="CoverSub", fontName="Helvetica", fontSize=12, leading=18, textColor=colors.HexColor("#C9D8E5"), spaceAfter=18))
styles.add(ParagraphStyle(name="H1x", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=NAVY_2, spaceAfter=10))
styles.add(ParagraphStyle(name="H2x", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=NAVY_3, spaceBefore=9, spaceAfter=6))
styles.add(ParagraphStyle(name="H3x", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=NAVY_3, spaceBefore=7, spaceAfter=4))
styles.add(ParagraphStyle(name="Bodyx", fontName="Helvetica", fontSize=8.8, leading=13.2, textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name="Smallx", fontName="Helvetica", fontSize=7.4, leading=10.6, textColor=MUTED, spaceAfter=4))
styles.add(ParagraphStyle(name="Callout", fontName="Helvetica-Bold", fontSize=9.2, leading=13.5, textColor=NAVY_2, backColor=TEAL_LIGHT, borderColor=TEAL, borderWidth=.6, borderPadding=9, spaceBefore=7, spaceAfter=9))
styles.add(ParagraphStyle(name="CodeBlock", fontName="Courier", fontSize=7.2, leading=10.2, textColor=colors.HexColor("#DDF6F1"), backColor=NAVY, borderPadding=8, spaceBefore=5, spaceAfter=8))
styles.add(ParagraphStyle(name="TableHead", fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=WHITE, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="TableCell", fontName="Helvetica", fontSize=7.2, leading=9.5, textColor=INK))
styles.add(ParagraphStyle(name="DiagramTitle", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=NAVY_3, alignment=TA_CENTER, spaceBefore=3, spaceAfter=5))


def P(text: str, style: str = "Bodyx") -> Paragraph:
    return Paragraph(text, styles[style])


def bullet(items: list[str]) -> Table:
    rows = [[P("•", "Bodyx"), P(item, "Bodyx")] for item in items]
    table = Table(rows, colWidths=[10, 470])
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    return table


def data_table(headers: list[str], rows: list[list[str]], widths: list[float] | None = None) -> Table:
    data = [[P(value, "TableHead") for value in headers]] + [[P(str(value), "TableCell") for value in row] for row in rows]
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY_2),
        ("GRID", (0, 0), (-1, -1), .45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def box(d: Drawing, x: float, y: float, w: float, h: float, label: str, fill=NAVY_2, stroke=NAVY_3, text=WHITE, size=8.2) -> None:
    d.add(Rect(x, y, w, h, rx=7, ry=7, fillColor=fill, strokeColor=stroke, strokeWidth=1))
    lines = label.split("\n")
    for idx, value in enumerate(lines):
        d.add(String(x + w / 2, y + h / 2 + (len(lines) - 1 - idx) * 10 - 3, value, fontName="Helvetica-Bold", fontSize=size, textAnchor="middle", fillColor=text))


def arrow(d: Drawing, x1: float, y1: float, x2: float, y2: float, color=MUTED) -> None:
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.2))
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 > x1 else -1
        d.add(Polygon([x2, y2, x2 - 6 * direction, y2 + 3, x2 - 6 * direction, y2 - 3], fillColor=color, strokeColor=color))
    else:
        direction = 1 if y2 > y1 else -1
        d.add(Polygon([x2, y2, x2 - 3, y2 - 6 * direction, x2 + 3, y2 - 6 * direction], fillColor=color, strokeColor=color))


def horizontal_flow(title: str, nodes: list[str], colorset: list | None = None) -> list:
    w, h = 500, 115
    d = Drawing(w, h)
    count = len(nodes)
    gap = 12
    bw = (w - gap * (count - 1)) / count
    y = 24
    for i, node in enumerate(nodes):
        x = i * (bw + gap)
        fill = colorset[i] if colorset else NAVY_2
        box(d, x, y, bw, 48, node, fill=fill)
        if i < count - 1:
            arrow(d, x + bw, y + 24, x + bw + gap - 2, y + 24)
    return [P(title, "DiagramTitle"), d]


def task_object_diagram() -> list:
    d = Drawing(500, 220)
    box(d, 185, 150, 130, 48, "Research Task", fill=NAVY)
    children = [(20, 50, "Config\nVersion"), (140, 50, "Task Run"), (260, 50, "Run Events"), (380, 50, "Evidence\nPacket")]
    for x, y, label in children:
        box(d, x, y, 100, 52, label, fill=NAVY_2)
        arrow(d, 250, 150, x + 50, y + 52)
    return [P("Figure 1. Product object model", "DiagramTitle"), d]


def state_diagram() -> list:
    d = Drawing(500, 210)
    box(d, 20, 125, 90, 42, "QUEUED", fill=BLUE)
    box(d, 205, 125, 90, 42, "RUNNING", fill=NAVY_2)
    box(d, 390, 155, 90, 36, "COMPLETED", fill=GREEN)
    box(d, 390, 95, 90, 36, "PARTIAL", fill=AMBER, text=NAVY)
    box(d, 390, 35, 90, 36, "FAILED", fill=RED)
    arrow(d, 110, 146, 205, 146)
    arrow(d, 295, 146, 390, 173)
    arrow(d, 295, 146, 390, 113)
    arrow(d, 295, 146, 390, 53)
    arrow(d, 110, 140, 390, 53)
    return [P("Figure 4. Run state machine", "DiagramTitle"), d]


def architecture_diagram() -> list:
    d = Drawing(500, 270)
    box(d, 185, 215, 130, 40, "Next.js Workspace", fill=BLUE)
    box(d, 185, 150, 130, 40, "FastAPI", fill=NAVY)
    box(d, 15, 75, 105, 42, "PostgreSQL", fill=NAVY_2)
    box(d, 145, 75, 105, 42, "Redis / RQ", fill=NAVY_2)
    box(d, 275, 75, 105, 42, "Research Worker", fill=NAVY_2)
    box(d, 395, 10, 95, 42, "Local Ollama", fill=GREEN)
    box(d, 275, 10, 95, 42, "Quant Engine", fill=TEAL, text=NAVY)
    box(d, 145, 10, 95, 42, "yfinance", fill=AMBER, text=NAVY)
    arrow(d, 250, 215, 250, 190)
    arrow(d, 185, 170, 120, 117)
    arrow(d, 230, 150, 198, 117)
    arrow(d, 270, 150, 327, 117)
    arrow(d, 275, 96, 240, 52)
    arrow(d, 327, 75, 322, 52)
    arrow(d, 380, 96, 442, 52)
    arrow(d, 275, 88, 120, 88)
    return [P("Figure 8. Runtime architecture", "DiagramTitle"), d]


def erd_diagram() -> list:
    d = Drawing(500, 250)
    box(d, 190, 188, 120, 42, "research_task", fill=NAVY)
    entities = [(10, 90, "task_config_version"), (135, 90, "task_run"), (260, 90, "run_event"), (385, 90, "evidence_item")]
    for x, y, label in entities:
        box(d, x, y, 105, 45, label, fill=NAVY_2, size=7.4)
        arrow(d, 250, 188, x + 52, y + 45)
    box(d, 135, 15, 105, 42, "recommendation_\nversion", fill=NAVY_3, size=7.2)
    arrow(d, 187, 90, 187, 57)
    return [P("Figure 10. Persistence model", "DiagramTitle"), d]


def authority_diagram() -> list:
    d = Drawing(500, 220)
    box(d, 20, 145, 135, 48, "Evidence Inputs", fill=BLUE)
    box(d, 185, 145, 135, 48, "Deterministic Engine", fill=NAVY)
    box(d, 350, 145, 130, 48, "Research Action", fill=TEAL, text=NAVY)
    box(d, 185, 45, 135, 48, "Local Ollama", fill=GREEN)
    box(d, 350, 45, 130, 48, "Narrative Review", fill=NAVY_3)
    arrow(d, 155, 169, 185, 169)
    arrow(d, 320, 169, 350, 169)
    arrow(d, 252, 145, 252, 93)
    arrow(d, 320, 69, 350, 69)
    d.add(Line(415, 93, 415, 145, strokeColor=RED, strokeWidth=2, strokeDashArray=[4, 3]))
    d.add(String(423, 116, "NO WRITE AUTHORITY", fontName="Helvetica-Bold", fontSize=6.5, fillColor=RED))
    return [P("Figure 7. AI authority boundary", "DiagramTitle"), d]


def sequence_diagram() -> list:
    d = Drawing(500, 260)
    actors = [(30, "User"), (145, "API"), (260, "Queue"), (375, "Worker"), (465, "Data/AI")]
    for x, label in actors:
        box(d, x - 34, 215, 68, 32, label, fill=NAVY_2, size=7.2)
        d.add(Line(x, 25, x, 215, strokeColor=LINE, strokeWidth=.8, strokeDashArray=[3, 3]))
    messages = [(30, 145, 190, "Start task"), (145, 260, 160, "Enqueue snapshot"), (260, 375, 130, "Execute"), (375, 465, 100, "Collect + review"), (375, 145, 70, "Persist packet/events"), (145, 30, 40, "Poll result")]
    for x1, x2, y, label in messages:
        arrow(d, x1, y, x2, y, color=NAVY_3)
        d.add(String((x1 + x2) / 2, y + 5, label, fontName="Helvetica", fontSize=6.5, textAnchor="middle", fillColor=INK))
    return [P("Figure 11. Run execution sequence", "DiagramTitle"), d]


def trust_diagram() -> list:
    d = Drawing(500, 240)
    d.add(Rect(5, 20, 490, 200, rx=10, ry=10, fillColor=LIGHT, strokeColor=LINE))
    d.add(String(15, 205, "LOCAL TRUST ZONE", fontName="Helvetica-Bold", fontSize=8, fillColor=NAVY_3))
    box(d, 25, 120, 95, 45, "Browser", fill=BLUE)
    box(d, 150, 120, 95, 45, "API + Worker", fill=NAVY)
    box(d, 275, 120, 95, 45, "Postgres/Redis", fill=NAVY_2)
    box(d, 150, 45, 95, 45, "Ollama", fill=GREEN)
    box(d, 385, 120, 95, 45, "Public data", fill=AMBER, text=NAVY)
    arrow(d, 120, 142, 150, 142)
    arrow(d, 245, 142, 275, 142)
    arrow(d, 197, 120, 197, 90)
    arrow(d, 370, 142, 385, 142)
    d.add(Line(378, 25, 378, 210, strokeColor=RED, strokeWidth=1.2, strokeDashArray=[5, 3]))
    d.add(String(382, 30, "NETWORK BOUNDARY", fontName="Helvetica-Bold", fontSize=6.5, fillColor=RED))
    return [P("Figure 13. Security trust zones", "DiagramTitle"), d]


class BlueprintDoc(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(filename, pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm, topMargin=19 * mm, bottomMargin=17 * mm, title="BuktiSaham PRD and TRD v2.0")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=self.page_decoration))

    def page_decoration(self, canvas, doc):
        if doc.page == 1:
            canvas.saveState()
            canvas.setFillColor(NAVY)
            canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
            canvas.restoreState()
            return
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, A4[1] - 13 * mm, A4[0] - 18 * mm, A4[1] - 13 * mm)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(NAVY_3)
        canvas.drawString(18 * mm, A4[1] - 10 * mm, "BuktiSaham v2.0 · Task-Based Indonesian Equity Research")
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"PRD + TRD · Page {doc.page}")
        canvas.restoreState()


def section(story: list, number: str, title: str, intro: str | None = None, page_break: bool = True):
    if page_break:
        story.append(PageBreak())
    story.append(P(f"{number}  {title}", "H1x"))
    if intro:
        story.append(P(intro, "Callout"))


def build_story() -> list:
    s: list = []
    s += [Spacer(1, 42 * mm), P("IMPLEMENTATION BLUEPRINT · VERSION 2.0", "CoverEyebrow"), P("BuktiSaham", "CoverTitle"), P("Task-Based Indonesian Equity Research Orchestration", "CoverTitle"), P("Combined Product Requirements Document (PRD) and Technical Requirements Document (TRD)", "CoverSub")]
    s += task_object_diagram()
    s += [Spacer(1, 16 * mm), P("Prepared as the approval baseline for actual product and engineering implementation.", "CoverSub"), P("19 September 2026 · Repository baseline: github.com/radhian/buktisaham", "Smallx")]

    section(s, "0", "Document Control and Decision Record", "This version supersedes the one-shot research-screen framing. It preserves the Indonesian methodology, local Ollama constraint, free-only data constraint, and deterministic authority boundary while making the task the primary product object.")
    s.append(data_table(["Field", "Decision"], [
        ["Product", "BuktiSaham"], ["Version", "2.0 task-orchestration blueprint"], ["Implementation checkpoint", "Repository v0.2.0"], ["Primary journey", "Create Task → Run Saved Method → Observe → Review Evidence → Rerun"], ["AI", "Local Ollama, explanation and challenge only"], ["Market data", "Free-only yfinance adapter for EOD/delayed MVP"], ["Decision authority", "Deterministic Python policy engine"], ["Approval effect", "Authorizes implementation against the contracts in this document; it is not an investment recommendation"]
    ], [115, 365]))
    s.append(P("Key architecture decisions", "H2x"))
    s.append(bullet(["A research task is a reusable mandate, not a recommendation.", "Every task update publishes a new immutable configuration version and hash.", "Every run snapshots the selected configuration before it enters the queue.", "A multi-ticker run may publish partial success; successful results are never discarded because one ticker failed.", "AI output is non-authoritative and may never overwrite a deterministic fact, score, scenario, policy result, or hash.", "The MVP has no automatic scheduler, authentication, broker connection, or paid-provider fallback."]))

    section(s, "1", "Executive Summary", "BuktiSaham is a personal research operating system for Indonesian equities. The user defines a repeatable decision mandate once and runs it whenever fresh evidence is required.")
    s.append(P("The prior screen executed one ticker immediately and then displayed the result. The underlying backend already had task and run records, but the product did not expose task persistence, configuration identity, run history, progress, or multi-stock orchestration. Version 2.0 aligns the visible product with its intended operating model.", "Bodyx"))
    s += horizontal_flow("Figure 2. End-to-end product journey", ["Define Task", "Run Snapshot", "Observe Stages", "Review Packet"], [BLUE, NAVY_2, NAVY_3, TEAL])
    s.append(P("Business outcome", "H2x"))
    s.append(bullet(["Users can reproduce a method instead of recreating inputs for every check.", "Teams can explain why a recommendation changed by comparing saved runs and evidence, not by guessing which prompt changed.", "A single task can compare a small IDX universe under one consistent horizon and policy.", "Failures become visible operational events and partial results remain usable."]))
    s.append(P("North-star metric", "H2x"))
    s.append(P("Percentage of active tasks that produce at least two successfully published, comparable evidence packets within 90 days. This measures recurring research utility rather than page visits or one-time analyses."))

    section(s, "2", "Problem, Users, and Jobs To Be Done")
    s.append(data_table(["User", "Job", "Current pain", "Success"], [
        ["Self-directed IDX investor", "Apply one method repeatedly", "Inputs are rebuilt manually and results are difficult to compare", "A saved task can be rerun in one action"],
        ["Equity research analyst", "Review several issuers consistently", "Per-stock work becomes inconsistent and evidence is scattered", "One task runs the same gates across the universe"],
        ["Product/engineering reviewer", "Audit result lineage", "UI shows a conclusion without execution trace", "Config hash, events, evidence and deterministic hash are visible"],
        ["Operator", "Diagnose failed execution", "Background work appears frozen", "Stage, percentage, error, and partial state are explicit"]
    ], [90, 120, 150, 120]))
    s.append(P("Primary job statement", "H2x"))
    s.append(P("When I want to revisit an Indonesian equity thesis, I want to run the same saved methodology against current available evidence, so I can understand what changed and make a more disciplined research decision."))
    s.append(P("Problem boundaries", "H2x"))
    s.append(bullet(["The product does not promise real-time exchange data.", "The product does not execute orders or optimize a live portfolio.", "The MVP does not claim official IDX data licensing.", "The MVP is single-user local software unless a later security phase adds identity and access controls."]))

    section(s, "3", "Product Principles and Non-Goals")
    s.append(data_table(["Principle", "Implementation meaning"], [
        ["Task before ticker", "The home experience starts from mandates and run history, not an isolated symbol form."],
        ["Evidence before confidence", "Missing or stale data lowers completeness and can hard-block an action."],
        ["Configuration is a fact", "A run always references an immutable version and hash."],
        ["Numbers are deterministic", "Python owns calculations, scenarios, and policy actions."],
        ["AI is review, not authority", "Ollama explains, challenges, and identifies gaps only."],
        ["Failures are data", "Every queue and worker transition is recorded as a run event."],
        ["Free means explicit trade-offs", "No billable fallback; availability can be lower and freshness is EOD/delayed."]
    ], [150, 330]))
    s.append(P("Non-goals for v0.2.0", "H2x"))
    s.append(bullet(["Automated recurring scheduling", "Authentication or shared workspaces", "Portfolio accounting", "Corporate action reconciliation", "Sector-specific valuation", "Automatic run PDF reports", "Regulated personalized advice", "Brokerage execution"]))

    section(s, "4", "User Journey and Information Architecture")
    s += horizontal_flow("Figure 3. Workspace information architecture", ["Overview", "Research Tasks", "Run History", "Methodology"], [BLUE, NAVY_2, NAVY_3, TEAL])
    s.append(data_table(["Area", "User question answered", "Primary actions"], [
        ["Overview", "What is active and what changed recently?", "Create task, open task, inspect recent run"],
        ["Research Tasks", "What reusable mandates exist?", "Create, inspect, run, later edit/archive"],
        ["Task Detail", "What exact method will execute?", "Review thesis, universe, modules, config hash, history"],
        ["Run History", "What happened in every execution?", "Inspect status, stage, progress, error, packet"],
        ["Run Detail", "What did the task conclude and why?", "Select ticker, inspect scenarios, evidence, Ollama review"],
        ["Methodology", "How are actions produced?", "Review deterministic and AI authority boundaries"]
    ], [95, 175, 210]))
    s.append(P("Happy path", "H2x"))
    s.append(bullet(["User creates a named task with thesis and one to ten IDX symbols.", "System normalizes symbols, validates the task, publishes config v1, and displays its hash.", "User selects Run saved methodology.", "API rejects duplicate active execution, snapshots the config, stores a queued event, and enqueues work.", "UI polls and shows aggregate stage progress.", "Worker publishes complete or partial packet with per-symbol drill-down.", "User revisits the task later and runs the same or a newly versioned configuration."]))

    section(s, "5", "Functional Requirements - Research Tasks")
    s.append(data_table(["ID", "Requirement", "Acceptance"], [
        ["TASK-01", "Create a task with name, thesis, symbols, horizon, capital context, cadence metadata, and modules", "Valid request returns 201, normalized .JK symbols, config version 1 and hash"],
        ["TASK-02", "Allow one to ten unique symbols", "Duplicates are removed; zero or more than ten fails validation"],
        ["TASK-03", "Preserve legacy single ticker input", "A request with ticker only creates a one-symbol task"],
        ["TASK-04", "List and retrieve active tasks", "Responses include latest run summary and config identity"],
        ["TASK-05", "Update task as new config version", "Core task ID remains stable while version increments and hash changes"],
        ["TASK-06", "Archive a task", "Archive is blocked while a run is active; archived task is omitted from lists"],
        ["TASK-07", "Show explicit MVP cadence boundary", "UI states that runs are manual; cadence is metadata only"]
    ], [55, 250, 175]))
    s.append(P("Task contract", "H2x"))
    s.append(P("name, thesis, tickers[], horizon_days, capital_idr, cadence, analysis_modules[], status, market_data_mode, provider", "Code"))

    section(s, "6", "Functional Requirements - Runs and Orchestration")
    s += state_diagram()
    s.append(data_table(["ID", "Requirement", "Acceptance"], [
        ["RUN-01", "Snapshot active config before enqueue", "Run contains config version, hash, and full config even if task later changes"],
        ["RUN-02", "Prevent concurrent duplicate task runs", "Second start returns HTTP 409 with active run ID"],
        ["RUN-03", "Emit append-only stage events", "Polling returns ordered stage, progress, message, and timestamp"],
        ["RUN-04", "Aggregate progress across ticker universe", "Progress is non-decreasing and reaches 100 in a terminal state"],
        ["RUN-05", "Continue after one symbol error", "Remaining tickers execute; mixed result becomes PARTIAL"],
        ["RUN-06", "Publish immutable task packet", "Bundle includes summary, analyses, errors, snapshot and SHA-256 hash"],
        ["RUN-07", "Expose task-specific and global history", "User can list all runs or filter by task ID"]
    ], [55, 250, 175]))

    section(s, "7", "Indonesian Equity Research Methodology", "The current methodology is deliberately transparent and provider-constrained. It is suitable as an MVP research screen, not a substitute for licensed data or professional judgment.")
    s += horizontal_flow("Figure 5. Per-ticker methodology", ["Free EOD Facts", "Scores", "Scenarios", "Policy Action"], [AMBER, BLUE, NAVY_2, TEAL])
    s.append(data_table(["Layer", "Current calculation", "Decision role"], [
        ["Market history", "One year daily close and volume", "Technical trend, volatility, drawdown, liquidity"],
        ["Fundamentals", "Available valuation, growth, profitability and leverage fields", "Fundamental score and evidence coverage"],
        ["Technical score", "Return, moving-average, RSI and risk signals", "Policy input"],
        ["Liquidity score", "Observed volume and tradability proxy", "Hard/soft policy gate"],
        ["Evidence completeness", "History depth plus available fundamental fields", "Confidence and hard gate"],
        ["Scenarios", "Bear/Base/Bull target prices and probabilities", "Expected return and downside"],
        ["Policy", "Configured thresholds and hard blocks", "Final research action"]
    ], [105, 230, 145]))
    s.append(P("Research actions", "H2x"))
    s.append(bullet(["BUY_RESEARCH: evidence and expected return pass configured upside and risk gates.", "HOLD_RESEARCH: evidence is usable but upside is inside hold range.", "SELL_RESEARCH: downside/valuation policy supports reduction research.", "WATCH: confidence, completeness, liquidity, or consistency is insufficient for a stronger action."]))

    section(s, "8", "Scenario, Confidence, and Risk Contracts")
    s.append(data_table(["Output", "Contract"], [
        ["Bear/Base/Bull", "Every scenario stores target price, return, and probability."],
        ["Expected return", "Probability-weighted scenario return; it is not a guaranteed forecast."],
        ["Bear downside", "Return from current price to bear target; used as an explicit risk gate."],
        ["Confidence", "Composite of technical, fundamental, liquidity and completeness dimensions."],
        ["Hard block", "A policy state that prevents a stronger action regardless of narrative."],
        ["Capital context", "Input carried into the research packet; it does not execute allocation or orders."]
    ], [130, 350]))
    s.append(P("Required interpretation text", "H2x"))
    s.append(P("Every scenario view must label values as scenarios, display the as-of timestamp, preserve the current price used, and show evidence-completeness limitations. The UI must never display a target price without its downside context and policy status."))
    s += horizontal_flow("Figure 6. Confidence composition", ["Technical", "Fundamental", "Liquidity", "Completeness"], [BLUE, NAVY_3, TEAL, AMBER])

    section(s, "9", "AI Review Requirements")
    s += authority_diagram()
    s.append(data_table(["AI may", "AI may not"], [
        ["Summarize the deterministic packet", "Change ticker, price, timestamps, or source facts"],
        ["List drivers and key risks", "Recalculate scores or scenarios"],
        ["Find contradictions and missing evidence", "Override hard blocks or research action"],
        ["Draft analyst follow-up questions", "Approve publication or execute trades"],
        ["Return unavailable status on failure", "Cause deterministic work to be discarded"]
    ], [240, 240]))
    s.append(P("Model configuration", "H2x"))
    s.append(P("AI_PROVIDER=ollama; OLLAMA_BASE_URL=http://ollama:11434; OLLAMA_MODEL=qwen3:8b; no external AI key is required.", "Code"))

    section(s, "10", "Evidence and Data Source Policy")
    s.append(data_table(["Source class", "MVP source", "Rights/quality posture", "Failure behavior"], [
        ["Price and volume", "Yahoo Finance via yfinance", "Public/unofficial; terms and continuity must be reviewed", "Ticker result fails; no paid fallback"],
        ["Fundamentals", "Fields exposed through yfinance", "May be incomplete and not filing-normalized", "Missing fields reduce coverage"],
        ["AI", "Local Ollama", "Data remains local to the configured host", "Deterministic result still publishes"],
        ["Future filings", "IDX/OJK/issuer IR", "Public availability does not automatically grant bulk automation rights", "Not implemented in v0.2.0"],
        ["Future licensed feed", "IDX/vendor adapter", "Entitlement required", "Architecture extension; not automatic fallback"]
    ], [90, 110, 180, 100]))
    s.append(P("Evidence record minimum", "H2x"))
    s.append(bullet(["evidence_type", "source_name and source_uri", "observed/retrieved timestamp", "ticker in payload", "rights note", "content hash", "run ID linkage"]))

    section(s, "11", "Technical Architecture")
    s += architecture_diagram()
    s.append(data_table(["Component", "Technology", "Responsibility"], [
        ["Web", "Next.js 15.5.24 + React 19.1.5", "Task workspace, polling, drill-down"],
        ["API", "Python 3.12 + FastAPI/Pydantic", "Validation, task/config APIs, queue submission, read models"],
        ["Worker", "Python + RQ", "Multi-ticker orchestration, events, publication"],
        ["Database", "PostgreSQL", "Tasks, versions, runs, events, packets, evidence"],
        ["Queue", "Redis", "Asynchronous job delivery"],
        ["Market adapter", "yfinance", "Free-only .JK EOD data"],
        ["AI adapter", "Ollama /api/chat", "Local narrative review"]
    ], [90, 145, 245]))
    s.append(P("Architecture style", "H2x"))
    s.append(P("Contract-enforced modular monolith. API and worker share domain code but run as independent containers. This preserves low operating cost and simple local deployment while keeping provider, policy, and orchestration seams replaceable."))

    section(s, "12", "Data Model and Immutability")
    s += erd_diagram()
    s.append(data_table(["Entity", "Key fields", "Mutability"], [
        ["research_task", "id, ticker, horizon_days, capital_idr, params_json", "Stable identity; active config projection may change"],
        ["task_config_version", "task_id, version, config_hash, config_json", "Append-only"],
        ["task_run", "task_id, status, result_json, timestamps", "State transitions then immutable terminal packet"],
        ["run_event", "run_id, stage, progress, message, created_at", "Append-only"],
        ["recommendation_version", "run_id, version, action, content_hash, payload", "Append-only"],
        ["evidence_item", "run_id, type, source, payload, hash", "Append-only"]
    ], [115, 245, 120]))
    s.append(P("Backward compatibility", "H2x"))
    s.append(P("The existing research_task and task_run schemas are not destructively altered. Rich task fields remain in params_json. New tables are created by metadata initialization. Legacy single-ticker tasks receive a fallback version-1 projection until they are updated."))

    section(s, "13", "API Contract")
    s.append(data_table(["Method", "Path", "Purpose", "Key response"], [
        ["GET", "/v1/dashboard", "Workspace summary", "Counts, recent tasks and runs"],
        ["GET", "/v1/research-tasks", "List active tasks", "Task cards with latest run"],
        ["POST", "/v1/research-tasks", "Create task/config v1", "201 task response"],
        ["GET", "/v1/research-tasks/{id}", "Get task", "Config identity and latest run"],
        ["PATCH", "/v1/research-tasks/{id}", "Publish new config", "Incremented version/hash"],
        ["DELETE", "/v1/research-tasks/{id}", "Archive task", "Archived state or 409"],
        ["POST", "/v1/research-tasks/{id}/runs", "Start run", "202 queued run or 409"],
        ["GET", "/v1/research-tasks/{id}/runs", "Task history", "Ordered runs"],
        ["GET", "/v1/runs", "Global/filterable history", "Ordered runs"],
        ["GET", "/v1/runs/{id}", "Poll run", "Stage, progress, events, packet"]
    ], [42, 170, 145, 123]))
    s.append(P("Compatibility rule", "H2x"))
    s.append(P("POST /v1/research-tasks continues to accept the v0.1 ticker field. The service converts it to a one-element tickers array and generates a default task name."))

    section(s, "14", "Execution Sequence and Failure Semantics")
    s += sequence_diagram()
    s.append(data_table(["Failure", "Visible outcome", "Recovery"], [
        ["Redis unavailable during start", "503; run becomes FAILED with event", "Restore queue and start a new run"],
        ["One ticker provider failure", "symbol_failed event; remaining tickers continue", "PARTIAL packet; rerun later"],
        ["All tickers fail", "FAILED packet with per-ticker errors", "Review provider status and rerun"],
        ["Ollama unavailable", "AI review marked unavailable", "Deterministic packet remains publishable"],
        ["Duplicate start", "409 with active run ID", "Open existing run instead"],
        ["Worker process crash", "Run may remain RUNNING in current MVP", "Operational restart; watchdog is next hardening step"]
    ], [120, 205, 155]))

    section(s, "15", "Frontend Experience Requirements")
    s.append(data_table(["View", "Must show", "Must avoid"], [
        ["Overview", "Task/run KPIs, recent tasks, recent runs, task CTA", "Starting with a raw ticker form"],
        ["Task Card", "Config version, symbols, thesis, latest status/progress", "Hiding whether the task is currently active"],
        ["Task Detail", "Thesis, universe, horizon, modules, config hash, run history", "Editing terminal run outputs"],
        ["Run Detail", "Status, stage, progress, events, summary, ticker tabs", "Showing a blank screen during background work"],
        ["Analysis", "Action, current price, upside/downside, confidence, scenarios", "Presenting scenario target as guaranteed forecast"],
        ["Evidence", "Source link, evidence type, hashes", "Unattributed numeric claims"],
        ["Methodology", "Deterministic/AI boundary and provider policy", "Suggesting AI selects the action"]
    ], [85, 245, 150]))
    s.append(P("Responsive behavior", "H2x"))
    s.append(P("Desktop uses persistent sidebar and multi-column cards. Tablet collapses the sidebar label density. Mobile converts navigation to a horizontal strip and all analytical grids to one column. Tables may scroll horizontally but action buttons and status remain visible."))

    section(s, "16", "Security, Privacy, and Trust")
    s += trust_diagram()
    s.append(data_table(["Control", "v0.2.0", "Production requirement"], [
        ["Authentication", "None; local single user", "OIDC/session identity and user-scoped tasks"],
        ["Authorization", "Process-local trust", "Task/run ownership and role policies"],
        ["Transport", "Local HTTP defaults", "TLS termination and secure headers"],
        ["Secrets", ".env and Docker environment", "Secret store, rotation, no secrets in source"],
        ["Input validation", "Pydantic bounds and enums", "Rate limits, body limits, abuse controls"],
        ["AI privacy", "Local Ollama", "Document retention and prompt audit policy"],
        ["Dependency security", "Pinned lockfile and patched maintenance versions", "Automated scanning and monthly updates"]
    ], [105, 160, 215]))
    s.append(P("Threat priorities", "H2x"))
    s.append(bullet(["Unauthorized public access to a local research instance", "Malicious or malformed ticker/task payload", "Dependency vulnerabilities in the web runtime", "Provider content treated as executable or trusted narrative", "Cross-user data exposure after multi-user expansion", "Silent corruption of task config or evidence lineage"]))

    section(s, "17", "Non-Functional Requirements")
    s.append(data_table(["Area", "MVP target", "Measurement"], [
        ["API availability", "99% during local process uptime", "Health endpoint and container state"],
        ["Task start", "202 or explicit error within 2 seconds excluding local host overload", "API latency"],
        ["Progress visibility", "First worker event within 10 seconds after dequeue", "Run event timestamps"],
        ["Run duration", "P95 under 5 minutes for one ticker with local model loaded", "started_at to finished_at"],
        ["Universe", "Maximum 10 tickers", "Pydantic validation"],
        ["Determinism", "Same facts/config/formula version yields same deterministic hash", "Regression test"],
        ["Recovery", "PostgreSQL backup and documented restore", "Restore rehearsal"],
        ["Accessibility", "Keyboard-operable forms and readable contrast", "Manual audit; WCAG test in P1"]
    ], [100, 235, 145]))

    section(s, "18", "Testing and Verification Strategy")
    s.append(data_table(["Layer", "Coverage"], [
        ["Unit", "Ticker normalization, policy gates, scoring, scenarios, schema validation, progress callbacks"],
        ["Domain/API", "Multi-ticker create, config version increment, hash persistence, legacy payload"],
        ["Worker", "Complete, partial, failed, event ordering, config snapshot, AI failure"],
        ["Frontend", "Production TypeScript build, task creation, polling, terminal packet rendering"],
        ["Contract", "OpenAPI response fields and backward-compatible create request"],
        ["Integration", "Postgres + Redis + worker + Ollama Compose smoke task"],
        ["Operational", "Backup/restore, container restart, provider outage, port conflict"],
        ["Security", "Dependency audit, secret scan, input abuse, unauthenticated exposure warning"]
    ], [110, 370]))
    s.append(P("Definition of Done for v0.2.0", "H2x"))
    s.append(bullet(["All backend tests and static checks pass.", "Frontend production build passes with lockfile.", "Shell scripts pass syntax validation.", "PDF renders without clipping or broken diagrams.", "Repository ZIP passes integrity test.", "README and implementation status do not claim automatic scheduling or report generation.", "GitHub is not modified without explicit user authorization."]))

    section(s, "19", "Deployment and Operations")
    s += horizontal_flow("Figure 12. Local deployment topology", ["Browser :3000", "API :18000", "Docker Network", "Worker + Stores"], [BLUE, NAVY, NAVY_3, TEAL])
    s.append(P("Bootstrap", "H2x"))
    s.append(P("cp .env.example .env\n./scripts/bootstrap.sh", "Code"))
    s.append(P("Operational routines", "H2x"))
    s.append(data_table(["Routine", "Command", "Expected result"], [
        ["Start", "./scripts/start.sh", "All services healthy"],
        ["Smoke", "./scripts/smoke-test.sh", "Health and free quote checks"],
        ["Demo task", "./scripts/task-demo.sh", "Published multi-stock packet"],
        ["Tests", "./scripts/test.sh", "Backend tests and frontend build"],
        ["Backup", "./scripts/backup.sh", "Timestamped database dump"],
        ["Restore", "./scripts/restore.sh <dir>", "Database restored from selected backup"],
        ["Stop", "./scripts/stop.sh", "Compose services stopped"]
    ], [95, 160, 225]))

    section(s, "20", "Implementation Mapping")
    s.append(data_table(["Requirement area", "Repository location"], [
        ["Task/config APIs", "backend/app/api/research.py"],
        ["Task config and event persistence", "backend/app/models.py"],
        ["Request/response validation", "backend/app/schemas.py"],
        ["Run orchestration", "backend/app/worker_jobs.py"],
        ["Deterministic analysis progress", "backend/app/services/analysis_engine.py"],
        ["Task workspace UI", "frontend/app/page.tsx"],
        ["Visual system", "frontend/app/globals.css"],
        ["Browser API client", "frontend/lib/api.ts"],
        ["End-to-end demo", "scripts/task-demo.sh"],
        ["Architecture and contracts", "docs/ARCHITECTURE.md and docs/TASK_ORCHESTRATION.md"]
    ], [175, 305]))
    s.append(P("Current implementation status", "H2x"))
    s.append(P("Implemented: task dashboard, multi-ticker tasks, configuration versions and hashes, snapshots, queue, events, progress, complete/partial/failed publication, per-ticker result views, local Ollama, free-only data, Docker and verification scripts. Not implemented: scheduler, authentication, official filing normalization, sector valuation, automatic report generation, outcome ledger."))

    section(s, "21", "Roadmap and Delivery Epics")
    s += horizontal_flow("Figure 14. Delivery roadmap", ["v0.2 Tasks", "v0.3 Reports", "v0.4 Scheduler/Auth", "v0.5 Data/Models"], [TEAL, BLUE, NAVY_3, AMBER])
    s.append(data_table(["Epic", "Outcome", "Exit gate"], [
        ["E1 Task orchestration", "Reusable task, config version, run trace", "Implemented in v0.2.0"],
        ["E2 Run PDF report", "Executive and audit-ready report per terminal run", "Report hash and download API"],
        ["E3 Scheduler", "Due-task execution with idempotency and missed-run recovery", "No duplicate scheduled packets"],
        ["E4 Identity", "User-scoped tasks and role-aware access", "Cross-user isolation tests"],
        ["E5 Official evidence", "IDX/OJK/issuer filing ingestion", "Point-in-time lineage and rights review"],
        ["E6 Sector routing", "Bank, insurer, commodity, consumer and infrastructure models", "Model-fit rules and tests"],
        ["E7 Outcome ledger", "Compare recommendations with realized outcomes", "Point-in-time, survivorship-aware evaluation"],
        ["E8 Licensed provider", "Replaceable entitled market-data adapter", "Contract parity and entitlement enforcement"]
    ], [105, 235, 140]))

    section(s, "22", "Acceptance Scenarios")
    s.append(data_table(["Scenario", "Given / When", "Then"], [
        ["Create task", "Three valid IDX tickers", "Symbols normalize, config v1 and hash return"],
        ["Legacy create", "ticker=BBCA only", "One-symbol task is created"],
        ["Duplicate ticker", "BBCA, BBRI, BBCA", "Universe becomes BBCA.JK and BBRI.JK"],
        ["Run task", "No active run", "202, queued event, immutable snapshot"],
        ["Duplicate run", "Run already queued/running", "409 and existing run ID"],
        ["Partial data", "One of three tickers fails", "Two analyses publish; status PARTIAL"],
        ["Ollama offline", "Deterministic work succeeds", "Packet publishes with AI unavailable"],
        ["Config update", "Horizon changes", "Version increments, new hash; old run snapshot unchanged"],
        ["Archive active task", "Run still active", "409; no archive"],
        ["Free-only guard", "Paid provider configured", "Startup rejects configuration"]
    ], [105, 220, 155]))

    section(s, "23", "Risks and Mitigations")
    s.append(data_table(["Risk", "Impact", "Mitigation"], [
        ["Unofficial provider availability", "Missing or rate-limited runs", "Explicit failure, caching, future licensed adapter"],
        ["Fundamental field inconsistency", "Misleading cross-company comparison", "Completeness score, field provenance, future filing normalization"],
        ["Generic valuation logic", "Poor model fit by sector", "Label current scenarios; implement sector routing before broad use"],
        ["Long local AI latency", "Slow multi-ticker run", "Progress events, smaller model option, AI non-blocking future mode"],
        ["Stuck worker state", "Run appears permanently active", "Add heartbeat/watchdog and retry policy in next hardening"],
        ["No authentication", "Unsafe public exposure", "Local-only warning; add identity before shared deployment"],
        ["False certainty", "User over-trusts action", "Research labels, evidence gaps, scenario language, no trade execution"]
    ], [135, 155, 190]))

    section(s, "24", "Glossary")
    s.append(data_table(["Term", "Definition"], [
        ["Task", "Reusable Indonesian equity research mandate"],
        ["Config version", "Immutable numbered task-method configuration"],
        ["Run", "One asynchronous execution of a task snapshot"],
        ["Run event", "Append-only stage/progress observation"],
        ["Evidence packet", "Published task-level bundle containing analyses, source lineage and hashes"],
        ["Research action", "Deterministic decision-support category; not an order"],
        ["Partial", "At least one ticker succeeded and at least one failed"],
        ["Free-only", "No automatic billable market-data provider path exists"],
        ["Local Ollama", "Model inference served from the user's environment"],
        ["PIT", "Point in time: only information available by the evaluation cutoff"]
    ], [120, 360]))

    section(s, "25", "References and Approval Checklist")
    s.append(P("Repository and implementation references", "H2x"))
    s.append(bullet(["BuktiSaham repository: https://github.com/radhian/buktisaham", "Next.js security maintenance guidance: https://nextjs.org/blog/tag/security", "Ollama local model API: https://ollama.com", "yfinance project and data-use notes: https://github.com/ranaroussi/yfinance", "IDX data services for future licensed production integration: https://data.idx.co.id", "OJK public information for future regulatory/filing evidence: https://www.ojk.go.id"]))
    s.append(P("Approval checklist", "H2x"))
    s.append(bullet(["Product approves task-first workflow and MVP non-goals.", "Research owner approves deterministic policy terminology and scenario labeling.", "Engineering approves API, event, data model and compatibility contracts.", "Security accepts local-only boundary for MVP and blocks public exposure without identity controls.", "Data owner accepts free-only provider limitations for MVP.", "Delivery owner accepts the roadmap order: report, scheduler, identity, official evidence, sector routing."]))
    s.append(Spacer(1, 10 * mm))
    s.append(P("Approval statement", "Callout"))
    s.append(P("Approval of this document authorizes implementation and iteration against the stated v2.0 contracts. It does not authorize brokerage execution, public multi-user deployment, paid data procurement, or claims of investment performance."))
    return s


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BlueprintDoc(str(OUTPUT))
    doc.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()
