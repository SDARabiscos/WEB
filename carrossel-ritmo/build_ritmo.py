#!/usr/bin/env python3
"""Ritmo da Marca — Carrosseis híbridos (abertura IA + internos clean tipográfico)."""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os, math

W, H   = 1080, 1350
MARGIN = 64
MAX_W  = W - MARGIN * 2

# ── Paleta Ritmo da Marca ──────────────────────────────────────────
BG1     = (9,   9,  11)   # #09090B fundo principal
BG2     = (24,  24, 27)   # #18181B fundo secundário
BG3     = (39,  39, 42)   # #27272A cards/bordas
PURPLE  = (168,  85, 247)  # #A855F7 principal
PUR_LT  = (192, 132, 252)  # #C084FC claro
PUR_MD  = (109,  40, 217)  # #6D28D9 médio
PUR_DK  = (107,  33, 168)  # #6B21A8 escuro
GRAY_M  = (161, 161, 170)  # #A1A1AA cinza médio
WHITE   = (255, 255, 255)
W_SOFT  = (244, 244, 245)  # #F4F4F5 branco suave

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
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

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

# ── Gradiente roxo no texto (último headline) ─────────────────────
def grad_text(canvas, d, text, font, x, y, c1=PURPLE, c2=PUR_LT):
    bb = d.textbbox((0,0), text, font=font)
    lw = bb[2] - bb[0]
    y0 = y + bb[1]; y1 = y + bb[3]
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

# ── @ritmodamarca no topo ─────────────────────────────────────────
def paste_handle(canvas, x=52, y=44):
    d   = ImageDraw.Draw(canvas)
    fnt = F("bold", 22)
    # "@" em roxo, "ritmodamarca" em branco
    aw = tw(d, "@", fnt)
    d.text((x, y), "@", font=fnt, fill=PURPLE)
    d.text((x+aw, y), "ritmodamarca", font=fnt, fill=WHITE)
    # barra roxa embaixo
    total = tw(d, "@ritmodamarca", fnt)
    d.rectangle([x, y+fnt.size+8, x+total, y+fnt.size+12], fill=PURPLE)

# ── Separador roxo gradiente ──────────────────────────────────────
def sep_line(d, y, w=56):
    x = (W-w)//2
    for xi in range(w):
        c = lerp(PURPLE, PUR_LT, xi/max(1,w-1))
        d.line([(x+xi,y),(x+xi,y+5)], fill=c)
    return y+5

