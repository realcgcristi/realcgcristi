#!/usr/bin/env python3
# regenerates fastfetch.svg (desktop) + fastfetch-mobile.svg (stacked) —
# live GitHub stats, uptime, and your age. birthdate lives in the SVG: BORN=ddmmyyyy
import json, calendar, re, urllib.request
from datetime import date
from pathlib import Path

GH_USER = "realcgcristi"
GIT_BORN = date(2022, 5, 28)
SVG_DIR = Path(__file__).parent

def since(start, end=None):
    end = end or date.today()
    y, m, d = end.year - start.year, end.month - start.month, end.day - start.day
    if d < 0:
        m -= 1
        pm, py = (end.month - 1) or 12, end.year - (end.month == 1)
        d += calendar.monthrange(py, pm)[1]
    if m < 0:
        y -= 1; m += 12
    return y, m, d

def fmt(t):
    parts = ([] if t[0] == 0 else [f"{t[0]} year{'s' if t[0] != 1 else ''}"]) + \
            ([] if t[1] == 0 else [f"{t[1]} month{'s' if t[1] != 1 else ''}"]) + \
            ([] if t[2] == 0 else [f"{t[2]} day{'s' if t[2] != 1 else ''}"])
    return " ".join(parts) or "0 days"

def gh(path):
    req = urllib.request.Request("https://api.github.com" + path, headers={"User-Agent": "fastfetch-gen"})
    return json.load(urllib.request.urlopen(req))

user = gh("/users/" + GH_USER)
repos = gh(f"/users/{GH_USER}/repos?per_page=100")
stars = sum(r["stargazers_count"] for r in repos if not r["fork"])

BORN = None
old = (SVG_DIR / "fastfetch.svg").read_text() if (SVG_DIR / "fastfetch.svg").exists() else ""
m = re.search(r"BORN=(\d{2})(\d{2})(\d{4})", old)
if m:
    BORN = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
born_line = BORN.strftime("%b %d, %Y") + f"  ({fmt(since(BORN))} old)" if BORN else "edit BORN=ddmmyyyy at the top of this file"

art = """
                                                 --------
                                           =-------------------
                                        --------------------------
                                     -------------------------------=
                                   =----------------------------------
                                  --------------------------------------
                                -----------------------------------------
                                ------------------------------------------
                              ---------------------------------------------
                              ----------------------------------------------
                   --------------------------------      -------------------
               ----------------------------------          ------------------     -====
            ------------------------------------            ---------------------------------
          -----------------------------------=                ----------------------------------
         -----------------------------------                    ----------------------------------
       -----------------------------------                        ----------------------------------
      ----------------------------------         --      --         ----------------------------------
     ---------------------------------=        =---      ----        ---------------------------------=
     --------------------------------        ------      -----=        --------------------------------
    ---------------------------------       -------      -------       ---------------------------------
   -----------------------------------    ---------      ---------    -----------------------------------
   ------------------------------------------------      ------------------------------------------------
   ------------------------------------------------      ------------------------------------------------
   ------------------------------------------------      ------------------------------------------------
   ------------------------------------------------      ------------------------------------------------
   ------------------------------------------------      ------------------------------------------------
    -----------------------------------------------      -----------------------------------------------
     ----------------------------------------------      ----------------------------------------------
     ----------------------------------------------      ---------------------------------------------=
      ---------------------------------------------      --------------------------------------------=
       --------------------------------------------      -------------------------------------------
        =-------------------------------------------=   -------------------------------------------
          ---------------------------------------------------------------------------------------
            =----------------------------------------------------------------------------------=
               ------------------------------------------------------------------------------
                  ------------------------------------------------------------------------
                        =----------------------------------------------------------
""".strip("\n").split("\n")
indents = [len(l) - len(l.lstrip()) for l in art if l.strip()]
pad = min(indents)
ART = [l[pad:].rstrip() for l in art]
MAXW = max(len(l) for l in ART)
NLINES = len(ART)

def esc(s): return s

def tspans_art(x, y0, afs, alh):
    return "\n".join(f'    <tspan x="{x}" y="{y0 + i*alh}">{esc(l)}</tspan>' for i, l in enumerate(ART))

