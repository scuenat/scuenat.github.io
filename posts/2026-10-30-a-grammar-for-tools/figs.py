"""Figures for "A Grammar for Tools".

Same style as "The Interface Is Data": Inter type, white cards with a faint shadow
and a coloured accent, colours taken from the site's palette.

Figure 3 is plain counting with an illustrative token cost per tool. Every other figure
is a schematic with hand-placed or seeded positions; the weights in Figure 6 are
illustrative. The JSON in Figure 7 is a proposal, not part of the MCP specification.
"""
import json
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

# ---------- palette (from light.scss) ----------
BG = "#fbfaf7"
INK = "#1f2328"
MUTED = "#5f6b76"
RULE = "#e6e2da"
NAVY = "#1d4f73"
DEEP = "#0b1733"
AMBER = "#f5b041"
WARM = "#b36b00"
GREEN = "#2e7d5b"
RED = "#a93226"
NAVY_T, AMBER_T, GREEN_T, SAND_T = "#e5eef5", "#fdf1dc", "#e2f0e8", "#f2efe9"

SANS, MONO = "Inter", "JetBrains Mono"
plt.rcParams.update({
    "font.family": SANS, "font.size": 10, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.pad_inches": 0.18,
    "legend.frameon": False,
})
OUT = "figures/"


# ---------- drawing helpers ----------
def canvas(w, h, xmax, ymax):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, xmax); ax.set_ylim(0, ymax); ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def shadow(ax, x, y, w, h, r=0.28, z=1):
    for i, a in enumerate((0.035, 0.03, 0.025)):
        d = 0.05 + 0.05 * i
        ax.add_patch(FancyBboxPatch((x + d * 0.4, y - d), w, h,
                                    boxstyle=f"round,pad=0,rounding_size={r + d * 0.5}",
                                    fc=DEEP, ec="none", alpha=a, zorder=z))


def card(ax, x, y, w, h, title, sub=None, accent=NAVY, fill="white", eyebrow=None,
         fs=10.5, subfs=8.4, z=2, r=0.28, bar=True, align="center", mono_sub=False):
    """A white card with a faint shadow and a coloured accent bar on the left.
    fill set to a colour gives a solid card with white text."""
    solid = fill not in ("white", BG, NAVY_T, AMBER_T, GREEN_T, SAND_T)
    shadow(ax, x, y, w, h, r, z)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fill, ec="none" if solid else RULE, lw=0.9, zorder=z + 1))
    if bar and not solid:
        ax.add_patch(FancyBboxPatch((x + 0.16, y + 0.2), 0.09, h - 0.4,
                                    boxstyle="round,pad=0,rounding_size=0.045",
                                    fc=accent, ec="none", zorder=z + 2))
    tcol = "white" if solid else INK
    scol = "#dfe8f1" if solid else MUTED
    shift = 0.12 if bar and not solid else 0
    cx = x + w / 2 + shift if align == "center" else x + 0.55
    ha = "center" if align == "center" else "left"
    # stack eyebrow, title and subtitle around the card's centre, measured in points
    nsub = sub.count("\n") + 1 if sub else 0
    parts = []
    if eyebrow:
        parts.append((eyebrow.upper(), dict(fontsize=6.6, weight="semibold",
                                            color=accent if not solid else AMBER), 6.6 * 1.25 + 3))
    if title:
        parts.append((title, dict(fontsize=fs, weight="semibold", color=tcol), fs * 1.25 + 3))
    if sub:
        parts.append((sub, dict(fontsize=subfs, color=scol, linespacing=1.3,
                                fontfamily=MONO if mono_sub else SANS), subfs * 1.3 * nsub))
    total = sum(p[2] for p in parts)
    off = total / 2
    for text, kw, hgt in parts:
        ax.annotate(text, (cx, y + h / 2), xytext=(0, off), textcoords="offset points",
                    ha=ha, va="top", zorder=z + 3, **kw)
        off -= hgt


