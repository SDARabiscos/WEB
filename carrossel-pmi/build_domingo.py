#!/usr/bin/env python3
"""
PMI — Carrosseis de Domingo.
3 carrosseis, 3 layouts completamente distintos.
  A: MANIFESTO  — tipografia gigante, editorial escuro
  B: RUPTURA    — contraste extremo, palavra riscada
  C: DADO       — número herói, data journalism
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os

W, H    = 1080, 1350
MARGIN  = 64
MAX_W   = W - MARGIN * 2

VLT    = (160,  60, 255)
PINK   = (236,  72, 153)
VIOLET = (134,   0, 255)
WHITE  = (255, 255, 255)
DARK   = (  8,   6,  14)
OFFWHT = (235, 228, 245)
GRAY   = (160, 155, 175)
BLACK  = (  0,   0,   0)
LIME   = ( 57, 255,  20)   # acento neon para carousel B

R = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"
def F(style, size):
    return ImageFont.truetype({
        "black":   f"{R}/Roboto-Black.ttf",
        "bold":    f"{R}/Roboto-Bold.ttf",
        "medium":  f"{R}/Roboto-Medium.ttf",
        "regular": f"{R}/Roboto-Regular.ttf",
        "light":   f"{R}/Roboto-Light.ttf",
    }[style], size)

def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def tw(d, t, f):
    bb = d.textbbox((0,0), t, font=f); return bb[2]-bb[0]
def th_bb(d, t, f):
    bb = d.textbbox((0,0), t, font=f); return bb

def wrap(d, text, font, max_w=MAX_W):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if tw(d, test, font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fit_font(d, lines, style, start=120, min_sz=40, max_w=MAX_W):
    sz = start
    while sz >= min_sz:
        f = F(style, sz)
        if all(tw(d, ln, f) <= max_w for ln in lines): return sz, f
        sz -= 4
    return min_sz, F(style, min_sz)

def grad_text(canvas, d, text, font, x, y, c1=VLT, c2=PINK):
    bb  = d.textbbox((0,0), text, font=font)
    lw_ = bb[2]-bb[0]; y0 = y+bb[1]; y1 = y+bb[3]
    lay = Image.new("RGBA", canvas.size, (0,0,0,0))
    ImageDraw.Draw(lay).text((x,y), text, font=font, fill=(*c1,255))
    tint = Image.new("RGBA", canvas.size, (0,0,0,0))
    dt   = ImageDraw.Draw(tint)
    for xi in range(x, x+lw_):
        c = lerp(c1, c2, (xi-x)/max(1,lw_-1))
        dt.line([(xi,y0),(xi,y1)], fill=(*c,255))
    _,_,_,a = lay.split(); tint.putalpha(a)
    base = canvas.convert("RGBA"); base.alpha_composite(tint)
    return base.convert("RGB")

def grad_line(d, y, h=5, c1=VLT, c2=PINK, x0=0, x1=W):
    for xi in range(x0, x1):
        d.line([(xi,y),(xi,y+h)], fill=lerp(c1,c2,(xi-x0)/max(1,x1-x0-1)))

def load_bg(path, ctr=(0.5,0.5)):
    return ImageOps.fit(Image.open(path).convert("RGB"), (W,H), Image.LANCZOS, centering=ctr)

def dark_vignette(canvas, strength=0.55):
    ov  = Image.new("RGBA", canvas.size, (0,0,0,0))
    dv  = ImageDraw.Draw(ov)
    for y in range(400):
        a = int(180*(1-y/400)**2)
        dv.line([(0,y),(W,y)], fill=(0,0,0,a))
    for y in range(H-1, H-500-1, -1):
        a = int(int(255*strength)*(1-(H-1-y)/500)**0.6)
        dv.line([(0,y),(W,y)], fill=(0,0,0,a))
    ov = ov.filter(ImageFilter.GaussianBlur(40))
    base = canvas.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

LOGO = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
def paste_logo(canvas, x=52, y=44, lh=42, pill=True, pill_color=(8,6,14,220)):
    if pill:
        d = ImageDraw.Draw(canvas)
        d.rounded_rectangle([x-10,y-8,x+185,y+lh+12], radius=12, fill=pill_color)
    logo = Image.open(LOGO).convert("RGBA")
    lw   = int(logo.width*lh/logo.height)
    logo = logo.resize((lw,lh), Image.LANCZOS)
    canvas.paste(logo, (x,y), logo)
    d = ImageDraw.Draw(canvas)
    d.rectangle([x,y+lh+7,x+lw,y+lh+10], fill=VIOLET)

BG  = "/home/user/WEB/carrossel-pmi"
OUT = "/home/user/WEB/carrossel-pmi/domingo"
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
# CAROUSEL A — MANIFESTO
# Layout: tipografia gigante topo-esquerda, imagem como textura
# Paleta: preto + branco + VLT/PINK
# ══════════════════════════════════════════════════════════════════

def a_s01():
    """Hook: frase incompleta que força o deslize."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_a_s01.png")
    ov     = Image.new("RGBA", bg.size, (0,0,10,160))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")

    d = ImageDraw.Draw(canvas)

    # linha decorativa topo VLT→PINK (4px)
    grad_line(d, 0, h=4)

    # "SEU CONTEÚDO" — branco, gigante, alinhado à esquerda
    fnt_big = F("black", 128)
    lines1  = ["SEU", "CONTEÚDO"]
    _, fnt_big = fit_font(d, lines1, "black", 128, max_w=MAX_W)
    ty = 90
    for ln in lines1:
        d.text((MARGIN, ty), ln, font=fnt_big, fill=WHITE)
        ty += int(fnt_big.size * 1.0)

    ty += 10
    # linha separadora curta
    grad_line(d, ty, h=5, x0=MARGIN, x1=MARGIN+180)
    ty += 28

    # "PARECE FEITO POR" — menor, cinza
    fnt_mid = F("bold", 52)
    d.text((MARGIN, ty), "PARECE FEITO POR", font=fnt_mid, fill=GRAY)
    ty += int(fnt_mid.size * 1.1)

    # "ROBÔ." — gradiente VLT→PINK, mesmo tamanho grande
    fnt_big2 = F("black", 118)
    canvas = grad_text(canvas, d, "ROBÔ.", fnt_big2, MARGIN, ty)
    d = ImageDraw.Draw(canvas)
    ty += int(fnt_big2.size * 1.1)

    ty += 24
    # subtítulo pequeno
    fnt_s = F("light", 28)
    sub   = "Porque parece mesmo."
    d.text((MARGIN, ty), sub, font=fnt_s, fill=OFFWHT)

    paste_logo(canvas)
    canvas.save(f"{OUT}/a_slide01.png"); print("✓ A s01")


