"""The site's hand-drawn figure style ("pen and marker").

Every figs.py calls `handdrawn.apply()` after its own rcParams. Nothing else changes in
the figure code: the look is added when a figure is saved.

What it does
- Handwriting: all text that is not code is set in Kalam (bundled in fonts/, SIL OFL),
  with DejaVu Sans as a fallback for symbols Kalam lacks (arrows, Greek, check marks).
  Code (monospace) text is left alone. Maths ($...$) uses Kalam too.
- Pen strokes: every line, box, arrow and marker wobbles a little, as if drawn by hand,
  and is drawn twice (a firm stroke and a lighter second pass), like a pen going over it.
- Marker fills: coloured areas are laid down slightly off the outline, like a felt-tip
  that does not quite stay inside the lines.

The wobble is deterministic (same output on every run) and scaled to the output
resolution, so the SVG in the page and the 400 dpi PNG used for cards look the same.

Use in a figs.py:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "_figstyle"))
    import handdrawn; handdrawn.apply()
"""
import re
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.artist import Artist
from matplotlib.collections import Collection
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.patheffects import AbstractPathEffect
from matplotlib.text import Text
from matplotlib.transforms import Affine2D, Bbox, IdentityTransform

HAND = "Kalam"
FALLBACK = ["DejaVu Sans"]
MONO_HINTS = ("mono", "courier", "consol", "menlo", "code")

# wobble at 72 dpi (points): amplitude, wavelength, randomness
WOBBLE = (0.75, 70.0, 6.0)
# offset of the marker fill relative to its outline, in points
FILL_SHIFT = (1.3, -1.0)
# Kalam's line height relative to Inter's
LINE_TIGHTEN = 0.74
SMALL = 14  # points: a shape smaller than this is a marker
DATA_POINTS = 40  # a path with more vertices is treated as data
NORMAL_SPACING = 1.2  # used when a label leaves line spacing to the font

_FONT_DIR = Path(__file__).resolve().parent / "fonts"
_applied = False


class PenStroke(AbstractPathEffect):
    """Offset marker fill, then a firm wobbly stroke and a lighter second pass."""

    def __init__(self, dpi, data=False):
        super().__init__()
        self.k = dpi / 72.0
        self.data = data   # collections (scatter dots, error bars, fills): data, drawn steady

    def draw_path(self, renderer, gc, tpath, affine, rgbFace=None):
        k = self.k
        amp, length, rnd = WOBBLE
        lw = gc.get_linewidth()
        # Data curves (many points) keep their shape: a light tremor, one pass.
        # Small shapes (markers, dots) stay round and do not get the offset fill.
        ext = affine.transform_path(tpath).get_extents()
        small = max(ext.width, ext.height) < SMALL * k
        data = self.data or small or len(tpath.vertices) > DATA_POINTS
        if data:
            amp *= 0.3
        elif lw < 1.2:
            amp *= max(lw, 0.4) / 1.2  # thin rules: a steadier hand
        if rgbFace is not None and len(rgbFace) and (len(rgbFace) < 4 or rgbFace[3] > 0):
            g = renderer.new_gc(); g.copy_properties(gc)
            g.set_linewidth(0); g.set_sketch_params(amp * k, length * k, rnd)
            shift = Affine2D() if small else Affine2D().translate(FILL_SHIFT[0] * k, FILL_SHIFT[1] * k)
            fill = (affine + shift).transform_path(tpath)
            # A shape that runs far off the canvas (a bar from zero on a log axis) is cut to the
            # canvas first: sketching its invisible length would bloat the SVG.
            w, h = renderer.get_canvas_width_height()
            fe = fill.get_extents()
            if fe.width > 2 * w or fe.height > 2 * h:
                m = 20 * k
                fill = fill.clip_to_bbox(Bbox([[-m, -m], [w + m, h + m]]))
            renderer.draw_path(g, fill, IdentityTransform(), rgbFace); g.restore()
        if lw <= 0:
            return
        g = renderer.new_gc(); g.copy_properties(gc)
        g.set_sketch_params(amp * k, length * k, rnd)
        g.set_capstyle("round"); g.set_joinstyle("round")
        renderer.draw_path(g, tpath, affine, None); g.restore()
        if data or lw < 0.9:
            return
        # second, lighter pass with a different wobble, like a pen going over it
        g = renderer.new_gc(); g.copy_properties(gc)
        g.set_linewidth(max(lw * 0.5, 0.4))
        g.set_alpha((gc.get_alpha() if gc.get_alpha() is not None else 1.0) * 0.45)
        g.set_sketch_params(amp * 1.15 * k, length * 0.63 * k, rnd * 1.4)
        g.set_capstyle("round"); g.set_joinstyle("round")
        renderer.draw_path(g, tpath, affine, None); g.restore()


_KALAM_CHARS = None
_TEX = {"→": r"\rightarrow", "←": r"\leftarrow", "↑": r"\uparrow", "↓": r"\downarrow", "✓": r"\checkmark"}