def arrow(ax, p, q, color=MUTED, rad=0.0, lw=1.5, ls="-", z=1.5, head=10, alpha=1.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>,head_length=0.55,head_width=0.3",
                                 mutation_scale=head, color=color, lw=lw, ls=ls, alpha=alpha,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0,
                                 capstyle="round", joinstyle="round", zorder=z))


def edge_point(x, y, w, h, tx, ty, gap=0.12):
    """Where the ray from the centre of box (x, y, w, h) toward (tx, ty) leaves the box."""
    cx, cy = x + w / 2, y + h / 2
    dx, dy = tx - cx, ty - cy
    t = min((w / 2 + gap) / abs(dx) if dx else 1e9, (h / 2 + gap) / abs(dy) if dy else 1e9)
    return cx + dx * t, cy + dy * t


def pill(ax, x, y, text, color=MUTED, fill=BG, fs=7.6, z=6, weight="medium", mono=False):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=color, weight=weight,
            fontfamily=MONO if mono else SANS, zorder=z,
            bbox=dict(boxstyle="round,pad=0.32,rounding_size=0.6", fc=fill, ec=RULE, lw=0.7))


def chip(ax, x, y, text, color=NAVY, fill=NAVY_T, fs=7.2, z=6):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=color, fontfamily=MONO,
            zorder=z, bbox=dict(boxstyle="round,pad=0.28,rounding_size=0.35", fc=fill, ec="none"))


def heading(ax, x, y, eyebrow, title, color=NAVY):
    ax.text(x, y, eyebrow.upper(), fontsize=7, weight="semibold", color=color, va="bottom")
    ax.text(x, y - 0.18, title, fontsize=11.5, weight="semibold", color=INK, va="top")


def tidy(ax, grid_axis="y"):
    ax.grid(axis=grid_axis, color=RULE, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=8.5)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(RULE if s == "left" else MUTED)




def _json_line(ax, x, y, line, fs):
    """Draw one line of JSON with simple syntax colours, token by token."""
    KEY, STR, LIT, PUN = "#8fc1e8", "#f5c77e", "#9fd8b8", "#aab4c0"
    tokens = re.findall(r'"[^"]*"\s*:|"[^"]*"?|\b(?:true|false|null)\b|-?\d+\.?\d*|\s+|.', line)
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(family=MONO, size=fs)
    cw = TextPath((0, 0), "M" * 10, prop=fp).get_extents().width / 10   # points per char
    cursor = 0
    for tok in tokens:
        if tok.endswith(":") and tok.startswith('"'):
            col = KEY
        elif tok.startswith('"'):
            col = STR
        elif re.fullmatch(r"true|false|null|-?\d+\.?\d*", tok):
            col = LIT
        else:
            col = PUN
        if tok.strip():
            ax.annotate(tok, (x, y), xytext=(cursor * cw, 0), textcoords="offset points",
                        fontfamily=MONO, fontsize=fs, color=col, va="center", ha="left", zorder=8)
        cursor += len(tok)



TEAL, PLUM = "#2a7f86", "#7a4e8c"
DOMCOL = [NAVY, GREEN, WARM, PLUM, TEAL, RED]


def blob(ax, cx, cy, rx, ry, color, alpha=0.08, z=0.5):
    from matplotlib.patches import Ellipse
    ax.add_patch(Ellipse((cx, cy), 2 * rx, 2 * ry, fc=color, ec=color, alpha=alpha, lw=0, zorder=z))
    ax.add_patch(Ellipse((cx, cy), 2 * rx, 2 * ry, fc="none", ec=color, alpha=0.35, lw=0.8,
                         ls=(0, (3, 3)), zorder=z))


def cluster_points(rng, centres, n=11, sx=0.85, sy=0.7):
    pts = []
    for (cx, cy) in centres:
        p = np.c_[rng.normal(cx, sx, n), rng.normal(cy, sy, n)]
        pts.append(p)
    return pts


