#!/usr/bin/env python3
# regenerates fastfetch.svg — live GitHub stats, uptime, and your age.
# your birthdate lives INSIDE fastfetch.svg: <!-- BORN=ddmmyyyy --> — edit it there.
import json, calendar, re, urllib.request
from datetime import date
from pathlib import Path

GH_USER = "realcgcristi"
GIT_BORN = date(2022, 5, 28)  # account created
SVG = Path(__file__).parent / "fastfetch.svg"

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
    req = urllib.request.Request(f"https://api.github.com{path}", headers={"User-Agent": "fastfetch-gen"})
    return json.load(urllib.request.urlopen(req))

user = gh("/users/" + GH_USER)
repos = gh(f"/users/{GH_USER}/repos?per_page=100")
stars = sum(r["stargazers_count"] for r in repos if not r["fork"])

BORN = None
old = SVG.read_text() if SVG.exists() else ""
match = re.search(r"BORN=(\d{2})(\d{2})(\d{4})", old)
if match:
    BORN = date(int(match.group(3)), int(match.group(2)), int(match.group(1)))

if BORN:
    born_line = BORN.strftime("%b %d, %Y") + f"  ({fmt(since(BORN))} old)"
else:
    born_line = "edit BORN=ddmmyyyy at the top of this file"

art = """;
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

W = 1060
AFS, ACH, ALH = 6.4, 3.85, 8.0
X = 24
maxw = max(len(l) for l in ART)
RX = int(X + maxw * ACH + 30)
COL, FSC, IFS = 38, 9.05, 15
DOT = '<tspan class="dot">. </tspan>'

def line(y, key, value, first=False):
    k = key + ":" if key else ""
    p = "." * max(2, COL - len(k))
    return f'<tspan x="{RX}" y="{y}">{"" if first else DOT}<tspan class="key">{k}</tspan><tspan class="dot">{p}</tspan><tspan class="val">{value}</tspan></tspan>'

def hdr(y, label):
    dashes = int((W - RX - FSC * (len(label) + 4)) / FSC) - 2
    return f'<tspan x="{RX}" y="{y}"><tspan class="key">- {label} </tspan><tspan class="dot">-{"-" * dashes}</tspan></tspan>'

rows = []
def emit(key=None, value="", hdr_label=None, first=False):
    y = 30 + len(rows) * 24
    rows.append(hdr(y, hdr_label) if hdr_label else line(y, key, value, first))

emit(hdr_label="cg@getswift")
emit("OS", "Romania (GMT+2)", first=True)
emit("Born", born_line)
emit("Uptime", fmt(since(GIT_BORN)) + " on GitHub")
emit("Host", "cgcristi.dev")
emit("Kernel", "edge-native (Cloudflare)")
emit("IDE", "VS Code, Android Studio")
emit()
emit("Langs.Code", "TypeScript, Kotlin, Dart,")
emit("", "Python, Java")
emit("Langs.Edge", "Workers, Pages, D1, R2, Cron")
emit("Langs.Human", "Romanian, English")
emit()
emit("Projects", "temp — files that self-delete")
emit("", "bin — burn-after-read pastes")
emit("", "dev — home base")
emit()
emit(hdr_label="GitHub Stats")
emit("Repos", f"{user['public_repos']} public | Stars: {stars}", first=True)
emit("Followers", f"{user['followers']} | streak: unbroken")
emit("Storage", "everything auto-deleted in 7d")

art_tspans = "\n".join(f'    <tspan x="{X}" y="{20 + i*ALH}">{l}</tspan>' for i, l in enumerate(ART))
body_h = max(int(20 + len(ART) * ALH + 16), int(30 + len(rows) * 24 + 14))
born_tag = BORN.strftime("%d%m%Y") if BORN else "ddmmyyyy"

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- BORN={born_tag}  <- your birthdate (ddmmyyyy). edit this line; the daily workflow keeps the age fresh -->
<svg xmlns="http://www.w3.org/2000/svg" font-family="Consolas,'Cascadia Mono',Menlo,monospace" width="{W}" height="{body_h}" font-size="{IFS}">
  <style>
    .key {{ fill: #ADF878; font-weight: bold; }}
    .val {{ fill: #C9D1D9; }}
    .dot {{ fill: #30363D; }}
    .art {{ fill: #C9D1D9; }}
    text, tspan {{ white-space: pre; }}
  </style>
  <rect width="{W}" height="{body_h}" fill="#0d1117" rx="15"/>
  <text class="art" font-size="{AFS}">
{art_tspans}
  </text>
  <text>{chr(10).join(rows)}</text>
</svg>
'''
SVG.write_text(svg)
print("born:", born_line, "| uptime:", fmt(since(GIT_BORN)), "| repos", user["public_repos"], "| stars", stars, "| followers", user["followers"])
