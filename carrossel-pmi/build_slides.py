#!/usr/bin/env python3
"""PMI Carousel — redesign com composição premium e backgrounds com profundidade."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1080, 1350
MARGIN = 72

# ── Paleta ───────────────────────────────────────────────────────────────────
BG        = (5,  10, 22)
NAVY      = (8,  15, 32)
VIOLET    = (134, 0, 255)
VIOLET_DK = (60,  0, 120)
VIOLET_LT = (180, 80, 255)
CYAN      = (0, 190, 255)
WHITE     = (255, 255, 255)
OFF_WHITE = (230, 230, 245)
GRAY      = (140, 145, 170)
GRAY_LT   = (185, 190, 210)
GREEN     = (0,  200, 100)
RED_ACC   = (220, 40,  70)

# ── Fontes ───────────────────────────────────────────────────────────────────
R = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"
C = "/usr/share/fonts/truetype/roboto/unhinted"

def F(style, size):
    m = {
        "black":   f"{R}/Roboto-Black.ttf",
        "bold":    f"{R}/Roboto-Bold.ttf",
        "medium":  f"{R}/Roboto-Medium.ttf",
        "regular": f"{R}/Roboto-Regular.ttf",
        "light":   f"{R}/Roboto-Light.ttf",
        "cbold":   f"{C}/RobotoCondensed-Bold.ttf",
    }
    return ImageFont.truetype(m[style], size)


# ── Utilidades de desenho ─────────────────────────────────────────────────────
def wrap(text, fnt, max_w, d):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textbbox((0,0), test, font=fnt)[2] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def tag(d, txt, x, y, fnt, fill=VIOLET, fg=WHITE, rx=14, ry=10):
    bb = d.textbbox((0,0), txt, font=fnt)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    d.rounded_rectangle([x, y, x+tw+rx*2, y+th+ry*2], radius=6, fill=fill)
    d.text((x+rx, y+ry), txt, font=fnt, fill=fg)
    return x+tw+rx*2, y+th+ry*2  # x2, y2


def hline(d, y, x1=MARGIN, x2=W-MARGIN, thick=2, color=VIOLET):
    d.rectangle([x1, y, x2, y+thick], fill=color)


def counter(d, n, total=5):
    f = F("regular", 26)
    txt = f"{n:02d} / {total:02d}"
    bb = d.textbbox((0,0), txt, font=f)
    d.text((W - MARGIN - (bb[2]-bb[0]), 58), txt, font=f, fill=GRAY)


def logo(img, path=None, h=58, bottom_pad=46):
    if path is None:
        path = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
    lg = Image.open(path).convert("RGBA")
    ratio = h / lg.height
    nw = int(lg.width * ratio)
    lg = lg.resize((nw, h), Image.LANCZOS)
    x = (W - nw) // 2
    y = H - bottom_pad - h
    img.paste(lg, (x, y), lg)


# ── Background engine ─────────────────────────────────────────────────────────
def make_bg(variant="default"):
    """
    Cria background com camadas:
    1. Base navy escuro
    2. Rings geométricos decorativos (círculos parciais)
    3. Glow direcional
    4. Dot-grid sutil
    """
    base = Image.new("RGB", (W, H), BG)
    layer = Image.new("RGBA", (W, H), (0,0,0,0))
    dl = ImageDraw.Draw(layer)

    if variant == "default":
        # Ring grande bottom-right (violeta, parcial)
        cx, cy, R_ring = W + 160, H + 100, 720
        for t in range(12, 0, -1):
            alpha = int(t * 5)
            dl.ellipse([cx-R_ring-t*4, cy-R_ring-t*4, cx+R_ring+t*4, cy+R_ring+t*4],
                       outline=(VIOLET[0], VIOLET[1], VIOLET[2], alpha), width=2)

        # Ring médio top-left
        cx2, cy2, R2 = -120, -80, 500
        for t in range(10, 0, -1):
            alpha = int(t * 6)
            dl.ellipse([cx2-R2-t*3, cy2-R2-t*3, cx2+R2+t*3, cy2+R2+t*3],
                       outline=(VIOLET_LT[0], VIOLET_LT[1], VIOLET_LT[2], alpha), width=2)

        # Glow blob top-left
        glow = Image.new("RGBA", (W, H), (0,0,0,0))
        dg = ImageDraw.Draw(glow)
        for r in range(500, 0, -20):
            a = int(28 * (1 - r/500))
            dg.ellipse([-r+200, -r+300, r+200, r+300],
                       fill=(VIOLET[0], VIOLET[1], VIOLET[2], a))
        glow = glow.filter(ImageFilter.GaussianBlur(60))
        base.paste(glow, mask=glow.split()[3])

        # Glow blob bottom-right
        glow2 = Image.new("RGBA", (W, H), (0,0,0,0))
        dg2 = ImageDraw.Draw(glow2)
        for r in range(600, 0, -24):
            a = int(20 * (1 - r/600))
            dg2.ellipse([W-r-80, H-r-80, W+r-80, H+r-80],
                        fill=(VIOLET_DK[0], VIOLET_DK[1], VIOLET_DK[2], a))
        glow2 = glow2.filter(ImageFilter.GaussianBlur(80))
        base.paste(glow2, mask=glow2.split()[3])

    elif variant == "cta":
        # CTA: glow centralizado mais intenso
        glow = Image.new("RGBA", (W, H), (0,0,0,0))
        dg = ImageDraw.Draw(glow)
        for r in range(800, 0, -24):
            a = int(35 * (1 - r/800))
            dg.ellipse([W//2-r, H//2-r, W//2+r, H//2+r],
                       fill=(VIOLET[0], VIOLET[1], VIOLET[2], a))
        glow = glow.filter(ImageFilter.GaussianBlur(80))
        base.paste(glow, mask=glow.split()[3])

        # Ring decorativo central
        for t in range(15, 0, -1):
            a = int(t * 4)
            layer.paste(Image.new("RGBA", (W,H), (0,0,0,0)))  # reset
        dl.ellipse([W//2-500, H//2-500, W//2+500, H//2+500],
                   outline=(VIOLET[0], VIOLET[1], VIOLET[2], 40), width=3)
        dl.ellipse([W//2-380, H//2-380, W//2+380, H//2+380],
                   outline=(VIOLET_LT[0], VIOLET_LT[1], VIOLET_LT[2], 25), width=2)

    elif variant == "split":
        # Split: linha diagonal no fundo
        glow = Image.new("RGBA", (W, H), (0,0,0,0))
        dg = ImageDraw.Draw(glow)
        for r in range(500, 0, -20):
            a = int(30 * (1 - r/500))
            dg.ellipse([W//2-r, 400-r, W//2+r, 400+r],
                       fill=(CYAN[0], CYAN[1], CYAN[2], a))
        for r in range(400, 0, -20):
            a = int(25 * (1 - r/400))
            dg.ellipse([-r+100, -r+100, r+100, r+100],
                       fill=(VIOLET[0], VIOLET[1], VIOLET[2], a))
        glow = glow.filter(ImageFilter.GaussianBlur(60))
        base.paste(glow, mask=glow.split()[3])

    # Dot-grid sobre tudo
    base.paste(layer, mask=layer.split()[3])
    d = ImageDraw.Draw(base)
    spacing = 54
    dot_col = (18, 24, 48)
    for x in range(0, W+spacing, spacing):
        for y in range(0, H+spacing, spacing):
            d.ellipse([x-1, y-1, x+1, y+1], fill=dot_col)

    return base


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 01 — CAPA
# ══════════════════════════════════════════════════════════════════════════════
def slide_01():
    img = make_bg("default")
    d = ImageDraw.Draw(img)
    counter(d, 1)

    # — Overline tag
    _, y2 = tag(d, "POSICIONAMENTO & AUTORIDADE", MARGIN, 96, F("bold", 24))

    y = y2 + 56

    # — Linha accent
    hline(d, y)
    y += 28

    # — Headline principal: 2 linhas, enorme
    fh = F("black", 112)
    d.text((MARGIN, y), "Marketing", font=fh, fill=WHITE)
    y += 128
    d.text((MARGIN, y), "é", font=fh, fill=WHITE)

    # "amplificador." em violeta, tamanho menor para caber
    fa = F("black", 96)
    x_amp = MARGIN + d.textbbox((0,0), "é ", font=fh)[2] + 8
    # nova linha
    y += 128
    d.text((MARGIN, y), "amplificador.", font=fa, fill=VIOLET)
    y += 120

    # — Bloco de contraste: o que NÃO é
    hline(d, y, thick=1, color=(60, 65, 100))
    y += 22

    fn = F("bold", 48)
    d.text((MARGIN, y), "Não é milagre.", font=fn, fill=GRAY_LT)
    y += 60
    d.text((MARGIN, y), "Não salva o que está quebrado.", font=fn, fill=GRAY)
    y += 76

    hline(d, y, thick=1, color=(60, 65, 100))
    y += 26

    # — Body
    fb = F("regular", 33)
    body = "Mas quando a base é sólida, marketing integrado transforma presença em resultado real e escalável."
    for line in wrap(body, fb, W - MARGIN*2, d):
        d.text((MARGIN, y), line, font=fb, fill=GRAY)
        y += 46

    y += 18
    d.text((MARGIN, y), "Arrasta para entender →", font=F("medium", 32), fill=VIOLET_LT)

    logo(img)
    img.save(f"{OUT}/slide_01.png")
    print("✓ slide_01")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 02 — O MITO
# ══════════════════════════════════════════════════════════════════════════════
def slide_02():
    img = make_bg("default")
    d = ImageDraw.Draw(img)
    counter(d, 2)

    y = 96

    # Tag de contexto
    _, y2 = tag(d, "ERRO MAIS CARO DO MERCADO", MARGIN, y, F("bold", 24), fill=(80, 0, 0))
    y = y2 + 20

    # Tag de categoria
    _, y2 = tag(d, "✗  O MITO", MARGIN, y, F("bold", 22), fill=RED_ACC)
    y = y2 + 32

    hline(d, y)
    y += 40

    # Aspas decorativas gigantes no fundo
    fq_deco = F("black", 320)
    d_tmp = ImageDraw.Draw(img)
    bb = d_tmp.textbbox((0,0), "❝", font=fq_deco)
    # Renderiza como watermark semi-transparente
    quote_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    dql = ImageDraw.Draw(quote_layer)
    dql.text((MARGIN - 30, y - 80), '"', font=fq_deco, fill=(VIOLET[0], VIOLET[1], VIOLET[2], 18))
    img.paste(quote_layer, mask=quote_layer.split()[3])

    # Quote principal — tipografia dominante
    fq = F("black", 72)
    quote_lines = ['"O marketing vai', 'resolver o problema', 'do nosso produto."']
    for line in quote_lines:
        d.text((MARGIN, y), line, font=fq, fill=WHITE)
        y += 86
    y += 10

    hline(d, y)
    y += 36

    # Destaque visual: caixa com borda
    box_y = y
    d.rounded_rectangle([MARGIN, box_y, W-MARGIN, box_y + 180], radius=12,
                         outline=RED_ACC, width=2, fill=(40, 5, 15))
    fb = F("regular", 30)
    body = "Investir em campanhas antes de resolver o produto, a entrega ou a proposta de valor é o erro mais caro que uma empresa pode cometer."
    blines = wrap(body, fb, W - MARGIN*2 - 40, d)
    by = box_y + 22
    for line in blines:
        d.text((MARGIN + 20, by), line, font=fb, fill=OFF_WHITE)
        by += 42
    y = box_y + 200

    y += 24
    d.text((MARGIN, y), "Continua no próximo slide →", font=F("medium", 32), fill=VIOLET_LT)

    logo(img)
    img.save(f"{OUT}/slide_02.png")
    print("✓ slide_02")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 03 — A VERDADE
# ══════════════════════════════════════════════════════════════════════════════
def slide_03():
    img = make_bg("split")
    d = ImageDraw.Draw(img)
    counter(d, 3)

    y = 96

    hline(d, y)
    y += 28

    # — Diagrama visual: duas colunas  NEGÓCIO → MARKETING
    col_labels_y = y
    d.text((MARGIN, col_labels_y), "NEGÓCIO", font=F("bold", 22), fill=GRAY)
    d.text((MARGIN+420, col_labels_y), "MARKETING INTEGRADO", font=F("bold", 22), fill=GRAY)
    y += 44

    # Row 1: Base sólida
    d.rounded_rectangle([MARGIN, y, MARGIN+340, y+58], radius=8,
                         fill=(0, 55, 35), outline=(0, 200, 100), width=2)
    d.text((MARGIN+14, y+13), "Base sólida", font=F("bold", 32), fill=GREEN)

    # Arrow
    ax = MARGIN + 350
    d.text((ax, y+14), "────→", font=F("regular", 30), fill=VIOLET)
    # Result box
    d.rounded_rectangle([ax+150, y, ax+330, y+58], radius=8,
                         fill=(30, 0, 70), outline=VIOLET, width=2)
    d.text((ax+162, y+13), "Escala", font=F("bold", 32), fill=VIOLET_LT)
    y += 76

    # Row 2: Base fraca
    d.rounded_rectangle([MARGIN, y, MARGIN+340, y+58], radius=8,
                         fill=(55, 5, 15), outline=RED_ACC, width=2)
    d.text((MARGIN+14, y+13), "Base fraca", font=F("bold", 32), fill=RED_ACC)
    ax2 = MARGIN + 350
    d.text((ax2, y+14), "────→", font=F("regular", 30), fill=(100, 30, 50))
    d.rounded_rectangle([ax2+150, y, ax2+330, y+58], radius=8,
                         fill=(50, 5, 15), outline=RED_ACC, width=2)
    d.text((ax2+162, y+13), "Colapso", font=F("bold", 32), fill=RED_ACC)
    y += 90

    hline(d, y)
    y += 30

    # — Métrica gigante centralizada
    # "x8" dominante
    fx8 = F("black", 200)
    bb = d.textbbox((0,0), "x8", font=fx8)
    x8_w = bb[2]-bb[0]
    x_x8 = (W - x8_w) // 2
    # Glow behind x8
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    dg = ImageDraw.Draw(glow)
    for r in range(280, 0, -14):
        a = int(40 * (1-r/280))
        cx_g = W//2
        cy_g = y + 110
        dg.ellipse([cx_g-r, cy_g-r, cx_g+r, cy_g+r],
                   fill=(VIOLET[0], VIOLET[1], VIOLET[2], a))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img.paste(glow, mask=glow.split()[3])
    d = ImageDraw.Draw(img)

    d.text((x_x8, y), "x8", font=fx8, fill=VIOLET)
    y_after_x8 = y + bb[3] - bb[1] + 4
    label_txt = "ROI MÉDIO PMI — quando bem aplicado"
    fb_label = F("bold", 28)
    bb2 = d.textbbox((0,0), label_txt, font=fb_label)
    d.text(((W-(bb2[2]-bb2[0]))//2, y_after_x8), label_txt, font=fb_label, fill=GRAY_LT)
    y = y_after_x8 + 50

    hline(d, y)
    y += 26

    # — A Verdade
    tag(d, "✓  A VERDADE", MARGIN, y, F("bold", 22), fill=(0, 120, 70))
    y += 62

    fv = F("black", 58)
    d.text((MARGIN, y), "Marketing amplifica o que", font=fv, fill=WHITE)
    y += 70
    d.text((MARGIN, y), "já existe — o bom", font=fv, fill=WHITE)
    y += 70
    d.text((MARGIN, y), "e o ruim.", font=fv, fill=VIOLET_LT)
    y += 82

    fb = F("regular", 30)
    body = "A diferença está no diagnóstico antes da execução."
    d.text((MARGIN, y), body, font=fb, fill=GRAY)
    y += 52

    d.text((MARGIN, y), "Continua no próximo slide →", font=F("medium", 30), fill=VIOLET_LT)

    logo(img)
    img.save(f"{OUT}/slide_03.png")
    print("✓ slide_03")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 04 — MÉTODO PMI
# ══════════════════════════════════════════════════════════════════════════════
def slide_04():
    img = make_bg("default")
    d = ImageDraw.Draw(img)
    counter(d, 4)

    y = 96
    hline(d, y)
    y += 28

    tag(d, "⚡  MÉTODO PMI", MARGIN, y, F("bold", 26), fill=VIOLET)
    y += 72

    # Headline
    fh = F("black", 88)
    d.text((MARGIN, y), "Do diagnóstico", font=fh, fill=WHITE)
    y += 102
    d.text((MARGIN, y), "ao crescimento", font=fh, fill=WHITE)
    y += 102
    d.text((MARGIN, y), "em 4 etapas.", font=fh, fill=VIOLET)
    y += 116

    hline(d, y, thick=1, color=(50, 55, 90))
    y += 30

    # 4 steps — layout compacto mas arejado
    steps = [
        ("01", "Diagnóstico",  "Entender antes de agir. Sem pacote, sem pitch."),
        ("02", "Estratégia",   "Plano sob medida integrando canais com meta clara."),
        ("03", "Execução",     "Em prática com dados em tempo real. Ajuste contínuo."),
        ("04", "Crescimento",  "Resultado previsível. Marca consolidada. Escala real."),
    ]

    fn = F("black", 32)
    ft = F("bold", 36)
    fd = F("regular", 28)
    step_h = 118

    for num, title, desc in steps:
        # Linha conectora (exceto último)
        if num != "04":
            d.rectangle([MARGIN + 22, y + step_h - 18, MARGIN + 26, y + step_h + 6],
                         fill=(60, 65, 100))

        # Número círculo
        cx, cy = MARGIN + 24, y + 22
        d.ellipse([cx-22, cy-22, cx+22, cy+22], fill=VIOLET)
        nbb = d.textbbox((0,0), num, font=fn)
        d.text((cx - (nbb[2]-nbb[0])//2, cy - (nbb[3]-nbb[1])//2 - 2), num, font=fn, fill=WHITE)

        # Título + desc
        tx = MARGIN + 64
        d.text((tx, y), title, font=ft, fill=WHITE)
        dy = y + 44
        for line in wrap(desc, fd, W - tx - MARGIN, d):
            d.text((tx, dy), line, font=fd, fill=GRAY)
            dy += 36
        y += step_h

    y += 10
    fb = F("regular", 28)
    d.text((MARGIN, y), "Sem surpresas. Sem pacotes genéricos.", font=fb, fill=GRAY)
    y += 42
    d.text((MARGIN, y), "Último slide →", font=F("medium", 30), fill=VIOLET_LT)

    logo(img)
    img.save(f"{OUT}/slide_04.png")
    print("✓ slide_04")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 05 — CTA
# ══════════════════════════════════════════════════════════════════════════════
def slide_05():
    img = make_bg("cta")
    d = ImageDraw.Draw(img)
    counter(d, 5)

    # Linha decorativa topo
    hline(d, 96)

    y = 130

    # Badge gratuidade
    tag(d, "DIAGNÓSTICO GRATUITO", MARGIN, y, F("bold", 26), fill=(0, 120, 70))
    y += 72

    # Headline central — massiva
    fh = F("black", 100)
    lines_h = ["Pronto para", "escalar o seu", "negócio", "de verdade?"]
    for i, line in enumerate(lines_h):
        color = VIOLET if i == 3 else WHITE
        d.text((MARGIN, y), line, font=fh, fill=color)
        y += 115

    y += 10
    hline(d, y)
    y += 36

    # Body
    fb = F("regular", 33)
    body = "A PMI analisa seu cenário, identifica gargalos reais e mostra o caminho mais curto para o resultado. Sem compromisso. Sem pitch."
    for line in wrap(body, fb, W - MARGIN*2, d):
        d.text((MARGIN, y), line, font=fb, fill=GRAY_LT)
        y += 46

    y += 28

    # CTA button — centralizado, destaque total
    cta_txt = "COMENTA ABAIXO"
    fc = F("black", 38)
    bb = d.textbbox((0,0), cta_txt, font=fc)
    btn_w = bb[2]-bb[0] + 80
    btn_h = bb[3]-bb[1] + 28
    btn_x = (W - btn_w) // 2
    d.rounded_rectangle([btn_x, y, btn_x+btn_w, y+btn_h], radius=10, fill=VIOLET)
    d.text((btn_x + 40, y + 14), cta_txt, font=fc, fill=WHITE)
    y += btn_h + 30

    # Handle
    handle_txt = "@perrymarketingintegrado"
    fh2 = F("medium", 30)
    bb2 = d.textbbox((0,0), handle_txt, font=fh2)
    d.text(((W-(bb2[2]-bb2[0]))//2, y), handle_txt, font=fh2, fill=GRAY_LT)

    logo(img)
    img.save(f"{OUT}/slide_05.png")
    print("✓ slide_05")


# ── Run ───────────────────────────────────────────────────────────────────────
OUT = "/home/user/WEB/carrossel-pmi/slides"
os.makedirs(OUT, exist_ok=True)

if __name__ == "__main__":
    slide_01()
    slide_02()
    slide_03()
    slide_04()
    slide_05()
    print(f"\nDone → {OUT}")