# ---------- Figure 1: points on a plane, and the same points with structure ----------
def fig_plane():
    rng = np.random.default_rng(11)
    centres = [(3.0, 6.6), (8.4, 6.9), (13.8, 6.5), (3.4, 2.0), (8.8, 2.3), (14.2, 1.9)]
    names = ["invoices", "currency", "mail", "documents", "identity", "calendar"]
    pts = cluster_points(rng, centres)
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.9))
    for ax in axes:
        ax.set_xlim(0, 17.2); ax.set_ylim(-1.0, 10.6); ax.set_aspect("equal"); ax.axis("off")
    # left: flat
    ax = axes[0]
    ax.text(0.3, 10.35, "TODAY · A FLAT CATALOGUE", fontsize=7.2, weight="semibold", color=NAVY, va="top")
    ax.text(0.3, 9.85, "Points, and a path drawn at run time", fontsize=11.5, weight="semibold", va="top")
    for p in pts:
        ax.scatter(p[:, 0], p[:, 1], s=26, color="white", edgecolor=MUTED, lw=0.9, zorder=3)
    path = [pts[0][2], pts[1][4], pts[3][1], pts[2][6]]
    for a, b in zip(path, path[1:]):
        arrow(ax, a, b, color=AMBER, ls=(0, (3, 2.5)), lw=1.6, rad=0.18, z=4)
    for i, q in enumerate(path):
        ax.scatter(*q, s=60, color=AMBER, edgecolor=WARM, lw=1, zorder=5)
        ax.text(q[0] + 0.25, q[1] + 0.3, str(i + 1), fontsize=8, color=WARM, weight="bold", zorder=6)
    pill(ax, 8.6, -0.6, "the graph lives for one task, then it is forgotten", color=WARM, fs=8)
    # right: structured
    ax = axes[1]
    ax.text(0.3, 10.35, "PROPOSED · A LOCAL GRAPH", fontsize=7.2, weight="semibold", color=GREEN, va="top")
    ax.text(0.3, 9.85, "The same points, with edges that persist", fontsize=11.5, weight="semibold", va="top")
    for i, (p, (cx, cy)) in enumerate(zip(pts, centres)):
        col = DOMCOL[i]
        blob(ax, cx, cy, 2.15, 1.75, col)
        ax.text(cx, cy - 1.45, names[i], ha="center", va="top", fontsize=7.6, color=col,
                weight="semibold", zorder=6,
                bbox=dict(boxstyle="round,pad=0.2", fc=BG, ec="none", alpha=0.85))
        d = np.linalg.norm(p[:, None] - p[None], axis=-1)
        for a in range(len(p)):
            for b in np.argsort(d[a])[1:3]:
                ax.plot(*zip(p[a], p[b]), color=col, lw=0.7, alpha=0.45, zorder=2)
        ax.scatter(p[:, 0], p[:, 1], s=26, color="white", edgecolor=col, lw=1.0, zorder=3)
    bridges = [(0, 2, 1, 4), (0, 5, 2, 6), (0, 7, 3, 1), (2, 3, 5, 8), (4, 0, 3, 5), (1, 9, 4, 2)]
    for a, ia, b, ib in bridges:
        ax.plot(*zip(pts[a][ia], pts[b][ib]), color=AMBER, lw=1.6, alpha=0.9, zorder=2.5,
                solid_capstyle="round")
    pill(ax, 8.6, -0.6, "edges inside clusters, and a few strong bridges between them", color=GREEN, fs=8)
    fig.subplots_adjust(wspace=0.04)
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