def build_rows(rx, col, w, ifs):
    fsc = ifs * 0.6033
    DOT = '<tspan class="dot">. </tspan>'
    def line(y, key, value, first=False):
        k = key + ":" if key else ""
        p = "." * max(2, col - len(k))
        return f'<tspan x="{rx}" y="{y}">{"" if first else DOT}<tspan class="key">{k}</tspan><tspan class="dot">{p}</tspan><tspan class="val">{value}</tspan></tspan>'
    def hdr(y, label):
        dashes = int((w - rx - fsc * (len(label) + 4)) / fsc) - 2
        return f'<tspan x="{rx}" y="{y}"><tspan class="key">- {label} </tspan><tspan class="dot">-{"-" * dashes}</tspan></tspan>'
    rows = []
    def emit(key=None, value="", hdr_label=None, first=False, y=None):
        rows.append(hdr(y, hdr_label) if hdr_label else line(y, key, value, first))
    return emit, line, hdr, rows

INFO = [
    ("hdr", "cg@getswift"), ("k", "OS", "Romania (GMT+2)"), ("k", "Born", born_line),
    ("k", "Uptime", fmt(since(GIT_BORN)) + " on GitHub"), ("k", "Host", "cgcristi.dev"),
    ("k", "Kernel", "edge-native (Cloudflare)"), ("k", "IDE", "VS Code, Android Studio"),
    ("gap",), ("k", "Langs.Code", "TypeScript, Kotlin, Dart,"), ("k", "", "Python, Java"),
    ("k", "Langs.Edge", "Workers, Pages, D1, R2, Cron"), ("k", "Langs.Human", "Romanian, English"),
    ("gap",), ("k", "Projects", "temp — files that self-delete"), ("k", "", "bin — burn-after-read pastes"),
    ("k", "", "dev — home base"), ("gap",), ("hdr", "GitHub Stats"),
    ("kf", "Repos", f"{user['public_repos']} public | Stars: {stars}"),
    ("k", "Followers", f"{user['followers']} | streak: unbroken"),
    ("k", "Storage", "everything auto-deleted in 7d"),
]

def make_svg(w, art_x, art_y, afs, alh, ifs, info_x, info_y, row_gap, col):
    emit, line, hdr, rows = build_rows(info_x, col, w, ifs)
    for item in INFO:
        y = info_y + len(rows) * row_gap
        if item[0] == "hdr": emit(hdr_label=item[1], y=y)
        elif item[0] == "gap": emit(y=y)
        elif item[0] == "kf": emit(item[1], item[2], first=True, y=y)
        else: emit(item[1], item[2], y=y)
    body_h = max(int(art_y + NLINES * alh + 16), int(info_y + len(rows) * row_gap + 14))
    born_tag = BORN.strftime("%d%m%Y") if BORN else "ddmmyyyy"
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- BORN={born_tag}  <- your birthdate (ddmmyyyy). edit this line; the daily workflow keeps the age fresh -->
<svg xmlns="http://www.w3.org/2000/svg" font-family="Consolas,'Cascadia Mono',Menlo,monospace" width="{w}" height="{body_h}" font-size="{ifs}" viewBox="0 0 {w} {body_h}">
  <style>
    .key {{ fill: #ADF878; font-weight: bold; }}
    .val {{ fill: #C9D1D9; }}
    .dot {{ fill: #30363D; }}
    .art {{ fill: #C9D1D9; }}
    text, tspan {{ white-space: pre; }}
  </style>
  <rect width="{w}" height="{body_h}" fill="#0d1117" rx="15"/>
  <text class="art" font-size="{afs}">
{tspans_art(art_x, art_y, afs, alh)}
  </text>
  <text>{chr(10).join(rows)}</text>
</svg>
'''

ACH = 0.2406 * 16   # ~3.85px per char at 6.4px font
ALH = 8.0
desktop = make_svg(1060, 24, 20, 6.4, ALH, 15, int(24 + MAXW * ACH + 30), 30, 24, 38)
mobile  = make_svg(560, 22, 18, 6.4, ALH, 13.5, 22, 18 + NLINES * ALH + 34, 22, 42)
(SVG_DIR / "fastfetch.svg").write_text(desktop)
(SVG_DIR / "fastfetch-mobile.svg").write_text(mobile)
print("born:", born_line, "| uptime:", fmt(since(GIT_BORN)), "| repos", user["public_repos"], "| stars", stars, "| followers", user["followers"])
