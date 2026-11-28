"""The site's figure house style ("printed chart, annotated by hand").

Every figs.py calls `house.apply()` right after importing pyplot. Nothing else has to change
in the figure code: the look is applied when a figure is saved, so old and new figures share
one identity.

The identity, in one sentence: a clean, precise chart in the site's own typefaces and palette,
with the author's notes written over it by hand, and a small signature that says where it is from.

What it does at save time
1. Palette. Every colour is snapped to the house palette (`PALETTE` below): six hue families
   (navy, amber, green, plum, red, teal), each with a fixed ramp from deep to tint, plus a neutral
   ramp. A colour keeps its family and its lightness step, so a light/dark pair stays a pair. Cream
   backgrounds become white. Colormaps (images, heat maps) are left alone.
2. Type. Labels, ticks and legends are set in Inter (the site's interface face). Titles (bold,
   13 pt or more) are set in Source Serif 4 Semibold, like the headings in a post. Small
   upper-case kickers ("EXPERIMENT 2") become amber Inter Semibold. Code stays monospace.
3. Notes. A callout (an annotation with an arrow and some text) is the author speaking: its text
   is handwritten (Kalam) and its arrow is drawn with a light pen. Nothing else is hand-drawn, so
   no value ever moves.
4. Axes. Hairline axes in a soft grey, no top or right frame on plots, a quiet grid, legends
   without boxes.
5. Signature. A short amber bar sits above the figure's top-left corner (the same amber as the
   rule under post titles) and a hairline with "AI, Honestly" closes the figure at the bottom
   right. Covers and dark posters (file name starting with "cover", or a dark figure background)
   are left unsigned.

The same look in the SVG (page) and the PNG (card): sizes are in points and the pen wobble is
scaled to the output resolution; it is the same on every run.

Use in a figs.py:

    import sys, pathlib  # house figure style: _figstyle/house.py at the site root
    sys.path.insert(0, str(next(p / "_figstyle" for p in pathlib.Path(__file__).resolve().parents if (p / "_figstyle").is_dir())))
    import house; house.apply()

Options (rarely needed), set on a figure before saving:
    fig._house_sign = False      # no signature on this figure
    fig._house_source = "Source: …"   # a source line at the bottom left, next to the signature
"""
import math
import os

import numpy as np
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.artist import Artist
from matplotlib.collections import Collection
from matplotlib.colors import to_rgba, to_hex
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.patheffects import AbstractPathEffect
from matplotlib.text import Annotation, Text
from matplotlib.transforms import Bbox

_FONT_DIR = Path(__file__).resolve().parent / "fonts"

SANS = "Inter"
SERIF = "Source Serif 4"
HAND = "Kalam"
FALLBACK = ["DejaVu Sans"]
MONO_HINTS = ("mono", "courier", "consol", "menlo", "code")

SIGNATURE = ("AI, ", "Honestly")   # second part in the signature amber, as in the site's hero

# ---------------------------------------------------------------- palette
# Categorical order (validated for colour-blind separation on white): navy, amber, green, plum,
# red, teal. Each family: deep (text on tint), main (lines, marks), mid, light, tint (box fills).
PALETTE = {
    "navy":  ["#0d1b2e", "#163a5f", "#245c96", "#6f97c2", "#b3c9e0", "#eaf0f7"],
    "amber": ["#8a5600", "#c98100", "#e9a93f", "#f5d7a1", "#fdf4e3"],
    "green": ["#175a3d", "#26895f", "#6db592", "#b2d9c5", "#e8f3ed"],
    "plum":  ["#4e2f68", "#7b4fa0", "#a989c4", "#d3c3e2", "#f3eef8"],
    "red":   ["#7f241b", "#c0392b", "#e07a6e", "#f0bbb4", "#fbecea"],
    "teal":  ["#005f68", "#00919e", "#4fb9c2", "#a3dbe0", "#e5f5f6"],
}
NEUTRAL = ["#14161a", "#2f343b", "#545b66", "#868d97", "#b9bec5", "#dcdee1", "#eceeef", "#f5f5f3", "#ffffff"]
MAIN = {k: v[1] if k != "navy" else v[2] for k, v in PALETTE.items()}