# ---------- Figure 3: what grows when the catalogue grows ----------
def fig_growth():
    n = np.logspace(1, 4, 200)
    tok = 350
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9))
    ax = axes[0]
    ax.plot(n, n * tok, color=NAVY, lw=2.2)
    for lim, lab in ((200e3, "a 200k-token context window"), (1e6, "a 1M-token context window")):
        ax.axhline(lim, color=WARM, lw=1, ls=(0, (4, 3)))
        ax.text(11, lim * 1.15, lab, fontsize=8, color=WARM)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("tools in the catalogue"); ax.set_ylabel("tokens to list every definition")
    ax.set_title("Listing everything", loc="left", fontsize=11, weight="semibold")
    tidy(ax, "both")
    ax = axes[1]
    ax.plot(n, n ** 4, color=RED, lw=2.2, label="possible 4-step chains, $N^4$")
    ax.plot(n, n * 3, color=GREEN, lw=2.2, label="edges in a sparse graph, ~$3N$")
    ax.plot(n, n / 2, color=GREEN, lw=1.4, ls=(0, (4, 2)), label="workflows actually run, ~$N/2$")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("tools in the catalogue"); ax.set_ylabel("count")
    ax.set_title("Possible compositions against useful ones", loc="left", fontsize=11, weight="semibold")
    ax.legend(fontsize=8, loc="upper left")
    tidy(ax, "both")
    fig.tight_layout(w_pad=3)
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


# ---------- Figure 7: the neural lens ----------
def fig_neurons():
    rng = np.random.default_rng(4)
    fig, ax = canvas(11.6, 5.0, 30, 12.9)
    heading(ax, 0.2, 12.6, "The lens", "A layer of neurons", NAVY)
    heading(ax, 10.6, 12.6, "Applied to tools", "Two tasks light two small neighbourhoods of one grammar", GREEN)
    # left: a small neural layer, sparse activation
    L = [np.c_[np.full(5, 1.5), np.linspace(2.2, 9.6, 5)], np.c_[np.full(7, 4.6), np.linspace(1.4, 10.4, 7)],
         np.c_[np.full(5, 7.7), np.linspace(2.2, 9.6, 5)]]
    act = [{1, 3}, {2, 5}, {1}]
    for a, b in ((0, 1), (1, 2)):
        for i, p in enumerate(L[a]):
            for j, q in enumerate(L[b]):
                on = i in act[a] and j in act[b]
                ax.plot(*zip(p, q), color=AMBER if on else RULE, lw=1.8 if on else 0.6, zorder=1)
    for k, layer in enumerate(L):
        for i, p in enumerate(layer):
            on = i in act[k]
            ax.add_patch(Circle(p, 0.42, fc=AMBER if on else "white", ec=WARM if on else MUTED, lw=1.1, zorder=3))
    ax.text(4.6, 0.25, "weights learned · few units fire per input", ha="center", fontsize=8, color=MUTED)
    # right: tool network, clusters, two tasks
    centres = [(13.6, 9.0), (19.0, 9.6), (24.8, 9.0), (14.6, 3.6), (20.2, 3.4), (25.8, 3.9)]
    names = ["invoices", "currency", "mail", "documents", "identity", "calendar"]
    pts = []
    for i, (cx, cy) in enumerate(centres):
        blob(ax, cx, cy, 2.25, 1.75, DOMCOL[i], alpha=0.06)
        ax.text(cx, cy - 2.0, names[i], ha="center", va="top", fontsize=7.4, color=DOMCOL[i], weight="semibold")
        p = np.c_[rng.normal(cx, 0.85, 7), rng.normal(cy, 0.6, 7)]
        pts.append(p)
        d = np.linalg.norm(p[:, None] - p[None], axis=-1)
        for a in range(7):
            for b in np.argsort(d[a])[1:3]:
                ax.plot(*zip(p[a], p[b]), color=RULE, lw=0.8, zorder=1)
    bridges = [(0, 1, 1, 2), (0, 3, 2, 4), (3, 2, 4, 1), (1, 5, 4, 3), (2, 1, 5, 2), (0, 6, 3, 0)]
    for a, ia, b, ib in bridges:
        ax.plot(*zip(pts[a][ia], pts[b][ib]), color=RULE, lw=1.2, zorder=1)
    taskA = [(0, 1), (0, 4), (1, 2), (2, 4)]           # pay an invoice in euros, confirm by mail
    taskB = [(3, 2), (4, 1), (4, 5), (5, 3)]           # sign a contract, book a meeting
    for task, col in ((taskA, AMBER), (taskB, TEAL)):
        for (a, ia), (b, ib) in zip(task, task[1:]):
            ax.plot(*zip(pts[a][ia], pts[b][ib]), color=col, lw=2.4, zorder=2, solid_capstyle="round")
    for k, p in enumerate(pts):
        for i, q in enumerate(p):
            col = AMBER if (k, i) in taskA else TEAL if (k, i) in taskB else None
            ax.add_patch(Circle(q, 0.3 if col else 0.2, fc=col or "white", ec=WARM if col == AMBER else (col or MUTED),
                                lw=1, zorder=3))
    pill(ax, 15.6, 0.25, "task A · pay an invoice in euros, confirm by mail", color=WARM, fs=7.6)
    pill(ax, 24.6, 0.25, "task B · sign a contract, book the meeting", color=TEAL, fs=7.6)
    ax.plot([9.6, 9.6], [0.6, 12.0], color=RULE, lw=1)
    fig.savefig(OUT + "fig08.png"); plt.close(fig)




