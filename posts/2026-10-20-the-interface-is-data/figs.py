"""Figures for "The Interface Is Data".

A new, softer style for the diagrams: Inter type, white cards with a faint shadow
and a coloured accent, colours taken from the site's own palette.

Figure 8 (right panel) uses the numbers reported by Anthropic (2025), "Code execution
with MCP". Everything else is a schematic, a count, or an illustrative value of my
own, as the captions say.
"""
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


# ---------- figures ----------
def fig_two_bindings():
    """Before: an interface bound when code is written. After: one read when the call is made."""
    fig, ax = canvas(8.6, 4.3, 21, 10.4)
    rows = [
        (6.4, "Before · SDK", "Bound when the code is written", NAVY, [
            ("Documentation", "read by a person"),
            ("Developer", "writes the glue"),
            ("Client library", "typed, versioned"),
            ("Service", "one SDK per\nlanguage"),
        ], "weeks, per pair", WARM),
        (0.4, "After · described tools", "Read when the call is made", GREEN, [
            ("Service", "publishes\nits tools"),
            ("tools/list", "names, text,\nschemas"),
            ("Any caller", "a model, a script,\na form"),
            ("tools/call", "checked against\nthe schema"),
        ], "seconds, at run time", GREEN),
    ]
    for y, eb, title, col, cards, note, ncol in rows:
        heading(ax, 0.2, y + 3.15, eb, title, col)
        pill(ax, 19.3, y + 2.75, note, color=ncol, fs=8)
        for i, (t, s) in enumerate(cards):
            x = 0.2 + i * 5.3
            card(ax, x, y, 4.4, 2.1, t, s, accent=col, fs=10, subfs=8.2)
            if i < len(cards) - 1:
                arrow(ax, (x + 4.5, y + 1.05), (x + 5.2, y + 1.05), color=col)
    ax.plot([0.2, 20.6], [5.15, 5.15], color=RULE, lw=1)
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


JSON = """{
  "name": "route_invoice",
  "title": "Route a supplier invoice",
  "description": "Assigns an invoice to a budget
                  and to the person who approves it.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "invoice_id": { "type": "string" },
      "amount_chf": { "type": "number" }
    },
    "required": ["invoice_id"]
  },
  "outputSchema": {
    "properties": { "budget":   { "type": "string" },
                    "approver": { "type": "string" } }
  },
  "annotations": { "readOnlyHint": false,
                   "idempotentHint": true }
}"""


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


def fig_anatomy():
    """A tool description, and who reads each part of it."""
    fig, ax = canvas(9.0, 5.6, 22, 13.6)
    shadow(ax, 0.2, 0.3, 11.6, 13.0, r=0.35)
    ax.add_patch(FancyBboxPatch((0.2, 0.3), 11.6, 13.0, boxstyle="round,pad=0,rounding_size=0.35",
                                fc=DEEP, ec="none", zorder=2))
    for i, c in enumerate(("#e06c5f", AMBER, "#5fb98a")):
        ax.add_patch(Circle((0.75 + i * 0.45, 12.8), 0.13, fc=c, ec="none", zorder=3))
    ax.text(11.4, 12.8, "tools/list → one entry", ha="right", va="center", fontsize=7.4,
            color="#8592a3", fontfamily=MONO, zorder=3)
    lines = JSON.split("\n")
    top, step = 12.05, 0.565
    ys = {}
    for i, line in enumerate(lines):
        y = top - i * step
        _json_line(ax, 0.75, y, line, 7.6)
        k = re.search(r'"(\w+)"\s*:', line)
        if k and line.startswith('  "'):
            ys[k.group(1)] = y
    notes = [  # key, title, text, reader, colour
        ("name", "Name", "a stable handle to call it by", "everyone", MUTED),
        ("description", "Description", "plain words: what it does and when", "a model or a person", AMBER),
        ("inputSchema", "Input schema", "what it accepts, as JSON Schema", "a validator, a form", NAVY),
        ("outputSchema", "Output schema", "what it returns, so tools can be chained", "a planner, a type checker", NAVY),
        ("annotations", "Hints", "read-only? destructive? safe to retry?", "a policy gateway", GREEN),
    ]
    ny = [12.15, 9.75, 7.35, 4.95, 2.55]
    for (key, t, txt, who, col), yy in zip(notes, ny):
        y0 = ys[key]
        ax.plot([11.85, 12.6], [y0, y0], color=col, lw=1.1, zorder=4)
        ax.plot([12.6, 13.05], [y0, yy], color=col, lw=1.1, zorder=4)
        ax.add_patch(Circle((11.85, y0), 0.09, fc=col, ec="none", zorder=5))
        card(ax, 13.1, yy - 1.0, 8.7, 2.0, "", None, accent=col, bar=True)
        ax.text(13.6, yy + 0.5, t, fontsize=10, weight="semibold", va="center", zorder=6)
        ax.text(13.6, yy - 0.05, txt, fontsize=8.2, color=MUTED, va="center", zorder=6)
        ax.text(13.6, yy - 0.58, "read by: " + who, fontsize=7.6, color=col if col != AMBER else WARM,
                weight="medium", va="center", zorder=6)
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


