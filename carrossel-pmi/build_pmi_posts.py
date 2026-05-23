#!/usr/bin/env python3
"""PMI — Posts sábado. Layout Modelo 2 "Faixa Neon"."""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os

W, H    = 1080, 1350
MARGIN  = 64
MAX_W   = W - MARGIN * 2

VIOLET  = (134,   0, 255)
VLT     = (160,  60, 255)
PINK    = (236,  72, 153)
WHITE   = (255, 255, 255)
OFFWHT  = (235, 228, 245)
DARK    = (  8,   6,  14)
GRAY    = (160, 155, 175)

# faixa escura começa a 60% da altura → 40% de strip
FAIXA_Y = int(H * 0.60)   # y=810
LINE_H  = 5               # espessura da linha neon

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

def tw(d, t, f): bb = d.textbbox((0,0), t, font=f); return bb[2]-bb[0]

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

def fit_font(d, lines, style, start=110, min_sz=44, max_w=MAX_W):
    sz = start
    while sz >= min_sz:
        f = F(style, sz)
        if all(tw(d, ln, f) <= max_w for ln in lines): return sz, f
        sz -= 4
    return min_sz, F(style, min_sz)

def grad_text(canvas, d, text, font, x, y):
    """Gradiente VLT→PINK horizontal no texto."""
    c1, c2 = VLT, PINK
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

# ── Logo PMI ──────────────────────────────────────────────────────
LOGO = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
def paste_logo(canvas, lh=44, x=52, y=44):
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x-10, y-8, x+185, y+lh+12], radius=12, fill=(8,6,14,210))
    logo = Image.open(LOGO).convert("RGBA")
    lw   = int(logo.width * lh / logo.height)
    logo = logo.resize((lw,lh), Image.LANCZOS)
    canvas.paste(logo, (x,y), logo)
    d = ImageDraw.Draw(canvas)
    d.rectangle([x, y+lh+7, x+lw, y+lh+10], fill=VIOLET)

# ── Tag de horário ────────────────────────────────────────────────
def paste_time(canvas, tag):
    d   = ImageDraw.Draw(canvas)
    fnt = F("medium", 17)
    lw_ = tw(d, tag, fnt)
    d.rounded_rectangle([W-60-lw_, 38, W-44, 70], radius=8, fill=(*VLT,200))
    d.text((W-52-lw_, 46), tag, font=fnt, fill=WHITE)


BG  = "/home/user/WEB/carrossel-pmi"
OUT = "/home/user/WEB/carrossel-pmi/posts"
os.makedirs(OUT, exist_ok=True)