def a_s02():
    """Corpo: o feed virou fábrica."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_a_s02.png", ctr=(0.5,0.4))
    ov     = Image.new("RGBA", bg.size, (0,0,8,180))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    # texto centralizado, grande
    lines = ["TODO MUNDO USA IA.", "TODO MUNDO", "SONA IGUAL."]
    _, fnt_h = fit_font(d, lines, "black", 104)
    lead = int(fnt_h.size * 1.04)
    block_h = lead * len(lines)
    ty = (H - block_h) // 2 - 80

    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h); x = (W - lw_) // 2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, ty); d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_h, fill=WHITE)
        ty += lead

    ty += 20
    fnt_s = F("regular", 30)
    sub = "O feed virou uma fábrica. Sem dono. Sem voz."
    lw_ = tw(d, sub, fnt_s); d.text(((W-lw_)//2, ty), sub, font=fnt_s, fill=GRAY)

    paste_logo(canvas)
    canvas.save(f"{OUT}/a_slide02.png"); print("✓ A s02")


def a_s03():
    """Contraste: corredor de manequins vs humano."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_a_s03.png")
    canvas = dark_vignette(bg, strength=0.5)
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    # texto na parte inferior, alinhado à direita
    lines = ["O QUE", "DIFERENCIA", "NÃO É", "A FERRAMENTA."]
    _, fnt_h = fit_font(d, lines, "black", 96, max_w=560)
    lead = int(fnt_h.size * 1.02)
    block_h = lead * len(lines)
    ty = H - 160 - block_h
    rx = W - MARGIN   # alinha à direita

    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h)
        x   = rx - lw_
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, ty); d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_h, fill=WHITE)
        ty += lead

    # linha vertical no lado direito
    for yi in range(int(H*0.3), int(H*0.85)):
        t = (yi - int(H*0.3)) / (int(H*0.85) - int(H*0.3))
        d.line([(W-14, yi), (W-10, yi)], fill=lerp(VLT, PINK, t))

    paste_logo(canvas)
    canvas.save(f"{OUT}/a_slide03.png"); print("✓ A s03")