def fig_many_readers():
    """One description, six readers; only one of them needs AI."""
    fig, ax = canvas(8.4, 5.4, 20, 12.8)
    cx, cy = 10, 6.3
    card(ax, cx - 3.0, cy - 1.25, 6.0, 2.5, "Tool description", "data: names, text,\nschemas, hints",
         fill=NAVY, eyebrow="one source")
    readers = [
        ("Language model", "chooses a tool,\nfills its arguments", AMBER, "needs AI"),
        ("Workflow or script", "calls it by name,\nno model involved", GREEN, "no AI"),
        ("Form generator", "renders a screen\nfrom the input schema", GREEN, "no AI"),
        ("Test generator", "builds valid and invalid\ncalls from the schema", GREEN, "no AI"),
        ("Policy gateway", "allows or blocks a call\nfrom its hints", GREEN, "no AI"),
        ("Catalogue", "search, docs and\nusage, kept current", GREEN, "no AI"),
    ]
    pos = [(2.0, 9.8), (12.4, 9.8), (14.2, 5.05), (12.4, 0.3), (2.0, 0.3), (0.2, 5.05)]
    hub = (cx - 3.0, cy - 1.25, 6.0, 2.5)
    for (t, s, col, tag), (x, y) in zip(readers, pos):
        card(ax, x, y, 5.6, 2.5, t, s, accent=col, eyebrow=tag, subfs=8)
        p = edge_point(*hub, x + 2.8, y + 1.25)
        q = edge_point(x, y, 5.6, 2.5, cx, cy, gap=0.22)
        lc = col if col == AMBER else "#8fb5a0"
        ax.add_patch(Circle(p, 0.11, fc=lc, ec="none", zorder=5))
        arrow(ax, p, q, color=lc, lw=1.5, z=5)
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


def fig_adapters():
    """How many adapters: one per client-service pair, or one per side."""
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    M = np.arange(1, 51)
    for N, ls, a in [(10, "-", 1.0), (5, (0, (4, 3)), 0.75)]:
        ax.plot(M, N * M, color=WARM, lw=2.2, ls=ls, alpha=a, solid_capstyle="round")
        ax.plot(M, N + M, color=GREEN, lw=2.2, ls=ls, alpha=a, solid_capstyle="round")
        ax.text(50.8, N * 50, f"one per pair, {N} clients:  {N * 50}", va="center", fontsize=8.4,
                color=WARM, weight="medium")
        ax.text(50.8, N + 50 + (14 if N == 10 else -14), f"one per side, {N} clients:  {N + 50}",
                va="center", fontsize=8.4, color=GREEN, weight="medium")
    ax.fill_between(M, 10 + M, 10 * M, color=AMBER, alpha=0.10, lw=0)
    ax.annotate("the glue nobody\nhas to write", (30, 190), fontsize=8.6, color=WARM,
                ha="center", style="italic")
    ax.set_xlim(0, 50); ax.set_ylim(0, 520)
    ax.set_xlabel("services to connect", fontsize=9.5)
    ax.set_ylabel("adapters to write and maintain", fontsize=9.5)
    tidy(ax)
    fig.savefig(OUT + "fig04.png"); plt.close(fig)


