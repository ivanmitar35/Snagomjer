"""Crta WBS i gantogram za projektnu dokumentaciju.

Uređivanje: promijeni popis `wbs` (WBS) ili `tasks` / `phases` (gantogram) ispod,
pa pokreni:  python crtanje_slika.py
Rezultat (u ovoj mapi): wbs.png, wbs.svg, gantogram.png, gantogram.svg.
PNG se ubacuje u Word; SVG se može dalje uređivati (Inkscape, Figma, draw.io).
Potrebno: pip install matplotlib
"""
import textwrap
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch, Rectangle

plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"  # tekst u SVG-u ostaje tekst (može se uređivati)
OUT = Path(__file__).resolve().parent

COLORS = ["#4C6A92", "#3E8E7E", "#C47F2C", "#8E5A9B", "#B5524B", "#5F7D3A"]
INK = "#222222"


def lighten(hex_color, f):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(int(c + (255 - c) * f) for c in (r, g, b))


# ---------------- WBS ----------------
wbs = [
    ("1. Upravljanje\nprojektom", ["1.1 Plan projekta", "1.2 Sastanci i zapisnici", "1.3 Praćenje napretka (board, gantogram)"]),
    ("2. Analiza\ni dizajn", ["2.1 Analiza sličnih aplikacija", "2.2 Zahtjevi i korisničke priče", "2.3 Wireframeovi i navigacija", "2.4 Model podataka", "2.5 Arhitektura aplikacije"]),
    ("3. Implementacija", ["3.1 Postavljanje projekta (repo, CI)", "3.2 Podatkovni sloj (SQLite)", "3.3 Katalog vježbi", "3.4 Unos treninga", "3.5 Izračuni (volumen, 1RM, rekordi)", "3.6 Povijest treninga", "3.7 Analitika i grafovi", "3.8 Postavke"]),
    ("4. Testiranje", ["4.1 Unit testovi", "4.2 Testovi komponenti i ekrana", "4.3 Testiranje s korisnicima"]),
    ("5. Dokumentacija\ni predaja", ["5.1 Tehnička dokumentacija", "5.2 Korisničke upute", "5.3 Izvještaj o testiranju", "5.4 Prezentacija i demonstracija"]),
]

W, H = 7.2, 5.6
fig = plt.figure(figsize=(W, H), dpi=220)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")


def box(x, y, w, h, text, fc, ec, fs, bold=False, color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.05",
                                fc=fc, ec=ec, lw=0.9))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color=color, linespacing=1.15)


# root
rw, rh = 3.6, 0.5
rx, ry = (W - rw) / 2, H - 0.15 - rh
box(rx, ry, rw, rh, "Mobilna aplikacija za praćenje\ni analizu rezultata treninga snage", "#2F3E52", "#2F3E52", 8.5, True, "white")

n = len(wbs)
margin, gap = 0.12, 0.1
cw = (W - 2 * margin - (n - 1) * gap) / n
l1y, l1h = ry - 0.45 - 0.55, 0.55
bus_y = ry - 0.22
ax.plot([W / 2, W / 2], [ry, bus_y], color="#555", lw=0.9)
centers = [margin + i * (cw + gap) + cw / 2 for i in range(n)]
ax.plot([centers[0], centers[-1]], [bus_y, bus_y], color="#555", lw=0.9)

for i, (title, items) in enumerate(wbs):
    x = margin + i * (cw + gap)
    c = COLORS[i]
    ax.plot([centers[i], centers[i]], [bus_y, l1y + l1h], color="#555", lw=0.9)
    box(x, l1y, cw, l1h, title, c, c, 7.6, True, "white")
    y = l1y - 0.14
    spine_x = x + 0.09
    for it in items:
        lines = textwrap.fill(it, 19)
        h = 0.2 + 0.13 * lines.count("\n") + 0.06
        y -= h
        bx = x + 0.2
        box(bx, y, cw - 0.2, h, lines, lighten(c, 0.85), c, 6.6)
        ax.plot([spine_x, bx], [y + h / 2, y + h / 2], color=c, lw=0.8)
        last_mid = y + h / 2
        y -= 0.07
    ax.plot([spine_x, spine_x], [l1y, last_mid], color=c, lw=0.8)

fig.savefig(OUT / "wbs.png", dpi=220, facecolor="white")
fig.savefig(OUT / "wbs.svg", facecolor="white")
plt.close(fig)