# ---------- Figure 2: a dictionary, and a grammar ----------
TOOLS = {"approve": "approve_invoice", "pay": "pay_supplier_invoice", "fx": "convert",
         "ledger": "post_ledger_entry", "mail": "send_message", "sched": "schedule_payment"}


def fig_grammar():
    fig, ax = canvas(11.6, 5.0, 30, 12.9)
    heading(ax, 0.2, 12.6, "MCP today", "A dictionary: every word defined, alone", NAVY)
    heading(ax, 11.4, 12.6, "What is missing", "A grammar: how the words combine", GREEN)
    defs = [("approve", "Approves an invoice."), ("pay", "Pays an approved invoice."),
            ("fx", "Converts an amount."), ("ledger", "Posts an accounting entry."),
            ("mail", "Sends a message."), ("sched", "Schedules a payment.")]
    for i, (k, d) in enumerate(defs):
        y = 10.0 - i * 1.75
        card(ax, 0.3, y, 9.0, 1.5, "", None, accent=NAVY, r=0.22)
        ax.text(0.9, y + 1.0, TOOLS[k], fontsize=8.6, fontfamily=MONO, color=INK, va="center", zorder=6)
        ax.text(0.9, y + 0.45, d, fontsize=7.8, color=MUTED, va="center", zorder=6)
    ax.plot([10.5, 10.5], [0.4, 12.0], color=RULE, lw=1)
    P = {"approve": (11.0, 5.6), "pay": (18.0, 5.6), "ledger": (24.9, 8.6), "fx": (18.0, 9.6),
         "mail": (24.9, 2.6), "sched": (18.0, 1.5)}
    W, H = 4.8, 1.5
    for k, (x, y) in P.items():
        main = k == "pay"
        card(ax, x, y, W, H, "", None, accent=GREEN, fill=GREEN if main else "white", r=0.22, bar=not main)
        ax.text(x + W / 2 + (0 if main else 0.1), y + H / 2, TOOLS[k], fontsize=7.8, fontfamily=MONO,
                color="white" if main else INK, ha="center", va="center", zorder=6)
    def link(a, b, rel, col, ls="-", rad=0.0, lab=None):
        (xa, ya), (xb, yb) = P[a], P[b]
        p = edge_point(xa, ya, W, H, xb + W / 2, yb + H / 2, 0.1)
        q = edge_point(xb, yb, W, H, xa + W / 2, ya + H / 2, 0.18)
        arrow(ax, p, q, color=col, ls=ls, rad=rad, lw=1.6, z=4)
        m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + (lab or 0))
        pill(ax, *m, rel, color=col, fs=7.4, mono=True)
    link("approve", "pay", "requires", NAVY, lab=0.6)
    link("pay", "ledger", "feeds", GREEN)
    link("fx", "pay", "used with", WARM)
    link("pay", "mail", "used with", WARM)
    link("sched", "pay", "alternative", MUTED, ls=(0, (4, 3)))
    ax.text(20.2, 0.25, "“Approve, convert, pay, then post and notify”: a sentence the grammar allows",
            ha="center", fontsize=8, color=GREEN, style="italic")
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