def fig_web():
    """A web of tools: clients, a gateway, a composite server that is also a client,
    atomic servers, and edges that can be computed from the schemas."""
    fig, ax = canvas(9.4, 6.0, 25.2, 15.8)
    clients = [("Assistant", "a model in a loop", AMBER, 11.4), ("Workflow engine", "no model", GREEN, 7.4),
               ("Nightly script", "no model", GREEN, 3.4)]
    for t, s, col, y in clients:
        card(ax, 0.2, y, 4.7, 2.1, t, s, accent=col, eyebrow="client", fs=10)
    gw = (6.2, 4.9, 3.5, 6.6)
    card(ax, *gw, "Gateway", "one catalogue\nidentity\npolicy\nlogs", fill=NAVY, eyebrow="hub", subfs=8.2)
    for _, _, col, y in clients:
        arrow(ax, (5.0, y + 1.05), (6.1, 8.2 + (y - 7.4) * 0.3), color=MUTED, lw=1.3, z=5)
    card(ax, 11.5, 11.6, 5.4, 2.7, "Invoice desk", "route_invoice()", accent=AMBER,
         eyebrow="server and client", mono_sub=True)
    card(ax, 11.5, 1.7, 5.4, 2.2, "Mail", "send()", accent=NAVY, eyebrow="server", mono_sub=True)
    AX, AW, AH = 18.7, 5.2, 2.2
    atoms = [("ERP", "match_po()", 12.8), ("Documents", "extract_invoice()", 9.6),
             ("Decision model", "pick_approver()", 6.4), ("Knowledge graph", "rules_for()", 3.2)]
    for t, s, y in atoms:
        card(ax, AX, y, AW, AH, t, s, accent=NAVY, eyebrow="server", mono_sub=True)
    arrow(ax, (9.8, 10.6), (11.4, 12.4), color=MUTED, lw=1.3, z=5)
    arrow(ax, (9.8, 5.6), (11.4, 3.2), color=MUTED, lw=1.3, z=5)
    arrow(ax, (9.8, 7.0), (18.6, 4.3), color=MUTED, lw=1.3, z=5)
    for y in (13.9, 10.7, 7.5):
        arrow(ax, (17.0, 12.95), (18.6, y), color=AMBER, lw=1.6, z=5)
    # typed edges: an output schema that fits an input schema, drawn as brackets on the right
    RX = AX + AW
    for (y1, y2, lab) in [(10.7, 13.9, "Invoice"), (4.3, 7.5, "Rules")]:
        ax.plot([RX + 0.1, RX + 0.6, RX + 0.6], [y1, y1, y2], color=GREEN, lw=1.4, ls=(0, (2, 2)),
                zorder=5, solid_capstyle="round")
        arrow(ax, (RX + 0.6, y2), (RX + 0.12, y2), color=GREEN, lw=1.4, z=5)
        pill(ax, RX + 0.6, (y1 + y2) / 2, lab, color=GREEN, fs=7.2, mono=True)
    ly = 0.55
    ax.plot([0.3, 1.3], [ly, ly], color=MUTED, lw=1.5)
    ax.text(1.5, ly, "a call", va="center", fontsize=8, color=MUTED)
    ax.plot([3.4, 4.4], [ly, ly], color=AMBER, lw=1.6)
    ax.text(4.6, ly, "a server calling other servers", va="center", fontsize=8, color=MUTED)
    ax.plot([10.6, 11.6], [ly, ly], color=GREEN, lw=1.5, ls=(0, (2, 2)))
    ax.text(11.8, ly, "an output that fits an input, found by reading the schemas", va="center",
            fontsize=8, color=MUTED)
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


def fig_shapes():
    """The same tools, arranged as a hub, a mesh or layers."""
    fig, axes = plt.subplots(1, 3, figsize=(9.0, 3.7))
    rng = np.random.default_rng(3)

    def node(ax, x, y, kind):
        style = {"client": dict(fc="white", ec=NAVY, lw=1.6, r=0.42),
                 "server": dict(fc=NAVY, ec="none", lw=0, r=0.42),
                 "hub": dict(fc=DEEP, ec=AMBER, lw=1.8, r=0.62),
                 "composite": dict(fc=AMBER, ec="none", lw=0, r=0.5),
                 "agent": dict(fc=GREEN, ec="none", lw=0, r=0.55)}[kind]
        r = style.pop("r")
        ax.add_patch(Circle((x + 0.05, y - 0.08), r, fc=DEEP, ec="none", alpha=0.07, zorder=2))
        ax.add_patch(Circle((x, y), r, zorder=3, **style))

    def edge(ax, a, b, col="#b9c3cc", lw=1.2, ls="-"):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=col, lw=lw, ls=ls, zorder=1, solid_capstyle="round")

    titles = [("Hub", "one gateway, one place\nfor identity and policy"),
              ("Mesh", "servers call each other;\nno single choke point"),
              ("Layers", "atomic tools, composites,\nthen agents exposed as tools")]
    for ax, (t, s) in zip(axes, titles):
        ax.set_xlim(0, 10); ax.set_ylim(-2.6, 10); ax.set_aspect("equal"); ax.axis("off")
        ax.text(5, -0.9, t, ha="center", fontsize=11, weight="semibold")
        ax.text(5, -1.55, s, ha="center", va="top", fontsize=8, color=MUTED, linespacing=1.35)
    # hub
    ax = axes[0]
    hub = (5, 5)
    ang = np.linspace(0, 2 * np.pi, 9)[:-1] + 0.2
    for i, a in enumerate(ang):
        p = (5 + 3.6 * np.cos(a), 5 + 3.6 * np.sin(a))
        edge(ax, hub, p)
        node(ax, *p, "client" if i in (0, 3, 6) else "server")
    node(ax, *hub, "hub")
    # mesh
    ax = axes[1]
    pts = [(1.6, 7.6), (5.0, 8.6), (8.4, 7.4), (2.4, 4.4), (5.6, 5.0), (8.6, 3.8), (1.4, 1.2),
           (4.6, 1.6), (7.8, 0.9)]
    pairs = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 4), (2, 5), (3, 4), (4, 5), (3, 6), (3, 7), (4, 7),
             (5, 8), (7, 8), (6, 7), (4, 8)]
    for a, b in pairs:
        edge(ax, pts[a], pts[b])
    for i, p in enumerate(pts):
        node(ax, *p, "client" if i in (0, 6) else ("composite" if i == 4 else "server"))
    # layers
    ax = axes[2]
    L = {"agent": [(5, 8.4)], "composite": [(2.6, 5.4), (7.4, 5.4)],
         "server": [(0.9, 1.6), (3.6, 1.6), (6.4, 1.6), (9.1, 1.6)]}
    for c in L["composite"]:
        edge(ax, L["agent"][0], c, col=AMBER, lw=1.5)
    for c, kids in zip(L["composite"], [(0, 1, 2), (1, 2, 3)]):
        for k in kids:
            edge(ax, c, L["server"][k], col="#9fb7cc", lw=1.3)
    for kind, ps in L.items():
        for p in ps:
            node(ax, *p, kind)
    for y, lab in [(8.4, "agent"), (5.4, "composite"), (1.6, "atomic")]:
        ax.text(10.2, y, lab, fontsize=7, color=MUTED, va="center", ha="left")
    fig.subplots_adjust(wspace=0.12)
    fig.savefig(OUT + "fig06.png"); plt.close(fig)


