#!/usr/bin/env python3
"""Gera os ativos de logo AQUAVIA (SVG puro, sem dependência de fonte nas peças-mestre)."""
from pathlib import Path

OUT = Path(__file__).parent / "logo"
NAVY, BLUE, CYAN, WHITE = "#12385A", "#178DD1", "#55C5E8", "#FFFFFF"

DROP = "M32 3 C32 3 11 25.5 11 41 A21 21 0 0 0 53 41 C53 25.5 32 3 32 3 Z"
P = [(2, 43), (20, 52), (34, 22), (62, 31)]  # canal (bézier cúbica): a "via"
GAP, BEAD, HALO = 4.2, 3.3, 5.8


def _bez(t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = P
    u = 1 - t
    return (u**3*x0 + 3*u*u*t*x1 + 3*u*t*t*x2 + t**3*x3, u**3*y0 + 3*u*u*t*y1 + 3*u*t*t*y2 + t**3*y3)


NX, NY = _bez(0.60)  # ponto de medição sobre o canal


def _curve(dy):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = P
    return f"M{x0} {y0+dy} C{x1} {y1+dy} {x2} {y2+dy} {x3} {y3+dy}"


def symbol_body(body, cap, bead, uid="s"):
    """Símbolo 64x64 só com geometria (sem máscaras): topo e corpo separados por um canal
    transparente; ao redor do ponto de medição há um halo vazado."""
    hole = f"M{NX-HALO:.2f} {NY:.2f} a{HALO} {HALO} 0 1 0 {2*HALO} 0 a{HALO} {HALO} 0 1 0 {-2*HALO} 0 Z"
    top = f"{_curve(-GAP/2)} L62 -6 L2 -6 Z"
    bot = f"{_curve(GAP/2)} L62 70 L2 70 Z"
    return (f'<defs><clipPath id="{uid}"><path clip-rule="evenodd" d="{DROP} {hole}"/></clipPath></defs>'
            f'<g clip-path="url(#{uid})"><path d="{top}" fill="{cap}"/><path d="{bot}" fill="{body}"/></g>'
            f'<circle cx="{NX:.2f}" cy="{NY:.2f}" r="{BEAD}" fill="{bead}"/>')


# Wordmark: traço monolinear (5), pontas e junções arredondadas, altura 40.
def wordmark_body(color, dot):
    s = f'fill="none" stroke="{color}" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"'
    A = lambda x: (f'<path {s} d="M{x} 40 L{x+15} 0 L{x+30} 40 M{x+5.6} 28 H{x+24.4}"/>')
    Q = lambda x: (f'<circle {s} cx="{x+20}" cy="20" r="20"/><path {s} d="M{x+27} 28 L{x+37} 39"/>')
    U = lambda x: f'<path {s} d="M{x} 0 V25 A15 15 0 0 0 {x+30} 25 V0"/>'
    V = lambda x: f'<path {s} d="M{x} 0 L{x+15} 40 L{x+30} 0"/>'
    I = lambda x: (f'<path {s} d="M{x} 13 V40"/><circle cx="{x}" cy="2.5" r="3.8" fill="{dot}"/>')
    return A(0) + Q(38) + U(86) + A(124) + V(152) + I(192) + A(202)


WM_W, WM_H = 232, 40  # largura útil do wordmark (sem folga de traço)


def svg(w, h, body, title, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{rect}{body}</svg>\n')


def horizontal(palette, mono=None, bg=None, pad=6):
    body, cap, node, wm, dot = palette
    ks, k, gap = 1.18, 1.0, 16
    sym = symbol_body(body, cap, node, uid=mono or "h")
    sh = 64 * ks
    x_wm = pad + 64 * ks * 0.9 + gap  # a gota é mais estreita que o quadro 64
    y_wm = pad + (sh - WM_H * k) / 2 + 2
    w = int(x_wm + WM_W * k + pad + 3)
    h = int(sh + 2 * pad)
    b = (f'<g transform="translate({pad},{pad}) scale({ks})">{sym}</g>'
         f'<g transform="translate({x_wm + 2.5:.1f},{y_wm:.1f})">{wordmark_body(wm, dot)}</g>')
    return svg(w, h, b, "AQUAVIA", bg)


def stacked(palette, mono=None, bg=None):
    body, cap, node, wm, dot = palette
    w, h = 300, 170
    sym = symbol_body(body, cap, node, uid=mono or "t")
    b = (f'<g transform="translate({w/2-38},4) scale(1.19)">{sym}</g>'
         f'<g transform="translate({(w - WM_W)/2 + 2.5:.1f},116)">{wordmark_body(wm, dot)}</g>')
    return svg(w, h, b, "AQUAVIA", bg)


def symbol_only(palette, mono=None, bg=None):
    body, cap, node, _, _ = palette
    return svg(64, 64, symbol_body(body, cap, node, uid=mono or 's'), "AQUAVIA — símbolo", bg)


LIGHT = (NAVY, CYAN, NAVY, NAVY, CYAN)
DARK = (BLUE, WHITE, BLUE, WHITE, CYAN)
MONO_NAVY = (NAVY, NAVY, NAVY, NAVY, NAVY)
MONO_WHITE = (WHITE, WHITE, WHITE, WHITE, WHITE)

files = {
    "aquavia-symbol.svg": symbol_only(LIGHT),
    "aquavia-symbol-dark.svg": symbol_only(DARK),
    "aquavia-symbol-mono-navy.svg": symbol_only(MONO_NAVY, mono="k1"),
    "aquavia-symbol-mono-white.svg": symbol_only(MONO_WHITE, mono="k2"),
    "aquavia-logo-horizontal.svg": horizontal(LIGHT),
    "aquavia-logo-horizontal-dark.svg": horizontal(DARK),
    "aquavia-logo-horizontal-mono-navy.svg": horizontal(MONO_NAVY, mono="k3"),
    "aquavia-logo-horizontal-mono-white.svg": horizontal(MONO_WHITE, mono="k4"),
    "aquavia-logo-stacked.svg": stacked(LIGHT),
    "aquavia-logo-stacked-dark.svg": stacked(DARK),
}
# favicon / ícone de app: símbolo sobre quadrado navy arredondado
fav_body = f'<rect width="64" height="64" rx="14" fill="{NAVY}"/><g transform="translate(8,8) scale(.75)">{symbol_body(BLUE, WHITE, BLUE)}</g>'
files["favicon.svg"] = svg(64, 64, fav_body, "AQUAVIA")

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(len(files), "arquivos em", OUT)