def make_slide(bg_path, headline, subtitle, accent=None,
               tag=None, centering=(0.5,0.5)):
    """
    Modelo 2 — Faixa Neon.
    Imagem full (overlay 100) + faixa sólida inf 40% + linha neon topo.
    Headline branca + última linha VLT→PINK. Subtítulo OFFWHT.
    """
    # 1. imagem full com overlay suave
    img    = ImageOps.fit(Image.open(bg_path).convert("RGB"), (W,H),
                          Image.LANCZOS, centering=centering)
    ov     = Image.new("RGBA", img.size, (0,0,0,100))
    base   = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")

    # 2. faixa escura sólida no terço inferior
    faixa = Image.new("RGBA", (W,H), (0,0,0,0))
    ImageDraw.Draw(faixa).rectangle([0, FAIXA_Y, W, H], fill=(*DARK, 248))
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(faixa)
    canvas = canvas.convert("RGB")
    d      = ImageDraw.Draw(canvas)

    # 3. linha neon no topo da faixa (PINK→VLT da esquerda pra direita)
    for xi in range(W):
        d.line([(xi, FAIXA_Y), (xi, FAIXA_Y + LINE_H)],
               fill=lerp(PINK, VLT, xi / (W-1)))

    # 4. headline
    ty = FAIXA_Y + LINE_H + 36
    _, fnt_h = fit_font(d, headline, "black", 108, max_w=MAX_W)
    lead     = int(fnt_h.size * 1.06)
    for i, ln in enumerate(headline):
        lw_ = tw(d, ln, fnt_h)
        x   = (W - lw_) // 2
        if i == len(headline) - 1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, ty)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((x, ty), ln, font=fnt_h, fill=WHITE)
        ty += lead

    # 5. subtítulo
    ty += 18
    fnt_s = F("regular", 30)
    for ln in wrap(d, subtitle, fnt_s):
        lw_ = tw(d, ln, fnt_s)
        d.text(((W - lw_) // 2, ty), ln, font=fnt_s, fill=OFFWHT)
        ty += int(30 * 1.55)

    # 6. acento extra (linha menor, destaque PINK)
    if accent:
        ty += 4
        fnt_a = F("bold", 27)
        for ln in wrap(d, accent, fnt_a):
            lw_ = tw(d, ln, fnt_a)
            d.text(((W - lw_) // 2, ty), ln, font=fnt_a, fill=PINK)
            ty += int(27 * 1.5)

    # 7. logo + tag
    paste_logo(canvas)
    if tag:
        paste_time(canvas, tag)

    return canvas


# ════════════════════════════════════════════════════════════════
# POST 1 — 10h30 — "Meta Ads ficou 12% mais caro"
# ════════════════════════════════════════════════════════════════

def p1_s01():
    c = make_slide(
        f"{BG}/bg2_p1_s01.png",
        headline = ["META ADS FICOU", "12% MAIS CARO."],
        subtitle = "Seu orçamento de tráfego pago acabou de encolher — sem aviso.",
        accent   = "Desliza e entende o que mudou.",
        tag      = "10:30 • PMI",
    )
    c.save(f"{OUT}/p1_slide01.png"); print("✓ p1_01")

def p1_s02():
    c = make_slide(
        f"{BG}/bg2_p1_s02.png",
        headline = ["SEU DINHEIRO SUMIU", "SEM VOCÊ SABER."],
        subtitle = "A Meta repassou PIS + COFINS + ISS direto pro anunciante. Você pagou a conta.",
        centering = (0.5, 0.4),
    )
    c.save(f"{OUT}/p1_slide02.png"); print("✓ p1_02")

def p1_s03():
    c = make_slide(
        f"{BG}/bg2_p1_s03.png",
        headline = ["A META PASSOU OS", "IMPOSTOS PRA VOCÊ."],
        subtitle = "12,15% a mais no CPM, no CPC, no CPL. Sem e-mail, sem comunicado.",
        accent   = "E o seu ROAS caiu junto.",
        centering = (0.5, 0.35),
    )
    c.save(f"{OUT}/p1_slide03.png"); print("✓ p1_03")

def p1_s04():
    c = make_slide(
        f"{BG}/bg2_p1_s04.png",
        headline = ["3 AJUSTES PARA", "FAZER AGORA."],
        subtitle = "Reajuste o budget. Priorize conversão. Revise o criativo.",
        accent   = "Quem age agora protege o ROAS.",
        centering = (0.5, 0.25),
    )
    c.save(f"{OUT}/p1_slide04.png"); print("✓ p1_04")

def p1_s05():
    c = make_slide(
        f"{BG}/bg2_p1_s05.png",
        headline = ["QUANTO VOCÊ PERDEU", "ESSE MÊS?"],
        subtitle = "Comenta aqui. A gente calcula o impacto exato no seu investimento.",
        accent   = "Responde nos comentários. ↓",
    )
    c.save(f"{OUT}/p1_slide05.png"); print("✓ p1_05")


# ════════════════════════════════════════════════════════════════
# POST 2 — 16h — "82% usam IA. Quase nenhum tem estratégia."
# ════════════════════════════════════════════════════════════════

def p2_s01():
    c = make_slide(
        f"{BG}/bg2_p2_s01.png",
        headline = ["82% USAM IA.", "ZERO ESTRATÉGIA."],
        subtitle = "A maioria só produz ruído com mais velocidade.",
        accent   = "Desliza e vê a diferença.",
        tag      = "16:00 • PMI",
    )
    c.save(f"{OUT}/p2_slide01.png"); print("✓ p2_01")

def p2_s02():
    c = make_slide(
        f"{BG}/bg2_p2_s02.png",
        headline = ["IA AUTOMATIZA.", "ESTRATÉGIA DECIDE O QUÊ."],
        subtitle = "Sem direção, você só escala o desperdício com mais eficiência.",
    )
    c.save(f"{OUT}/p2_slide02.png"); print("✓ p2_02")

def p2_s03():
    c = make_slide(
        f"{BG}/bg2_p2_s03.png",
        headline = ["FERRAMENTA ERRADA", "É PREJUÍZO DOBRADO."],
        subtitle = "IA na mão certa escala resultado. Na errada, só escala o custo.",
        centering = (0.5, 0.3),
    )
    c.save(f"{OUT}/p2_slide03.png"); print("✓ p2_03")

def p2_s04():
    c = make_slide(
        f"{BG}/bg2_p2_s04.png",
        headline = ["O QUE A IA", "NÃO FAZ POR VOCÊ."],
        subtitle = "Posicionar sua marca. Entender seu cliente. Definir onde crescer.",
        accent   = "Isso ainda é 100% seu.",
        centering = (0.5, 0.25),
    )
    c.save(f"{OUT}/p2_slide04.png"); print("✓ p2_04")

def p2_s05():
    c = make_slide(
        f"{BG}/bg2_p2_s05.png",
        headline = ["SALVA ESSE POST.", "SEGUNDA A CONVERSA MUDA."],
        subtitle = "Você usa IA com estratégia ou no piloto automático?",
        accent   = "Responde aqui embaixo. ↓",
        centering = (0.5, 0.3),
    )
    c.save(f"{OUT}/p2_slide05.png"); print("✓ p2_05")


if __name__ == "__main__":
    print("=== POST 1 — 10h30 ===")
    p1_s01(); p1_s02(); p1_s03(); p1_s04(); p1_s05()
    print("\n=== POST 2 — 16h ===")
    p2_s01(); p2_s02(); p2_s03(); p2_s04(); p2_s05()
    print(f"\nDone → {OUT}")