def fig_zoom():
    """The same capability offered at four grains."""
    fig, ax = canvas(9.2, 5.0, 24.5, 13.2)
    levels = [
        ("Capability", "one agent, used as a tool", AMBER, ["invoices.handle(task)"]),
        ("Workflows", "a few steps, one result", GREEN, ["route_invoice", "dispute_invoice", "close_month"]),
        ("Tools", "one action each", NAVY, ["extract", "match_po", "assign_budget", "pick_approver", "notify"]),
        ("Operations", "the API underneath", MUTED,
         ["GET /po/{id}", "POST /approvals", "GET /budgets", "PUT /invoices/{id}", "POST /mail", "…"]),
    ]
    CH, PAD, GAP = 0.172, 0.5, 0.5      # data units per mono character at 7.2 pt, padding, gap
    cx, y, h, prev = 13.0, 10.2, 2.1, 0
    for name, sub, col, chips in levels:
        cws = [len(c) * CH + PAD for c in chips]
        need = sum(cws) + GAP * (len(chips) - 1) + 1.2
        w = max(need, prev + 3.2)
        prev = w
        x0 = cx - w / 2
        tint = {AMBER: AMBER_T, GREEN: GREEN_T, NAVY: NAVY_T, MUTED: SAND_T}[col]
        shadow(ax, x0, y, w, h, 0.3)
        ax.add_patch(FancyBboxPatch((x0, y), w, h, boxstyle="round,pad=0,rounding_size=0.3",
                                    fc=tint, ec="none", zorder=2))
        ax.text(0.2, y + h / 2 + 0.3, name, fontsize=10.5, weight="semibold", va="center")
        ax.text(0.2, y + h / 2 - 0.35, sub, fontsize=8, color=MUTED, va="center")
        xc = cx - (sum(cws) + GAP * (len(chips) - 1)) / 2
        for c, cw in zip(chips, cws):
            chip(ax, xc + cw / 2, y + h / 2, c, color=col if col != AMBER else WARM, fill="white", fs=7.2)
            xc += cw + GAP
        y -= 2.9
    arrow(ax, (23.3, 12.0), (23.3, 1.5), color=NAVY, lw=1.6)
    arrow(ax, (24.1, 1.5), (24.1, 12.0), color=WARM, lw=1.6)
    ax.text(22.95, 6.75, "zoom in: more control, more calls", rotation=90, ha="center", va="center",
            fontsize=7.6, color=NAVY)
    ax.text(24.45, 6.75, "zoom out: fewer calls, more trust", rotation=270, ha="center", va="center",
            fontsize=7.6, color=WARM)
    ax.text(13.0, 0.35, "one server can publish all four levels; each caller picks its grain",
            ha="center", fontsize=8.6, color=INK, style="italic")
    fig.savefig(OUT + "fig07.png"); plt.close(fig)


