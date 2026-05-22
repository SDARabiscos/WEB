#!/usr/bin/env python3
"""PMI Perry — Carrosseis IA e Viral. Overlay esfumaçado via GaussianBlur."""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os, math

W, H   = 1080, 1080
VIOLET = (134, 0, 255)
VLT    = (160, 60, 255)   # violet light para gradiente
PINK   = (236, 72, 153)
WHITE  = (255, 255, 255)
GRAY   = (165, 168, 185)
BLACK  = (0, 0, 0)

R = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"
def F(style, size):
    return ImageFont.truetype({
        "black":   f"{R}/Roboto-Black.ttf",
        "bold":    f"{R}/Roboto-Bold.ttf",
        "medium":  f"{R}/Roboto-Medium.ttf",
        "regular": f"{R}/Roboto-Regular.ttf",
    }[style], size)

def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def tw(d, text, font):
    bb = d.textbbox((0,0), text, font=font); return bb[2]-bb[0]
def th(d, text, font):
    bb = d.textbbox((0,0), text, font=font); return bb[3]-bb[1]

def wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if tw(d,test,font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ── Overlay ESFUMAÇADO: gradiente + GaussianBlur forte ────────────
def smoky_overlay(img, top_strength=160, bot_strength=252,
                  top_reach=280, bot_reach=620, blur=52):
    """Overlay escuro com bordas esfumaçadas — sem corte chapado."""
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    dv = ImageDraw.Draw(ov)
    IW, IH = img.size
    for y in range(top_reach):
        a = int(top_strength * (1 - y/top_reach)**1.8)
        dv.line([(0,y),(IW,y)], fill=(0,0,0,a))
    for y in range(IH-1, IH-bot_reach-1, -1):
        a = int(bot_strength * ((IH-y)/bot_reach)**0.72)
        dv.line([(0,y),(IW,y)], fill=(0,0,0,a))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    base = img.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

# ── Logo PMI real ──────────────────────────────────────────────────
LOGO_PATH = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
def paste_logo(canvas, size=54, x=52, y=42):
    logo = Image.open(LOGO_PATH).convert("RGBA")
    lh = size; lw = int(logo.width * lh / logo.height)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    canvas.paste(logo, (x, y), logo)
    d = ImageDraw.Draw(canvas)
    d.rectangle([x, y+lh+8, x+lw, y+lh+12], fill=VIOLET)

# ── Gradiente texto via máscara ────────────────────────────────────
def grad_text(canvas, d, text, font, x, y, c1=VLT, c2=PINK):
    lw = tw(d,text,font); lh = th(d,text,font)
    lay  = Image.new("RGBA", canvas.size, (0,0,0,0))
    dl   = ImageDraw.Draw(lay)
    dl.text((x,y), text, font=font, fill=(*c1,255))
    tint = Image.new("RGBA", canvas.size, (0,0,0,0))
    dt   = ImageDraw.Draw(tint)
    for xi in range(x, x+lw):
        t = (xi-x)/max(1,lw-1)
        dt.line([(xi,y),(xi,y+lh)], fill=(*lerp(c1,c2,t),255))
    _,_,_,ach = lay.split(); tint.putalpha(ach)
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(tint)
    return canvas.convert("RGB")

def text_c(d, text, font, y, color=WHITE, max_w=None, leading=1.08):
    mw = max_w or W-116
    for line in wrap(d, text, font, mw):
        lw = tw(d,line,font)
        d.text(((W-lw)//2, y), line, font=font, fill=color)
        y += int(font.size * leading)
    return y

def sep(d, y, w=56):
    x = (W-w)//2
    for xi in range(w):
        c = lerp(VLT, PINK, xi/max(1,w-1))
        d.line([(x+xi,y),(x+xi,y+5)], fill=c)
    return y+5

def load_bg(path, centering=(0.5,0.5)):
    img = Image.open(path).convert("RGB")
    return ImageOps.fit(img, (W,H), Image.LANCZOS, centering=centering)

OUT = "/home/user/WEB/carrossel-pmi/slides"
BG  = "/home/user/WEB/carrossel-pmi"
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
# CARROSSEL 1 — "A IA VAI MATAR SEU NEGÓCIO?"
# ══════════════════════════════════════════════════════════════════

def c1_slide01():
    canvas = smoky_overlay(load_bg(f"{BG}/bg_ia_slide01.png"),
                           top_strength=150, bot_strength=252,
                           top_reach=260, bot_reach=640, blur=58)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt  = F("black", 112)
    lead = int(112*1.06)
    y0   = H - 448

    for i, line in enumerate(["A IA VAI","MATAR SEU"]):
        lw = tw(d,line,fnt)
        d.text(((W-lw)//2, y0+i*lead), line, font=fnt, fill=WHITE)

    line3 = "NEGÓCIO?"
    lw3 = tw(d,line3,fnt); ny = y0+2*lead
    canvas = grad_text(canvas, d, line3, fnt, (W-lw3)//2, ny)
    d = ImageDraw.Draw(canvas)

    y_sub = ny + th(d,line3,fnt) + 18
    text_c(d, "A resposta honesta que ninguém do mercado quer dar.",
           F("regular",28), y_sub, GRAY, leading=1.5)
    canvas.save(f"{OUT}/c1_slide01.png"); print("✓ c1_slide01")


def c1_slide02():
    canvas = smoky_overlay(load_bg(f"{BG}/bg_ia_slide02.png"),
                           top_strength=120, bot_strength=248,
                           top_reach=240, bot_reach=660, blur=60)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    # "60%" hero gradiente
    fnt_big = F("black", 180)
    num = "60%"
    nw = tw(d,num,fnt_big); ny = H - 560
    canvas = grad_text(canvas, d, num, fnt_big, (W-nw)//2, ny)
    d = ImageDraw.Draw(canvas)

    y = ny + th(d,num,fnt_big) - 10
    y = sep(d, y+10)
    y += 20

    fnt_h = F("black", 58)
    y = text_c(d, "DOS NEGÓCIOS JÁ USAM IA PARA CRIAR CONTEÚDO",
               fnt_h, y, WHITE, leading=1.1)
    y += 14
    text_c(d, "Estão produzindo mais, mais rápido. E convertendo menos. Volume sem estratégia é ruído.",
           F("regular",27), y, GRAY, leading=1.48)
    canvas.save(f"{OUT}/c1_slide02.png"); print("✓ c1_slide02")


def c1_slide03():
    canvas = smoky_overlay(load_bg(f"{BG}/bg_ia_slide03.png"),
                           top_strength=100, bot_strength=245,
                           top_reach=220, bot_reach=580, blur=55)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_h = F("black", 96)
    lead  = int(96*1.06)
    y0    = H - 420

    # Linha 1 branca
    line1 = "A IA EXECUTA."
    lw1 = tw(d,line1,fnt_h)
    d.text(((W-lw1)//2, y0), line1, font=fnt_h, fill=WHITE)

    # Linha 2 gradiente
    line2 = "ESTRATÉGIA É HUMANA."
    lw2 = tw(d,line2,fnt_h); ny2 = y0+lead
    canvas = grad_text(canvas, d, line2, fnt_h, (W-lw2)//2, ny2)
    d = ImageDraw.Draw(canvas)

    y_sub = ny2 + th(d,line2,fnt_h) + 14
    y_sub = sep(d, y_sub) + 18
    text_c(d, "Ferramenta não diagnostica negócio. Não lê contexto de mercado. Não constrói posicionamento real.",
           F("regular",27), y_sub, GRAY, leading=1.48)
    canvas.save(f"{OUT}/c1_slide03.png"); print("✓ c1_slide03")


def c1_slide04():
    canvas = smoky_overlay(load_bg(f"{BG}/bg_ia_slide04.png"),
                           top_strength=130, bot_strength=250,
                           top_reach=250, bot_reach=620, blur=56)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_h = F("black", 100)
    lead  = int(100*1.06)
    y0    = H - 470

    lines = ["O NEGÓCIO QUE", "VAI MORRER"]
    for i, line in enumerate(lines):
        lw = tw(d,line,fnt_h)
        d.text(((W-lw)//2, y0+i*lead), line, font=fnt_h, fill=WHITE)

    line3 = "NÃO USA IA."
    lw3 = tw(d,line3,fnt_h); ny3 = y0+2*lead
    canvas = grad_text(canvas, d, line3, fnt_h, (W-lw3)//2, ny3)
    d = ImageDraw.Draw(canvas)

    y_sub = ny3 + th(d,line3,fnt_h) + 16
    text_c(d, "É o que não sabe o que fazer com ela. O problema nunca foi a ferramenta. Foi sempre a falta de estratégia.",
           F("regular",26), y_sub, GRAY, leading=1.48)
    canvas.save(f"{OUT}/c1_slide04.png"); print("✓ c1_slide04")


def c1_slide05():
    canvas = smoky_overlay(load_bg(f"{BG}/bg_ia_slide05.png"),
                           top_strength=110, bot_strength=250,
                           top_reach=240, bot_reach=660, blur=60)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_h = F("black", 96)
    lead  = int(96*1.06)
    y0    = H - 490

    line1 = "VOCÊ USA IA NO"
    lw1 = tw(d,line1,fnt_h)
    d.text(((W-lw1)//2, y0), line1, font=fnt_h, fill=WHITE)

    line2 = "SEU NEGÓCIO?"
    lw2 = tw(d,line2,fnt_h); ny2 = y0+lead
    canvas = grad_text(canvas, d, line2, fnt_h, (W-lw2)//2, ny2)
    d = ImageDraw.Draw(canvas)

    y_sub = ny2 + th(d,line2,fnt_h) + 16
    y_sub = sep(d, y_sub) + 22

    # Botões USE / MEDO lado a lado centralizados
    fnt_b = F("bold", 28)
    labels = [("USE", VLT), ("MEDO", PINK)]
    btns = []
    for lbl, col in labels:
        bw = tw(d,lbl,fnt_b)+52; bh = th(d,lbl,fnt_b)+22
        btns.append((lbl, col, bw, bh))
    gap = 20
    total_bw = sum(b[2] for b in btns) + gap
    bx = (W-total_bw)//2
    for lbl, col, bw, bh in btns:
        d.rounded_rectangle([bx,y_sub,bx+bw,y_sub+bh], radius=10, fill=col)
        d.text((bx+(bw-tw(d,lbl,fnt_b))//2, y_sub+(bh-th(d,lbl,fnt_b))//2),
               lbl, font=fnt_b, fill=WHITE)
        bx += bw+gap
    y_sub += btns[0][3] + 18
    text_c(d, "Comenta aqui. Vamos falar sobre isso.",
           F("regular",26), y_sub, GRAY, leading=1.5)
    canvas.save(f"{OUT}/c1_slide05.png"); print("✓ c1_slide05")


# ══════════════════════════════════════════════════════════════════
# CARROSSEL 2 — "VIRAL ESTÁ MORTO"
# ══════════════════════════════════════════════════════════════════

def c2_slide01():
    canvas = smoky_overlay(load_bg(f"{BG}/bg_viral_slide01.png"),
                           top_strength=140, bot_strength=252,
                           top_reach=260, bot_reach=640, blur=58)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_h = F("black", 130)
    lead  = int(130*1.06)
    y0    = H - 480

    # "VIRAL" com risco por cima (tachado)
    line1 = "VIRAL"
    lw1 = tw(d,line1,fnt_h); lh1 = th(d,line1,fnt_h)
    x1 = (W-lw1)//2
    d.text((x1, y0), line1, font=fnt_h, fill=WHITE)
    # tachado vermelho
    mid_y = y0 + lh1//2
    d.line([(x1-8, mid_y),(x1+lw1+8, mid_y)], fill=(230,40,40), width=10)

    line2 = "ESTÁ MORTO."
    lw2 = tw(d,line2,fnt_h); ny2 = y0+lead
    canvas = grad_text(canvas, d, line2, fnt_h, (W-lw2)//2, ny2)
    d = ImageDraw.Draw(canvas)

    y_sub = ny2 + th(d,line2,fnt_h) + 16
    text_c(d, "E quem ainda corre atrás disso está perdendo tempo, dinheiro e posicionamento.",
           F("regular",27), y_sub, GRAY, leading=1.48)
    canvas.save(f"{OUT}/c2_slide01.png"); print("✓ c2_slide01")


def c2_slide02():
    canvas = smoky_overlay(load_bg(f"{BG}/bg_viral_slide02.png"),
                           top_strength=120, bot_strength=248,
                           top_reach=230, bot_reach=650, blur=56)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_h = F("black", 88)
    lead  = int(88*1.06)
    y0    = H - 460

    lines = ["O ALGORITMO PAROU", "DE PREMIAR BARULHO"]
    for i, line in enumerate(lines[:1]):
        lw = tw(d,line,fnt_h)
        d.text(((W-lw)//2, y0+i*lead), line, font=fnt_h, fill=WHITE)

    lw2 = tw(d,lines[1],fnt_h); ny2 = y0+lead
    canvas = grad_text(canvas, d, lines[1], fnt_h, (W-lw2)//2, ny2)
    d = ImageDraw.Draw(canvas)

    y_sub = ny2 + th(d,lines[1],fnt_h) + 14
    y_sub = sep(d, y_sub) + 18
    text_c(d, "Em 2026 o Instagram virou curador de relevância. Conteúdo apelativo e sem substância perdeu alcance.",
           F("regular",27), y_sub, GRAY, leading=1.48)
    canvas.save(f"{OUT}/c2_slide02.png"); print("✓ c2_slide02")


def c2_slide03():
    canvas = smoky_overlay(load_bg(f"{BG}/bg_viral_slide03.png"),
                           top_strength=130, bot_strength=250,
                           top_reach=250, bot_reach=620, blur=55)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_h = F("black", 72)
    lead  = int(72*1.1)
    y0    = H - 500

    lines_h = ["1 MILHÃO DE VIEWS", "DE QUEM NÃO COMPRA"]
    for i, line in enumerate(lines_h):
        lw = tw(d,line,fnt_h)
        d.text(((W-lw)//2, y0+i*lead), line, font=fnt_h, fill=WHITE)

    line3 = "NÃO PAGA BOLETO."
    lw3 = tw(d,line3,fnt_h); ny3 = y0+2*lead
    canvas = grad_text(canvas, d, line3, fnt_h, (W-lw3)//2, ny3)
    d = ImageDraw.Draw(canvas)

    y_sub = ny3 + th(d,line3,fnt_h) + 14
    y_sub = sep(d, y_sub) + 18
    text_c(d, "Alcance sem retenção é vaidade. Quem retém audiência qualificada vende. Quem viraliza pra nada, some.",
           F("regular",26), y_sub, GRAY, leading=1.48)
    canvas.save(f"{OUT}/c2_slide03.png"); print("✓ c2_slide03")


def c2_slide04():
    canvas = smoky_overlay(load_bg(f"{BG}/bg_viral_slide04.png"),
                           top_strength=110, bot_strength=245,
                           top_reach=230, bot_reach=600, blur=54)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_h = F("black", 100)
    lead  = int(100*1.06)
    y0    = H - 450

    line1 = "O QUE REALMENTE"
    lw1 = tw(d,line1,fnt_h)
    d.text(((W-lw1)//2, y0), line1, font=fnt_h, fill=WHITE)

    line2 = "FUNCIONA AGORA"
    lw2 = tw(d,line2,fnt_h); ny2 = y0+lead
    canvas = grad_text(canvas, d, line2, fnt_h, (W-lw2)//2, ny2)
    d = ImageDraw.Draw(canvas)

    y_sub = ny2 + th(d,line2,fnt_h) + 14
    y_sub = sep(d, y_sub) + 18
    text_c(d, "Conteúdo que resolve. Que ensina. Que posiciona. Consistência bate viral eventual toda semana.",
           F("regular",27), y_sub, GRAY, leading=1.48)
    canvas.save(f"{OUT}/c2_slide04.png"); print("✓ c2_slide04")


def c2_slide05():
    canvas = smoky_overlay(load_bg(f"{BG}/bg_viral_slide05.png"),
                           top_strength=130, bot_strength=252,
                           top_reach=260, bot_reach=650, blur=58)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_h = F("black", 96)
    lead  = int(96*1.06)
    y0    = H - 500

    line1 = "PARA DE PERSEGUIR"
    lw1 = tw(d,line1,fnt_h)
    d.text(((W-lw1)//2, y0), line1, font=fnt_h, fill=WHITE)

    line2 = "VIRAL."
    lw2 = tw(d,line2,fnt_h); ny2 = y0+lead
    canvas = grad_text(canvas, d, line2, fnt_h, (W-lw2)//2, ny2)
    d = ImageDraw.Draw(canvas)

    line3 = "CONSTRÓI AUTORIDADE."
    lw3 = tw(d,line3,fnt_h); ny3 = ny2+lead
    d = ImageDraw.Draw(canvas)
    d.text(((W-lw3)//2, ny3), line3, font=fnt_h, fill=WHITE)

    y_sub = ny3 + th(d,line3,fnt_h) + 14
    y_sub = sep(d, y_sub) + 20

    # Botões SIM / NÃO
    fnt_b = F("bold", 28)
    labels = [("SIM", VIOLET), ("NÃO", PINK)]
    btns = []
    for lbl, col in labels:
        bw = tw(d,lbl,fnt_b)+52; bh = th(d,lbl,fnt_b)+22
        btns.append((lbl, col, bw, bh))
    gap = 20
    total_bw = sum(b[2] for b in btns) + gap
    bx = (W-total_bw)//2
    for lbl, col, bw, bh in btns:
        d.rounded_rectangle([bx,y_sub,bx+bw,y_sub+bh], radius=10, fill=col)
        d.text((bx+(bw-tw(d,lbl,fnt_b))//2, y_sub+(bh-th(d,lbl,fnt_b))//2),
               lbl, font=fnt_b, fill=WHITE)
        bx += bw+gap
    y_sub += btns[0][3] + 18
    text_c(d, "Curioso pra saber a proporção.",
           F("regular",26), y_sub, GRAY, leading=1.5)
    canvas.save(f"{OUT}/c2_slide05.png"); print("✓ c2_slide05")


if __name__ == "__main__":
    print("=== Carrossel 1: A IA vai matar seu negócio? ===")
    c1_slide01(); c1_slide02(); c1_slide03(); c1_slide04(); c1_slide05()
    print("\n=== Carrossel 2: Viral está morto ===")
    c2_slide01(); c2_slide02(); c2_slide03(); c2_slide04(); c2_slide05()
    print(f"\nDone → {OUT}")