def draw_sub(canvas, d, text, y, fnt_sz=26, color=GRAY_M):
    if not text: return y
    fnt = F("regular", fnt_sz)
    lh  = int(fnt_sz*1.55)
    for line in wrap(d, text, fnt):
        lw = tw(d, line, fnt)
        d.text(((W-lw)//2, y), line, font=fnt, fill=color)
        y += lh
    return y

# ══════════════════════════════════════════════════════════════════
# SLIDE DE ABERTURA — background IA + smoky overlay roxo
# ══════════════════════════════════════════════════════════════════
def smoky_purple(img, top_s=160, bot_s=255, top_r=320, bot_r=800, blur=60):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    dv = ImageDraw.Draw(ov)
    IW, IH = img.size
    for y in range(top_r):
        a = int(top_s * (1 - y/top_r)**1.8)
        dv.line([(0,y),(IW,y)], fill=(5,0,10,a))
    for y in range(IH-1, IH-bot_r-1, -1):
        dist = IH - 1 - y
        a = int(bot_s * (1 - dist/bot_r)**0.55)
        dv.line([(0,y),(IW,y)], fill=(5,0,12,a))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    base = img.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

def darken_zone(canvas, y_top):
    """Dois passes: gradiente suave + camada sólida escura na zona de texto."""
    IH, IW = canvas.size[1], canvas.size[0]
    t = max(y_top - 200, 0)

    # Passe 1: gradiente suave de cima para baixo
    tz = Image.new("RGBA", canvas.size, (0,0,0,0))
    dz = ImageDraw.Draw(tz)
    for iy in range(t, IH):
        a = int(235 * ((iy-t)/max(1,IH-t))**0.45)
        dz.line([(0,iy),(IW,iy)], fill=(4,0,10,a))
    tz = tz.filter(ImageFilter.GaussianBlur(40))
    base = canvas.convert("RGBA"); base.alpha_composite(tz)
    canvas = base.convert("RGB")

    # Passe 2: retângulo sólido com bordas suavizadas na zona do texto
    pad = Image.new("RGBA", canvas.size, (0,0,0,0))
    dp  = ImageDraw.Draw(pad)
    dp.rectangle([0, y_top - 20, IW, IH], fill=(4, 0, 10, 200))
    pad = pad.filter(ImageFilter.GaussianBlur(24))
    base = canvas.convert("RGBA"); base.alpha_composite(pad)
    return base.convert("RGB")

def make_open_slide(bg_path, headlines, subtitle, out_path,
                    centering=(0.5,0.5), h_start=100, extra_fn=None,
                    badge=None):
    img    = Image.open(bg_path).convert("RGB")
    canvas = ImageOps.fit(img, (W,H), Image.LANCZOS, centering=centering)
    canvas = smoky_purple(canvas)
    paste_handle(canvas)
    d = ImageDraw.Draw(canvas)

    h_sz, fnt_h = fit_font(d, headlines, "black", h_start)
    lead   = int(h_sz * 1.08)
    fnt_s  = F("regular", 26)
    sub_ls = wrap(d, subtitle, fnt_s)
    sub_h  = len(sub_ls) * int(26*1.55)
    badge_h = 60 if badge else 0
    extra_h = 80 if extra_fn else 0
    block_h = badge_h + lead*len(headlines) + 20+5+18 + sub_h + extra_h
    y = max(H - 120 - block_h, 560)

    canvas = darken_zone(canvas, y)
    d = ImageDraw.Draw(canvas)

    # ── Badge de pilar ─────────────────────────────────────────────
    if badge:
        pill_w = tw(d, f"{badge['num']}  {badge['label']}", F("medium",13)) + 40
        pill_h = 34
        px     = (W - pill_w) // 2
        d.rounded_rectangle([px, y, px+pill_w, y+pill_h], radius=17, fill=(*PUR_DK,))
        d.rounded_rectangle([px, y, px+pill_w, y+pill_h], radius=17, outline=PURPLE, width=1)
        inner_x = px + 16
        d.text((inner_x, y+10), badge["num"], font=F("black",13), fill=PUR_LT)
        sep_x = inner_x + tw(d, badge["num"], F("black",13)) + 8
        d.line([(sep_x, y+8),(sep_x, y+pill_h-8)], fill=BG3, width=1)
        d.text((sep_x+8, y+10), badge["label"], font=F("medium",13), fill=GRAY_M)
        y += pill_h + 18

    for i, line in enumerate(headlines):
        lw = tw(d, line, fnt_h); x = (W-lw)//2
        if i == len(headlines)-1:
            canvas = grad_text(canvas, d, line, fnt_h, x, y)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((x, y), line, font=fnt_h, fill=WHITE)
        y += lead

    y += 20; y = sep_line(d, y) + 18
    y  = draw_sub(canvas, d, subtitle, y, fnt_sz=28, color=W_SOFT)
    if extra_fn: extra_fn(canvas, d, y)
    canvas.save(out_path); print(f"✓ {os.path.basename(out_path)}")


# ══════════════════════════════════════════════════════════════════
# SLIDE CLEAN — fundo escuro PIL + glow roxo sutil
# ══════════════════════════════════════════════════════════════════
def make_dark_bg():
    """Fundo clean: gradiente radial roxo sutil sobre #09090B."""
    canvas = Image.new("RGB", (W,H), BG1)
    glow   = Image.new("RGBA", (W,H), (0,0,0,0))
    dg     = ImageDraw.Draw(glow)
    cx, cy = W//2, H//2
    for r in range(500, 0, -4):
        t = r / 500
        a = int(38 * (1-t)**2.2)
        dg.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*PUR_DK, a))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(glow)
    return canvas.convert("RGB")

