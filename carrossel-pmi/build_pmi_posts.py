#!/usr/bin/env python3
"""PMI — Posts sábado: Meta Ads 12% + IA sem estratégia. 1080×1350."""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os

W, H   = 1080, 1350
MARGIN = 60
MAX_W  = W - MARGIN * 2

VIOLET = (134,  0, 255)
VLT    = (160, 60, 255)
PINK   = (236, 72, 153)
WHITE  = (255, 255, 255)
GRAY   = (200, 200, 210)
RED    = (220,  38,  38)

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

def tw(d, text, font): bb = d.textbbox((0,0), text, font=font); return bb[2]-bb[0]
def th(d, text, font): bb = d.textbbox((0,0), text, font=font); return bb[3]-bb[1]

def wrap(d, text, font, max_w=MAX_W):
    if not text: return []
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if tw(d, test, font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fit_font(d, lines, style, start=100, min_sz=48):
    sz = start
    while sz >= min_sz:
        fnt = F(style, sz)
        if all(tw(d, ln, fnt) <= MAX_W for ln in lines):
            return sz, fnt
        sz -= 4
    return min_sz, F(style, min_sz)

# ── Gradiente violeta→rosa no último headline ─────────────────────
def grad_text(canvas, d, text, font, x, y, c1=VLT, c2=PINK):
    bb = d.textbbox((0,0), text, font=font)
    lw = bb[2]-bb[0]
    y0 = y+bb[1]; y1 = y+bb[3]
    lay = Image.new("RGBA", canvas.size, (0,0,0,0))
    dl  = ImageDraw.Draw(lay); dl.text((x,y), text, font=font, fill=(*c1,255))
    tint = Image.new("RGBA", canvas.size, (0,0,0,0))
    dt   = ImageDraw.Draw(tint)
    for xi in range(x, x+lw):
        t = (xi-x)/max(1,lw-1)
        dt.line([(xi,y0),(xi,y1)], fill=(*lerp(c1,c2,t),255))
    _,_,_,ach = lay.split(); tint.putalpha(ach)
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(tint)
    return canvas.convert("RGB")

# ── Overlay esfumaçado ────────────────────────────────────────────
def smoky(img, top_s=150, bot_s=255, top_r=300, bot_r=820, blur=60):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    dv = ImageDraw.Draw(ov)
    IW, IH = img.size
    for y in range(top_r):
        a = int(top_s * (1-y/top_r)**1.8)
        dv.line([(0,y),(IW,y)], fill=(0,0,0,a))
    for y in range(IH-1, IH-bot_r-1, -1):
        dist = IH-1-y
        a = int(bot_s * (1-dist/bot_r)**0.55)
        dv.line([(0,y),(IW,y)], fill=(0,0,0,a))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    base = img.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

# ── Painel escuro atrás do bloco de texto ─────────────────────────
def text_panel(canvas, y_top, y_bot):
    IW = canvas.size[0]
    fade_top, fade_bot = 100, 140
    alpha = 185

    layer = Image.new("RGBA", canvas.size, (0,0,0,0))
    dl    = ImageDraw.Draw(layer)
    dl.rectangle([0, y_top, IW, y_bot], fill=(0,0,0,alpha))
    for iy in range(fade_top):
        a = int(alpha * (iy/fade_top)**1.8)
        dl.line([(0,y_top-fade_top+iy),(IW,y_top-fade_top+iy)], fill=(0,0,0,a))
    for iy in range(fade_bot):
        a = int(alpha * (1-iy/fade_bot)**1.4)
        dl.line([(0,y_bot+iy),(IW,y_bot+iy)], fill=(0,0,0,a))
    layer = layer.filter(ImageFilter.GaussianBlur(14))
    base  = canvas.convert("RGBA"); base.alpha_composite(layer)
    return base.convert("RGB")

# ── Logo PMI ──────────────────────────────────────────────────────
LOGO = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
def paste_logo(canvas, lh=54, x=52, y=42):
    logo = Image.open(LOGO).convert("RGBA")
    lw   = int(logo.width * lh / logo.height)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    canvas.paste(logo, (x, y), logo)
    d = ImageDraw.Draw(canvas)
    d.rectangle([x, y+lh+8, x+lw, y+lh+12], fill=VIOLET)

# ── Separador ─────────────────────────────────────────────────────
def sep_line(d, y, w=56):
    x = (W-w)//2
    for xi in range(w):
        c = lerp(VLT, PINK, xi/max(1,w-1))
        d.line([(x+xi,y),(x+xi,y+5)], fill=c)
    return y+5

def draw_sub(canvas, d, text, y, fnt_sz=30, color=WHITE):
    if not text: return y
    fnt = F("regular", fnt_sz)
    lh  = int(fnt_sz*1.55)
    for line in wrap(d, text, fnt):
        lw = tw(d, line, fnt)
        d.text(((W-lw)//2, y), line, font=fnt, fill=color)
        y += lh
    return y

# ── Horário no topo direito ───────────────────────────────────────
def paste_time(canvas, time_str):
    d   = ImageDraw.Draw(canvas)
    fnt = F("medium", 18)
    lw  = tw(d, time_str, fnt)
    d.text((W-52-lw, 50), time_str, font=fnt, fill=(200,200,210))

# ── Builder genérico ──────────────────────────────────────────────
def make_slide(bg_path, headlines, subtitle, out_path,
               time_str="", h_start=100, centering=(0.5,0.5),
               highlight_num=None):
    """
    highlight_num: str exibido em fonte grande antes dos headlines (ex: "12%")
    """
    img    = Image.open(bg_path).convert("RGB")
    canvas = ImageOps.fit(img, (W,H), Image.LANCZOS, centering=centering)
    canvas = smoky(canvas)
    paste_logo(canvas)
    if time_str: paste_time(canvas, time_str)
    d = ImageDraw.Draw(canvas)

    h_sz, fnt_h = fit_font(d, headlines, "black", h_start)
    lead   = int(h_sz * 1.08)
    fnt_s  = F("regular", 30)
    sub_ls = wrap(d, subtitle, fnt_s)
    sub_h  = len(sub_ls) * int(30*1.55)

    num_h = 0
    if highlight_num:
        fnt_big = F("black", 148)
        num_bb  = d.textbbox((0,0), highlight_num, font=fnt_big)
        num_h   = num_bb[3] - num_bb[1] + 16

    block_h = num_h + lead*len(headlines) + 20+5+18 + sub_h
    y_start = max(int(H*0.46) - block_h//2, 340)
    y_start = min(y_start, H - 130 - block_h)
    y = y_start

    canvas = text_panel(canvas, y-70, y_start+block_h+50)
    d = ImageDraw.Draw(canvas)

    # número destaque
    if highlight_num:
        fnt_big = F("black", 148)
        nw = tw(d, highlight_num, fnt_big)
        canvas = grad_text(canvas, d, highlight_num, fnt_big, (W-nw)//2, y)
        d = ImageDraw.Draw(canvas)
        y += num_h

    # headlines
    for i, line in enumerate(headlines):
        lw = tw(d, line, fnt_h); x = (W-lw)//2
        if i == len(headlines)-1:
            canvas = grad_text(canvas, d, line, fnt_h, x, y)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((x, y), line, font=fnt_h, fill=WHITE)
        y += lead

    y += 20; y = sep_line(d, y)+18
    draw_sub(canvas, d, subtitle, y)
    canvas.save(out_path); print(f"✓ {os.path.basename(out_path)}")


OUT = "/home/user/WEB/carrossel-pmi/posts"
BG  = "/home/user/WEB/carrossel-pmi"
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
# POST 1 — 10h30 — "Meta Ads ficou 12% mais caro"
# ══════════════════════════════════════════════════════════════════

def p1_s01():
    make_slide(
        f"{BG}/bg_p1_s01.png",
        ["META ADS", "FICOU 12%", "MAIS CARO."],
        "E a maioria dos negócios ainda não ajustou nada.",
        f"{OUT}/p1_slide01.png",
        time_str="10:30", h_start=108,
    )

def p1_s02():
    make_slide(
        f"{BG}/bg_p1_s02.png",
        ["VOCÊ ESTÁ PAGANDO MAIS", "E ENTREGANDO MENOS."],
        "A Meta repassa PIS, COFINS e ISS direto pra você. R$5k virou R$5.607 pelo mesmo resultado.",
        f"{OUT}/p1_slide02.png",
        h_start=84,
    )

def p1_s03():
    make_slide(
        f"{BG}/bg_p1_s03.png",
        ["JÁ AJUSTOU SEU", "ORÇAMENTO?"],
        "Comenta aqui. Vamos calcular o impacto no seu investimento.",
        f"{OUT}/p1_slide03.png",
        h_start=100,
    )


# ══════════════════════════════════════════════════════════════════
# POST 2 — 16h — "82% usam IA. Quase nenhum tem estratégia."
# ══════════════════════════════════════════════════════════════════

def p2_s01():
    make_slide(
        f"{BG}/bg_p2_s01.png",
        ["JÁ USAM IA.", "QUASE NENHUM", "TEM ESTRATÉGIA."],
        "É isso que separa quem cresce de quem só produz ruído.",
        f"{OUT}/p2_slide01.png",
        time_str="16:00", h_start=100,
        highlight_num="82%",
    )

def p2_s02():
    make_slide(
        f"{BG}/bg_p2_s02.png",
        ["FERRAMENTA SEM", "DIREÇÃO É DESPERDÍCIO."],
        "IA executa. Quem define o que executar ainda é humano. Estratégia não se automatiza.",
        f"{OUT}/p2_slide02.png",
        h_start=84,
    )

def p2_s03():
    make_slide(
        f"{BG}/bg_p2_s03.png",
        ["SALVA ESSE POST.", "SEGUNDA A", "CONVERSA MUDA."],
        "Você usa IA com estratégia ou no piloto automático?",
        f"{OUT}/p2_slide03.png",
        h_start=96,
    )


if __name__ == "__main__":
    print("=== POST 1 — 10h30: Meta Ads 12% mais caro ===")
    p1_s01(); p1_s02(); p1_s03()
    print("\n=== POST 2 — 16h: 82% usam IA sem estratégia ===")
    p2_s01(); p2_s02(); p2_s03()
    print(f"\nDone → {OUT}")