def a_s04():
    """É A VOZ."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_a_s04.png", ctr=(0.5,0.5))
    ov     = Image.new("RGBA", bg.size, (0,0,10,140))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    # "É A VOZ." enorme, centralizado
    fnt_big = F("black", 180)
    text    = "É A VOZ."
    _, fnt_big = fit_font(d, [text], "black", 180)
    lw_     = tw(d, text, fnt_big)
    canvas  = grad_text(canvas, d, text, fnt_big, (W-lw_)//2, int(H*0.30))
    d       = ImageDraw.Draw(canvas)

    # abaixo: explicação em duas linhas pequenas
    ty = int(H*0.30) + int(fnt_big.size*1.2) + 20
    grad_line(d, ty, h=4, x0=(W-200)//2, x1=(W+200)//2)
    ty += 24

    fnt_s = F("regular", 36)
    lines = ["E voz não se automatiza.", "Nunca."]
    for ln in lines:
        lw_ = tw(d, ln, fnt_s); d.text(((W-lw_)//2, ty), ln, font=fnt_s, fill=OFFWHT)
        ty  += int(fnt_s.size*1.5)

    paste_logo(canvas)
    canvas.save(f"{OUT}/a_slide04.png"); print("✓ A s04")


def a_s05():
    """CTA: pure typography, sem imagem de fundo (full dark)."""
    canvas = Image.new("RGB", (W,H), DARK)

    # glow roxo sutil
    glow = Image.new("RGBA", (W,H), (0,0,0,0))
    dg   = ImageDraw.Draw(glow)
    for r in range(500, 0, -8):
        a = int(22*(1-r/500)**2.5)
        dg.ellipse([W//2-r, H//2-r, W//2+r, H//2+r], fill=(*VLT, a))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(glow)
    canvas = canvas.convert("RGB")
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    fnt_big = F("black", 72)
    question = [
        "VOCÊ CONSEGUE LER",
        "SEU ÚLTIMO POST",
        "E SENTIR QUE FOI",
        "VOCÊ QUE ESCREVEU?"
    ]
    _, fnt_big = fit_font(d, question, "black", 72)
    lead = int(fnt_big.size * 1.08)
    block_h = lead * len(question)
    ty = (H - block_h)//2 - 40

    for i, ln in enumerate(question):
        lw_ = tw(d, ln, fnt_big); x = (W-lw_)//2
        if i == len(question)-1:
            canvas = grad_text(canvas, d, ln, fnt_big, x, ty); d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_big, fill=WHITE)
        ty += lead

    ty += 32; grad_line(d, ty, h=4, x0=(W-120)//2, x1=(W+120)//2); ty += 22
    fnt_s = F("regular", 30)
    cta = "Responde nos comentários."
    lw_ = tw(d, cta, fnt_s); d.text(((W-lw_)//2, ty), cta, font=fnt_s, fill=GRAY)

    paste_logo(canvas)
    canvas.save(f"{OUT}/a_slide05.png"); print("✓ A s05")


# ══════════════════════════════════════════════════════════════════
# CAROUSEL B — RUPTURA
# Layout: palavra central gigante com RISCAR visual ("VIRAL")
# Paleta: imagem colorida + branco + risca PINK
# ══════════════════════════════════════════════════════════════════

def b_s01():
    """Hook: 'VIRAL' com risca grossa."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_b_s01.png")
    ov     = Image.new("RGBA", bg.size, (0,0,0,130))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)

    # "VIRALIZAR" enorme ao centro
    fnt_v = F("black", 148)
    word  = "VIRALIZAR"
    _, fnt_v = fit_font(d, [word], "black", 148)
    lw_   = tw(d, word, fnt_v)
    x_v   = (W - lw_) // 2
    y_v   = int(H * 0.27)
    d.text((x_v, y_v), word, font=fnt_v, fill=WHITE)

    # RISCA GROSSA sobre a palavra (PINK sólido + 2px extra)
    bb      = d.textbbox((0,0), word, font=fnt_v)
    txt_h   = bb[3] - bb[1]
    mid_y   = y_v + bb[1] + txt_h // 2
    line_h  = max(12, txt_h // 9)
    d.rectangle([x_v - 10, mid_y - line_h//2,
                 x_v + lw_ + 10, mid_y + line_h//2], fill=PINK)

    # linha cinza horizontal abaixo da palavra
    ty = y_v + int(fnt_v.size * 1.15) + 12
    grad_line(d, ty, h=4)
    ty += 28

    # subtítulo
    lines = ["NÃO É MAIS O OBJETIVO.", "NA VERDADE,", "NUNCA FOI."]
    _, fnt_s = fit_font(d, lines, "bold", 58)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_s); x = (W-lw_)//2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_s, x, ty); d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_s, fill=WHITE)
        ty += int(fnt_s.size * 1.1)

    paste_logo(canvas)
    canvas.save(f"{OUT}/b_slide01.png"); print("✓ B s01")


def b_s02():
    """200 mil curtidas. Zero vendas."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_b_s02.png", ctr=(0.5,0.3))
    ov     = Image.new("RGBA", bg.size, (0,0,0,150))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    # dois blocos em contraste visual — um lado por vez
    ty = int(H * 0.22)

    # bloco 1: stat branca
    fnt_n  = F("black", 140)
    fnt_lbl= F("bold", 38)
    stat1  = "200 MIL"
    lw_    = tw(d, stat1, fnt_n)
    d.text(((W-lw_)//2, ty), stat1, font=fnt_n, fill=WHITE)
    ty    += int(fnt_n.size * 0.95)
    lab1   = "CURTIDAS."
    lw_    = tw(d, lab1, fnt_lbl); d.text(((W-lw_)//2, ty), lab1, font=fnt_lbl, fill=GRAY)
    ty    += int(fnt_lbl.size * 1.4)

    # linha separadora
    grad_line(d, ty, h=5); ty += 30

    # bloco 2: stat gradiente (o choque)
    fnt_n2 = F("black", 140)
    stat2  = "ZERO"
    lw_    = tw(d, stat2, fnt_n2)
    canvas = grad_text(canvas, d, stat2, fnt_n2, (W-lw_)//2, ty, c1=PINK, c2=VLT)
    d      = ImageDraw.Draw(canvas)
    ty    += int(fnt_n2.size * 0.95)
    lab2   = "VENDAS."
    lw_    = tw(d, lab2, fnt_lbl); d.text(((W-lw_)//2, ty), lab2, font=fnt_lbl, fill=GRAY)
    ty    += int(fnt_lbl.size * 1.4)

    ty += 10
    fnt_s = F("regular", 30)
    sub   = "Isso acontece todo dia."
    lw_   = tw(d, sub, fnt_s); d.text(((W-lw_)//2, ty), sub, font=fnt_s, fill=OFFWHT)

    paste_logo(canvas)
    canvas.save(f"{OUT}/b_slide02.png"); print("✓ B s02")


def b_s03():
    """Viral é ego. Comunidade é negócio."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_b_s03.png")
    ov     = Image.new("RGBA", bg.size, (0,0,0,140))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    # layout: linha 1 branca / divisor / linha 2 gradiente
    ty = int(H * 0.32)

    fnt_h = F("black", 106)
    l1    = "VIRAL É EGO."
    _, fnt_h = fit_font(d, [l1, "COMUNIDADE É NEGÓCIO."], "black", 106)
    lw_   = tw(d, l1, fnt_h)
    d.text(((W-lw_)//2, ty), l1, font=fnt_h, fill=WHITE)
    ty   += int(fnt_h.size * 1.12)

    # linha decorativa curta
    mx = (W - 80) // 2
    grad_line(d, ty, h=5, x0=mx, x1=mx+80); ty += 28

    l2    = "COMUNIDADE É NEGÓCIO."
    lw_   = tw(d, l2, fnt_h)
    canvas= grad_text(canvas, d, l2, fnt_h, (W-lw_)//2, ty)
    d     = ImageDraw.Draw(canvas)
    ty   += int(fnt_h.size * 1.2)

    fnt_s = F("light", 32)
    sub   = "As marcas que mais vendem em 2026 têm comunidade pequena e lista de espera."
    for ln in wrap(d, sub, fnt_s, max_w=900):
        lw_ = tw(d, ln, fnt_s); d.text(((W-lw_)//2, ty), ln, font=fnt_s, fill=GRAY)
        ty += int(fnt_s.size * 1.5)

    paste_logo(canvas)
    canvas.save(f"{OUT}/b_slide03.png"); print("✓ B s03")


def b_s04():
    """Chama e vela — o que dura vs o que explode."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_b_s04.png")
    ov     = Image.new("RGBA", bg.size, (0,0,0,120))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    # duas colunas de texto na parte inferior
    col_w  = (W - MARGIN*2 - 40) // 2
    col2_x = MARGIN + col_w + 40

    ty1    = int(H * 0.58)
    fnt_lbl= F("black", 36)
    fnt_s  = F("regular", 26)

    # col esquerda — "O QUE DURA"
    label1 = "O QUE DURA"
    d.text((MARGIN, ty1), label1, font=fnt_lbl, fill=WHITE)
    grad_line(d, ty1+44, h=3, x0=MARGIN, x1=MARGIN+col_w, c1=VLT, c2=PINK)
    ty_c1  = ty1 + 56
    items1 = ["Comunidade fiel", "Conteúdo consistente", "Autoridade real"]
    for it in items1:
        d.text((MARGIN, ty_c1), it, font=fnt_s, fill=OFFWHT); ty_c1 += int(fnt_s.size*1.6)

    # col direita — "O QUE EXPLODE E SOME"
    label2 = "O QUE EXPLODE"
    canvas = grad_text(canvas, d, label2, fnt_lbl, col2_x, ty1, c1=PINK, c2=VLT)
    d      = ImageDraw.Draw(canvas)
    grad_line(d, ty1+44, h=3, x0=col2_x, x1=col2_x+col_w, c1=PINK, c2=VLT)
    ty_c2  = ty1 + 56
    items2 = ["Post viral isolado", "Trend sem contexto", "Curtida sem conversão"]
    for it in items2:
        d.text((col2_x, ty_c2), it, font=fnt_s, fill=GRAY); ty_c2 += int(fnt_s.size*1.6)

    paste_logo(canvas)
    canvas.save(f"{OUT}/b_slide04.png"); print("✓ B s04")


def b_s05():
    """CTA: Qual o tamanho do seu público mais fiel?"""
    bg     = load_bg(f"{BG}/bg_domingo_dom_b_s05.png", ctr=(0.5,0.4))
    ov     = Image.new("RGBA", bg.size, (0,0,0,150))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    # Faixa escura inferior para CTA
    fy     = int(H * 0.55)
    faixa  = Image.new("RGBA", (W,H), (0,0,0,0))
    ImageDraw.Draw(faixa).rectangle([0, fy, W, H], fill=(*DARK, 240))
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(faixa)
    canvas = canvas.convert("RGB"); d = ImageDraw.Draw(canvas)
    grad_line(d, fy, h=5)

    ty  = fy + 40
    fnt_h = F("black", 66)
    lines = ["QUAL O TAMANHO", "DO SEU PÚBLICO", "MAIS FIEL?"]
    _, fnt_h = fit_font(d, lines, "black", 66, max_w=MAX_W)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h); x = (W-lw_)//2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, ty); d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_h, fill=WHITE)
        ty += int(fnt_h.size*1.08)

    ty += 18
    fnt_s = F("regular", 30)
    sub   = "Nem precisa ser grande. Precisa ser seu."
    lw_   = tw(d, sub, fnt_s); d.text(((W-lw_)//2, ty), sub, font=fnt_s, fill=OFFWHT)

    paste_logo(canvas)
    canvas.save(f"{OUT}/b_slide05.png"); print("✓ B s05")


# ══════════════════════════════════════════════════════════════════
# CAROUSEL C — DADO
# Layout: número herói top + faixa central + narrativa gradual
# Paleta: escuro + branco + acento PINK no dado
# ══════════════════════════════════════════════════════════════════

def c_s01():
    """Hook: 47M herói."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_c_s01.png")
    ov     = Image.new("RGBA", bg.size, (0,0,0,170))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")

    # glow VLT atrás do número
    glow   = Image.new("RGBA", (W,H), (0,0,0,0))
    dg     = ImageDraw.Draw(glow)
    for r in range(420, 0, -6):
        a = int(28*(1-r/420)**2.8)
        dg.ellipse([W//2-r, 60, W//2+r, 60+r*2], fill=(*VLT, a))
    glow   = glow.filter(ImageFilter.GaussianBlur(60))
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(glow)
    canvas = canvas.convert("RGB")

    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    # número herói "47M"
    fnt_num = F("black", 220)
    num     = "47M"
    _, fnt_num = fit_font(d, [num], "black", 220, max_w=W-40)
    lw_     = tw(d, num, fnt_num)
    canvas  = grad_text(canvas, d, num, fnt_num, (W-lw_)//2, 80, c1=PINK, c2=VLT)
    d       = ImageDraw.Draw(canvas)

    # label abaixo do número
    ty      = 80 + int(fnt_num.size * 1.0) + 8
    fnt_lbl = F("bold", 38)
    lbl     = "DE EMPREENDEDORES NO BRASIL."
    lw_     = tw(d, lbl, fnt_lbl)
    # quebrar se necessário
    for ln in wrap(d, lbl, fnt_lbl, max_w=MAX_W):
        lw_ = tw(d, ln, fnt_lbl); d.text(((W-lw_)//2, ty), ln, font=fnt_lbl, fill=GRAY)
        ty += int(fnt_lbl.size * 1.2)

    ty += 16
    grad_line(d, ty, h=5)
    ty += 30

    fnt_h   = F("black", 80)
    twist   = ["A MAIORIA NÃO SABE", "O QUE ESTÁ VENDENDO."]
    _, fnt_h = fit_font(d, twist, "black", 80)
    for i, ln in enumerate(twist):
        lw_ = tw(d, ln, fnt_h); x = (W-lw_)//2
        if i == len(twist)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, ty); d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_h, fill=WHITE)
        ty += int(fnt_h.size * 1.08)

    paste_logo(canvas)
    canvas.save(f"{OUT}/c_slide01.png"); print("✓ C s01")


def c_s02():
    """Não é falta de produto."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_c_s02.png", ctr=(0.5,0.4))
    ov     = Image.new("RGBA", bg.size, (0,0,0,155))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    # 3 linhas de negação, depois revelação
    ty = int(H * 0.18)
    items = [
        ("NÃO É falta de produto.",   GRAY,  "regular", 46),
        ("NÃO É falta de cliente.",   GRAY,  "regular", 46),
        ("NÃO É falta de verba.",     GRAY,  "regular", 46),
    ]
    for text, color, style, sz in items:
        fnt = F(style, sz)
        lw_ = tw(d, text, fnt)
        d.text(((W-lw_)//2, ty), text, font=fnt, fill=color)
        ty += int(sz * 1.55)

    ty += 16
    grad_line(d, ty, h=5); ty += 30

    fnt_big = F("black", 88)
    reveal  = ["É FALTA DE CLAREZA."]
    _, fnt_big = fit_font(d, reveal, "black", 88)
    lw_     = tw(d, reveal[0], fnt_big)
    canvas  = grad_text(canvas, d, reveal[0], fnt_big, (W-lw_)//2, ty)
    d       = ImageDraw.Draw(canvas)
    ty     += int(fnt_big.size * 1.15)

    fnt_s   = F("light", 30)
    sub     = "Sobre o que você vende. Para quem. E por que escolher você."
    for ln in wrap(d, sub, fnt_s, max_w=900):
        lw_ = tw(d, ln, fnt_s); d.text(((W-lw_)//2, ty), ln, font=fnt_s, fill=OFFWHT)
        ty += int(fnt_s.size * 1.55)

    paste_logo(canvas)
    canvas.save(f"{OUT}/c_slide02.png"); print("✓ C s02")


def c_s03():
    """Teste do megafone vs sussurro."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_c_s03.png")
    ov     = Image.new("RGBA", bg.size, (0,0,0,145))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    ty = int(H * 0.3)
    fnt_h = F("black", 84)
    lines = ["FALAR ALTO", "NÃO É", "SER OUVIDO."]
    _, fnt_h = fit_font(d, lines, "black", 84)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h); x = (W-lw_)//2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, ty); d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_h, fill=WHITE)
        ty += int(fnt_h.size * 1.05)

    ty += 24
    grad_line(d, ty, h=4, x0=(W-160)//2, x1=(W+160)//2); ty += 26

    fnt_s = F("regular", 32)
    sub   = "Quem fala para todos não fala com ninguém."
    lw_   = tw(d, sub, fnt_s); d.text(((W-lw_)//2, ty), sub, font=fnt_s, fill=GRAY)
    ty   += int(fnt_s.size * 1.6)

    fnt_s2 = F("bold", 32)
    sub2   = "Clareza atrai. Volume cansa."
    lw_    = tw(d, sub2, fnt_s2); d.text(((W-lw_)//2, ty), sub2, font=fnt_s2, fill=OFFWHT)

    paste_logo(canvas)
    canvas.save(f"{OUT}/c_slide03.png"); print("✓ C s03")


def c_s04():
    """Split água clara vs turva."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_c_s04.png")
    ov     = Image.new("RGBA", bg.size, (0,0,0,130))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    # linha vertical divisora no centro
    for yi in range(int(H*0.15), int(H*0.78)):
        t = (yi - int(H*0.15)) / (int(H*0.78) - int(H*0.15))
        d.line([(W//2-1, yi), (W//2+1, yi)], fill=lerp(VLT, PINK, t))

    # lado esquerdo — clareza
    fnt_lbl = F("black", 52)
    lbl_l   = "CLAREZA"
    lw_     = tw(d, lbl_l, fnt_lbl)
    canvas  = grad_text(canvas, d, lbl_l, fnt_lbl, (W//2-40-lw_), int(H*0.22))
    d       = ImageDraw.Draw(canvas)

    fnt_s   = F("regular", 26)
    items_l = ["Proposta única", "Público definido", "Mensagem direta"]
    ty_l    = int(H*0.22) + int(fnt_lbl.size*1.2)
    for it in items_l:
        lw_ = tw(d, it, fnt_s); d.text((W//2-40-lw_, ty_l), it, font=fnt_s, fill=OFFWHT)
        ty_l += int(fnt_s.size*1.7)

    # lado direito — confusão
    fnt_lbl2 = F("black", 52)
    lbl_r    = "CONFUSÃO"
    d.text((W//2 + 40, int(H*0.22)), lbl_r, font=fnt_lbl2, fill=GRAY)
    ty_r     = int(H*0.22) + int(fnt_lbl2.size*1.2)
    items_r  = ["Fala tudo pra todos", "Sem foco de canal", "Mensagem genérica"]
    for it in items_r:
        d.text((W//2+40, ty_r), it, font=fnt_s, fill=GRAY); ty_r += int(fnt_s.size*1.7)

    # pergunta no rodapé
    ty_bot  = int(H * 0.82)
    grad_line(d, ty_bot, h=4); ty_bot += 24
    fnt_q   = F("bold", 34)
    q       = "Em qual lado está o seu negócio hoje?"
    lw_     = tw(d, q, fnt_q); d.text(((W-lw_)//2, ty_bot), q, font=fnt_q, fill=WHITE)

    paste_logo(canvas)
    canvas.save(f"{OUT}/c_slide04.png"); print("✓ C s04")


def c_s05():
    """CTA: explica em uma frase."""
    bg     = load_bg(f"{BG}/bg_domingo_dom_c_s05.png", ctr=(0.5,0.4))
    ov     = Image.new("RGBA", bg.size, (0,0,0,160))
    base   = bg.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")

    glow = Image.new("RGBA", (W,H), (0,0,0,0))
    dg   = ImageDraw.Draw(glow)
    for r in range(360, 0, -6):
        a = int(20*(1-r/360)**3)
        dg.ellipse([W//2-r, H//2-r-100, W//2+r, H//2+r-100], fill=(*VLT, a))
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(glow)
    canvas = canvas.convert("RGB")
    d      = ImageDraw.Draw(canvas)
    grad_line(d, 0, h=4)

    ty = int(H * 0.28)
    fnt_h = F("black", 72)
    lines = ["ESCREVE AQUI", "O QUE VOCÊ VENDE", "EM UMA FRASE."]
    _, fnt_h = fit_font(d, lines, "black", 72)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h); x = (W-lw_)//2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, ty); d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_h, fill=WHITE)
        ty += int(fnt_h.size*1.1)

    ty += 28
    grad_line(d, ty, h=4, x0=(W-100)//2, x1=(W+100)//2); ty += 26

    fnt_s = F("bold", 32)
    rule  = "Sem usar a palavra 'solução'."
    lw_   = tw(d, rule, fnt_s)
    canvas= grad_text(canvas, d, rule, fnt_s, (W-lw_)//2, ty, c1=PINK, c2=VLT)
    d     = ImageDraw.Draw(canvas)
    ty   += int(fnt_s.size*1.6)

    fnt_tiny = F("regular", 28)
    hint     = "Quem consegue tem clareza. Quem não consegue, tem trabalho."
    for ln in wrap(d, hint, fnt_tiny, max_w=900):
        lw_ = tw(d, ln, fnt_tiny); d.text(((W-lw_)//2, ty), ln, font=fnt_tiny, fill=GRAY)
        ty += int(fnt_tiny.size*1.55)

    paste_logo(canvas)
    canvas.save(f"{OUT}/c_slide05.png"); print("✓ C s05")


if __name__ == "__main__":
    print("=== CAROUSEL A — MANIFESTO ===")
    a_s01(); a_s02(); a_s03(); a_s04(); a_s05()

    print("\n=== CAROUSEL B — RUPTURA ===")
    b_s01(); b_s02(); b_s03(); b_s04(); b_s05()

    print("\n=== CAROUSEL C — DADO ===")
    c_s01(); c_s02(); c_s03(); c_s04(); c_s05()

    print(f"\nDone → {OUT}")