INK, MUTED, FAINT, AXIS, RULE, GRID = NEUTRAL[0], NEUTRAL[2], NEUTRAL[3], NEUTRAL[4], NEUTRAL[5], NEUTRAL[6]
PANEL = NEUTRAL[7]   # a neutral box fill

# Named colours for new figures (`from house import NAVY, AMBER, ...`): main colour, then its tint.
NAVY, NAVY_T, NAVY_DEEP = PALETTE["navy"][2], PALETTE["navy"][5], PALETTE["navy"][1]
AMBER, AMBER_T, AMBER_FILL = PALETTE["amber"][1], PALETTE["amber"][4], PALETTE["amber"][2]
GREEN, GREEN_T = PALETTE["green"][1], PALETTE["green"][4]
PLUM, PLUM_T = PALETTE["plum"][1], PALETTE["plum"][4]
RED, RED_T = PALETTE["red"][1], PALETTE["red"][4]
TEAL, TEAL_T = PALETTE["teal"][1], PALETTE["teal"][4]
SIGN_AMBER = "#f5b041"     # the site's amber, for the signature bar only
MARK = PALETTE["amber"][0]  # amber text on white (kickers, the signature word)


# ---------------------------------------------------------------- colour maths (OKLab)
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _oklab(rgb):
    r, g, b = (_lin(c) for c in rgb[:3])
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, A, B


def _lch(rgb):
    L, A, B = _oklab(rgb)
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


_FAMILY_HUE = {k: _lch(to_rgba(MAIN[k]))[2] for k in PALETTE}
_FAMILY_HUE["amber"] = 70.0   # browns, oranges and yellows all read as amber
_FAMILY_HUE["red"] = 30.0
_CACHE = {}


def snap(color):
    """The house colour closest in role to `color` (same family, same lightness step)."""
    rgba = to_rgba(color)
    key = tuple(round(c, 4) for c in rgba[:3])
    if key in _CACHE:
        return (*_CACHE[key], rgba[3])
    L, C, h = _lch(rgba)
    # warm greys (the old cream rules) are greys; a faint blue is still a blue tint
    if 40 <= h <= 120:
        neutral_c = 0.022
    else:
        neutral_c = 0.025 if L < 0.88 else 0.008
    if L > 0.965 and C < (0.011 if 40 <= h <= 120 else 0.006):
        out = "#ffffff"
    elif C < neutral_c or (L < 0.33 and not (190 < h < 290)) or (L < 0.42 and C < 0.05):
        out = min(NEUTRAL, key=lambda n: abs(_lch(to_rgba(n))[0] - L))
    else:
        def hdist(a, b):
            d = abs(a - b) % 360
            return min(d, 360 - d)
        fam = min(_FAMILY_HUE, key=lambda k: hdist(_FAMILY_HUE[k], h))
        out = min(PALETTE[fam], key=lambda n: abs(_lch(to_rgba(n))[0] - L))
    rgb = to_rgba(out)[:3]
    _CACHE[key] = rgb
    return (*rgb, rgba[3])


def _line_color(rgba, original):
    """A line or marker is never drawn in a box tint: step up to the family's light colour."""
    h = to_hex(rgba[:3])
    for ramp in PALETTE.values():
        if h == ramp[-1]:
            return (*to_rgba(ramp[-2])[:3], rgba[3])
    if h in (NEUTRAL[6], NEUTRAL[7]) and _lch(to_rgba(original))[0] < 0.97:
        return (*to_rgba(NEUTRAL[5])[:3], rgba[3])
    return rgba