def make_clean_slide(headlines, subtitle, out_path, h_start=100,
                     badge=None, extra_fn=None):
    """
    badge: dict com {"num": "01", "label": "PILAR"} — badge de pilar
    """
    canvas = make_dark_bg()
    paste_handle(canvas)

    # borda sutil no topo
    d = ImageDraw.Draw(canvas)
    for xi in range(W):
        t = xi / (W-1)
        c = lerp(PUR_DK, PURPLE, t) if xi < W//2 else lerp(PURPLE, PUR_DK, (xi-W//2)/(W//2))
        d.line([(xi,0),(xi,3)], fill=c)

    d = ImageDraw.Draw(canvas)
    h_sz, fnt_h = fit_font(d, headlines, "black", h_start)
    lead = int(h_sz * 1.08)
    fnt_s  = F("regular", 26)
    sub_ls = wrap(d, subtitle, fnt_s)
    sub_h  = len(sub_ls)*int(26*1.55)

    badge_h = 72 if badge else 0
    extra_h = 80 if extra_fn else 0
    block_h = badge_h + lead*len(headlines) + 20+5+18 + sub_h + extra_h
    y = (H - block_h) // 2
    y = max(y, 160)

    # ── Badge de pilar ─────────────────────────────────────────────
    if badge:
        fnt_nb = F("black", 13)
        fnt_lb = F("medium", 13)
        num_txt = badge["num"]
        lbl_txt = badge["label"]
        pill_w  = tw(d, f"{num_txt}  {lbl_txt}", F("medium",13)) + 40
        pill_h  = 34
        px      = (W - pill_w) // 2
        # fundo pill roxo escuro
        d.rounded_rectangle([px, y, px+pill_w, y+pill_h], radius=17,
                             fill=(*PUR_DK, 255))
        # borda roxa
        d.rounded_rectangle([px, y, px+pill_w, y+pill_h], radius=17,
                             outline=PURPLE, width=1)
        # texto: número roxo claro + label cinza
        inner_x = px + 16
        d.text((inner_x, y+10), num_txt, font=F("black",13), fill=PUR_LT)
        sep_x = inner_x + tw(d, num_txt, F("black",13)) + 8
        d.line([(sep_x, y+8),(sep_x, y+pill_h-8)], fill=BG3, width=1)
        d.text((sep_x+8, y+10), lbl_txt, font=F("medium",13), fill=GRAY_M)
        y += pill_h + 22

    # ── Headlines ─────────────────────────────────────────────────
    for i, line in enumerate(headlines):
        lw = tw(d, line, fnt_h); x = (W-lw)//2
        if i == len(headlines)-1:
            canvas = grad_text(canvas, d, line, fnt_h, x, y)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((x, y), line, font=fnt_h, fill=WHITE)
        y += lead

    y += 20; y = sep_line(d, y) + 18
    y  = draw_sub(canvas, d, subtitle, y, fnt_sz=28, color=W_SOFT)
    if extra_fn: extra_fn(canvas, d, y)
    canvas.save(out_path); print(f"✓ {os.path.basename(out_path)}")


