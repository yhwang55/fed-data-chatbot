"""Generate all technical report figures for fed-data-chatbot."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from PIL import Image
import os

FIGURES_DIR = "assets/figures"
os.makedirs(FIGURES_DIR, exist_ok=True)

# ── Color palette ──────────────────────────────────────────────────────────────
C_BLUE    = "#1B2A4A"
C_INDIGO  = "#3B4D8A"
C_PURPLE  = "#7C6FCD"
C_TEAL    = "#1D7A73"
C_GREEN   = "#16A34A"
C_RED     = "#DC2626"
C_AMBER   = "#D97706"
C_GRAY    = "#6B7280"
C_LIGHT   = "#F3F4F6"
C_WHITE   = "#FFFFFF"
C_BORDER  = "#D1D5DB"

plt.rcParams.update({
    "font.family":     "DejaVu Sans",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "figure.dpi":         150,
})

# ══════════════════════════════════════════════════════════════════════════════
# Figure 01 — System Architecture Overview
# ══════════════════════════════════════════════════════════════════════════════
def fig01_architecture():
    fig, ax = plt.subplots(figsize=(14, 8.5))
    ax.set_xlim(0, 14); ax.set_ylim(0, 8.5)
    ax.axis("off")
    fig.patch.set_facecolor(C_WHITE)

    # Muted palette — two subtle tints + cream SEP
    L_FC, L_EC, L_TC = "#F0F7F4", "#9DBFB5", "#0F4C3A"   # soft sage — Chart Path
    R_FC, R_EC, R_TC = "#F0F4FB", "#9AAFD4", "#1B2A4A"   # soft slate — Text Path
    S_FC, S_EC, S_TC = "#FDFAEF", "#C9AA6E", "#78350F"   # pale cream — SEP
    UQ_FC, UQ_EC, UQ_TC = "#F8F9FA", "#6B7280", "#1B2A4A"

    LX, BW_L = 0.3, 4.5    # left col  0.3 – 4.8
    RX, BW_R = 9.2, 4.5    # right col 9.2 – 13.7  (wide centre gap)
    L_CX = LX + BW_L / 2   # 2.55
    R_CX = RX + BW_R / 2   # 11.45
    BH = 0.9

    R1_B = 5.8
    R2_B = 4.3
    R3_B = 2.8

    SEP_H = 0.80
    SEP_W = 2.8
    SEPX  = (LX + BW_L + RX) / 2 - SEP_W / 2   # centred in gap ≈ 5.7
    SEP_B = R2_B + (BH - SEP_H) / 2             # aligned with row-2

    UQ_B, UQ_H = 7.3, 0.85
    UQ_CX  = 7.0
    SPLIT_Y = 7.0

    def box(x, y, w, h, l1, l2="", fc=UQ_FC, ec=C_BORDER,
            tc=C_BLUE, sc=C_GRAY, fs=11, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                    facecolor=fc, edgecolor=ec, linewidth=1.2, zorder=2))
        yoff = 0.13 if l2 else 0
        ax.text(x+w/2, y+h/2+yoff, l1, ha="center", va="center",
                fontsize=fs, color=tc, fontweight="bold" if bold else "normal", zorder=3)
        if l2:
            ax.text(x+w/2, y+h/2-0.17, l2, ha="center", va="center",
                    fontsize=8.5, color=sc, zorder=3)

    def varr(x, y_from, y_to, c=C_GRAY):
        ax.annotate("", xy=(x, y_to), xytext=(x, y_from),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=1.4, mutation_scale=13), zorder=4)

    def harr(x1, y, x2, lbl="", c=C_GRAY):
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=1.4, mutation_scale=13), zorder=4)
        if lbl:
            ax.text((x1+x2)/2, y+0.14, lbl, ha="center", fontsize=8,
                    color=c, style="italic", zorder=5)

    # ── Title ─────────────────────────────────────────────────────────────
    ax.text(7.0, 8.36, "Fed Data Chatbot — System Architecture",
            ha="center", fontsize=13, fontweight="bold", color=C_BLUE)

    # ── User Query ────────────────────────────────────────────────────────
    box(UQ_CX - 3.0, UQ_B, 6.0, UQ_H, "User Query (Natural Language)",
        fc=UQ_FC, ec="#9CA3AF", tc=C_BLUE, bold=True)

    # ── T-junction ────────────────────────────────────────────────────────
    ax.plot([UQ_CX, UQ_CX], [UQ_B, SPLIT_Y],   color=C_GRAY, lw=1.4, zorder=3)
    ax.plot([L_CX,  R_CX],  [SPLIT_Y, SPLIT_Y], color=C_GRAY, lw=1.4, zorder=3)
    varr(L_CX, SPLIT_Y, R1_B + BH)
    varr(R_CX, SPLIT_Y, R1_B + BH)

    ax.text(L_CX, SPLIT_Y + 0.1, "Chart Path", fontsize=9,
            color="#4B8C7A", ha="center", style="italic")
    ax.text(R_CX, SPLIT_Y + 0.1, "Text Path",  fontsize=9,
            color="#4A5EA8", ha="center", style="italic")

    # ══ LEFT COLUMN ═══════════════════════════════════════════════════════
    box(LX, R1_B, BW_L, BH, "Keyword Resolver",
        "NL → FRED Ticker (deterministic)",
        fc=L_FC, ec=L_EC, tc=L_TC)
    varr(L_CX, R1_B, R2_B + BH)

    box(LX, R2_B, BW_L, BH, "FRED API",
        "10 macroeconomic time-series",
        fc=L_FC, ec=L_EC, tc=L_TC)
    varr(L_CX, R2_B, R3_B + BH)

    box(LX, R3_B, BW_L, BH, "Plotly.js Interactive Chart",
        "Line / Scatter + SEP Overlay",
        fc=L_FC, ec=L_EC, tc=L_TC)

    # ══ RIGHT COLUMN ══════════════════════════════════════════════════════
    box(RX, R1_B, BW_R, BH, "ChromaDB (MMR Retrieval)",
        "Fed Speeches · FOMC Minutes · SEP Docs  (APScheduler daily)",
        fc=R_FC, ec=R_EC, tc=R_TC, sc="#4A5EA8", fs=10.5)
    varr(R_CX, R1_B, R2_B + BH)

    box(RX, R2_B, BW_R, BH, "GPT-4o-mini (RAG Chain)",
        "Retrieved context + SEP projection",
        fc=R_FC, ec=R_EC, tc=R_TC)
    varr(R_CX, R2_B, R3_B + BH)

    box(RX, R3_B, BW_R, BH, "Grounded Analytical Response",
        "Strictly from retrieved docs + SEP",
        fc=R_FC, ec=R_EC, tc=R_TC)

    # ══ SEP CSV (centred in wide gap) ════════════════════════════════════
    box(SEPX, SEP_B, SEP_W, SEP_H, "sep_values.csv",
        "SEP projections (quarterly)",
        fc=S_FC, ec=S_EC, tc=S_TC, fs=9.5)
    SEP_CY = SEP_B + SEP_H / 2

    harr(SEPX,          SEP_CY, LX + BW_L + 0.05, lbl="SEP overlay",     c="#B45309")
    harr(SEPX + SEP_W,  SEP_CY, RX - 0.05,         lbl="get_sep_context()", c="#B45309")

    # ── Legend ────────────────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(facecolor=L_FC, edgecolor=L_EC, label="Chart Path (FRED API)"),
        mpatches.Patch(facecolor=R_FC, edgecolor=R_EC, label="Text Path (RAG)"),
        mpatches.Patch(facecolor=S_FC, edgecolor=S_EC, label="SEP Projections"),
    ]
    ax.legend(handles=legend_items, loc="lower left", fontsize=9,
              framealpha=0.9, bbox_to_anchor=(0.01, 0.01))

    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/01_system_architecture.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Figure 01 saved.")


# ══════════════════════════════════════════════════════════════════════════════
# Figure 02 — RAG Pipeline Detail
# ══════════════════════════════════════════════════════════════════════════════
def fig02_rag_pipeline():
    fig, ax = plt.subplots(figsize=(14, 6.5))
    ax.set_xlim(0, 14); ax.set_ylim(0, 6.5)
    ax.axis("off")
    fig.patch.set_facecolor(C_WHITE)

    # Monochrome palette — one accent (dark navy storage, muted amber for SEP)
    BFC = "#F9FAFB"; BEC = "#9CA3AF"; BTC = "#1F2937"   # standard box
    DFC = "#E5E7EB"; DEC = "#4B5563"; DTC = C_BLUE       # ChromaDB (storage)
    SFC = "#FFFBEB"; SEC = "#9CA3AF"; STC = "#92400E"    # SEP (muted amber)
    ARR = "#6B7280"

    def box(x, y, w, h, line1, line2="",
            fc=BFC, ec=BEC, tc=BTC, size=10):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                    facecolor=fc, edgecolor=ec, linewidth=1.2, zorder=2))
        yoff = 0.14 if line2 else 0
        ax.text(x+w/2, y+h/2+yoff, line1, ha="center", va="center",
                fontsize=size, color=tc, fontweight="bold", zorder=3)
        if line2:
            ax.text(x+w/2, y+h/2-0.20, line2, ha="center", va="center",
                    fontsize=8, color=C_GRAY, zorder=3)

    def arr(x1, y1, x2, y2, lbl="", color=ARR, lw=1.5):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                   lw=lw, mutation_scale=13), zorder=4)
        if lbl:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my+0.13, lbl, ha="center", fontsize=8,
                    color=ARR, style="italic", zorder=5)

    # ══ A. INDEXING PIPELINE ═══════════════════════════════════════════════
    ax.text(7.0, 6.15, "A.  Indexing Pipeline  (APScheduler · daily 04:00 UTC)",
            ha="center", fontsize=11, fontweight="bold", color=C_BLUE)

    BH = 1.0; BY = 3.9; CY = BY + BH/2

    box(0.2,  BY, 2.0, BH, "Fed.gov",  "Speeches / Minutes / SEP")
    arr(2.2, CY, 3.0, CY, "crawl")

    box(3.0,  BY, 2.0, BH, "Parser",   "BeautifulSoup / pypdf")
    arr(5.0, CY, 5.8, CY, "chunk")

    box(5.8,  BY, 2.2, BH, "Chunker",  "RecursiveCharText\nSplitter", size=9.5)
    arr(8.0, CY, 8.7, CY, "embed")

    box(8.7,  BY, 2.0, BH, "Embedder", "text-embedding-\n3-small", size=9.5)
    arr(10.7, CY, 11.4, CY, "store")

    box(11.4, BY, 1.8, BH, "ChromaDB", "", fc=DFC, ec=DEC, tc=DTC, size=10)

    # Dedup callout — plain italic note, no colored box
    DEDUP_Y = 5.55
    ax.annotate("", xy=(5.4, BY+BH), xytext=(5.4, DEDUP_Y-0.12),
                arrowprops=dict(arrowstyle="-|>", color=ARR, lw=1.1, mutation_scale=11), zorder=4)
    ax.text(5.4, DEDUP_Y, "source-URL dedup: skip if already indexed",
            ha="center", va="bottom", fontsize=8.5, color=C_GRAY,
            style="italic",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#F9FAFB",
                      edgecolor="#D1D5DB", linewidth=0.8), zorder=5)

    # ══ B. QUERY PIPELINE ══════════════════════════════════════════════════
    ax.axhline(3.4, color=C_BORDER, lw=0.8, linestyle="--", xmin=0.01, xmax=0.99)
    ax.text(7.0, 3.2, "B.  Query Pipeline  (per request)",
            ha="center", fontsize=11, fontweight="bold", color=C_BLUE)

    QBH = 1.0; QBY = 1.8; QCY = QBY + QBH/2

    box(0.2,  QBY, 2.2, QBH, "User Query",     "natural language")
    arr(2.4, QCY, 3.0, QCY, "embed")

    box(3.0,  QBY, 2.2, QBH, "Query\nVector",  "text-embed-3-small", size=9)
    arr(5.2, QCY, 5.8, QCY, "MMR")

    box(5.8,  QBY, 2.3, QBH, "ChromaDB\n(MMR k=8)", "fetch_k=20, λ=0.7",
        fc=DFC, ec=DEC, tc=DTC, size=9.5)
    arr(8.1, QCY, 8.7, QCY, "context")

    box(8.7,  QBY, 2.4, QBH, "GPT-4o-mini",    "context + sep_context\n+ today", size=9.5)
    arr(11.1, QCY, 11.7, QCY, "answer")

    box(11.7, QBY, 1.7, QBH, "Response",        "grounded", size=9.5)

    # SEP injection — muted amber, one accent
    GPT_CX = 8.7 + 2.4/2
    SEP_W, SEP_H = 2.6, 0.75
    SEP_X = GPT_CX - SEP_W/2
    SEP_Y = 0.7
    box(SEP_X, SEP_Y, SEP_W, SEP_H, "get_sep_context()", "sep_values.csv → string",
        fc=SFC, ec=SEC, tc=STC, size=9)
    arr(GPT_CX, SEP_Y + SEP_H, GPT_CX, QBY, color=ARR)
    ax.text(GPT_CX + 0.15, (SEP_Y + SEP_H + QBY) / 2, "inject",
            fontsize=8, color=C_GRAY, style="italic", va="center")

    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/02_rag_pipeline.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Figure 02 saved.")


# ══════════════════════════════════════════════════════════════════════════════
# Figure 03 — App UI Composite Screenshot
# ══════════════════════════════════════════════════════════════════════════════
def fig03_ui_composite():
    asset_paths = {
        "main":       "assets/main.png",
        "language":   "assets/language.png",
        "indicators": "assets/indicators.png",
        "scatter":    "assets/scatter.png",
    }
    imgs = {}
    for k, p in asset_paths.items():
        if os.path.exists(p):
            imgs[k] = Image.open(p).convert("RGB")

    if len(imgs) < 2:
        print("Figure 03 skipped — screenshots not found.")
        return

    fig = plt.figure(figsize=(13, 8))
    fig.patch.set_facecolor(C_WHITE)

    labels = {
        "main":       "(a) Main interface — query input and response panel",
        "scatter":    "(b) Scatter plot — CPI vs. Unemployment correlation",
        "language":   "(c) Language selector — EN / KO / ES",
        "indicators": "(d) Used Indicators panel — localized names",
    }
    order = ["main", "scatter", "language", "indicators"]
    positions = [(0.02, 0.35, 0.60, 0.61),   # (a) main — large left
                 (0.02, 0.01, 0.58, 0.32),   # (b) scatter — bottom left
                 (0.64, 0.35, 0.34, 0.61),   # (c) language — right top
                 (0.64, 0.01, 0.34, 0.32)]   # (d) indicators — right bottom, aligned with (c)

    for key, (left, bottom, width, height) in zip(order, positions):
        if key not in imgs:
            continue
        ax = fig.add_axes([left, bottom, width, height])
        ax.imshow(imgs[key])
        ax.axis("off")
        # Minimal label: small, gray, no color
        ax.set_title(labels[key], fontsize=8.5, color="#6B7280", pad=3, loc="left")
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor("#D1D5DB")
            spine.set_linewidth(0.6)

    plt.savefig(f"{FIGURES_DIR}/03_ui_composite.png", dpi=130, bbox_inches="tight")
    plt.close()
    print("Figure 03 saved.")


# ══════════════════════════════════════════════════════════════════════════════
# Figure 04 — FRED Indicator Coverage
# ══════════════════════════════════════════════════════════════════════════════
def fig04_indicators():
    categories = {
        "Monetary Policy": [
            ("FEDFUNDS", "Federal Funds Rate",          "daily → monthly"),
            ("DGS10",    "10-Year Treasury Yield",      "daily"),
            ("DGS2",     "2-Year Treasury Yield",       "daily"),
        ],
        "Inflation": [
            ("CPIAUCSL", "Consumer Price Index (CPI)",  "monthly"),
            ("PCEPI",    "PCE Price Index",             "monthly"),
        ],
        "Labor Market": [
            ("UNRATE",   "Unemployment Rate",           "monthly"),
            ("PAYEMS",   "Nonfarm Payrolls",            "monthly"),
        ],
        "Real Activity": [
            ("GDPC1",    "Real GDP (Billions $)",       "quarterly"),
            ("INDPRO",   "Industrial Production Index", "monthly"),
            ("HOUST",    "Housing Starts (thousands)",  "monthly"),
        ],
    }

    # Monochrome: dark navy headers, light gray item rows — no per-category color
    HDR_FC = C_BLUE;   HDR_TC = "#FFFFFF"
    ROW_FC = "#F3F4F6"; ROW_FC2 = "#FFFFFF"   # alternating
    ROW_EC = "#D1D5DB"
    TKR_TC = C_BLUE;   NAM_TC = "#374151";   FRQ_TC = "#6B7280"

    fig, axes = plt.subplots(1, 4, figsize=(14, 5))
    fig.patch.set_facecolor(C_WHITE)
    fig.suptitle("Fig. 4 — FRED Indicator Coverage by Category",
                 fontsize=13, fontweight="bold", color=C_BLUE, y=1.01)

    for ax, (cat, items) in zip(axes, categories.items()):
        n = len(items)
        ax.set_xlim(0, 4); ax.set_ylim(-0.5, n + 0.7)
        ax.axis("off")

        # Category header bar
        ax.add_patch(FancyBboxPatch((0.0, n - 0.02), 4.0, 0.62,
                                    boxstyle="square,pad=0",
                                    facecolor=HDR_FC, edgecolor="none", zorder=2))
        ax.text(2.0, n + 0.29, cat, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=HDR_TC, zorder=3)

        for i, (ticker, name, freq) in enumerate(items):
            y = n - 1 - i
            fc = ROW_FC if i % 2 == 0 else ROW_FC2
            ax.add_patch(FancyBboxPatch((0.05, y - 0.38), 3.9, 0.76,
                                        boxstyle="square,pad=0",
                                        facecolor=fc, edgecolor=ROW_EC,
                                        linewidth=0.7, zorder=2))
            ax.text(0.20, y + 0.09, ticker, fontsize=9.5, fontweight="bold",
                    color=TKR_TC, va="center", zorder=3)
            ax.text(0.20, y - 0.15, name, fontsize=8, color=NAM_TC, va="center", zorder=3)
            ax.text(3.92, y - 0.04, freq, fontsize=7.5, color=FRQ_TC,
                    va="center", ha="right", style="italic", zorder=3)

    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/04_fred_indicators.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Figure 04 saved.")


# ══════════════════════════════════════════════════════════════════════════════
# Figure 05 — MMR vs Top-k Retrieval
# ══════════════════════════════════════════════════════════════════════════════
def fig05_mmr_vs_topk():
    np.random.seed(42)

    # Simulate document clusters in 2D embedding space (PCA-projected)
    n_docs = 80
    clusters = [
        (0.3,  0.7, 0.08, 22, "#60A5FA"),   # cluster A (near query)
        (0.25, 0.62, 0.05, 18, "#60A5FA"),  # cluster A sub
        (0.75, 0.3,  0.09, 20, "#A78BFA"),  # cluster B
        (0.55, 0.85, 0.07, 20, "#34D399"),  # cluster C
    ]
    docs_x, docs_y = [], []
    for cx, cy, std, n, _ in clusters:
        docs_x.extend(np.random.normal(cx, std, n))
        docs_y.extend(np.random.normal(cy, std, n))
    docs_x = np.array(docs_x); docs_y = np.array(docs_y)

    query = np.array([0.28, 0.75])

    # Top-k: 8 nearest by Euclidean (proxy for cosine)
    dists = np.sqrt((docs_x - query[0])**2 + (docs_y - query[1])**2)
    topk_idx = np.argsort(dists)[:8]

    # MMR: simulate diverse selection (manually picked to show diversity)
    mmr_idx = [np.argsort(dists)[0]]   # closest first
    # then greedily add diverse ones
    candidate_pool = list(np.argsort(dists)[:20])
    while len(mmr_idx) < 8:
        best, best_score = None, -1
        for cand in candidate_pool:
            if cand in mmr_idx:
                continue
            rel  = 1 - dists[cand]
            div  = min(np.sqrt((docs_x[cand]-docs_x[s])**2 +
                               (docs_y[cand]-docs_y[s])**2) for s in mmr_idx)
            score = 0.7 * rel + 0.3 * div
            if score > best_score:
                best_score = score; best = cand
        mmr_idx.append(best)
    mmr_idx = np.array(mmr_idx)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.patch.set_facecolor(C_WHITE)

    for ax, selected, title in [
        (ax1, topk_idx, "Top-k (cosine similarity, k=8)\n— redundant cluster over-representation"),
        (ax2, mmr_idx,  "MMR (k=8, fetch k=20, λ=0.7)\n— diverse topical coverage"),
    ]:
        ax.set_facecolor("#FAFAFA")
        ax.scatter(docs_x, docs_y, s=28, color="#CBD5E1", alpha=0.6, zorder=2, label="Document chunks")
        ax.scatter(query[0], query[1], s=180, color=C_AMBER, marker="*", zorder=5,
                   edgecolors="white", linewidths=0.8, label="Query")
        ax.scatter(docs_x[selected], docs_y[selected], s=90,
                   color=C_BLUE if ax is ax1 else C_TEAL,
                   edgecolors="white", linewidths=0.8, zorder=4,
                   label=f"Selected ({len(selected)})")
        for idx in selected:
            ax.plot([query[0], docs_x[idx]], [query[1], docs_y[idx]],
                    lw=0.6, color=C_BLUE if ax is ax1 else C_TEAL, alpha=0.3, zorder=3)

        # cluster ellipses annotation
        for cx, cy, std, _, col in clusters:
            ellipse = plt.matplotlib.patches.Ellipse(
                (cx, cy), std*5, std*5, fill=False, edgecolor=col, lw=0.8,
                alpha=0.4, linestyle="--", zorder=1)
            ax.add_patch(ellipse)

        ax.set_title(title, fontsize=10.5, color=C_BLUE, pad=6, fontweight="bold")
        ax.set_xlabel("Embedding Dimension 1 (PCA)", fontsize=9, color=C_GRAY)
        ax.set_ylabel("Embedding Dimension 2 (PCA)", fontsize=9, color=C_GRAY)
        ax.legend(fontsize=8.5, framealpha=0.9, loc="lower right")
        ax.tick_params(labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(C_BORDER)

    # coverage annotation
    ax1.text(0.02, 0.04, "Coverage:\n1 topic cluster", transform=ax1.transAxes,
             fontsize=9, color=C_RED, bbox=dict(fc="#FEE2E2", ec=C_RED, alpha=0.8, pad=3))
    ax2.text(0.02, 0.04, "Coverage:\n3 topic clusters", transform=ax2.transAxes,
             fontsize=9, color=C_TEAL, bbox=dict(fc="#D1FAE5", ec=C_TEAL, alpha=0.8, pad=3))

    fig.suptitle("Fig. 5 — MMR vs. Top-k Retrieval: Context Diversity Comparison",
                 fontsize=13, fontweight="bold", color=C_BLUE, y=1.01)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/05_mmr_vs_topk.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Figure 05 saved.")


# ══════════════════════════════════════════════════════════════════════════════
# Figure 06 — Keyword Mapping Structure
# ══════════════════════════════════════════════════════════════════════════════
def fig06_keyword_map():
    rows = [
        ("Monetary Policy", "FEDFUNDS",        "Rate (%)",       ["interest rate", "fed funds", "federal funds", "rate hike", "rate cut", "rate increase", "rate decrease"]),
        ("Inflation",       "CPIAUCSL / PCEPI","YoY (%)",        ["inflation", "cpi", "consumer price", "price level", "pce"]),
        ("Labor Market",    "UNRATE / PAYEMS",  "% / thousands", ["unemployment", "jobless rate", "payroll", "jobs added", "nonfarm", "labor market", "employment"]),
        ("GDP / Growth",    "GDPC1",            "Billions $",    ["gdp", "gdp growth", "real gdp", "economic growth", "output", "growth rate"]),
        ("Yield Curve",     "DGS10 / DGS2",     "Rate (%)",      ["treasury yield", "10-year yield", "2-year yield", "yield curve", "inversion"]),
        ("Other",           "INDPRO / HOUST",   "Index / K",     ["industrial production", "manufacturing", "housing starts", "home building"]),
    ]

    fig, ax = plt.subplots(figsize=(13, 6.5))
    fig.patch.set_facecolor(C_WHITE)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, len(rows))
    ax.axis("off")

    row_h   = 1.0          # height per row
    cat_w   = 2.8          # width of left (category) column
    pad     = 0.18
    tag_h   = 0.30
    tag_pad = 0.08

    # ── Column headers ────────────────────────────────────────────────────────
    for x, label in [(cat_w / 2, "Category / Ticker"), (cat_w + 0.3, "Matched Natural Language Phrases")]:
        ax.text(x, len(rows) - 0.04, label,
                ha="center" if x < cat_w else "left",
                va="bottom", fontsize=10, fontweight="bold",
                color=C_BLUE)
    ax.axhline(len(rows) - 0.08, color=C_BLUE, lw=1.2, xmin=0, xmax=1)

    for i, (cat, ticker, unit, kws) in enumerate(rows):
        y_center = len(rows) - i - 0.5   # top → bottom

        # alternating row background
        if i % 2 == 1:
            ax.add_patch(plt.Rectangle((0, y_center - row_h/2), 13, row_h,
                                        facecolor="#F8F9FB", edgecolor="none", zorder=0))

        # ── Left cell: category name + ticker ────────────────────────────────
        ax.text(cat_w / 2, y_center + 0.10, cat,
                ha="center", va="center", fontsize=10, fontweight="bold",
                color=C_BLUE, zorder=2)
        ax.text(cat_w / 2, y_center - 0.18, ticker,
                ha="center", va="center", fontsize=8.5,
                color=C_GRAY, style="italic", zorder=2)

        # vertical divider
        ax.axvline(cat_w, color=C_BORDER, lw=0.8, ymin=(len(rows)-i-1)/len(rows),
                   ymax=(len(rows)-i)/len(rows))

        # ── Right cell: keyword tags ──────────────────────────────────────────
        x_cur = cat_w + 0.25
        row_top = y_center + 0.28

        # wrap tags into two sub-rows
        line_kws = [[], []]
        cur_line, x_test = 0, x_cur
        for kw in kws:
            tag_w = len(kw) * 0.082 + 0.22
            if x_test + tag_w > 12.85 and cur_line == 0:
                cur_line = 1
                x_test   = cat_w + 0.25
            line_kws[cur_line].append((kw, x_test))
            x_test += tag_w + tag_pad

        for line_idx, line in enumerate(line_kws):
            y_tag = row_top - line_idx * (tag_h + 0.10)
            for kw, x_tag in line:
                tag_w = len(kw) * 0.082 + 0.22
                rect = FancyBboxPatch((x_tag, y_tag - tag_h/2), tag_w, tag_h,
                                       boxstyle="round,pad=0.04",
                                       facecolor="#EEF2FF", edgecolor="#C7D2FE",
                                       linewidth=0.7, zorder=2)
                ax.add_patch(rect)
                ax.text(x_tag + tag_w/2, y_tag, kw,
                        ha="center", va="center", fontsize=8.5,
                        color=C_BLUE, zorder=3)

        # row divider
        ax.axhline(y_center - row_h/2, color=C_BORDER, lw=0.5, xmin=0, xmax=1)

    # outer border
    ax.add_patch(plt.Rectangle((0, 0), 13, len(rows),
                                facecolor="none", edgecolor=C_BORDER, lw=1.0, zorder=4))

    ax.set_title("Fig. 6 — Keyword Mapping Structure: Natural Language Phrase → FRED Ticker",
                 fontsize=12, fontweight="bold", color=C_BLUE, pad=10)

    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/06_keyword_mapping.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Figure 06 saved.")


# ══════════════════════════════════════════════════════════════════════════════
# Figure 07 — SEP Overlay Logic & Auto-Suppression
# ══════════════════════════════════════════════════════════════════════════════
def fig07_sep_logic():
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    fig.patch.set_facecolor(C_WHITE)
    fig.suptitle("Fig. 7 — SEP Overlay Auto-Suppression Logic",
                 fontsize=13, fontweight="bold", color=C_BLUE, y=1.01)

    current_year = 2026

    for ax, (start, end, title) in zip(axes, [
        (2005, 2015, "Historical Query (2005–2015)\n→ SEP overlay SUPPRESSED"),
        (2020, 2028, "Current/Future Query (2020–2028)\n→ SEP overlay SHOWN"),
    ]):
        years = np.arange(start, end + 1)
        # Simulate FEDFUNDS-like data
        np.random.seed(start)
        base = 2.5 + 2 * np.sin(np.linspace(0, np.pi, len(years))) + np.random.normal(0, 0.3, len(years))
        hist_mask = years < current_year
        fwd_mask  = years >= current_year

        ax.plot(years[hist_mask], base[hist_mask], lw=2, color=C_BLUE, label="FRED actual data", zorder=3)

        if fwd_mask.any():
            ax.plot(years[hist_mask][-1:].tolist() + years[fwd_mask].tolist(),
                    base[hist_mask][-1:].tolist() + base[fwd_mask].tolist(),
                    lw=1.5, color=C_BLUE, linestyle="--", alpha=0.4, zorder=2)

        show_sep = not (end < current_year)
        if show_sep and fwd_mask.any():
            sep_years = years[fwd_mask]
            sep_vals  = np.linspace(base[hist_mask][-1], base[hist_mask][-1] - 1.2, len(sep_years))
            ax.plot(sep_years, sep_vals, lw=2, color=C_RED, linestyle=":",
                    label="SEP projections (FOMC)", zorder=4)
            ax.fill_between(sep_years, sep_vals - 0.4, sep_vals + 0.4,
                            color=C_RED, alpha=0.08)
            ax.axvline(current_year, color=C_GRAY, lw=1, linestyle="--", alpha=0.5)
            ax.text(current_year + 0.1, ax.get_ylim()[1] * 0.92, "Today",
                    fontsize=8.5, color=C_GRAY, style="italic")

        # show_sep indicator box
        color_box = C_TEAL if show_sep else C_RED
        label_box = "show_sep = True" if show_sep else "show_sep = False"
        ax.text(0.97, 0.04, label_box, transform=ax.transAxes,
                ha="right", va="bottom", fontsize=10, fontweight="bold",
                color="white",
                bbox=dict(facecolor=color_box, edgecolor=color_box, pad=4, boxstyle="round"))

        ax.set_title(title, fontsize=10, color=C_BLUE, pad=5)
        ax.set_xlabel("Year", fontsize=9, color=C_GRAY)
        ax.set_ylabel("Fed Funds Rate (%)", fontsize=9, color=C_GRAY)
        ax.legend(fontsize=8.5, framealpha=0.9)
        ax.tick_params(labelsize=8.5)
        for spine in ax.spines.values():
            spine.set_color(C_BORDER)
        ax.set_facecolor("#FAFAFA")

    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/07_sep_logic.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Figure 07 saved.")


# ── Run all ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig01_architecture()
    fig02_rag_pipeline()
    fig03_ui_composite()
    fig04_indicators()
    fig05_mmr_vs_topk()
    fig06_keyword_map()
    fig07_sep_logic()
    print("\nAll figures saved to", FIGURES_DIR)
