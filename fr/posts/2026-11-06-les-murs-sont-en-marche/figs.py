"""Figures pour « Les murs, eux, sont en marche ».

Version française des trois figures de l'édition de la newsletter, dans la palette du site.
Exécuter depuis ce dossier : python figs.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---------- palette (from light.scss) ----------
BG = "#fbfaf7"
INK = "#1f2328"
MUTED = "#5f6b76"
RULE = "#e6e2da"
NAVY = "#1d4f73"
GREEN = "#2e7d5b"
RED = "#a93226"
SAND = "#c9c3b6"
NAVY_T, GREEN_T, RED_T, SAND_T = "#e5eef5", "#e2f0e8", "#f8e8e6", "#ebe7df"

plt.rcParams.update({
    "font.family": "Inter", "font.size": 10, "text.color": INK,
    "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.pad_inches": 0.35,
})
OUT = "figures/"


def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, edge, fill="white", lw=1.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                fc=fill, ec=edge, lw=lw))


def arrow(ax, pts):
    for (x0, y0), (x1, y1) in zip(pts[:-2], pts[1:-1]):
        ax.plot([x0, x1], [y0, y1], color=SAND, lw=1.3, solid_capstyle="butt")
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=11,
                                 color=SAND, lw=1.3, shrinkA=0, shrinkB=0))


def fig_test_de_masse():
    W, H = 9.6, 4.3
    fig, ax = canvas(W, H)
    ax.text(0.25, H - 0.3, "Ce qui dit non passe le test de la masse. Ce qui compte échoue.",
            fontsize=12.5, weight="semibold", va="top")
    # question
    qx, qy, qw, qh = 2.1, 2.95, 5.4, 0.55
    box(ax, qx, qy, qw, qh, SAND)
    ax.text(qx + qw / 2, qy + qh / 2, "Retire-t-il ou évite-t-il plus de masse qu'il n'en ajoute ?",
            ha="center", va="center", fontsize=10.5)
    lx, rx, by = 2.4, 7.2, 2.5
    arrow(ax, [(3.75, qy), (3.75, 2.75), (lx, 2.75), (lx, by)])
    arrow(ax, [(5.85, qy), (5.85, 2.75), (rx, 2.75), (rx, by)])
    ax.text(2.28, 2.6, "oui", color=MUTED, fontsize=9.5, ha="right", va="center")
    ax.text(7.32, 2.6, "non", color=MUTED, fontsize=9.5, ha="left", va="center")
    cols = [
        (0.25, GREEN, GREEN_T, "À garder : il dit non", [
            "Un objectif clair pour la période",
            "Une définition partagée de « terminé »",
            "Des demandes qui expirent si personne ne les renouvelle",
            "Un budget de masse qui oblige à retirer",
        ]),
        (5.05, RED, RED_T, "À couper ou alléger : il compte", [
            "Estimer chaque élément",
            "Rapports et tableaux de bord que personne ne lit",
            "Mesures d'activité : heures, points, volume",
            "Nouveaux comités, cérémonies et rôles",
        ]),
    ]
    for x, edge, fill, title, items in cols:
        box(ax, x, 0.15, 4.3, 2.35, edge, fill, lw=1.6)
        ax.text(x + 0.22, 2.22, title, fontsize=10.5, weight="semibold", va="top")
        for i, t in enumerate(items):
            ax.text(x + 0.22, 1.72 - i * 0.4, t, fontsize=10, va="top")
    fig.savefig(OUT + "fig01.png")
    plt.close(fig)


def fig_paillasse():
    fig, ax = plt.subplots(figsize=(9.6, 3.9))
    fig.subplots_adjust(left=0.17, right=0.9, top=0.66, bottom=0.2)
    fig.text(0.02, 0.97, "Automatisez toutes les étapes non physiques : "
             "les sciences de laboratoire plafonnent à 3–4×",
             fontsize=12.5, weight="semibold", va="top")
    fig.text(0.02, 0.89, "Production de recherche à budget constant, par rapport à aujourd'hui "
             "sans IA · modèle d'Anthropic, 2026", fontsize=9.5, color=MUTED, va="top")
    rows = [  # nom, IA d'aujourd'hui, (bas, haut), couleur
        ("Statistique", 2.0, (15, 16), SAND),
        ("Chimie", 1.4, (3, 4), NAVY),
    ]
    for i, (name, today, (lo, hi), col) in enumerate(rows):
        y = 1 - i
        mid = (lo + hi) / 2
        ax.barh(y + 0.17, today, height=0.2, color=SAND_T)
        ax.barh(y - 0.13, mid, height=0.24, color=col)
        ax.errorbar(mid, y - 0.13, xerr=[[mid - lo], [hi - mid]], fmt="none",
                    ecolor=INK, elinewidth=1.1, capsize=5)
        ax.text(today + 0.2, y + 0.17, f"{today:.1f}×".replace(".", ","),
                va="center", fontsize=9.5, color=MUTED)
        ax.text(hi + 0.25, y - 0.13, f"{lo}–{hi}×", va="center", fontsize=10.5,
                weight="semibold")
    ax.set_yticks([1, 0])
    ax.set_yticklabels([r[0] for r in rows], fontsize=10.5, color=INK)
    ax.get_yticklabels()[1].set_weight("semibold")
    ax.tick_params(axis="y", length=0, pad=12)
    ax.set_xlim(0, 17.5)
    ax.set_ylim(-0.55, 1.5)
    ax.set_xticks([0, 4, 8, 12, 16])
    ax.set_xticklabels(["0×", "4×", "8×", "12×", "16×"])
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="x", color=RULE, lw=0.9)
    ax.set_axisbelow(True)
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(SAND)
    # légende
    for x, c, t in [(0.02, SAND_T, "L'IA d'aujourd'hui, largement adoptée"),
                    (0.42, SAND, "Toutes les étapes non physiques automatisées (fourchette)")]:
        fig.patches.append(FancyBboxPatch((x, 0.745), 0.018, 0.04, boxstyle="square,pad=0",
                                          transform=fig.transFigure, fc=c, ec="none"))
        fig.text(x + 0.027, 0.765, t, fontsize=9.5, color=MUTED, va="center")
    fig.text(0.02, 0.04, "Pourquoi : les sciences de laboratoire et de terrain consacrent 38 à 41 % "
             "du temps de recherche à des étapes physiques ; le domaine médian, environ 4 %.",
             fontsize=9, color=MUTED)
    fig.savefig(OUT + "fig02.png")
    plt.close(fig)


def fig_trois_murs():
    W, H = 9.6, 4.6
    fig, ax = canvas(W, H)
    ax.text(0.25, H - 0.3, "Rendez la production rapide, et le mur se déplace en trois endroits",
            fontsize=12.5, weight="semibold", va="top")
    box(ax, 0.25, 1.725, 2.3, 0.9, NAVY, NAVY_T, lw=1.8)
    ax.text(1.4, 2.32, "Produire", ha="center", va="center", fontsize=11, weight="semibold")
    ax.text(1.4, 2.0, "désormais rapide et bon marché", ha="center", va="center",
            fontsize=9.5, color=MUTED)
    walls = [
        ("1. Ce que vous portez",
         "Plus de choses à stocker, retrouver, vérifier et faire vivre",
         "À faire : faire du retrait un livrable"),
        ("2. Le point de contrôle",
         "Même dans un labo d'IA, l'inquiétude porte sur juger, pas construire",
         "À faire : approuver ce qui est irréversible, surveiller le reste"),
        ("3. Le monde physique",
         "Science : les labos plafonnent à 3–4×, les domaines de bureau atteignent 15–16×",
         "À faire : repenser les étapes qui se déroulent dans le monde"),
    ]
    bx, bw, bh = 3.25, 6.1, 0.95
    ys = [3.0 - i * 1.3 for i in range(3)]
    for (t, s, d), y in zip(walls, ys):
        box(ax, bx, y, bw, bh, SAND)
        ax.text(bx + 0.2, y + bh - 0.17, t, fontsize=11, weight="semibold", va="top")
        ax.text(bx + 0.2, y + bh - 0.47, s, fontsize=9.3, color=MUTED, va="top")
        ax.text(bx + 0.2, y + bh - 0.71, d, fontsize=9.3, va="top")
    mx = 2.85
    ax.plot([2.55, mx], [2.175, 2.175], color=SAND, lw=1.3)
    ax.plot([mx, mx], [ys[2] + bh / 2, ys[0] + bh / 2], color=SAND, lw=1.3)
    for y in ys:
        arrow(ax, [(mx, y + bh / 2), (bx, y + bh / 2)])
    fig.savefig(OUT + "fig03.png")
    plt.close(fig)


if __name__ == "__main__":
    fig_test_de_masse()
    fig_paillasse()
    fig_trois_murs()