def _is_dark(color):
    try:
        return _lch(to_rgba(color))[0] < 0.4
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------- the pen (callout arrows only)
class Pen(AbstractPathEffect):
    """A light hand-drawn stroke: a small wobble and a fainter second pass."""

    def __init__(self, dpi):
        super().__init__()
        self.k = dpi / 72.0

    def draw_path(self, renderer, gc, tpath, affine, rgbFace=None):
        k = self.k
        if rgbFace is not None:
            g = renderer.new_gc(); g.copy_properties(gc); g.set_linewidth(0)
            renderer.draw_path(g, tpath, affine, rgbFace); g.restore()
        g = renderer.new_gc(); g.copy_properties(gc)
        g.set_sketch_params(0.55 * k, 60 * k, 5.0)
        g.set_capstyle("round"); g.set_joinstyle("round")
        renderer.draw_path(g, tpath, affine, None); g.restore()
        g = renderer.new_gc(); g.copy_properties(gc)
        g.set_linewidth(max(gc.get_linewidth() * 0.5, 0.4))
        g.set_alpha((gc.get_alpha() if gc.get_alpha() is not None else 1.0) * 0.4)
        g.set_sketch_params(0.7 * k, 40 * k, 7.0)
        g.set_capstyle("round"); g.set_joinstyle("round")
        renderer.draw_path(g, tpath, affine, None); g.restore()


# ---------------------------------------------------------------- restyling
def _is_mono(text):
    fam = " ".join(text.get_fontfamily()).lower()
    return any(h in fam for h in MONO_HINTS)


def _weight(text):
    w = text.get_fontweight()
    return w if isinstance(w, (int, float)) else font_manager.weight_dict.get(w, 400)


def _readable(rgba, on_dark=False):
    """Text needs contrast: step a light colour down its family ramp until it reads on white."""
    if on_dark:
        return rgba
    L = _lch(rgba)[0]
    if L <= 0.62:
        return rgba
    h = to_hex(rgba[:3])
    for ramp in list(PALETTE.values()) + [NEUTRAL]:
        if h in ramp:
            i = ramp.index(h)
            while i > 0 and _lch(to_rgba(ramp[i]))[0] > 0.62:
                i -= 1
            return (*to_rgba(ramp[i])[:3], rgba[3])
    return rgba


