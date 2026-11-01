"""Figures for "The Context Is the Wire".

Same style as "A Grammar for Tools": Inter type, white cards with a faint shadow
and a coloured accent, colours taken from the site's palette.

All three figures are schematics. The tool names are my own examples, and the labels
on the context are the ones used in the note's hook: private and untrusted.
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


# ---------- shared pieces ----------
CTX = "#d6d2c9"   # the context band: a neutral, slightly warm grey


def tool(ax, x, y, w, h, name, accent=NAVY, z=2):
    """A tool card: a white card with the tool name in monospace."""
    card(ax, x, y, w, h, None, accent=accent, z=z)
    ax.text(x + w / 2 + 0.12, y + h / 2, name, ha="center", va="center", fontsize=9.6,
            fontfamily=MONO, weight="medium", color=INK, zorder=z + 4)


def context_band(ax, x0, x1, y):
    ax.plot([x0, x1], [y, y], color=CTX, lw=11, solid_capstyle="round", zorder=1)
    ax.text(x0, y + 0.55, "MODEL CONTEXT", fontsize=7, weight="semibold", color=MUTED, va="bottom")


# ---------- Figure 1: a generative effect ----------
def fig_generative():
    fig, ax = canvas(11, 4.3, 22, 8.6)
    heading(ax, 0.4, 8.35, "A generative effect", "Each tool alone cannot leak; the three together can")
    names = ["read_private_files", "fetch_web_page", "send_email"]
    for i, n in enumerate(names):
        y = 5.3 - i * 1.6
        tool(ax, 0.5, y, 6.4, 1.1, n)
        chip(ax, 8.4, y + 0.55, "alone: no", color=GREEN, fill=GREEN_T, fs=7.6)
    arrow(ax, (10.1, 3.85), (12.5, 3.85), color=MUTED, lw=1.4)
    ax.text(11.3, 4.25, "put together", ha="center", fontsize=8, color=MUTED)
    ax.add_patch(FancyBboxPatch((12.9, 1.45), 8.7, 5.55, boxstyle="round,pad=0,rounding_size=0.35",
                                fc=RED, ec="none", alpha=0.05, zorder=0.5))
    ax.add_patch(FancyBboxPatch((12.9, 1.45), 8.7, 5.55, boxstyle="round,pad=0,rounding_size=0.35",
                                fc="none", ec=RED, alpha=0.5, lw=0.9, ls=(0, (3, 3)), zorder=0.6))
    for i, n in enumerate(names):
        tool(ax, 13.4, 5.5 - i * 1.6, 5.4, 1.0, n, accent=RED)
    chip(ax, 20.15, 4.1, "together:\nyes", color=RED, fill="#f6e3e0", fs=7.6)
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


# ---------- Figure 2: the hidden wire ----------
def fig_wire():
    fig, ax = canvas(11, 4.7, 22, 9.4)
    heading(ax, 0.4, 9.15, "The hidden wire", "Every tool output enters the context, and the context chooses the next call")
    tool(ax, 0.9, 6.0, 5.4, 1.3, "read_private_files")
    tool(ax, 8.3, 6.0, 5.4, 1.3, "fetch_web_page")
    tool(ax, 15.7, 6.0, 5.4, 1.3, "send_email", accent=RED)
    context_band(ax, 0.5, 21.5, 3.0)
    arrow(ax, (3.7, 5.9), (3.7, 3.35), color=NAVY)
    arrow(ax, (11.1, 5.9), (11.1, 3.35), color=NAVY)
    arrow(ax, (18.5, 3.35), (18.5, 5.9), color=RED)
    ax.text(18.8, 4.6, "chooses the\narguments", fontsize=8, color=MUTED, va="center")
    chip(ax, 1.4, 2.0, "{ }", color=MUTED, fill=SAND_T)
    chip(ax, 6.6, 2.0, "{ private }", color=WARM, fill=AMBER_T)
    chip(ax, 14.4, 2.0, "{ private, untrusted }", color=WARM, fill=AMBER_T)
    pill(ax, 15.6, 0.75, "stop and ask: untrusted context, private data, outbound call", color=RED, fs=8)
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


# ---------- Figure 3: routing untrusted content around the context ----------
def fig_reroute():
    fig, ax = canvas(11, 4.7, 22, 9.4)
    heading(ax, 0.4, 9.15, "Rerouting the wire", "Untrusted content goes around the model; only a handle enters the context")
    tool(ax, 0.9, 6.0, 5.4, 1.3, "read_private_files")
    tool(ax, 8.3, 6.0, 5.4, 1.3, "fetch_web_page", accent=WARM)
    tool(ax, 15.7, 6.0, 5.4, 1.3, "send_email", accent=GREEN)
    context_band(ax, 0.5, 21.5, 3.0)
    arrow(ax, (3.7, 5.9), (3.7, 3.35), color=NAVY)
    ax.plot([11.1, 11.1], [5.9, 3.35], color=MUTED, lw=1.3, ls=(0, (2, 3)), zorder=1.5)
    ax.text(11.4, 4.6, "only a handle, $page", fontsize=8, color=MUTED, va="center")
    arrow(ax, (13.8, 6.65), (15.6, 6.65), color=WARM, lw=2)
    chip(ax, 14.7, 7.85, "untrusted value", color=WARM, fill=AMBER_T)
    arrow(ax, (18.5, 3.35), (18.5, 5.9), color=NAVY)
    chip(ax, 6.6, 2.0, "{ private }", color=WARM, fill=AMBER_T)
    chip(ax, 14.4, 2.0, "still { private }", color=WARM, fill=AMBER_T)
    pill(ax, 15.6, 0.75, "checked at the call: may $page be used here?", color=GREEN, fs=8)
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


if __name__ == "__main__":
    fig_generative()
    fig_wire()
    fig_reroute()