def _math_safe(t):
    """In a label that mixes text and $maths$, the plain text is drawn in Kalam with no
    fallback: wrap the symbols Kalam lacks (Greek letters, arrows) in $...$ so they are drawn."""
    global _KALAM_CHARS
    parts = re.split(r"(?<!\\)\$", t)
    if len(parts) < 3 or len(parts) % 2 == 0:
        return t
    if _KALAM_CHARS is None:
        from matplotlib.ft2font import FT2Font
        _KALAM_CHARS = set(FT2Font(str(_FONT_DIR / "Kalam-Regular.ttf")).get_charmap())
    for i in range(0, len(parts), 2):
        parts[i] = "".join(c if (ord(c) in _KALAM_CHARS or c.isspace()) else "$" + _TEX.get(c, c) + "$"
                           for c in parts[i])
    return "$".join(parts).replace("$$", "")


def _is_mono(text):
    fam = " ".join(text.get_fontfamily()).lower()
    return any(h in fam for h in MONO_HINTS)


def _restyle(fig, dpi):
    pe = [PenStroke(dpi)]
    pe_data = [PenStroke(dpi, data=True)]
    for a in fig.findobj(Artist):
        if isinstance(a, Text):
            if not _is_mono(a) and not getattr(a, "_hand", False):
                a.set_fontfamily([HAND] + FALLBACK)
                # Kalam's lines are taller than Inter's: tighten multi-line labels
                ls = getattr(a, "_linespacing", None)
                ls = ls if isinstance(ls, (int, float)) else NORMAL_SPACING
                a.set_linespacing(ls * LINE_TIGHTEN)
                a._hand = True
                if "$" in a.get_text():
                    a.set_text(_math_safe(a.get_text()))
            # boxes behind text (bbox=dict(...)) get the pen too
            patch = a.get_bbox_patch()
            if patch is not None:
                patch.set_path_effects(pe)
        elif isinstance(a, (Line2D, Patch, Collection)):
            if a is fig.patch or (getattr(a, "axes", None) is not None and a is a.axes.patch):
                continue
            a.set_path_effects(pe_data if isinstance(a, Collection) else pe)


def _redirect_fonts():
    """Any non-code font a script asks for (Inter, DejaVu Serif, ...) resolves to Kalam,
    so text measured while laying out a figure has the same size as the drawn text."""
    fm = font_manager.fontManager
    original = fm.findfont
    regular = str(_FONT_DIR / "Kalam-Regular.ttf")
    bold = str(_FONT_DIR / "Kalam-Bold.ttf")

    def findfont(prop, *args, **kwargs):
        if isinstance(prop, str):
            prop = font_manager.FontProperties(family=prop)
        elif prop is None:
            prop = font_manager.FontProperties()
        fam = " ".join(prop.get_family()).lower()
        if any(h in fam for h in MONO_HINTS) or fam.startswith("dejavu sans"):
            return original(prop, *args, **kwargs)
        w = prop.get_weight()
        heavy = (w if isinstance(w, (int, float)) else font_manager.weight_dict.get(w, 400)) >= 600
        return bold if heavy else regular

    fm.findfont = findfont
    font_manager.findfont = findfont


def _hand_families():
    """A label that asks for any non-code font gets Kalam, with DejaVu Sans behind it for
    the symbols Kalam lacks, from the moment it is created (so layout sees the real text)."""
    original = font_manager.FontProperties.set_family

    def set_family(self, family):
        if family is None:
            family = matplotlib.rcParams["font.family"]
        fams = [family] if isinstance(family, str) else list(family or [])
        low = " ".join(fams).lower()
        if fams and not any(h in low for h in MONO_HINTS) and HAND.lower() not in low \
                and low not in [f.lower() for f in FALLBACK]:
            family = [HAND] + FALLBACK
        return original(self, family)

    font_manager.FontProperties.set_family = set_family
    font_manager.FontProperties.set_name = set_family


def _wrap_savefig():
    original = Figure.savefig

    def savefig(self, fname, *args, **kwargs):
        dpi = kwargs.get("dpi") or matplotlib.rcParams["savefig.dpi"]
        if dpi == "figure":
            dpi = self.dpi
        name = str(fname).lower()
        fmt = (kwargs.get("format") or name.rsplit(".", 1)[-1]).lower()
        if fmt in ("svg", "pdf", "eps", "ps"):
            dpi = 72.0  # vector backends draw in points
        _restyle(self, float(dpi))
        return original(self, fname, *args, **kwargs)

    Figure.savefig = savefig


def apply():
    """Switch the current matplotlib session to the hand-drawn style."""
    global _applied
    for f in _FONT_DIR.glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))
    plt.rcParams.update({
        "font.family": [HAND] + FALLBACK,
        "mathtext.fontset": "custom",
        "mathtext.rm": HAND, "mathtext.it": f"{HAND}", "mathtext.bf": f"{HAND}:bold",
        "mathtext.sf": HAND, "mathtext.cal": HAND,
        "mathtext.fallback": "stixsans",  # Kalam has no Greek letters
        "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
        "lines.dash_capstyle": "round",
        "axes.unicode_minus": False,
        "svg.fonttype": "path",
    })
    if not _applied:
        _redirect_fonts()
        _hand_families()
        _wrap_savefig()
        _applied = True