# ---------------- Gantt ----------------
D = lambda s: date(*map(int, s.split("-")))
tasks = [
    # (phase index, label, start, duration days | None for milestone)
    (0, "Formiranje tima, uloge", "2026-11-10", 4),
    (0, "Alati, plan projekta", "2026-11-16", 5),
    (0, "M1 Plan projekta v1", "2026-11-20", None),
    (1, "Analiza sličnih aplikacija", "2026-11-23", 4),
    (1, "Korisničke priče, prioriteti", "2026-11-23", 7),
    (1, "Wireframeovi", "2026-11-26", 7),
    (1, "Model podataka", "2026-11-30", 4),
    (1, "Expo projekt + prototip", "2026-11-23", 12),
    (1, "M2 Specifikacija gotova", "2026-12-04", None),
    (2, "Podatkovni sloj", "2026-12-07", 7),
    (2, "Katalog vježbi", "2026-12-07", 7),
    (2, "Unos treninga", "2026-12-09", 10),
    (2, "Povijest treninga", "2026-12-14", 5),
    (2, "M3 MVP", "2026-12-18", None),
    (3, "Grafovi napretka", "2027-01-07", 9),
    (3, "Osobni rekordi, 1RM", "2027-01-07", 6),
    (3, "Poželjne funkcije", "2027-01-11", 5),
    (3, "M4 Feature freeze", "2027-01-15", None),
    (4, "Testiranje s korisnicima", "2027-01-18", 4),
    (4, "Ispravci i poliranje", "2027-01-18", 5),
    (4, "M5 Testiranje završeno", "2027-01-22", None),
    (5, "Dokumentacija, upute", "2027-01-18", 10),
    (5, "Prezentacija", "2027-01-25", 4),
    (5, "M6 Primopredaja", "2027-01-29", None),
]
phases = ["1. Pokretanje i planiranje", "2. Analiza i dizajn", "3. Iteracija 1: jezgra (MVP)",
          "4. Iteracija 2: analitika", "5. Testiranje i poliranje", "6. Dokumentacija i predaja"]

fig, ax = plt.subplots(figsize=(7.2, 6.2), dpi=220)
n = len(tasks)
for row, (p, label, s, d) in enumerate(tasks):
    y = n - 1 - row
    c = COLORS[p]
    st = D(s)
    if d is None:
        ax.scatter(mdates.date2num(st) + 0.5, y, marker="D", s=34, color=INK, zorder=3)
    else:
        ax.barh(y, d, left=mdates.date2num(st), height=0.6, color=c, edgecolor=c, zorder=2)

ax.set_yticks(range(n))
ax.set_yticklabels([t[1] for t in reversed(tasks)], fontsize=7)
for lbl, t in zip(ax.get_yticklabels(), reversed(tasks)):
    if t[3] is None:
        lbl.set_fontweight("bold")

start, end = D("2026-11-09"), D("2027-01-31")
ax.set_xlim(mdates.date2num(start), mdates.date2num(end))
ax.set_ylim(-0.7, n - 0.3)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m."))
ax.tick_params(axis="x", labelsize=6.8, top=True, labeltop=True, bottom=True, labelbottom=True)
ax.tick_params(axis="y", length=0)
ax.set_axisbelow(True)
ax.grid(axis="x", color="#dddddd", lw=0.6, zorder=0)
for sp in ["right", "left"]:
    ax.spines[sp].set_visible(False)
for sp in ["top", "bottom"]:
    ax.spines[sp].set_color("#999")

# holidays band
h0, h1 = mdates.date2num(D("2026-12-21")), mdates.date2num(D("2027-01-07"))
ax.add_patch(Rectangle((h0, -0.7), h1 - h0, n + 0.4, color="#eeeeee", zorder=1))
ax.text((h0 + h1) / 2, n / 2, "Božićni praznici\n(rezerva)", ha="center", va="center",
        fontsize=7.5, color="#666", zorder=1.5,
        bbox=dict(fc="#eeeeee", ec="none", pad=2))

# phase separators
prev = None
for row, t in enumerate(tasks):
    if prev is not None and t[0] != prev:
        ax.axhline(n - 1 - row + 0.5, color="#cccccc", lw=0.6, zorder=1)
    prev = t[0]

handles = [Rectangle((0, 0), 1, 1, color=COLORS[i]) for i in range(len(phases))]
handles.append(plt.Line2D([], [], marker="D", color=INK, ls="", markersize=5))
ax.legend(handles, phases + ["Kontrolna točka"], fontsize=6.5, loc="upper center",
          bbox_to_anchor=(0.42, -0.06), ncol=3, frameon=False)
fig.tight_layout()
fig.savefig(OUT / "gantogram.png", dpi=220, facecolor="white")
fig.savefig(OUT / "gantogram.svg", facecolor="white")
print("Spremljeno u", OUT)
