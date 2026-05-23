#!/usr/bin/env python3
"""
PMI — Carrosseis Domingo V2. Saindo da caixinha.
  A: NEO-BRUTALISMO   — bordas grossas, blocos de cor sólida, texto nas bordas
  B: ZINE / PUNK      — grão, múltiplas fontes, texto rotacionado, caos controlado
  C: SURREAL LIMPO    — fundo CLARO (choque no feed escuro), escala impossível
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os, random, math

W, H    = 1080, 1350
MARGIN  = 60

# paleta A — brutalismo
VLT    = (160,  60, 255)
PINK   = (236,  72, 153)
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
DARK   = (  8,   6,  14)
OFFWHT = (235, 228, 245)
GRAY   = (150, 145, 165)

# paleta B — zine
LIME   = ( 57, 255,  20)
ORANGE = (255, 100,   0)
CREAM  = (245, 240, 228)

# paleta C — editorial claro
CLAY   = (230, 218, 200)   # bege quente
INK    = ( 18,  12,  24)   # preto quase roxo
PLUM   = (100,  20, 140)   # roxo escuro
BLUSH  = (220,  80, 120)   # rosa forte

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

def wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if tw(d, test, font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fit_font(d, lines, style, start=120, min_sz=36, max_w=W-80):
    sz = start
    while sz >= min_sz:
        f = F(style, sz)
        if all(tw(d, ln, f) <= max_w for ln in lines): return sz, f
        sz -= 4
    return min_sz, F(style, min_sz)

def load_bg(path, ctr=(0.5,0.5)):
    return ImageOps.fit(Image.open(path).convert("RGB"), (W,H),
                        Image.LANCZOS, centering=ctr)

def grad_text(canvas, d, text, font, x, y, c1=VLT, c2=PINK):
    bb  = d.textbbox((0,0), text, font=font)
    lw_ = bb[2]-bb[0]; y0=y+bb[1]; y1=y+bb[3]
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

def add_grain(canvas, intensity=18):
    """Adiciona grão analógico sobre a imagem."""
    import random
    grain = Image.new("RGBA", canvas.size, (0,0,0,0))
    px    = grain.load()
    rng   = random.Random(42)
    for y in range(canvas.height):
        for x in range(canvas.width):
            n = rng.randint(-intensity, intensity)
            px[x,y] = (max(0,n), max(0,n), max(0,n), abs(n)*2)
    base = canvas.convert("RGBA"); base.alpha_composite(grain)
    return base.convert("RGB")

def rotated_text(canvas, text, font, x, y, angle, fill):
    """Renderiza texto rotacionado sobre o canvas."""
    d    = ImageDraw.Draw(canvas)
    bb   = d.textbbox((0,0), text, font=font)
    tw_  = bb[2]-bb[0]; th_ = bb[3]-bb[1]
    # cria layer isolada
    lay  = Image.new("RGBA", (tw_+20, th_+20), (0,0,0,0))
    ld   = ImageDraw.Draw(lay)
    ld.text((10, 10-bb[1]), text, font=font, fill=(*fill,255))
    lay  = lay.rotate(-angle, expand=True, resample=Image.BICUBIC)
    base = canvas.convert("RGBA")
    # centraliza no ponto (x,y)
    px   = x - lay.width//2
    py   = y - lay.height//2
    base.alpha_composite(lay, (max(0,px), max(0,py)))
    return base.convert("RGB")

LOGO = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
def paste_logo(canvas, x=MARGIN, y=44, lh=40, dark_pill=True, light_pill=False):
    if dark_pill:
        ImageDraw.Draw(canvas).rounded_rectangle(
            [x-8, y-6, x+182, y+lh+10], radius=10, fill=(8,6,14,220))
    if light_pill:
        ImageDraw.Draw(canvas).rounded_rectangle(
            [x-8, y-6, x+182, y+lh+10], radius=10, fill=(240,235,220,200))
    logo = Image.open(LOGO).convert("RGBA")
    lw   = int(logo.width*lh/logo.height)
    logo = logo.resize((lw,lh), Image.LANCZOS)
    canvas.paste(logo, (x,y), logo)
    ImageDraw.Draw(canvas).rectangle([x, y+lh+6, x+lw, y+lh+9],
                                     fill=VLT if dark_pill else PLUM)

BG  = "/home/user/WEB/carrossel-pmi"
OUT = "/home/user/WEB/carrossel-pmi/domingo_v2"
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
# CAROUSEL A — NEO-BRUTALISMO
# Bloco de cor sólida (sem gradiente) + borda grossa preta
# Texto crashing nas bordas, sem centralização obrigatória
# ══════════════════════════════════════════════════════════════════

BORDER = 8   # espessura da borda brutalista

def brut_border(canvas, color=BLACK, thick=BORDER):
    d = ImageDraw.Draw(canvas)
    d.rectangle([0,0,W-1,H-1], outline=color, width=thick)

def brut_block(canvas, x, y, w, h, color, alpha=255):
    """Bloco sólido brutalista."""
    lay = Image.new("RGBA", canvas.size, (0,0,0,0))
    ImageDraw.Draw(lay).rectangle([x,y,x+w,y+h], fill=(*color, alpha))
    base = canvas.convert("RGBA"); base.alpha_composite(lay)
    return base.convert("RGB")


def a_s01():
    """Hook — split: metade VLT sólido / metade imagem. Texto crashing."""
    img    = load_bg(f"{BG}/bg_v2_v2_a_s01.png", ctr=(0.7,0.5))
    canvas = img.copy()

    # bloco sólido VLT no lado esquerdo (55% da largura)
    split  = int(W * 0.52)
    canvas = brut_block(canvas, 0, 0, split, H, VLT)
    d      = ImageDraw.Draw(canvas)

    # borda preta na divisória
    d.rectangle([split-4, 0, split+4, H], fill=BLACK)

    # "SEU" enorme, fora do bloco (começa na borda)
    fnt_big = F("black", 200)
    # fit para não ultrapassar a div
    while tw(d, "SEU", fnt_big) > split + 40:
        fnt_big = F("black", fnt_big.size - 8)
    # texto começa em -10 (sanga para a esquerda)
    canvas  = grad_text(canvas, d, "SEU", fnt_big, -10, 60, c1=WHITE, c2=(200,180,255))
    d       = ImageDraw.Draw(canvas)

    # "CONTEÚDO" no segundo terço, menor
    fnt_mid = F("black", 108)
    while tw(d, "CONTEÚDO", fnt_mid) > split - 20:
        fnt_mid = F("black", fnt_mid.size - 4)
    d.text((8, 60 + int(fnt_big.size*0.92)), "CONTEÚDO", font=fnt_mid, fill=WHITE)

    # linha preta grossa separadora
    ly = 60 + int(fnt_big.size*0.92) + int(fnt_mid.size*1.05) + 8
    d.rectangle([8, ly, split-12, ly+8], fill=BLACK)
    ly += 20

    # "PARECE FEITO" pequeno, muda de tom
    fnt_s = F("bold", 38)
    d.text((8, ly), "PARECE FEITO", font=fnt_s, fill=(220,200,255))
    ly += int(fnt_s.size * 1.2)
    fnt_s2 = F("black", 54)
    d.text((8, ly), "POR ROBÔ.", font=fnt_s2, fill=BLACK)

    # borda brutalista
    brut_border(canvas)
    paste_logo(canvas)
    canvas.save(f"{OUT}/a_slide01.png"); print("✓ A s01")


def a_s02():
    """Fábrica de rostos — UMA palavra enorme, imagem ao fundo."""
    img    = load_bg(f"{BG}/bg_v2_v2_a_s02.png")
    # overlay forte
    ov     = Image.new("RGBA", img.size, (8,0,20,185))
    base   = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")

    d = ImageDraw.Draw(canvas)

    # "IDÊNTICO." gigante, centralizado, sangrando nos lados
    fnt_big = F("black", 178)
    text    = "IDÊNTICO."
    lw_     = tw(d, text, fnt_big)
    x_start = (W - lw_) // 2
    # gradiente
    canvas = grad_text(canvas, d, text, fnt_big, x_start, int(H*0.22))
    d = ImageDraw.Draw(canvas)

    # linha grossa preta abaixo da palavra
    ty = int(H*0.22) + int(fnt_big.size * 1.0)
    d.rectangle([0, ty, W, ty+10], fill=BLACK)
    ty += 28

    # bloco de texto branco menor
    fnt_m = F("bold", 48)
    lines = ["Todo mundo usa a mesma IA.", "Todo mundo soa a mesma coisa."]
    for ln in lines:
        lw_ = tw(d, ln, fnt_m)
        d.text(((W-lw_)//2, ty), ln, font=fnt_m, fill=WHITE)
        ty += int(fnt_m.size * 1.12)

    ty += 16
    # bloco cinza + texto pequeno
    canvas = brut_block(canvas, MARGIN, ty, W-MARGIN*2, 6, PINK)
    d = ImageDraw.Draw(canvas)
    ty += 18
    fnt_s = F("light", 30)
    sub   = "O feed virou uma fábrica."
    lw_   = tw(d, sub, fnt_s)
    d.text(((W-lw_)//2, ty), sub, font=fnt_s, fill=OFFWHT)

    brut_border(canvas)
    paste_logo(canvas)
    canvas.save(f"{OUT}/a_slide02.png"); print("✓ A s02")


def a_s03():
    """O que diferencia — fundo PRETO puro, sem imagem. Choque total."""
    canvas = Image.new("RGB", (W,H), BLACK)
    d      = ImageDraw.Draw(canvas)

    # bloco VLT no canto superior direito
    canvas = brut_block(canvas, W-220, 0, 220, 180, VLT)
    d      = ImageDraw.Draw(canvas)

    # bloco PINK pequeno canto inferior esquerdo
    canvas = brut_block(canvas, 0, H-140, 180, 140, PINK)
    d      = ImageDraw.Draw(canvas)

    # tipografia central
    ty = int(H * 0.22)
    fnt_h = F("black", 96)
    lines = ["O QUE", "DIFERENCIA", "NÃO É"]
    _, fnt_h = fit_font(d, lines, "black", 96, max_w=W-80)
    for ln in lines:
        lw_ = tw(d, ln, fnt_h)
        d.text(((W-lw_)//2, ty), ln, font=fnt_h, fill=WHITE)
        ty += int(fnt_h.size * 1.06)

    ty += 12
    # linha grossa branca
    d.rectangle([MARGIN, ty, W-MARGIN, ty+6], fill=WHITE)
    ty += 26

    # "A FERRAMENTA." enorme, gradiente
    fnt_big = F("black", 116)
    text    = "A FERRAMENTA."
    _, fnt_big = fit_font(d, [text], "black", 116)
    lw_ = tw(d, text, fnt_big)
    canvas = grad_text(canvas, d, text, fnt_big, (W-lw_)//2, ty)
    d      = ImageDraw.Draw(canvas)
    ty    += int(fnt_big.size*1.1) + 18

    fnt_s = F("regular", 32)
    sub   = "É a VOZ. E voz não se automatiza."
    lw_   = tw(d, sub, fnt_s)
    d.text(((W-lw_)//2, ty), sub, font=fnt_s, fill=GRAY)

    brut_border(canvas, color=WHITE, thick=6)
    paste_logo(canvas)
    canvas.save(f"{OUT}/a_slide03.png"); print("✓ A s03")


def a_s04():
    """Mão humana vs circuito — duas colunas brutalistas."""
    img    = load_bg(f"{BG}/bg_v2_v2_a_s04.png")
    ov     = Image.new("RGBA", img.size, (0,0,10,140))
    base   = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)

    # barra VLT horizontal no topo, grossa
    canvas = brut_block(canvas, 0, 0, W, 90, VLT)
    d      = ImageDraw.Draw(canvas)
    fnt_tag = F("black", 40)
    tag     = "QUEM VÊ VOCÊ COMO PESSOA?"
    lw_     = tw(d, tag, fnt_tag)
    d.text(((W-lw_)//2, 22), tag, font=fnt_tag, fill=WHITE)

    # barra preta separadora
    canvas = brut_block(canvas, 0, 90, W, 8, BLACK)
    d      = ImageDraw.Draw(canvas)

    # texto na parte inferior
    ty = int(H * 0.62)
    canvas = brut_block(canvas, 0, ty-8, W, H-ty+8, (4,2,10), alpha=230)
    d      = ImageDraw.Draw(canvas)

    fnt_h = F("black", 80)
    lines = ["A FERRAMENTA", "OU O CRIADOR?"]
    _, fnt_h = fit_font(d, lines, "black", 80)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h); x = (W-lw_)//2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, ty); d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_h, fill=WHITE)
        ty += int(fnt_h.size*1.06)

    ty += 16
    fnt_s = F("regular", 30)
    sub   = "Quem usa IA SEM voz própria nunca vai ser insubstituível."
    for ln in wrap(d, sub, fnt_s, max_w=W-80):
        lw_ = tw(d, ln, fnt_s); d.text(((W-lw_)//2, ty), ln, font=fnt_s, fill=OFFWHT)
        ty  += int(fnt_s.size*1.5)

    brut_border(canvas)
    paste_logo(canvas)
    canvas.save(f"{OUT}/a_slide04.png"); print("✓ A s04")


def a_s05():
    """CTA brutalista — texto atravessa o slide como pôster."""
    img    = load_bg(f"{BG}/bg_v2_v2_a_s05.png")
    ov     = Image.new("RGBA", img.size, (0,0,10,160))
    base   = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)

    # "VOCÊ AINDA / SENTE SUA / VOZ NOS SEUS / POSTS?" — esquerda
    ty = int(H * 0.30)
    fnt_h = F("black", 86)
    lines = ["VOCÊ AINDA", "SENTE SUA", "VOZ NOS SEUS", "POSTS?"]
    _, fnt_h = fit_font(d, lines, "black", 86)
    for i, ln in enumerate(lines):
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, MARGIN, ty); d = ImageDraw.Draw(canvas)
        else:
            d.text((MARGIN, ty), ln, font=fnt_h, fill=WHITE)
        ty += int(fnt_h.size * 1.04)

    # linha vertical direita
    d = ImageDraw.Draw(canvas)
    for yi in range(int(H*0.28), ty+20):
        t = (yi - int(H*0.28)) / (ty+20 - int(H*0.28))
        d.line([(W-12, yi),(W-8,yi)], fill=lerp(VLT,PINK,t))

    ty += 28
    fnt_s = F("light", 32)
    sub   = "Responde aqui embaixo."
    d.text((MARGIN, ty), sub, font=fnt_s, fill=GRAY)

    brut_border(canvas)
    paste_logo(canvas)
    canvas.save(f"{OUT}/a_slide05.png"); print("✓ A s05")


# ══════════════════════════════════════════════════════════════════
# CAROUSEL B — ZINE / PUNK
# Grão, texto rotacionado, múltiplas fontes, caos intencional
# ══════════════════════════════════════════════════════════════════

def zine_stamp(canvas, text, x, y, size, color=LIME, angle=0):
    """Stamp de texto como carimbo de zine."""
    d   = ImageDraw.Draw(canvas)
    fnt = F("black", size)
    if angle != 0:
        canvas = rotated_text(canvas, text, fnt, x, y, angle, color)
    else:
        lw_ = tw(d, text, fnt)
        d.text((x, y), text, font=fnt, fill=color)
    return canvas

def zine_box(canvas, x, y, w, h, color=BLACK, fill_color=None, thick=4):
    d = ImageDraw.Draw(canvas)
    if fill_color:
        d.rectangle([x,y,x+w,y+h], fill=fill_color)
    d.rectangle([x,y,x+w,y+h], outline=color, width=thick)
    return canvas


def b_s01():
    """VIRAL RISCADO — bolha de sabão prestes a explodir."""
    img    = load_bg(f"{BG}/bg_v2_v2_b_s01.png")
    ov     = Image.new("RGBA", img.size, (0,0,0,100))
    base   = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    canvas = add_grain(canvas, intensity=12)
    d      = ImageDraw.Draw(canvas)

    # barra grossa LIME no topo
    canvas = brut_block(canvas, 0, 0, W, 12, LIME)
    d      = ImageDraw.Draw(canvas)

    # "VIRALIZAR" enorme — texto BRANCO
    fnt_v   = F("black", 155)
    word    = "VIRALIZAR"
    _, fnt_v = fit_font(d, [word], "black", 155, max_w=W-20)
    lw_     = tw(d, word, fnt_v)
    x_v     = (W - lw_) // 2
    y_v     = int(H * 0.24)
    d.text((x_v, y_v), word, font=fnt_v, fill=WHITE)

    # RISCA TRIPLA: preta grossa + LIME fina + PINK pontilhada
    bb    = d.textbbox((0,0), word, font=fnt_v)
    txt_h = bb[3]-bb[1]
    mid_y = y_v + bb[1] + txt_h//2
    lh    = max(14, txt_h//8)
    d.rectangle([x_v-8, mid_y-lh//2, x_v+lw_+8, mid_y+lh//2], fill=PINK)
    d.rectangle([x_v-8, mid_y-lh//2-2, x_v+lw_+8, mid_y-lh//2+2], fill=LIME)

    # caixa preta com texto
    ty = y_v + int(fnt_v.size*1.15) + 16
    bx = MARGIN; bw = W - MARGIN*2
    canvas = zine_box(canvas, bx, ty, bw, 200, BLACK, fill_color=(8,6,14), thick=5)
    d      = ImageDraw.Draw(canvas)

    fnt_inner = F("bold", 52)
    lines = ["NÃO É MAIS O OBJETIVO.", "NA VERDADE, NUNCA FOI."]
    _, fnt_inner = fit_font(d, lines, "bold", 52, max_w=bw-40)
    ty2 = ty + 20
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_inner); xi = bx+20+(bw-40-lw_)//2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_inner, xi, ty2, c1=LIME, c2=PINK)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((xi, ty2), ln, font=fnt_inner, fill=WHITE)
        ty2 += int(fnt_inner.size*1.1)

    # stamp rotacionado no canto
    canvas = zine_stamp(canvas, "2026", W-120, 60, 28, LIME, angle=-15)

    paste_logo(canvas)
    canvas.save(f"{OUT}/b_slide01.png"); print("✓ B s01")


def b_s02():
    """200K curtidas / 0 vendas — contraste numérico brutal."""
    img    = load_bg(f"{BG}/bg_v2_v2_b_s02.png", ctr=(0.5,0.3))
    ov     = Image.new("RGBA", img.size, (0,0,0,160))
    base   = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    canvas = add_grain(canvas, intensity=10)
    d      = ImageDraw.Draw(canvas)

    # barra LIME topo
    canvas = brut_block(canvas, 0, 0, W, 12, LIME)
    d      = ImageDraw.Draw(canvas)

    # Número 1: "200K" — LIME, gigante, left-aligned
    fnt_n1 = F("black", 160)
    n1     = "200K"
    _, fnt_n1 = fit_font(d, [n1], "black", 160, max_w=W//2-20)
    d.text((MARGIN, 100), n1, font=fnt_n1, fill=LIME)

    fnt_lbl = F("bold", 32)
    d.text((MARGIN, 100+int(fnt_n1.size*0.96)), "CURTIDAS.", font=fnt_lbl, fill=GRAY)

    # divisor vertical
    d.rectangle([W//2-3, 90, W//2+3, 90+int(fnt_n1.size*1.1)+40], fill=WHITE)

    # Número 2: "ZERO" — PINK, right-aligned
    fnt_n2 = F("black", 160)
    n2     = "ZERO"
    _, fnt_n2 = fit_font(d, [n2], "black", 160, max_w=W//2-40)
    lw_    = tw(d, n2, fnt_n2)
    d.text((W//2+20, 100), n2, font=fnt_n2, fill=PINK)
    lw2_   = tw(d, "VENDAS.", fnt_lbl)
    d.text((W//2+20, 100+int(fnt_n2.size*0.96)), "VENDAS.", font=fnt_lbl, fill=GRAY)

    ty = 100 + int(fnt_n1.size*1.1) + 50
    # linha grossa
    d.rectangle([0, ty, W, ty+8], fill=WHITE)
    ty += 24

    fnt_h = F("black", 68)
    lines = ["ISSO ACONTECE", "TODO DIA."]
    _, fnt_h = fit_font(d, lines, "black", 68)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h); x = (W-lw_)//2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, ty, c1=PINK, c2=LIME)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_h, fill=WHITE)
        ty += int(fnt_h.size*1.08)

    ty += 18
    fnt_s = F("regular", 30)
    sub   = "Viral é ego. Conversão é negócio."
    lw_   = tw(d, sub, fnt_s); d.text(((W-lw_)//2, ty), sub, font=fnt_s, fill=OFFWHT)

    paste_logo(canvas)
    canvas.save(f"{OUT}/b_slide02.png"); print("✓ B s02")


def b_s03():
    """Duas portas — contraste visual extremo."""
    img    = load_bg(f"{BG}/bg_v2_v2_b_s03.png")
    ov     = Image.new("RGBA", img.size, (0,0,0,125))
    base   = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    canvas = add_grain(canvas, intensity=14)
    d      = ImageDraw.Draw(canvas)

    # stamp no canto superior esquerdo rotacionado
    canvas = zine_stamp(canvas, "VIRAL", 110, 120, 80, PINK, angle=12)
    canvas = zine_stamp(canvas, "VS", W//2-30, 170, 44, WHITE, angle=-5)
    canvas = zine_stamp(canvas, "COMUNIDADE", W-240, 130, 34, LIME, angle=-8)
    d      = ImageDraw.Draw(canvas)

    # caixa brutalista inferior com texto
    ty = int(H * 0.57)
    canvas = zine_box(canvas, 0, ty, W, H-ty, BLACK, fill_color=(8,6,14), thick=0)
    d      = ImageDraw.Draw(canvas)
    # barra lime no topo da caixa
    canvas = brut_block(canvas, 0, ty, W, 8, LIME)
    d      = ImageDraw.Draw(canvas)

    ty += 24
    fnt_h = F("black", 78)
    lines = ["VIRAL É PICO.", "COMUNIDADE É RENDA."]
    _, fnt_h = fit_font(d, lines, "black", 78)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h); x = (W-lw_)//2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, ty, c1=LIME, c2=PINK)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_h, fill=WHITE)
        ty += int(fnt_h.size*1.08)

    ty += 16
    fnt_s = F("regular", 30)
    sub   = "Marcas que só viralizam têm audiência. Marcas com comunidade têm clientes."
    for ln in wrap(d, sub, fnt_s, max_w=W-80):
        lw_ = tw(d, ln, fnt_s); d.text(((W-lw_)//2, ty), ln, font=fnt_s, fill=OFFWHT)
        ty += int(fnt_s.size*1.5)

    paste_logo(canvas)
    canvas.save(f"{OUT}/b_slide03.png"); print("✓ B s03")


def b_s04():
    """Confetti que desaparece — o efêmero vs o duradouro."""
    img    = load_bg(f"{BG}/bg_v2_v2_b_s04.png")
    ov     = Image.new("RGBA", img.size, (0,0,0,130))
    base   = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    canvas = add_grain(canvas, intensity=11)
    d      = ImageDraw.Draw(canvas)

    # barra LIME topo
    canvas = brut_block(canvas, 0, 0, W, 12, LIME)
    d      = ImageDraw.Draw(canvas)

    # duas colunas zine
    col_w  = (W - MARGIN*2 - 32) // 2
    col2_x = MARGIN + col_w + 32
    ty_base = int(H * 0.55)

    # col 1 — "O QUE EXPLODE"
    fnt_col = F("black", 36)
    canvas  = zine_stamp(canvas, "O QUE EXPLODE", MARGIN, ty_base, 32, PINK, angle=-4)
    d       = ImageDraw.Draw(canvas)
    canvas  = zine_box(canvas, MARGIN, ty_base+48, col_w, 3, PINK, thick=3)
    d       = ImageDraw.Draw(canvas)
    items1  = ["Post viral isolado", "Trend sem contexto", "Like sem compra", "Hype de semana"]
    fnt_it  = F("regular", 24)
    ty1     = ty_base + 60
    for it in items1:
        d.text((MARGIN+8, ty1), f"/ {it}", font=fnt_it, fill=GRAY); ty1+=int(fnt_it.size*1.7)

    # col 2 — "O QUE FICA"
    canvas = zine_stamp(canvas, "O QUE FICA", col2_x, ty_base, 32, LIME, angle=3)
    d      = ImageDraw.Draw(canvas)
    canvas = zine_box(canvas, col2_x, ty_base+48, col_w, 3, LIME, thick=3)
    d      = ImageDraw.Draw(canvas)
    items2 = ["Comunidade fiel", "Conteúdo com voz", "Autoridade real", "Recomendação"]
    ty2    = ty_base + 60
    for it in items2:
        d.text((col2_x+8, ty2), f"+ {it}", font=fnt_it, fill=OFFWHT); ty2+=int(fnt_it.size*1.7)

    # pergunta no topo antes das colunas
    ty_q = int(H * 0.28)
    fnt_q = F("black", 72)
    lines = ["EM QUAL", "LADO VOCÊ", "ESTÁ APOSTANDO?"]
    _, fnt_q = fit_font(d, lines, "black", 72)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_q); x = (W-lw_)//2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_q, x, ty_q, c1=LIME, c2=PINK)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty_q), ln, font=fnt_q, fill=WHITE)
        ty_q += int(fnt_q.size*1.06)

    paste_logo(canvas)
    canvas.save(f"{OUT}/b_slide04.png"); print("✓ B s04")


def b_s05():
    """CTA — mesa íntima, pergunta direta."""
    img    = load_bg(f"{BG}/bg_v2_v2_b_s05.png", ctr=(0.5,0.4))
    # overlay mais claro para preservar o calor da imagem
    ov     = Image.new("RGBA", img.size, (0,0,0,85))
    base   = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    canvas = add_grain(canvas, intensity=8)
    d      = ImageDraw.Draw(canvas)

    # barra preta inferior com texto CTA
    ty = int(H * 0.62)
    canvas = brut_block(canvas, 0, ty, W, H-ty, (6,4,12), alpha=240)
    d      = ImageDraw.Draw(canvas)
    canvas = brut_block(canvas, 0, ty, W, 8, LIME)
    d      = ImageDraw.Draw(canvas)

    ty += 28
    fnt_h = F("black", 70)
    lines = ["QUAL O TAMANHO", "DO SEU PÚBLICO", "MAIS FIEL?"]
    _, fnt_h = fit_font(d, lines, "black", 70)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h); x = (W-lw_)//2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, ty, c1=LIME, c2=PINK)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_h, fill=WHITE)
        ty += int(fnt_h.size*1.08)

    ty += 16
    fnt_s = F("regular", 30)
    sub   = "Nem precisa ser grande. Precisa ser seu."
    lw_   = tw(d, sub, fnt_s); d.text(((W-lw_)//2, ty), sub, font=fnt_s, fill=OFFWHT)

    paste_logo(canvas)
    canvas.save(f"{OUT}/b_slide05.png"); print("✓ B s05")


# ══════════════════════════════════════════════════════════════════
# CAROUSEL C — SURREAL EDITORIAL CLARO
# Fundo CREME / BEGE — choque total num feed escuro
# Texto PRETO, dados gigantes, zero gradiente roxo
# ══════════════════════════════════════════════════════════════════

def c_s01():
    """47M herói — fundo creme com número preto gigante."""
    # metade superior: imagem surreal com overlay claro
    img    = load_bg(f"{BG}/bg_domingo_dom_c_s01.png", ctr=(0.5,0.3))
    cut    = int(H * 0.42)
    img_top = img.crop((0, 0, W, cut))

    canvas = Image.new("RGB", (W,H), CLAY)
    canvas.paste(img_top, (0,0))

    # linha separadora preta
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, cut, W, cut+8], fill=INK)

    # "47M" enorme, PRETO, fundo creme
    ty = cut + 20
    fnt_num = F("black", 210)
    num     = "47M"
    _, fnt_num = fit_font(d, [num], "black", 210, max_w=W-40)
    lw_     = tw(d, num, fnt_num)
    d.text(((W-lw_)//2, ty), num, font=fnt_num, fill=INK)
    ty     += int(fnt_num.size * 0.92)

    # linha PLUM abaixo
    d.rectangle([MARGIN, ty, W-MARGIN, ty+6], fill=PLUM)
    ty += 18

    fnt_lbl = F("bold", 40)
    lbl     = "DE EMPREENDEDORES NO BRASIL."
    for ln in wrap(d, lbl, fnt_lbl, max_w=W-80):
        lw_ = tw(d, ln, fnt_lbl)
        d.text(((W-lw_)//2, ty), ln, font=fnt_lbl, fill=PLUM)
        ty += int(fnt_lbl.size*1.15)

    ty += 12
    fnt_h = F("black", 54)
    twist = "A maioria não sabe o que está vendendo."
    for ln in wrap(d, twist, fnt_h, max_w=W-80):
        lw_ = tw(d, ln, fnt_h)
        d.text(((W-lw_)//2, ty), ln, font=fnt_h, fill=BLUSH)
        ty += int(fnt_h.size*1.1)

    paste_logo(canvas, dark_pill=False, light_pill=True)
    canvas.save(f"{OUT}/c_slide01.png"); print("✓ C s01")


def c_s02():
    """Negação tripla + revelação — fundo creme."""
    img    = load_bg(f"{BG}/bg_domingo_dom_c_s02.png", ctr=(0.5,0.4))
    cut    = int(H * 0.38)
    img_top = img.crop((0,0,W,cut))

    canvas = Image.new("RGB", (W,H), CLAY)
    canvas.paste(img_top, (0,0))
    d      = ImageDraw.Draw(canvas)
    d.rectangle([0, cut, W, cut+8], fill=INK)

    ty = cut + 24
    fnt_neg = F("bold", 44)
    negs    = [
        "NÃO É falta de produto.",
        "NÃO É falta de cliente.",
        "NÃO É falta de orçamento.",
    ]
    for txt in negs:
        lw_ = tw(d, txt, fnt_neg)
        d.text(((W-lw_)//2, ty), txt, font=fnt_neg, fill=(160,140,120))
        ty += int(fnt_neg.size*1.5)

    ty += 8
    d.rectangle([MARGIN, ty, W-MARGIN, ty+6], fill=PLUM)
    ty += 20

    fnt_big = F("black", 98)
    reveal  = "É FALTA DE CLAREZA."
    _, fnt_big = fit_font(d, [reveal], "black", 98, max_w=W-40)
    lw_     = tw(d, reveal, fnt_big)
    d.text(((W-lw_)//2, ty), reveal, font=fnt_big, fill=INK)
    ty     += int(fnt_big.size*1.1)

    fnt_s = F("regular", 32)
    sub   = "Clareza sobre o que você vende, para quem, e por que você."
    for ln in wrap(d, sub, fnt_s, max_w=W-80):
        lw_ = tw(d, ln, fnt_s)
        d.text(((W-lw_)//2, ty), ln, font=fnt_s, fill=PLUM)
        ty += int(fnt_s.size*1.5)

    paste_logo(canvas, dark_pill=False, light_pill=True)
    canvas.save(f"{OUT}/c_slide02.png"); print("✓ C s02")


def c_s03():
    """Megafone vs sussurro."""
    img    = load_bg(f"{BG}/bg_domingo_dom_c_s03.png")
    cut    = int(H * 0.45)
    img_top = img.crop((0,0,W,cut))

    canvas = Image.new("RGB", (W,H), CLAY)
    canvas.paste(img_top, (0,0))
    d      = ImageDraw.Draw(canvas)
    d.rectangle([0, cut, W, cut+8], fill=INK)

    ty = cut + 24
    fnt_h = F("black", 90)
    lines = ["FALAR ALTO", "NÃO É", "SER OUVIDO."]
    _, fnt_h = fit_font(d, lines, "black", 90, max_w=W-60)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h)
        x   = MARGIN if i % 2 == 0 else W - MARGIN - tw(d, ln, fnt_h)
        col = INK if i < len(lines)-1 else BLUSH
        d.text((x, ty), ln, font=fnt_h, fill=col)
        ty += int(fnt_h.size*1.04)

    ty += 14
    d.rectangle([MARGIN, ty, W-MARGIN, ty+5], fill=PLUM)
    ty += 18

    fnt_s = F("regular", 32)
    sub   = "Quem fala para todos não fala com ninguém."
    for ln in wrap(d, sub, fnt_s, max_w=W-80):
        lw_ = tw(d, ln, fnt_s)
        d.text(((W-lw_)//2, ty), ln, font=fnt_s, fill=PLUM)
        ty += int(fnt_s.size*1.5)

    paste_logo(canvas, dark_pill=False, light_pill=True)
    canvas.save(f"{OUT}/c_slide03.png"); print("✓ C s03")


def c_s04():
    """Fishbowl — claro vs turvo."""
    img    = load_bg(f"{BG}/bg_domingo_dom_c_s04.png")

    # imagem full com overlay CLARO (inusitado)
    ov     = Image.new("RGBA", img.size, (245,240,228,90))
    base   = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")
    d      = ImageDraw.Draw(canvas)

    # barra PLUM no topo
    d.rectangle([0,0,W,10], fill=PLUM)

    # texto direto ao ponto no centro/inferior
    ty = int(H * 0.60)
    d.rectangle([0, ty-8, W, H], fill=CLAY)
    d.rectangle([0, ty-8, W, ty], fill=INK)

    ty += 16
    fnt_h = F("black", 76)
    lines = ["POSICIONAMENTO CLARO", "VENDE MAIS QUE", "CRIATIVIDADE."]
    _, fnt_h = fit_font(d, lines, "black", 76, max_w=W-60)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h)
        col = INK if i < len(lines)-1 else BLUSH
        d.text(((W-lw_)//2, ty), ln, font=fnt_h, fill=col)
        ty += int(fnt_h.size*1.06)

    ty += 16
    fnt_s = F("regular", 30)
    sub   = "Sempre vendeu. Só ninguém falava isso abertamente."
    for ln in wrap(d, sub, fnt_s, max_w=W-80):
        lw_ = tw(d, ln, fnt_s); d.text(((W-lw_)//2, ty), ln, font=fnt_s, fill=PLUM)
        ty += int(fnt_s.size*1.5)

    paste_logo(canvas, dark_pill=False, light_pill=True)
    canvas.save(f"{OUT}/c_slide04.png"); print("✓ C s04")


def c_s05():
    """CTA — palco com holofote, pergunta final."""
    img    = load_bg(f"{BG}/bg_domingo_dom_c_s05.png", ctr=(0.5,0.4))
    cut    = int(H * 0.44)
    img_top = img.crop((0,0,W,cut))

    canvas = Image.new("RGB", (W,H), CLAY)
    canvas.paste(img_top, (0,0))
    d      = ImageDraw.Draw(canvas)
    d.rectangle([0, cut, W, cut+8], fill=INK)

    ty = cut + 24
    fnt_h = F("black", 72)
    lines = ["ESCREVE NOS", "COMENTÁRIOS O QUE", "VOCÊ VENDE.", "UMA FRASE SÓ."]
    _, fnt_h = fit_font(d, lines, "black", 72, max_w=W-60)
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h)
        col = INK if i < len(lines)-1 else BLUSH
        d.text(((W-lw_)//2, ty), ln, font=fnt_h, fill=col)
        ty += int(fnt_h.size*1.06)

    ty += 14
    d.rectangle([MARGIN, ty, W-MARGIN, ty+5], fill=PLUM)
    ty += 18

    fnt_s = F("bold", 30)
    rule  = "Sem usar a palavra 'solução'."
    lw_   = tw(d, rule, fnt_s); d.text(((W-lw_)//2, ty), rule, font=fnt_s, fill=PLUM)
    ty   += int(fnt_s.size*1.6)
    fnt_tiny = F("regular", 26)
    hint     = "Quem consegue está no caminho. Quem trava, a gente conversa."
    for ln in wrap(d, hint, fnt_tiny, max_w=W-80):
        lw_ = tw(d, ln, fnt_tiny); d.text(((W-lw_)//2, ty), ln, font=fnt_tiny, fill=(130,110,90))
        ty += int(fnt_tiny.size*1.5)

    paste_logo(canvas, dark_pill=False, light_pill=True)
    canvas.save(f"{OUT}/c_slide05.png"); print("✓ C s05")


if __name__ == "__main__":
    print("=== A — NEO-BRUTALISMO ===")
    a_s01(); a_s02(); a_s03(); a_s04(); a_s05()
    print("\n=== B — ZINE / PUNK ===")
    b_s01(); b_s02(); b_s03(); b_s04(); b_s05()
    print("\n=== C — SURREAL EDITORIAL CLARO ===")
    c_s01(); c_s02(); c_s03(); c_s04(); c_s05()
    print(f"\nDone → {OUT}")
