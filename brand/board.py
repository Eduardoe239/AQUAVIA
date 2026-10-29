from pathlib import Path
import re, cairosvg
L = Path(__file__).parent / "logo"
def inner(name):
    t = (L / name).read_text()
    vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', t); w, h = map(int, vb.groups())
    body = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", t.strip()); body = re.sub(r"<title>.*?</title>", "", body)
    return body, w, h
def place(name, x, y, width):
    body, w, h = inner(name); k = width / w
    return f'<g transform="translate({x},{y}) scale({k:.4f})">{body}</g>', h * k
F = 'font-family="Inter, Helvetica, Arial, sans-serif"'
parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="1200" height="900">',
         '<rect width="1200" height="900" fill="#F4F7FA"/>',
         f'<text x="48" y="56" {F} font-size="14" fill="#5B6B78" letter-spacing="2">AQUAVIA · PRANCHA DE MARCA · v1.0 (proposta)</text>']
parts.append('<rect x="48" y="80" width="700" height="260" rx="16" fill="#fff"/>')
g, _ = place("aquavia-logo-horizontal.svg", 100, 160, 600); parts.append(g)
parts.append('<rect x="772" y="80" width="380" height="260" rx="16" fill="#12385A"/>')
g, _ = place("aquavia-logo-stacked-dark.svg", 812, 112, 300); parts.append(g)
parts.append(f'<text x="48" y="392" {F} font-size="22" font-weight="700" fill="#12385A">Uma união para um gasto eficiente.</text>')
parts.append(f'<text x="48" y="418" {F} font-size="14" fill="#5B6B78">AQUA + VIA: a água e o caminho — a união entre o que flui e o que se mede.</text>')
# tamanhos do símbolo + favicon
x = 48
for wd in (96, 64, 40, 24, 16):
    g, h = place("aquavia-symbol.svg", x, 470, wd); parts.append(g); x += wd + 28
g, _ = place("favicon.svg", x + 12, 470, 64); parts.append(g)
parts.append(f'<text x="48" y="580" {F} font-size="12" fill="#5B6B78">Símbolo em 96 · 64 · 40 · 24 · 16 px e ícone de app/favicon</text>')
# monocromáticas
parts.append('<rect x="48" y="610" width="360" height="110" rx="12" fill="#fff"/>')
g, _ = place("aquavia-logo-horizontal-mono-navy.svg", 72, 640, 310); parts.append(g)
parts.append('<rect x="428" y="610" width="360" height="110" rx="12" fill="#178DD1"/>')
g, _ = place("aquavia-logo-horizontal-mono-white.svg", 452, 640, 310); parts.append(g)
# paleta
sw = [("#12385A", "Navy", "estrutura"), ("#178DD1", "Azul", "ação e dados"), ("#55C5E8", "Ciano", "água / destaque"), ("#F4F7FA", "Gelo", "fundo")]
for i, (c, n, u) in enumerate(sw):
    x = 828 + (i % 2) * 168; y = 400 + (i // 2) * 150
    parts.append(f'<rect x="{x}" y="{y}" width="152" height="100" rx="12" fill="{c}" stroke="#D5DEE6"/>')
    parts.append(f'<text x="{x}" y="{y+120}" {F} font-size="14" font-weight="700" fill="#203040">{n} {c}</text>')
    parts.append(f'<text x="{x}" y="{y+138}" {F} font-size="12" fill="#5B6B78">{u}</text>')
parts.append(f'<text x="48" y="780" {F} font-size="12" fill="#5B6B78">Tipografia de apoio: Inter (ou equivalente licenciada). Verde, âmbar e vermelho ficam reservados a estados de sistema, nunca à marca.</text>')
parts.append(f'<text x="48" y="880" {F} font-size="11" fill="#5B6B78">Proposta de identidade — requer pesquisa de anterioridade (INPI) e revisão jurídica antes de uso comercial ou registro.</text>')
parts.append("</svg>")
Path(__file__).with_name("aquavia-brand-board.svg").write_text("\n".join(parts))
cairosvg.svg2png(url=str(Path(__file__).with_name("aquavia-brand-board.svg")), write_to=str(Path(__file__).with_name("aquavia-brand-board.png")), output_width=1600)