def fig_context():
    """What the caller must read before acting. Left: illustrative; right: Anthropic (2025)."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.7), gridspec_kw=dict(width_ratios=[1.35, 1]))
    # left: progressive disclosure for a catalogue of 200 tools (illustrative assumptions)
    labels = ["names\nonly", "names +\ndescriptions", "every\nschema", "names, then\n3 on demand"]
    vals = [200 * 10, 200 * 50, 200 * 450, 200 * 10 + 3 * 450]
    cols = [GREEN, NAVY, WARM, GREEN]
    x = np.arange(len(vals))
    a1.bar(x, vals, color=cols, width=0.62, zorder=3)
    for xi, v in zip(x, vals):
        a1.text(xi, v + 1800, f"{v:,}".replace(",", " "), ha="center", fontsize=8.4, weight="medium")
    a1.set_xticks(x); a1.set_xticklabels(labels, fontsize=7.8)
    a1.set_ylabel("tokens read before the first call", fontsize=9)
    a1.set_ylim(0, 100000)
    a1.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v / 1000)}k"))
    a1.set_title("A catalogue of 200 tools (illustrative)", fontsize=9.5, weight="semibold", loc="left",
                 color=INK, pad=10)
    tidy(a1)
    # right: Anthropic's reported example
    v = [150000, 2000]
    a2.barh([1, 0], v, color=[WARM, GREEN], height=0.5, zorder=3)
    a2.set_yticks([1, 0]); a2.set_yticklabels(["every tool definition\nloaded up front",
                                                "tools read as files,\nwhen needed"], fontsize=7.9)
    for yi, vi in zip([1, 0], v):
        a2.text(vi + 3000, yi, f"{vi:,}".replace(",", " "), va="center", fontsize=8.4, weight="medium")
    a2.set_xlim(0, 185000)
    a2.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v / 1000)}k"))
    a2.set_xlabel("tokens", fontsize=9)
    a2.set_title("One workflow, reported by Anthropic", fontsize=9.5, weight="semibold", loc="left",
                 color=INK, pad=10)
    a2.text(80000, 0, "−98.7%", va="center", fontsize=10, color=GREEN, weight="semibold")
    tidy(a2, "x")
    fig.subplots_adjust(wspace=0.55)
    fig.savefig(OUT + "fig08.png"); plt.close(fig)


def fig_where():
    """Where each kind of binding belongs: how often a call repeats, how much the task varies."""
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    xx, yy = np.meshgrid(np.linspace(0, 6, 300), np.linspace(0, 1, 200))
    score = (xx / 6) - yy            # high: frequent and stable; low: rare and varied
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("w", [AMBER_T, "#f6f3ec", GREEN_T])
    ax.imshow(score, extent=(0, 6, 0, 1), origin="lower", aspect="auto", cmap=cmap, zorder=0)
    ax.text(0.2, 0.95, "AGENT LOOP OVER DESCRIBED TOOLS", fontsize=7.4, weight="semibold", color=WARM, va="top")
    ax.text(0.2, 0.905, "explore, combine, ask", fontsize=8, color=MUTED, va="top")
    ax.text(0.2, 0.12, "DESCRIBED TOOLS, CALLED BY CODE", fontsize=7.4, weight="semibold", color=NAVY)
    ax.text(0.2, 0.065, "scripts and workflows, no model", fontsize=8, color=MUTED)
    ax.text(5.8, 0.12, "COMPILED PATH", fontsize=7.4, weight="semibold", color=GREEN, ha="right")
    ax.text(5.8, 0.065, "typed SDK, fixed recipe, decision model", fontsize=8, color=MUTED, ha="right")
    pts = [(0.5, 0.76, "a supplier's\nunusual question", "left"), (1.35, 0.6, "month-end exception", "left"),
           (2.8, 0.4, "weekly report", "left"), (4.05, 0.3, "nightly sync", "above"),
           (5.1, 0.22, "route an invoice,\n10,000 a day", "right")]
    for x, y, lab, side in pts:
        ax.scatter(x, y, s=46, color="white", edgecolor=DEEP, lw=1.3, zorder=4)
        if side == "left":
            ax.text(x + 0.11, y, lab, fontsize=7.8, color=INK, zorder=4, va="center", linespacing=1.25)
        elif side == "above":
            ax.text(x, y + 0.035, lab, fontsize=7.8, color=INK, zorder=4, ha="center", va="bottom")
        else:
            ax.text(x, y + 0.05, lab, fontsize=7.8, color=INK, zorder=4, ha="center", va="bottom",
                    linespacing=1.25)
    ax.add_patch(FancyArrowPatch((1.7, 0.8), (4.8, 0.42), arrowstyle="-|>,head_length=0.6,head_width=0.32",
                                 mutation_scale=12, color=DEEP, lw=1.6, ls=(0, (5, 3)),
                                 connectionstyle="arc3,rad=-0.22", zorder=3))
    ax.text(3.75, 0.76, "compile what repeats", fontsize=8.8, color=DEEP, style="italic", weight="medium")
    ax.set_xlim(0, 6); ax.set_ylim(0, 1)
    ax.set_xticks([0.5, 2, 3.5, 5]); ax.set_xticklabels(["once", "weekly", "daily", "thousands a day"])
    ax.set_yticks([0.1, 0.9]); ax.set_yticklabels(["same every time", "different every time"])
    ax.set_xlabel("how often the same call is made", fontsize=9.5)
    ax.set_ylabel("how much the task varies", fontsize=9.5)
    ax.tick_params(length=0, labelsize=8.4)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.savefig(OUT + "fig14.png"); plt.close(fig)


def fig_alternatives():
    """A map of the alternatives: when the interface is bound, and who reads it. My own placement."""
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    items = [  # x: bound at write time (0) to run time (1); y: read by compiler/person (0) to model (1)
        ("Typed SDK, gRPC", 0.08, 0.10, "old"), ("OpenAPI + code generation", 0.22, 0.24, "old"),
        ("GraphQL introspection", 0.55, 0.18, "old"), ("REST hypermedia (HATEOAS)", 0.83, 0.08, "old"),
        ("Function calling\n(schemas in the app)", 0.30, 0.62, "new"),
        ("CLI + --help", 0.62, 0.40, "new"),
        ("Code mode: the model\nwrites code against an SDK", 0.40, 0.79, "new"),
        ("MCP", 0.80, 0.70, "mcp"), ("Agent Skills (files read on demand)", 0.90, 0.94, "new"),
        ("A2A (agents as peers)", 0.93, 0.57, "new"),
    ]
    col = {"old": NAVY, "new": GREEN, "mcp": WARM}
    for t, x, y, k in items:
        s = 140 if k == "mcp" else 60
        ax.scatter(x, y, s=s, color=col[k] if k != "mcp" else AMBER, edgecolor="white" if k != "mcp" else WARM,
                   lw=1.2, zorder=4)
        ha = "right" if x > 0.75 and k != "mcp" else "left"
        dx = -0.025 if ha == "right" else 0.025
        if k == "mcp":
            ax.text(x + 0.035, y, t, fontsize=11, weight="semibold", color=WARM, va="center")
        else:
            ax.text(x + dx, y, t, fontsize=8, color=INK, va="center", ha=ha, linespacing=1.2)
    ax.axhline(0.5, color=RULE, lw=1, zorder=1); ax.axvline(0.5, color=RULE, lw=1, zorder=1)
    ax.set_xlim(0, 1.02); ax.set_ylim(0, 1.0)
    ax.set_xticks([0.03, 0.97]); ax.set_xticklabels(["bound when code is written", "bound when the call is made"])
    ax.get_xticklabels()[0].set_ha("left"); ax.get_xticklabels()[1].set_ha("right")
    ax.set_yticks([0.03, 0.97]); ax.set_yticklabels(["read by a person\nor a compiler", "read by\na model"])
    ax.get_yticklabels()[0].set_va("bottom"); ax.get_yticklabels()[1].set_va("top")
    ax.tick_params(length=0, labelsize=8.4)
    for s in ax.spines.values():
        s.set_visible(False)
    leg = [plt.Line2D([], [], marker="o", ls="", color=NAVY, label="before agents", markersize=7),
           plt.Line2D([], [], marker="o", ls="", color=GREEN, label="made for agents", markersize=7)]
    ax.legend(handles=leg, loc="lower right", bbox_to_anchor=(1.0, 0.18), fontsize=8)
    fig.savefig(OUT + "fig13.png"); plt.close(fig)


def fig_embedding_map():
    """Tool descriptions as points in a space of meaning; a question finds its neighbours.
    Positions are hand-placed for legibility: a schematic, not a real embedding."""
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    PURPLE = "#6c5b7b"
    clusters = [
        ("Invoices and payments", GREEN, (2.6, 7.35), {
            "route_invoice": (3.4, 6.3), "pick_approver": (2.2, 4.9), "assign_budget": (2.0, 5.9),
            "match_po": (2.4, 6.7), "pay_invoice": (0.9, 6.9), "dispute_invoice": (3.6, 7.0)}),
        ("Documents", NAVY, (7.9, 7.35), {
            "extract_invoice": (7.2, 6.4), "ocr_page": (8.2, 6.8), "summarise_pdf": (8.9, 6.1),
            "archive": (7.6, 5.6), "sign_pdf": (8.6, 5.4)}),
        ("People and rules", PURPLE, (1.9, 0.35), {
            "rules_for": (2.9, 2.5), "org_chart": (1.3, 1.6), "who_is_absent": (2.2, 1.1),
            "policy_text": (0.9, 2.6)}),
        ("Data", MUTED, (7.3, 1.85), {
            "get_supplier": (5.6, 4.4), "run_sql": (7.5, 3.5), "list_budgets": (7.5, 4.4),
            "export_csv": (7.1, 2.6)}),
        ("Messages", WARM, (9.3, 0.35), {
            "notify": (8.6, 2.1), "send_mail": (9.6, 2.6), "post_chat": (10.0, 1.5),
            "schedule_call": (8.9, 1.2)}),
    ]
    q = (3.9, 4.0)
    near = ["pick_approver", "assign_budget", "rules_for", "route_invoice", "get_supplier"]
    lab_off = {"pick_approver": (-0.25, 0, "right", "center"), "assign_budget": (0, 0.3, "center", "bottom"),
               "rules_for": (0.25, 0, "left", "center"), "route_invoice": (0.25, -0.05, "left", "center"),
               "get_supplier": (0, 0.32, "center", "bottom")}
    for name, col, (lx, ly), pts in clusters:
        ax.text(lx, ly, name.upper(), ha="center", fontsize=6.8, weight="semibold", color=col)
        for t, (x, y) in pts.items():
            hit = t in near
            if hit:
                ax.plot([q[0], x], [q[1], y], color=AMBER, lw=1.3, zorder=2, solid_capstyle="round")
            ax.scatter(x, y, s=70 if hit else 28, color=col, edgecolor="white", lw=1.0, zorder=4,
                       alpha=1 if hit else 0.45)
            if hit:
                dx, dy, ha, va = lab_off[t]
                ax.text(x + dx, y + dy, t, ha=ha, va=va, fontsize=7.4, fontfamily=MONO, color=INK, zorder=5)
    ax.add_patch(Circle(q, 2.75, fc=AMBER, ec="none", alpha=0.07, zorder=1))
    ax.add_patch(Circle(q, 2.75, fc="none", ec=AMBER, lw=0.9, ls=(0, (3, 3)), zorder=1))
    ax.scatter(*q, s=260, marker="*", color=AMBER, edgecolor=WARM, lw=1, zorder=6)
    ax.text(q[0] + 0.3, q[1] - 0.45, "“who must approve this\nsupplier invoice?”", fontsize=8.4,
            style="italic", color=WARM, va="top", zorder=6, linespacing=1.3,
            bbox=dict(boxstyle="round,pad=0.25", fc=BG, ec="none", alpha=0.9))
    X = 11.3
    shadow(ax, X, 1.6, 4.1, 5.6, 0.25)
    ax.add_patch(FancyBboxPatch((X, 1.6), 4.1, 5.6, boxstyle="round,pad=0,rounding_size=0.25",
                                fc="white", ec=RULE, lw=0.9, zorder=3))
    ax.text(X + 0.35, 6.7, "RETURNED: 5 OF 23 TOOLS", fontsize=6.8, weight="semibold", color=WARM, zorder=4)
    for i, t in enumerate(near):
        ax.text(X + 0.35, 6.0 - i * 0.75, f"{i + 1}", fontsize=7.8, color=MUTED, zorder=4)
        ax.text(X + 0.8, 6.0 - i * 0.75, t, fontsize=7.8, fontfamily=MONO, color=INK, zorder=4)
    ax.text(X + 0.35, 2.0, "only their schemas are read", fontsize=7.4, color=MUTED, style="italic", zorder=4)
    ax.set_xlim(0.2, 15.6); ax.set_ylim(0.0, 7.8); ax.set_aspect("equal"); ax.axis("off")
    fig.savefig(OUT + "fig09.png"); plt.close(fig)


GRAPH = """{
  "returns": "graph",
  "name": "route_invoice@v3",
  "nodes": {
    "doc":   { "tool": "extract_invoice",
               "args": { "file": "$input.file" } },
    "po":    { "tool": "match_po",
               "args": { "invoice": "$doc" } },
    "rules": { "tool": "rules_for",
               "args": { "supplier": "$doc.supplier" } },
    "who":   { "tool": "pick_approver",
               "args": { "po": "$po", "rules": "$rules" } },
    "send":  { "tool": "notify",
               "args": { "to": "$who.approver" } }
  },
  "output": "$who",
  "limits": { "max_calls": 8, "max_depth": 2 }
}"""


def fig_returned_graph():
    """A tool whose result is a small program: a graph of tool calls, checked, then run."""
    fig, ax = canvas(9.6, 5.4, 25.6, 14.2)
    shadow(ax, 0.2, 0.3, 13.4, 13.6, r=0.35)
    ax.add_patch(FancyBboxPatch((0.2, 0.3), 13.4, 13.6, boxstyle="round,pad=0,rounding_size=0.35",
                                fc=DEEP, ec="none", zorder=2))
    for i, c in enumerate(("#e06c5f", AMBER, "#5fb98a")):
        ax.add_patch(Circle((0.75 + i * 0.45, 13.4), 0.13, fc=c, ec="none", zorder=3))
    ax.text(13.2, 13.4, "plan_invoice_routing() → result", ha="right", va="center", fontsize=7.4,
            color="#8592a3", fontfamily=MONO, zorder=3)
    for i, line in enumerate(GRAPH.split("\n")):
        _json_line(ax, 0.7, 12.65 - i * 0.6, line, 7.4)
    # the graph it describes
    X0 = 14.4
    ax.text(X0 + 0.1, 13.55, "WHAT THE EXECUTOR RUNS", fontsize=7, weight="semibold", color=GREEN)
    ax.text(X0 + 0.1, 13.0, "no model in the loop", fontsize=8, color=MUTED)
    nodes = {"doc": (X0 + 5.4, 11.0, "extract_invoice"), "po": (X0 + 2.0, 8.2, "match_po"),
             "rules": (X0 + 8.8, 8.2, "rules_for"), "who": (X0 + 5.4, 5.4, "pick_approver"),
             "send": (X0 + 5.4, 2.6, "notify")}
    W, H = 3.9, 1.5
    for k, (x, y, t) in nodes.items():
        card(ax, x - W / 2, y - H / 2, W, H, k, t, accent=GREEN if k != "send" else NAVY, fs=9.5,
             subfs=7.6, mono_sub=True)
    def link(a, b):
        xa, ya, _ = nodes[a]; xb, yb, _ = nodes[b]
        arrow(ax, (xa, ya - H / 2 - 0.08), (xb, yb + H / 2 + 0.12), color=GREEN, lw=1.5, z=6)
    for a, b in [("doc", "po"), ("doc", "rules"), ("po", "who"), ("rules", "who"), ("who", "send")]:
        link(a, b)
    pill(ax, X0 + 5.4, 8.2, "in parallel", color=GREEN, fs=7.2)
    ax.text(X0 + 0.1, 1.05, "checked first: every tool exists, every $ref fits its schema,\n"
            "no cycles, policy allows it, within limits", fontsize=7.4, color=MUTED, va="center",
            linespacing=1.35)
    fig.savefig(OUT + "fig10.png"); plt.close(fig)


def fig_recursion():
    """A node can be a tool that returns a graph: programs nest, up to a fixed depth."""
    fig, ax = canvas(9.0, 4.9, 24, 13.0)
    def row(y, names, x0, gap, accent, expand=None, label=None):
        pos = {}
        for i, n in enumerate(names):
            x = x0 + i * gap
            hot = n == expand
            card(ax, x, y, 3.4, 1.4, n, None, accent=AMBER if hot else accent, fs=8.6,
                 fill="white", z=3)
            pos[n] = (x, y)
            if i:
                arrow(ax, (x - gap + 3.5, y + 0.7), (x - 0.1, y + 0.7), color=accent, lw=1.3, z=5)
        if label:
            ax.text(0.2, y + 1.15, label[0], fontsize=9.5, weight="semibold", va="center")
            ax.text(0.2, y + 0.75, label[1], fontsize=7.6, color=MUTED, va="top", linespacing=1.3)
        return pos
    p1 = row(10.6, ["receive", "route_invoice", "archive"], 6.2, 5.2, NAVY, expand="route_invoice",
             label=("Level 1", "the process"))
    p2 = row(6.0, ["extract", "match_po", "approve", "notify"], 4.4, 4.4, GREEN, expand="approve",
             label=("Level 2", "a graph returned\nby route_invoice"))
    p3 = row(1.4, ["rules_for", "pick_approver", "escalate?"], 8.8, 4.4, "#6c5b7b",
             label=("Level 3", "a graph returned\nby approve"))
    def funnel(src, dst_first, dst_last, y_src, y_dst):
        xs, _ = src
        for xa, xb in [(xs, dst_first[0]), (xs + 3.4, dst_last[0] + 3.4)]:
            ax.plot([xa, xb], [y_src, y_dst + 1.45], color=AMBER, lw=1.0, ls=(0, (3, 2.5)), zorder=1)
        ax.add_patch(plt.Polygon([(xs, y_src), (xs + 3.4, y_src), (dst_last[0] + 3.4, y_dst + 1.45),
                                  (dst_first[0], y_dst + 1.45)], fc=AMBER_T, ec="none", alpha=0.55, zorder=0))
    funnel(p1["route_invoice"], p2["extract"], p2["notify"], 10.6, 6.0)
    funnel(p2["approve"], p3["rules_for"], p3["escalate?"], 6.0, 1.4)
    pill(ax, 22.4, 12.2, "max depth 3", color=WARM, fs=7.4)
    pill(ax, 22.4, 11.3, "max 20 calls", color=WARM, fs=7.4)
    fig.savefig(OUT + "fig11.png"); plt.close(fig)


def fig_program_loop():
    """Programs inside the process: search, plan, check, run, keep; the kept graph becomes a tool."""
    fig, ax = canvas(9.2, 3.9, 25.1, 10.4)
    steps = [("Search", "embeddings find\nthe few tools that fit", AMBER),
             ("Plan", "a tool or a model\nreturns a sub-graph", AMBER),
             ("Check", "schemas, policy,\nlimits, no cycles", NAVY),
             ("Run", "an executor,\nno model needed", GREEN),
             ("Keep", "the graph is stored,\nnamed, versioned", GREEN)]
    W, gap, y = 4.4, 5.0, 5.6
    for i, (t, s, col) in enumerate(steps):
        x = 0.3 + i * gap
        card(ax, x, y, W, 2.6, t, s, accent=col, eyebrow=f"step {i + 1}", subfs=7.6)
        if i < len(steps) - 1:
            arrow(ax, (x + W + 0.1, y + 1.3), (x + gap - 0.1, y + 1.3), color=col)
    # the loop back: the kept graph is published as a new tool
    xl = 0.3 + 4 * gap + W / 2
    ax.plot([xl, xl], [y - 0.1, 2.6], color=GREEN, lw=1.6, zorder=1)
    ax.plot([xl, 0.3 + W / 2], [2.6, 2.6], color=GREEN, lw=1.6, zorder=1)
    arrow(ax, (0.3 + W / 2, 2.6), (0.3 + W / 2, y - 0.1), color=GREEN, lw=1.6)
    pill(ax, (xl + 0.3 + W / 2) / 2, 2.6, "published back as a tool: route_invoice@v3", color=GREEN,
         fs=7.8, mono=False)
    ax.text(12.3, 1.1, "next time, search finds the stored program first, and the planning step is skipped",
            ha="center", fontsize=8.4, style="italic", color=INK)
    ax.text(0.3, 8.85, "SLOW, ONCE", fontsize=7, weight="semibold", color=WARM)
    ax.text(0.3 + 3 * gap, 8.85, "FAST, EVERY TIME", fontsize=7, weight="semibold", color=GREEN)
    fig.savefig(OUT + "fig12.png"); plt.close(fig)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    fig_two_bindings(); fig_anatomy(); fig_many_readers(); fig_adapters(); fig_web()
    fig_shapes(); fig_zoom(); fig_context(); fig_embedding_map(); fig_returned_graph()
    fig_recursion(); fig_program_loop(); fig_alternatives(); fig_where()