# ---------- Figure 4: where edges come from ----------
def fig_sources():
    fig, ax = canvas(11.6, 4.6, 30, 11.9)
    heading(ax, 0.2, 11.6, "Four sources", "Where the grammar comes from, and how far to trust it", NAVY)
    cols = [
        ("Computed", "from types", "outputSchema of A\nmatches inputSchema of B", NAVY,
         ["cheap, automatic", "verifiable", "finds data flow only"], "checked", "derived by any reader"),
        ("Declared", "by authors", "“pay requires approve”,\n“schedule is an alternative”", PLUM,
         ["knows intent", "partial: one side only", "can be self-serving"], "claimed", "published by the server"),
        ("Observed", "from use", "paths agents actually\nwalked, with weights", GREEN,
         ["what really happens", "needs history", "private by default"], "measured", "kept by the client"),
        ("Imposed", "by the organisation", "pairs that must never\nrun in one task", RED,
         ["encodes policy", "small, deliberate", "overrides the rest"], "enforced", "held by the gateway"),
    ]
    for i, (t, sub, ex, col, notes, trust, home) in enumerate(cols):
        x = 0.2 + i * 7.45
        card(ax, x, 5.4, 6.9, 4.3, t, ex, accent=col, eyebrow=sub, fs=11, subfs=8)
        for j, n in enumerate(notes):
            ax.text(x + 0.5, 4.5 - j * 0.85, ("+ " if j == 0 or (i in (0, 3) and j == 1) else "– ") + n,
                    fontsize=8.2, color=MUTED, va="center")
        pill(ax, x + 3.45, 1.15, "trust: " + trust, color=col, fs=8)
        ax.text(x + 3.45, 0.2, home, ha="center", fontsize=8, color=MUTED, style="italic")
    fig.savefig(OUT + "fig04.png"); plt.close(fig)


# ---------- Figure 5: an edge computed from types ----------
def fig_types():
    fig, ax = canvas(10.4, 4.0, 26, 10.0)
    heading(ax, 0.2, 9.7, "Computed edge", "When one tool's output is another tool's input", NAVY)
    def schema(x, y, name, label, fields, col):
        card(ax, x, y, 9.0, 5.4, "", None, accent=col)
        ax.text(x + 0.6, y + 4.75, name, fontsize=9.6, fontfamily=MONO, weight="semibold", va="center", zorder=6)
        ax.text(x + 0.6, y + 4.05, label, fontsize=7.6, color=MUTED, va="center", zorder=6)
        ys = {}
        for i, (f, t) in enumerate(fields):
            yy = y + 3.1 - i * 0.85
            ax.text(x + 0.9, yy, f, fontsize=8.4, fontfamily=MONO, color=INK, va="center", zorder=6)
            ax.text(x + 8.4, yy, t, fontsize=8, fontfamily=MONO, color=MUTED, va="center", ha="right", zorder=6)
            ys[f] = yy
        return ys
    a = schema(0.3, 1.3, "pay_supplier_invoice", "outputSchema", [("payment_id", "string"), ("amount", "number"),
                                                                    ("currency", "string"), ("paid_at", "date-time")], NAVY)
    b = schema(16.4, 1.3, "post_ledger_entry", "inputSchema (required)", [("payment_id", "string"), ("account", "string"),
                                                                          ("amount", "number")], GREEN)
    for f, col, lw in (("payment_id", GREEN, 2.2), ("amount", MUTED, 1.0)):
        arrow(ax, (9.4, a[f]), (16.3, b[f]), color=col, lw=lw, z=5)
    pill(ax, 12.85, (a["payment_id"] + b["payment_id"]) / 2 + 0.45, "feeds · via payment_id", color=GREEN, fs=7.8, mono=True)
    pill(ax, 12.85, (a["amount"] + b["amount"]) / 2 - 0.85, "same name, too weak alone", color=MUTED, fs=7.4)
    ax.text(13.0, 0.3, "An identifier that one tool creates and another requires is strong evidence; a shared generic field is not.",
            ha="center", fontsize=8, color=MUTED, style="italic")
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