# ── Botões de engajamento ─────────────────────────────────────────
def btn_row(canvas, d, y, labels_colors, caption=""):
    fnt_b = F("bold", 28)
    btns  = [(lbl, col, tw(d,lbl,fnt_b)+52, th(d,lbl,fnt_b)+22)
             for lbl, col in labels_colors]
    total = sum(b[2] for b in btns) + 20*(len(btns)-1)
    bx    = (W-total)//2
    y2    = y + 14
    for lbl, col, bw, bh in btns:
        d.rounded_rectangle([bx,y2,bx+bw,y2+bh], radius=10, fill=col)
        d.text((bx+(bw-tw(d,lbl,fnt_b))//2, y2+(bh-th(d,lbl,fnt_b))//2),
               lbl, font=fnt_b, fill=WHITE)
        bx += bw + 20
    if caption:
        draw_sub(canvas, d, caption, y2+btns[0][3]+14)


OUT = "/home/user/WEB/carrossel-ritmo/slides"
BG  = "/home/user/WEB/carrossel-ritmo"
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
# CARROSSEL 1 — "SUA MARCA TEM RITMO OU TEM PRESSA?"
# ══════════════════════════════════════════════════════════════════

def c1_s01():
    make_open_slide(
        f"{BG}/bg_c1_s01.png",
        ["SUA MARCA TEM", "RITMO OU", "TEM PRESSA?"],
        "A resposta muda tudo sobre como você cresce.",
        f"{OUT}/c1_slide01.png",
        h_start=108,
    )

def c1_s02():
    make_open_slide(
        f"{BG}/bg_c1_s02.png",
        ["PRESSA É ANSIEDADE", "DISFARÇADA DE ESTRATÉGIA."],
        "Postar todo dia sem direção não é consistência. É ruído com calendário.",
        f"{OUT}/c1_slide02.png", h_start=84,
    )

def c1_s03():
    make_open_slide(
        f"{BG}/bg_c1_s03.png",
        ["RITMO NÃO É", "VELOCIDADE."],
        "É cadência. O ciclo certo de criar, distribuir e converter. Sem queimar a audiência.",
        f"{OUT}/c1_slide03.png", h_start=100,
    )

def c1_s04():
    make_open_slide(
        f"{BG}/bg_c1_s04.png",
        ["MARCAS QUE ESCALAM", "CONSTROEM ANTES DE ACELERAR."],
        "DNA claro. Posicionamento afiado. Sistema que repete resultado.",
        f"{OUT}/c1_slide04.png", h_start=84,
    )

def c1_s05():
    make_open_slide(
        f"{BG}/bg_c1_s05.png",
        ["QUAL É O", "RITMO DA SUA MARCA?"],
        "Comenta aqui. Conta como está o ritmo do seu negócio agora.",
        f"{OUT}/c1_slide05.png", h_start=100,
    )


# ══════════════════════════════════════════════════════════════════
# CARROSSEL 2 — "O COMPASSO QUE TRANSFORMA MARKETING EM PREVISIBILIDADE"
# ══════════════════════════════════════════════════════════════════

def c2_s01():
    make_open_slide(
        f"{BG}/bg_c2_s01.png",
        ["O COMPASSO", "QUE TRANSFORMA", "MARKETING EM", "PREVISIBILIDADE."],
        "3 pilares. 1 sistema. Resultado que se repete.",
        f"{OUT}/c2_slide01.png",
        h_start=96,
    )

def c2_s02():
    make_open_slide(
        f"{BG}/bg_c2_s02.png",
        ["DNA &", "POSICIONAMENTO."],
        "Sem clareza de quem você é e para quem fala, qualquer estratégia é desperdício.",
        f"{OUT}/c2_slide02.png", h_start=108,
        badge={"num": "01", "label": "PILAR"},
    )

def c2_s03():
    make_open_slide(
        f"{BG}/bg_c2_s03.png",
        ["TRÁFEGO", "& TRAÇÃO."],
        "Meta e Google só funcionam quando criativo e público estão alinhados ao posicionamento.",
        f"{OUT}/c2_slide03.png", h_start=112,
        badge={"num": "02", "label": "PILAR"},
    )

def c2_s04():
    make_open_slide(
        f"{BG}/bg_c2_s04.png",
        ["ECOSSISTEMA", "DE CONVERSÃO."],
        "CRM, automação e funil não são luxo. São o que transforma clique em cliente recorrente.",
        f"{OUT}/c2_slide04.png", h_start=108,
        badge={"num": "03", "label": "PILAR"},
    )

def c2_s05():
    make_open_slide(
        f"{BG}/bg_c2_s05.png",
        ["QUAL PILAR", "É SEU GARGALO?"],
        "Comenta o número: 01, 02 ou 03. A gente te diz o próximo passo.",
        f"{OUT}/c2_slide05.png", h_start=104,
    )


# ── Run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Carrossel 1: Sua marca tem ritmo ou tem pressa? ===")
    c1_s01(); c1_s02(); c1_s03(); c1_s04(); c1_s05()
    print("\n=== Carrossel 2: O compasso que transforma marketing ===")
    c2_s01(); c2_s02(); c2_s03(); c2_s04(); c2_s05()
    print(f"\nDone → {OUT}")