def _centre(t):
    """The middle of a label on the canvas (works for offset annotations too)."""
    import warnings
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            bb = t.get_window_extent(t.figure.canvas.get_renderer())
        return (bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2
    except Exception:
        try:
            return tuple(t.get_transform().transform(t.get_position()))
        except Exception:
            return None


def _over_dark_patch(t):
    """Is this label drawn on top of a dark box (white or pale text on navy, say)?"""
    xy = _centre(t)
    if xy is None:
        return False
    x, y = xy
    for p in t.axes.patches:
        fc = p.get_facecolor()
        if fc is None or fc[3] < 0.5 or _lch(fc)[0] > 0.62:
            continue
        try:
            if p.contains_point((x, y)):
                return True
        except Exception:
            pass
    return False


def _recolor_text(t):
    c = t.get_color()
    try:
        rgba = snap(c)
        bg = t.get_bbox_patch().get_facecolor() if t.get_bbox_patch() is not None else None
        on_dark = (bg is not None and _is_dark(bg)) or _is_dark(t.figure.get_facecolor()) if t.figure else False
        if t.axes is not None and (_is_dark(t.axes.get_facecolor()) or _over_dark_patch(t)):
            on_dark = True
        t._house_on_dark = on_dark
        t.set_color(rgba if _lch(rgba)[0] > 0.9 else _readable(rgba, on_dark))
    except (ValueError, TypeError):
        pass
    patch = t.get_bbox_patch()
    if patch is not None:
        _recolor_patch(patch)


def _recolor_patch(p):
    fc, ec = p.get_facecolor(), p.get_edgecolor()
    if fc is not None and len(fc) and fc[3] > 0:
        p.set_facecolor(snap(fc))
    if ec is not None and len(ec) and ec[3] > 0:
        p.set_edgecolor(snap(ec))


def _recolor_collection(c):
    if c.get_array() is not None and c.get_cmap() is not None and not isinstance(c, matplotlib.collections.LineCollection):
        # coloured by a colormap: leave the data colours, tidy only the edges
        try:
            ec = c.get_edgecolor()
            if len(ec) and not c._edge_is_mapped:
                c.set_edgecolor([snap(e) for e in ec])
        except Exception:
            pass
        return
    if c.get_array() is not None:
        return
    try:
        if len({tuple(np.round(x, 3)) for x in c.get_facecolor()}) > 16:
            return   # a shaded surface or an image made of patches: its colours are data
    except Exception:
        pass
    for get, put in ((c.get_facecolor, c.set_facecolor), (c.get_edgecolor, c.set_edgecolor)):
        try:
            cols = get()
        except Exception:
            continue
        if cols is None or not len(cols):
            continue
        try:
            put([snap(x) for x in cols])
        except Exception:
            pass


def _style_text(t, fig):
    if _is_mono(t) or getattr(t, "_house", False):
        return
    t._house = True
    txt = t.get_text()
    size = t.get_fontsize()
    is_callout = isinstance(t, Annotation) and t.arrow_patch is not None and txt.strip()
    letters = [ch for ch in txt if ch.isalpha()]
    if is_callout:
        t.set_fontfamily([HAND] + FALLBACK)
        t.set_fontweight("normal")
        t.set_fontsize(size * 1.12)
        ls = getattr(t, "_linespacing", 1.2)
        t.set_linespacing((ls if isinstance(ls, (int, float)) else 1.2) * 0.8)
        t.arrow_patch.set_path_effects([Pen(fig._house_dpi)])
        if "$" in txt:
            t.set_text(_hand_math(txt))
    elif _is_title(t, txt, size):
        t.set_fontfamily([SERIF] + FALLBACK)
        t.set_fontweight("semibold")
        t.set_fontsize(size * 1.04)
    elif letters and len(letters) >= 3 and txt.upper() == txt and size < 11.5 and "$" not in txt:
        # a kicker: small capitals above a title
        t.set_fontfamily([SANS] + FALLBACK)
        t.set_fontweight("semibold")
        c = to_rgba(t.get_color())
        if not getattr(t, "_house_on_dark", False) and (_lch(c)[1] < 0.04 or abs(_lch(c)[2] - 70) < 30):
            t.set_color(MARK)
    else:
        t.set_fontfamily([SANS] + FALLBACK)


def _is_title(t, txt, size):
    """Headline voice (Source Serif 4): bold words that title a figure, a panel or a chart,
    not a label inside a box and not a number."""
    if _weight(t) < 600 or "$" in txt or txt.upper() == txt:
        return False
    letters = sum(ch.isalpha() for ch in txt)
    if txt.lstrip()[:1].isdigit() or txt.lstrip()[:1] in "+-−~≈<>$€£":
        return False
    if letters < 3 or letters < 0.5 * len(txt.replace(" ", "")):
        return False
    ax = t.axes
    if ax is not None and t in (ax.title, ax._left_title, ax._right_title):
        return True
    if size < 9.5:
        return False
    return not _in_small_box(t)


def _in_small_box(t):
    ax = t.axes
    if ax is None:
        return False
    xy = _centre(t)
    if xy is None:
        return False
    x, y = xy
    fig_h = t.figure.bbox.height
    for p in ax.patches:
        fc, ec = p.get_facecolor(), p.get_edgecolor()
        visible = (fc is not None and fc[3] > 0.05) or (ec is not None and ec[3] > 0.05 and p.get_linewidth() > 0)
        if not visible:
            continue
        try:
            ext = p.get_window_extent()
            if ext.height < 0.3 * fig_h and ext.contains(x, y):
                return True
        except Exception:
            pass
    return False


_KALAM_CHARS = None


def _hand_math(t):
    """In handwritten text with $maths$, keep the maths in the math font and let Kalam draw the rest."""
    import re
    global _KALAM_CHARS
    parts = re.split(r"(?<!\\)\$", t)
    if len(parts) < 3 or len(parts) % 2 == 0:
        return t
    if _KALAM_CHARS is None:
        from matplotlib.ft2font import FT2Font
        _KALAM_CHARS = set(FT2Font(str(_FONT_DIR / "Kalam-Regular.ttf")).get_charmap())
    for i in range(0, len(parts), 2):
        parts[i] = "".join(c if (ord(c) in _KALAM_CHARS or c.isspace()) else "$" + c + "$" for c in parts[i])
    return "$".join(parts).replace("$$", "")


def _style_axes(ax):
    if ax.name == "3d":
        for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
            try:
                axis.set_pane_color((1, 1, 1, 0))
                axis._axinfo["grid"]["color"] = to_rgba(GRID)
                axis.line.set_color(AXIS)
            except Exception:
                pass
        return
    if not ax.axison:
        return
    has_image = any(isinstance(a, AxesImage) for a in ax.get_children()) or any(
        isinstance(c, matplotlib.collections.QuadMesh) for c in ax.collections)
    fc = ax.get_facecolor()
    dark = _is_dark(fc)
    for side, sp in ax.spines.items():
        if not sp.get_visible():
            continue
        if not has_image and side in ("top", "right") and not dark and _both_sides(ax, side):
            sp.set_visible(False)
            continue
        sp.set_color(AXIS if not dark else NEUTRAL[3])
        sp.set_linewidth(0.8)
    ax.tick_params(which="both", colors=AXIS, labelcolor=MUTED if not dark else NEUTRAL[5], width=0.7)
    ax.tick_params(which="major", length=3.5)
    ax.tick_params(which="minor", length=2)
    for gl in ax.get_xgridlines() + ax.get_ygridlines():
        gl.set_color(GRID if not dark else NEUTRAL[1])
        gl.set_linewidth(0.7)
        gl.set_linestyle("-")
    for lab in (ax.xaxis.label, ax.yaxis.label):
        lab.set_color(MUTED if not dark else NEUTRAL[5])


def _both_sides(ax, side):
    """Hide the top/right frame only when nothing is attached to it (twin axes, ticks on top)."""
    if side == "top":
        return not ax.xaxis.get_ticks_position() in ("top", "both") or not any(
            t.tick2line.get_visible() for t in ax.xaxis.get_major_ticks()[:1])
    return not ax.yaxis.get_ticks_position() in ("right", "both") or not any(
        t.tick2line.get_visible() for t in ax.yaxis.get_major_ticks()[:1])


def _style_legend(leg):
    fr = leg.get_frame()
    if not _is_dark(fr.get_facecolor()):
        fr.set_edgecolor("none")
        fr.set_facecolor((1, 1, 1, 0.85))
    for t in leg.get_texts():
        t.set_color(snap(t.get_color()))
    if leg.get_title():
        leg.get_title().set_color(MUTED)


def _restyle(fig):
    if getattr(fig, "_house_done", False):
        return
    fig._house_done = True
    if not _is_dark(fig.patch.get_facecolor()):
        fig.patch.set_facecolor("white")
        fig._house_white = True
    for a in fig.findobj(Artist):
        if a is fig.patch:
            continue
        if isinstance(a, Text):
            _recolor_text(a)
            _style_text(a, fig)
        elif isinstance(a, Line2D):
            for get, put in ((a.get_color, a.set_color), (a.get_markerfacecolor, a.set_markerfacecolor),
                             (a.get_markeredgecolor, a.set_markeredgecolor)):
                try:
                    c = get()
                    if c is not None and not (isinstance(c, str) and c in ("none", "auto")):
                        put(_line_color(snap(c), c))
                except (ValueError, TypeError):
                    pass
        elif isinstance(a, Patch):
            _recolor_patch(a)
        elif isinstance(a, Collection):
            _recolor_collection(a)
        elif isinstance(a, Legend):
            _style_legend(a)
    for ax in fig.axes:
        _style_axes(ax)
    _fit_labels(fig)


def _fit_labels(fig):
    """A label inside a box must stay inside it: shrink it a little when the house font is wider
    than the one the figure was drawn with (never below 75 %)."""
    import sys
    import warnings
    r = fig.canvas.get_renderer()
    pad = 3.0 * fig.dpi / 72
    for ax in fig.axes:
        boxes = []
        for p in ax.patches:
            fc, ec = p.get_facecolor(), p.get_edgecolor()
            if not ((fc is not None and fc[3] > 0.05) or (ec is not None and ec[3] > 0.05 and p.get_linewidth() > 0)):
                continue
            try:
                e = p.get_window_extent(r)
            except Exception:
                continue
            if e.height < 0.3 * fig.bbox.height and e.width > 12 * fig.dpi / 72:
                boxes.append(e)
        if not boxes:
            continue
        for t in ax.texts:
            if not t.get_visible() or not t.get_text().strip() or getattr(t, "_house_fit", False):
                continue
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tb = t.get_window_extent(r)
            cx, cy = (tb.x0 + tb.x1) / 2, (tb.y0 + tb.y1) / 2
            inside = [b for b in boxes if b.contains(cx, cy)]
            if not inside:
                continue
            b = min(inside, key=lambda e: e.width * e.height)
            room = b.width - 2 * pad
            if tb.width > room and tb.width < 1.6 * room:
                k = max(room / tb.width, 0.75)
                t.set_fontsize(t.get_fontsize() * k)
                t._house_fit = True
                if k == 0.75:
                    print(f"house: label still too wide for its box: {t.get_text()[:40]!r}", file=sys.stderr)


# ---------------------------------------------------------------- the signature
def _sign(fig, renderer):
    """Add the amber bar (top left) and the closing hairline with the site's name (bottom right).
    Positions are in figure fractions so they follow the tight crop. Returns the artists so they
    can be removed after saving."""
    bb = fig.get_tightbbox(renderer)   # inches
    W, H = fig.get_size_inches()
    fx = lambda x: x / W
    fy = lambda y: y / H
    x0, x1, y0, y1 = bb.x0, bb.x1, bb.y0, bb.y1
    tr = fig.transFigure
    k = min(max((x1 - x0) / 9.0, 0.7), 1.6)   # every figure is shown at the column width
    gap = 0.17 * k
    made = []
    bar = Rectangle((fx(x0), fy(y1 + gap)), fx(0.42 * k), fy(0.045 * k), transform=tr, facecolor=SIGN_AMBER,
                    edgecolor="none")
    fig.add_artist(bar); made.append(bar)
    yl = y0 - gap
    rule = Line2D([fx(x0), fx(x1)], [fy(yl), fy(yl)], transform=tr, color=RULE, linewidth=0.7 * k)
    fig.add_artist(rule); made.append(rule)
    size = 7.6 * k
    t2 = fig.text(fx(x1), fy(yl - 0.08 * k), SIGNATURE[1], ha="right", va="top", fontsize=size,
                  fontfamily=[SANS], fontweight="semibold", color=MARK)
    t2._house = True
    w2 = t2.get_window_extent(renderer).width / fig.dpi
    t1 = fig.text(fx(x1 - w2), fy(yl - 0.08 * k), SIGNATURE[0], ha="right", va="top", fontsize=size,
                  fontfamily=[SANS], fontweight="semibold", color=INK)
    t1._house = True
    made += [t1, t2]
    src = getattr(fig, "_house_source", None)
    if src:
        t3 = fig.text(fx(x0), fy(yl - 0.08 * k), src, ha="left", va="top", fontsize=size,
                      fontfamily=[SANS], color=MUTED)
        t3._house = True
        made.append(t3)
    return made


def _wants_sign(fig, fname, kwargs):
    if getattr(fig, "_house_sign", True) is False:
        return False
    if Path(str(fname)).stem.lower().startswith("cover"):
        return False
    if isinstance(kwargs.get("bbox_inches"), Bbox):
        return False
    fc = kwargs.get("facecolor", fig.get_facecolor())
    return not _is_dark(fc)


def _report_collisions(fig, fname):
    """HOUSE_CHECK=1 python figs.py: list labels that overlap each other (a layout check)."""
    import sys
    import warnings
    items = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        for t in fig.findobj(Text):
            if t.get_visible() and len(t.get_text().strip()) > 1 and t.get_alpha() != 0:
                try:
                    items.append((t, t.get_window_extent(r)))
                except Exception:
                    pass
    for i, (a, ea) in enumerate(items):
        for b, eb in items[i + 1:]:
            w = min(ea.x1, eb.x1) - max(ea.x0, eb.x0)
            h = min(ea.y1, eb.y1) - max(ea.y0, eb.y0)
            if w > 2 and h > 2 and w * h > 0.15 * min(ea.width * ea.height, eb.width * eb.height):
                print(f"house-check {Path(str(fname)).name}: {a.get_text()[:30]!r} overlaps {b.get_text()[:30]!r}",
                      file=sys.stderr)


def _wrap_savefig():
    original = Figure.savefig

    def savefig(self, fname, *args, **kwargs):
        dpi = kwargs.get("dpi") or matplotlib.rcParams["savefig.dpi"]
        if dpi == "figure":
            dpi = self.dpi
        fmt = (kwargs.get("format") or str(fname).lower().rsplit(".", 1)[-1]).lower()
        self._house_dpi = 72.0 if fmt in ("svg", "pdf", "eps", "ps") else float(dpi)
        fc = kwargs.get("facecolor", matplotlib.rcParams["savefig.facecolor"])
        if fc in (None, "auto"):
            fc = self.get_facecolor()
        kwargs["facecolor"] = snap(fc) if _is_dark(fc) else "white"
        _restyle(self)
        # callout pens must match this output's resolution
        for a in self.findobj(Annotation):
            if a.arrow_patch is not None and a.arrow_patch.get_path_effects():
                a.arrow_patch.set_path_effects([Pen(self._house_dpi)])
        if os.environ.get("HOUSE_CHECK"):
            _report_collisions(self, fname)
        made = []
        if _wants_sign(self, fname, kwargs):
            if kwargs.get("bbox_inches", matplotlib.rcParams["savefig.bbox"]) != "tight":
                kwargs["bbox_inches"] = "tight"
            kwargs.setdefault("pad_inches", max(matplotlib.rcParams["savefig.pad_inches"], 0.3))
            self.canvas.draw()
            made = _sign(self, self.canvas.get_renderer())
        try:
            return original(self, fname, *args, **kwargs)
        finally:
            for m in made:
                m.remove()

    Figure.savefig = savefig


def _redirect_fonts():
    """Any proportional font a script asks for resolves to the house faces: serif → Source Serif 4,
    everything else → Inter. Code fonts and the handwriting are left alone."""
    original = font_manager.FontManager.findfont

    def findfont(self, prop, fontext="ttf", directory=None, fallback_to_default=True, rebuild_if_missing=True):
        if isinstance(prop, str):
            prop = font_manager.FontProperties(family=prop)
        elif prop is None:
            prop = font_manager.FontProperties()
        fams = [f.lower() for f in prop.get_family()]
        first = fams[0] if fams else "sans-serif"
        if any(h in first for h in MONO_HINTS) or first in (HAND.lower(), "dejavu sans", "stixgeneral",
                                                           "stixsizeonesym", "cmr10", "cmsy10", "cmex10",
                                                           "dejavu sans display", "stix", "stixsizetwosym"):
            return original(self, prop, fontext, directory, fallback_to_default, rebuild_if_missing)
        if first.startswith("stix") or first.startswith("cm"):
            return original(self, prop, fontext, directory, fallback_to_default, rebuild_if_missing)
        want = SERIF if ("serif" in first and "sans" not in first) or first == SERIF.lower() else SANS
        p = prop.copy()
        p.set_family(want)
        return original(self, p, fontext, directory, fallback_to_default, rebuild_if_missing)

    font_manager.FontManager.findfont = findfont


_applied = False


def apply():
    """Switch the current matplotlib session to the house style."""
    global _applied
    import logging
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    for f in sorted(_FONT_DIR.glob("*.[ot]tf")):
        font_manager.fontManager.addfont(str(f))
    plt.rcParams.update({
        "font.family": [SANS] + FALLBACK,
        "font.sans-serif": [SANS] + FALLBACK,
        "font.serif": [SERIF, "DejaVu Serif"],
        "mathtext.fontset": "custom",
        "mathtext.rm": SANS, "mathtext.it": f"{SANS}:italic", "mathtext.bf": f"{SANS}:bold",
        "mathtext.sf": SANS, "mathtext.cal": SANS,
        "mathtext.fallback": "stixsans",
        "text.color": INK,
        "axes.edgecolor": AXIS, "axes.labelcolor": MUTED, "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlelocation": "left", "axes.titleweight": "semibold", "axes.titlesize": 12,
        "axes.prop_cycle": matplotlib.cycler(color=[MAIN[k] for k in PALETTE]),
        "xtick.color": AXIS, "ytick.color": AXIS, "xtick.labelcolor": MUTED, "ytick.labelcolor": MUTED,
        "grid.color": GRID, "grid.linewidth": 0.7,
        "legend.frameon": False,
        "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round", "lines.dash_capstyle": "round",
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "axes.unicode_minus": True,
        "svg.fonttype": "path",
    })
    if not _applied:
        _redirect_fonts()
        _wrap_savefig()
        _applied = True