# ---------- Figure 6: a tool entry with its grammar ----------
JSON = """{
  "name": "pay_supplier_invoice",
  "description": "Pays an approved invoice.",
  "inputSchema": { ... },
  "outputSchema": { ... },
  "annotations": { "destructiveHint": true,
                   "openWorldHint": true },
  "_meta": {
    "roles": ["pays"],
    "grammar": [
      { "rel": "requires",    "role": "approves" },
      { "rel": "usedWith",    "role": "converts" },
      { "rel": "requires",    "tool": "approve_invoice" },
      { "rel": "alternative", "tool": "schedule_payment" }
    ]
  }
}"""


def fig_entry():
    fig, ax = canvas(10.4, 5.6, 25, 13.4)
    shadow(ax, 0.2, 1.4, 13.9, 11.8, r=0.35)
    ax.add_patch(FancyBboxPatch((0.2, 1.4), 13.9, 11.8, boxstyle="round,pad=0,rounding_size=0.35",
                                fc=DEEP, ec="none", zorder=2))
    for i, c in enumerate(("#e06c5f", AMBER, "#5fb98a")):
        ax.add_patch(Circle((0.75 + i * 0.45, 12.7), 0.13, fc=c, ec="none", zorder=3))
    ax.text(13.7, 12.7, "tools/list → what the server publishes", ha="right", va="center",
            fontsize=7.4, color="#8592a3", fontfamily=MONO, zorder=3)
    lines = JSON.split("\n")
    top, step = 11.95, 0.56
    ys = {}
    for i, line in enumerate(lines):
        y = top - i * step
        _json_line(ax, 0.7, y, line, 7.6)
        for key, pat in (("ann", '"annotations"'), ("roles", '"roles"'), ("rule", '"role": "approves"'),
                         ("tool", '"tool": "approve_invoice"')):
            if pat in line and key not in ys:
                ys[key] = y
    notes = [
        ("ann", "Parts of speech MCP already has", "annotations say read-only, destructive,\nopen-world: the start of a role system", NAVY),
        ("roles", "Roles: what kind of word", "a small shared list: approves, pays,\nconverts, notifies, reads private data", PLUM),
        ("rule", "Rules over roles", "apply to tools never seen before:\nanything that pays needs an approval", GREEN),
        ("tool", "Edges to named tools", "the author's local knowledge; names are\nunique per server, so they need a registry", WARM),
    ]
    ny = [11.7, 8.9, 6.1, 3.3]
    for (key, t, txt, col), yy in zip(notes, ny):
        y0 = ys[key]
        ax.plot([14.15, 14.6], [y0, y0], color=col, lw=1.1, zorder=4)
        ax.plot([14.6, 15.0], [y0, yy], color=col, lw=1.1, zorder=4)
        ax.add_patch(Circle((14.15, y0), 0.09, fc=col, ec="none", zorder=5))
        card(ax, 15.05, yy - 1.1, 9.8, 2.2, "", None, accent=col, bar=True)
        ax.text(15.55, yy + 0.5, t, fontsize=9.8, weight="semibold", va="center", zorder=6)
        ax.text(15.55, yy - 0.32, txt, fontsize=7.9, color=MUTED, va="center", zorder=6, linespacing=1.35)
    pill(ax, 12.5, 0.45, "not published here: observed weights (kept by the client) and policy rules (kept by the gateway)",
         color=MUTED, fs=7.8)
    fig.savefig(OUT + "fig07.png"); plt.close(fig)


# ---------- Figure 6: two levels of grammar ----------
def fig_levels():
    fig, ax = canvas(11.6, 5.2, 30, 13.4)
    heading(ax, 0.2, 13.1, "Level 1 · grammar rules", "Rules over roles", GREEN)
    heading(ax, 15.4, 13.1, "Level 2 · collocations", "Habits of named tools", WARM)
    rules = [("pays", "requires", "approves", NAVY), ("returns payment_id", "feeds", "needs payment_id", GREEN),
             ("pays", "used with", "notifies", WARM), ("reads private data", "excludes", "sends externally", RED)]
    for i, (a, rel, b, col) in enumerate(rules):
        y = 10.2 - i * 2.35
        chip(ax, 3.0, y, a, color=INK, fill=SAND_T, fs=8)
        chip(ax, 11.4, y, b, color=INK, fill=SAND_T, fs=8)
        arrow(ax, (5.4, y), (8.9, y), color=col, lw=1.5)
        pill(ax, 7.15, y + 0.62, rel, color=col, fs=7.4, mono=True)
    ax.text(7.2, 0.9, "written once, about kinds of tools:\nholds for tools nobody has used yet", ha="center",
            fontsize=8.2, color=GREEN, linespacing=1.45)
    ax.plot([14.6, 14.6], [0.4, 12.4], color=RULE, lw=1)
    coll = [("pay_supplier_invoice", "fx-rates · convert", 0.71), ("pay_supplier_invoice", "mail · send_message", 0.64),
            ("create_contract", "sign · request_signature", 0.88), ("book_meeting", "calendar · find_slot", 0.93)]
    for i, (a, b, wgt) in enumerate(coll):
        y = 10.2 - i * 2.35
        chip(ax, 18.6, y, a, color=INK, fill=AMBER_T, fs=7.4)
        chip(ax, 26.6, y, b, color=INK, fill=AMBER_T, fs=7.4)
        arrow(ax, (21.0, y), (23.8, y), color=WARM, lw=0.8 + 3 * wgt)
        ax.text(22.4, y + 0.5, f"{wgt:.2f}", ha="center", fontsize=7.6, color=WARM, fontfamily=MONO)
    ax.text(22.6, 0.9, "learned from use, about specific tools:\nsharp for known work, silent for new work",
            ha="center", fontsize=8.2, color=WARM, linespacing=1.45)
    fig.savefig(OUT + "fig06.png"); plt.close(fig)


# ---------- Figure 8: who reads the grammar ----------
def fig_readers():
    fig, ax = canvas(8.4, 5.4, 20, 12.8)
    cx, cy = 10, 6.3
    card(ax, cx - 3.0, cy - 1.25, 6.0, 2.5, "Tool grammar", "data: typed edges,\nsources, weights",
         fill=GREEN, eyebrow="one source")
    readers = [
        ("Language model", "loads a neighbourhood,\nnot the catalogue", AMBER, "needs AI"),
        ("Workflow engine", "runs a known path\nwithout a model", NAVY, "no AI"),
        ("Policy gateway", "blocks pairs the\ngrammar excludes", NAVY, "no AI"),
        ("Contract tests", "checks every feeds\nedge still type-checks", NAVY, "no AI"),
        ("Catalogue", "shows how tools\ncombine, not just what", NAVY, "no AI"),
        ("Small router", "learned later, once\nthe same routes repeat", PLUM, "optional"),
    ]
    pos = [(2.0, 9.8), (12.4, 9.8), (14.2, 5.05), (12.4, 0.3), (2.0, 0.3), (0.2, 5.05)]
    hub = (cx - 3.0, cy - 1.25, 6.0, 2.5)
    for (t, s_, col, tag), (x, y) in zip(readers, pos):
        card(ax, x, y, 5.6, 2.5, t, s_, accent=col, eyebrow=tag, subfs=8)
        p = edge_point(*hub, x + 2.8, y + 1.25)
        q = edge_point(x, y, 5.6, 2.5, cx, cy, gap=0.22)
        lc = {AMBER: AMBER, PLUM: "#b49cc0"}.get(col, "#9db3c6")
        ax.add_patch(Circle(p, 0.11, fc=lc, ec="none", zorder=5))
        arrow(ax, p, q, color=lc, lw=1.5, z=5)
    fig.savefig(OUT + "fig09.png"); plt.close(fig)


if __name__ == "__main__":
    fig_plane(); fig_grammar(); fig_growth(); fig_sources(); fig_types()
    fig_levels(); fig_entry(); fig_neurons(); fig_readers()
