#!/usr/bin/env python3
"""PMI Social Manager — 5 Ad Pieces. Consistent brand identity."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

OUT = "/home/user/WEB/pmi-social-ads/out"
os.makedirs(OUT, exist_ok=True)

# ── Brand Colors ──────────────────────────────────────────────────────────────
PURPLE    = (123, 47, 255)    # #7B2FFF  primary
PINK      = (236, 72, 153)    # #EC4899  accent
PURPLE_LT = (139, 92, 246)    # #8B5CF6  gradient start
BLACK     = (10, 10, 10)      # #0A0A0A
WHITE     = (255, 255, 255)
GRAY_BG   = (248, 248, 248)   # #F8F8F8  light bg
GRAY_TEXT = (85, 85, 85)      # #555     light-mode body
GRAY_BODY = (176, 176, 176)   # #B0B0B0  dark-mode body
TEXT_DARK = (17, 17, 17)      # #111     headlines on light

# ── Fonts ─────────────────────────────────────────────────────────────────────
R = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"

def F(style, size):
    return ImageFont.truetype({
        "black":   f"{R}/Roboto-Black.ttf",
        "bold":    f"{R}/Roboto-Bold.ttf",
        "medium":  f"{R}/Roboto-Medium.ttf",
        "regular": f"{R}/Roboto-Regular.ttf",
        "light":   f"{R}/Roboto-Light.ttf",
    }[style], size)

# ── Color helpers ─────────────────────────────────────────────────────────────
def lerp(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def grad_h(d, x1, y1, x2, y2, c1, c2):
    for i in range(x2 - x1):
        d.line([(x1+i, y1), (x1+i, y2)], fill=lerp(c1, c2, i / max(1, x2-x1-1)))

def grad_v(d, x1, y1, x2, y2, c1, c2):
    for i in range(y2 - y1):
        d.line([(x1, y1+i), (x2, y1+i)], fill=lerp(c1, c2, i / max(1, y2-y1-1)))

def grad_diag_bg(W, H, c1, c2):
    """Diagonal gradient background."""
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        for x in range(0, W, 4):
            t = (x/W * 0.4 + y/H * 0.6)
            d.line([(x, y), (min(x+4, W), y)], fill=lerp(c1, c2, t))
    return img

# ── Effect helpers ────────────────────────────────────────────────────────────
def glow(img, cx, cy, radius, color, opacity=0.14):
    lay = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(lay)
    for r in range(radius, 0, -12):
        a = int(opacity * 255 * (1 - r/radius) ** 0.5)
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*color, a))
    lay = lay.filter(ImageFilter.GaussianBlur(radius // 5))
    base = img.convert("RGBA")
    base.alpha_composite(lay)
    return base.convert("RGB")

def grid(img, color=PURPLE, opacity=0.05, spacing=72):
    W, H = img.size
    lay = Image.new("RGBA", (W, H), (0,0,0,0))
    d = ImageDraw.Draw(lay)
    a = int(opacity * 255)
    for x in range(0, W, spacing):
        d.line([(x,0),(x,H)], fill=(*color, a), width=1)
    for y in range(0, H, spacing):
        d.line([(0,y),(W,y)], fill=(*color, a), width=1)
    base = img.convert("RGBA")
    base.alpha_composite(lay)
    return base.convert("RGB")

def vignette(img, strength=0.4):
    W, H = img.size
    lay = Image.new("RGBA", (W, H), (0,0,0,0))
    d = ImageDraw.Draw(lay)
    steps = 30
    for i in range(steps, 0, -1):
        r_w = int(W * i / steps)
        r_h = int(H * i / steps)
        a = int(strength * 255 * (1 - i/steps) ** 1.5)
        d.rectangle([W//2-r_w, H//2-r_h, W//2+r_w, H//2+r_h], outline=(0,0,0,a), width=3)
    lay = lay.filter(ImageFilter.GaussianBlur(40))
    base = img.convert("RGBA")
    base.alpha_composite(lay)
    return base.convert("RGB")

# ── Typography helpers ────────────────────────────────────────────────────────
def wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textbbox((0,0), test, font=font)[2] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def text_w(d, text, font):
    bb = d.textbbox((0,0), text, font=font)
    return bb[2] - bb[0]

def text_h(d, text, font):
    bb = d.textbbox((0,0), text, font=font)
    return bb[3] - bb[1]

def draw_left(d, text, font, x, y, color, max_w=None, leading=1.35):
    if max_w:
        lines = wrap(d, text, font, max_w)
    else:
        lines = [text]
    lh = int(font.size * leading)
    for line in lines:
        d.text((x, y), line, font=font, fill=color)
        y += lh
    return y

def draw_center(d, text, font, W, y, color, max_w=None, leading=1.35):
    lines = wrap(d, text, font, max_w or W) if max_w else [text]
    lh = int(font.size * leading)
    for line in lines:
        lw = text_w(d, line, font)
        d.text(((W - lw)//2, y), line, font=font, fill=color)
        y += lh
    return y

# ── Logo ──────────────────────────────────────────────────────────────────────
def logo_left(d, x, y, size=42, on_dark=True):
    """PMI. + Social Manager — left-anchored."""
    fg    = WHITE if on_dark else TEXT_DARK
    sub_c = (160, 155, 175) if on_dark else (110, 105, 120)
    f = F("black", size)
    fs = F("medium", int(size * 0.36))
    pmi_w = text_w(d, "PMI", f)
    d.text((x, y), "PMI", font=f, fill=fg)
    d.text((x + pmi_w, y), ".", font=f, fill=PURPLE)
    sh = text_h(d, "PMI", f)
    d.text((x, y + sh + 2), "Social Manager", font=fs, fill=sub_c)

def logo_center(d, W, y, size=40, on_dark=True):
    """PMI. + Social Manager — centered."""
    fg    = WHITE if on_dark else TEXT_DARK
    sub_c = (160, 155, 175) if on_dark else (110, 105, 120)
    f = F("black", size)
    fs = F("medium", int(size * 0.36))
    pmi_w = text_w(d, "PMI", f)
    dot_w = text_w(d, ".", f)
    total = pmi_w + dot_w
    x = (W - total) // 2
    d.text((x, y), "PMI", font=f, fill=fg)
    d.text((x + pmi_w, y), ".", font=f, fill=PURPLE)
    sh = text_h(d, "PMI", f)
    sm_w = text_w(d, "Social Manager", fs)
    d.text(((W - sm_w)//2, y + sh + 2), "Social Manager", font=fs, fill=sub_c)

# ── Buttons ───────────────────────────────────────────────────────────────────
def btn_solid(d, x, y, text, font, W_max=None, color=PURPLE, pad_x=36, pad_y=16):
    tw = text_w(d, text, font)
    th = text_h(d, text, font)
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    d.rounded_rectangle([x, y, x+bw, y+bh], radius=10, fill=color)
    d.text((x + pad_x, y + pad_y), text, font=font, fill=WHITE)
    return y + bh

def btn_gradient(d, cx, y, text, font, W, pad_x=40, pad_y=16):
    tw = text_w(d, text, font)
    th = text_h(d, text, font)
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    x = cx - bw // 2
    grad_h(d, x, y, x+bw, y+bh, PURPLE_LT, PINK)
    # rounded corner overlay
    d.rounded_rectangle([x, y, x+bw, y+bh], radius=10, outline=None)
    d.text((x + pad_x, y + pad_y), text, font=font, fill=WHITE)
    return y + bh

# ── Checkmark icon ─────────────────────────────────────────────────────────────
def checkmark(d, cx, cy, r=16, color=PURPLE):
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
    d.line([(cx-r*0.38, cy+r*0.05), (cx-r*0.05, cy+r*0.42)], fill=WHITE, width=max(2, r//6))
    d.line([(cx-r*0.05, cy+r*0.42), (cx+r*0.42, cy-r*0.30)], fill=WHITE, width=max(2, r//6))


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 1 — GRATUITO · LIGHT · 1080x1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_01():
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), GRAY_BG)
    d = ImageDraw.Draw(img)

    # Top gradient bar
    grad_h(d, 0, 0, W, 7, PURPLE_LT, PINK)

    # Decorative large circle background (bottom-right, very subtle)
    lay = Image.new("RGBA", (W, H), (0,0,0,0))
    dl = ImageDraw.Draw(lay)
    for r in range(500, 0, -20):
        a = int(18 * (1 - r/500)**0.8)
        dl.ellipse([W-r+60, H-r+60, W+r+60, H+r+60], fill=(*PURPLE_LT, a))
    lay = lay.filter(ImageFilter.GaussianBlur(50))
    img = img.convert("RGBA"); img.alpha_composite(lay); img = img.convert("RGB")
    d = ImageDraw.Draw(img)

    # Logo top-left
    logo_left(d, 56, 36, size=42, on_dark=False)

    # GRATUITO badge — top right
    f_badge = F("bold", 22)
    badge = "GRATUITO"
    bw = text_w(d, badge, f_badge) + 30
    bh = text_h(d, badge, f_badge) + 14
    bx, by = W - 56 - bw, 42
    grad_h(d, bx, by, bx+bw, by+bh, PURPLE_LT, PINK)
    d.text((bx + 15, by + 7), badge, font=f_badge, fill=WHITE)

    # ── Content ─────────────────────────────────────────────────────────────
    col_text  = 56
    col_card  = W - 320
    col_text_w = col_card - col_text - 48
    y = 148

    # Headline
    f_h = F("black", 54)
    headline = "Agências que crescem sem contratar mais ninguém têm uma coisa em comum."
    hl_lines = wrap(d, headline, f_h, col_text_w)
    lh_h = int(54 * 1.1)
    for line in hl_lines:
        d.text((col_text, y), line, font=f_h, fill=TEXT_DARK)
        y += lh_h
    y += 10

    # Accent line
    d.rectangle([col_text, y, col_text + 56, y + 4], fill=PURPLE)
    y += 24

    # Body
    f_body = F("regular", 28)
    f_emph = F("bold", 28)
    items = [
        ("Não é o número de clientes.", False),
        ("Não é o time maior.", False),
        ("", False),
        ("É controle.", True),
        ("", False),
        ("Relatórios que o cliente entende, conteúdo no horário certo e inbox sem mensagem perdida — sem planilha, sem post-it.", False),
    ]
    for text, emph in items:
        if not text:
            y += 10
            continue
        f = f_emph if emph else f_body
        c = PURPLE if emph else GRAY_TEXT
        y = draw_left(d, text, f, col_text, y, c, max_w=col_text_w, leading=1.38)

    y += 12
    # Sub-CTA text
    f_sub = F("medium", 26)
    y = draw_left(d, "Checklist gratuito de gestão para agências que querem atender mais com a mesma equipe.", f_sub, col_text, y, TEXT_DARK, max_w=col_text_w, leading=1.4)

    y += 20
    # CTA button
    f_cta = F("bold", 24)
    btn_solid(d, col_text, y, "Acesse e veja onde sua operacao esta vazando →", f_cta, color=PURPLE)

    # ── Checklist card (right column) ────────────────────────────────────────
    items_check = [
        "Relatorios automaticos",
        "Agendamento inteligente",
        "Inbox unificado",
        "IA para legendas",
        "Dashboard por cliente",
        "Aprovacao de conteudo",
    ]
    card_x = col_card
    card_y = 148
    card_w = W - col_card - 40
    card_h = len(items_check) * 64 + 36

    # White card with subtle border
    d.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+card_h],
                         radius=16, fill=WHITE)
    d.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+card_h],
                         radius=16, outline=(220, 215, 235), width=2)
    # Top accent bar on card
    grad_h(d, card_x, card_y, card_x+card_w, card_y+5, PURPLE_LT, PINK)
    d.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+5], radius=4, outline=None)

    for i, item in enumerate(items_check):
        cy_item = card_y + 30 + i * 64 + 16
        checkmark(d, card_x + 28, cy_item, r=16, color=PURPLE)
        d.text((card_x + 54, cy_item - 12), item, font=F("medium", 22), fill=TEXT_DARK)

    img.save(f"{OUT}/peca_01.png")
    print(f"✓ peca_01 — GRATUITO · 1080x1080")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 2 — PAGO / A · DARK · 1080x1350
# ══════════════════════════════════════════════════════════════════════════════
def peca_02():
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), BLACK)
    img = glow(img, W//2, int(H*0.38), 560, PURPLE, opacity=0.13)
    img = grid(img, PURPLE, opacity=0.05, spacing=72)
    d = ImageDraw.Draw(img)

    # Top bar
    grad_h(d, 0, 0, W, 6, PURPLE_LT, PINK)

    # Logo top-left
    logo_left(d, 56, 36, size=42, on_dark=True)

    # ── Dashboard mockup ─────────────────────────────────────────────────────
    mx, my = 64, 148
    mw, mh = W - 128, 390

    # Outer glow
    lay = Image.new("RGBA", (W, H), (0,0,0,0))
    dl = ImageDraw.Draw(lay)
    for r in range(80, 0, -4):
        a = int(50 * (1 - r/80))
        dl.rounded_rectangle([mx-r//2, my-r//2, mx+mw+r//2, my+mh+r//2],
                               radius=20+r//3, outline=(*PURPLE, a), width=2)
    lay = lay.filter(ImageFilter.GaussianBlur(12))
    img = img.convert("RGBA"); img.alpha_composite(lay); img = img.convert("RGB")
    d = ImageDraw.Draw(img)

    # Dashboard frame
    d.rounded_rectangle([mx, my, mx+mw, my+mh], radius=16,
                         fill=(18, 10, 36), outline=(70, 35, 140), width=2)

    # Header bar (gradient)
    grad_h(d, mx, my, mx+mw, my+48, PURPLE_LT, PINK)
    d.text((mx+18, my+12), "PMI Social Manager", font=F("bold", 22), fill=WHITE)
    # Circles for dots
    for i, c in enumerate([(255,100,100),(255,200,60),(100,220,100)]):
        d.ellipse([mx+mw-70+i*22, my+18, mx+mw-56+i*22, my+32], fill=c)

    # Metric cards
    n_cards = 4
    cpad = 10
    cw   = (mw - (n_cards+1)*cpad) // n_cards
    ch   = 88
    cards = [("12","Contas ativas"),("847","Posts agend."),("99%","Entrega"),("5h+","Economizado")]
    for i, (val, lbl) in enumerate(cards):
        cx = mx + cpad + i*(cw+cpad)
        cy = my + 58
        d.rounded_rectangle([cx, cy, cx+cw, cy+ch], radius=10, fill=(26, 14, 52))
        grad_h(d, cx, cy, cx+cw, cy+4, PURPLE_LT, PINK)
        d.text((cx+12, cy+12), val, font=F("black", 30), fill=WHITE)
        d.text((cx+12, cy+52), lbl, font=F("regular", 16), fill=(150, 135, 175))

    # Account rows
    row_y = my + 160
    for i in range(4):
        ry = row_y + i * 50
        c = lerp(PURPLE_LT, PINK, i/3)
        d.ellipse([mx+cpad, ry+6, mx+cpad+34, ry+40], fill=c)
        d.text((mx+cpad+44, ry+4), f"@cliente_0{i+1}", font=F("medium", 18), fill=WHITE)
        d.text((mx+cpad+44, ry+28), "Ativo  ·  3 posts agendados  ·  Proximo: 18h", font=F("regular", 14), fill=(130, 120, 155))
        d.ellipse([mx+mw-28, ry+14, mx+mw-12, ry+30], fill=(40, 220, 110))

    # ── Text content ─────────────────────────────────────────────────────────
    y = my + mh + 48

    f_h = F("black", 74)
    d.text((56, y), "Chega de gerenciar", font=f_h, fill=WHITE)
    y += 85
    d.text((56, y), "Instagram no grito.", font=f_h, fill=WHITE)
    y += 100

    f_body = F("regular", 30)
    body = "Agendar post. Responder DM. Gerar relatorio. Criar legenda. Tudo isso todo dia. Pra todo cliente. O PMI reune tudo em um unico lugar — o que tomava horas passa a tomar minutos."
    y = draw_left(d, body, f_body, 56, y, GRAY_BODY, max_w=W-112, leading=1.52)

    y += 34
    f_cta = F("bold", 26)
    btn_solid(d, 56, y, "Comece agora e teste sem risco →", f_cta, color=PURPLE)

    img.save(f"{OUT}/peca_02.png")
    print(f"✓ peca_02 — Pago A · 1080x1350")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 3 — PAGO / B · DARK GRADIENT · 1080x1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_03():
    W, H = 1080, 1080
    # Vertical gradient bg
    img = Image.new("RGB", (W, H))
    d_bg = ImageDraw.Draw(img)
    grad_v(d_bg, 0, 0, W, H, (12, 6, 28), (6, 3, 16))
    img = glow(img, W//2, H//2, 620, PURPLE, opacity=0.16)
    img = grid(img, PURPLE, opacity=0.04, spacing=88)
    d = ImageDraw.Draw(img)

    # ── Headline top ──────────────────────────────────────────────────────────
    y = 52
    f_h = F("black", 50)
    hl = "Quanto tempo voce perde fazendo o que a IA faria em 10 segundos?"
    for line in wrap(d, hl, f_h, W-112):
        lw = text_w(d, line, f_h)
        d.text(((W-lw)//2, y), line, font=f_h, fill=WHITE)
        y += 58
    y += 20

    # ── 700+ hero number ──────────────────────────────────────────────────────
    f_big = F("black", 210)
    num = "700+"
    nw = text_w(d, num, f_big)
    nh = text_h(d, num, f_big)
    nx = (W - nw) // 2
    ny = y

    # Glow behind number
    img = glow(img, W//2, ny + nh//2, 340, PURPLE, opacity=0.22)
    d = ImageDraw.Draw(img)

    # Number in gradient — draw left half in PURPLE_LT, right in PINK, blend
    # Simple approach: draw in PURPLE_LT then blend right portion
    d.text((nx, ny), num, font=f_big, fill=PURPLE_LT)
    # Overlay right half in PINK using line-by-line
    for xi in range(nx + nw//2, nx + nw):
        t = (xi - (nx + nw//2)) / max(1, nw//2)
        c = lerp(PURPLE_LT, PINK, t)
        d.line([(xi, ny), (xi, ny + nh)], fill=c)
    # Re-draw text clipped — use PINK for the second draw to tint right side
    # Simpler: just redraw full text in gradient via a separate layer
    num_lay = Image.new("RGBA", (W, H), (0,0,0,0))
    dn = ImageDraw.Draw(num_lay)
    dn.text((nx, ny), num, font=f_big, fill=(*PURPLE_LT, 255))
    # Gradient tint layer
    tint = Image.new("RGBA", (W, H), (0,0,0,0))
    dt = ImageDraw.Draw(tint)
    for xi in range(nx, nx+nw):
        t = (xi - nx) / max(1, nw)
        c = lerp(PURPLE_LT, PINK, t)
        dt.line([(xi, ny), (xi, ny+nh)], fill=(*c, 255))
    # Mask tint to text alpha
    r,g,b,a_ch = num_lay.split()
    tint.putalpha(a_ch)
    img = img.convert("RGBA")
    img.alpha_composite(tint)
    img = img.convert("RGB")
    d = ImageDraw.Draw(img)

    y = ny + nh - 10

    # Label below number
    f_lbl = F("medium", 30)
    lbl = "profissionais ja economizam horas por semana com o PMI"
    lw = text_w(d, lbl, f_lbl)
    d.text(((W-lw)//2, y), lbl, font=f_lbl, fill=GRAY_BODY)
    y += 52

    # ── Avatars row ───────────────────────────────────────────────────────────
    n_av = 9
    av_r = 26
    av_gap = 6
    total_av = n_av * (av_r*2 + av_gap) - av_gap
    av_x = (W - total_av) // 2
    av_y = y + av_r
    initials = list("ABCDEFGHI")
    for i in range(n_av):
        ax = av_x + i * (av_r*2 + av_gap) + av_r
        c = lerp(PURPLE_LT, PINK, i/(n_av-1))
        # Overlap effect
        d.ellipse([ax-av_r-2, av_y-av_r-2, ax+av_r+2, av_y+av_r+2], fill=(12, 6, 24))
        d.ellipse([ax-av_r, av_y-av_r, ax+av_r, av_y+av_r], fill=c)
        f_init = F("bold", 20)
        iw = text_w(d, initials[i], f_init)
        ih = text_h(d, initials[i], f_init)
        d.text((ax-iw//2, av_y-ih//2-2), initials[i], font=f_init, fill=WHITE)
    y = av_y + av_r + 36

    # ── Body text ────────────────────────────────────────────────────────────
    f_body = F("regular", 28)
    body = "Gestores que usam o PMI criam a legenda de uma semana inteira em menos de 5 minutos, automatizam respostas e entregam relatorios com a marca da agencia."
    y = draw_center(d, body, f_body, W, y, GRAY_BODY, max_w=W-112, leading=1.52)
    y += 26

    # CTA gradient button
    f_cta = F("bold", 26)
    cta = "Veja como funciona e comece hoje →"
    cw_btn = text_w(d, cta, f_cta) + 80
    bx = (W - cw_btn) // 2
    grad_h(d, bx, y, bx+cw_btn, y+54, PURPLE_LT, PINK)
    d.text((bx + 40, y + 13), cta, font=f_cta, fill=WHITE)
    y += 68

    # Logo bottom center
    logo_center(d, W, y, size=36, on_dark=True)

    img.save(f"{OUT}/peca_03.png")
    print(f"✓ peca_03 — Pago B · 1080x1080")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 4 — PAGO / C · DARK · HUB DIAGRAM · 1080x1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_04():
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), BLACK)
    img = glow(img, W//2, H//2, 540, PURPLE, opacity=0.11)
    img = grid(img, PURPLE, opacity=0.05, spacing=72)
    d = ImageDraw.Draw(img)

    # ── Headline top ──────────────────────────────────────────────────────────
    y = 52
    f_h = F("black", 54)
    hl1 = "Sua agencia ainda usa uma ferramenta"
    hl2 = "diferente pra cada coisa?"
    for line in [hl1, hl2]:
        lw = text_w(d, line, f_h)
        d.text(((W-lw)//2, y), line, font=f_h, fill=WHITE)
        y += 64
    y += 8

    # ── Hub diagram ───────────────────────────────────────────────────────────
    hub_cx = W // 2
    hub_cy = y + 220
    hub_r  = 68
    spoke  = 195
    node_r = 54

    tools = [
        ("Agendamento", 270),   # top
        ("Inbox",        342),  # top-right
        ("Relatorio",    54),   # right  (was 54 → actually these are degrees from top)
        ("Criativo",     126),  # bottom-right
        ("Legenda IA",   198),  # bottom-left
    ]
    # Remap angles: start at top (270°) going clockwise
    angles_deg = [270, 342, 54, 126, 198]
    tool_labels = ["Agendamento", "Inbox", "Relatorio", "Criativo", "Legenda IA"]

    # Spokes and nodes
    for label, ang in zip(tool_labels, angles_deg):
        rad = math.radians(ang)
        nx = hub_cx + int(spoke * math.cos(rad))
        ny = hub_cy + int(spoke * math.sin(rad))

        # Dashed spoke
        dx = nx - hub_cx; dy = ny - hub_cy
        length = math.sqrt(dx*dx + dy*dy)
        ux, uy = dx/length, dy/length
        pos = hub_r + 4
        while pos < length - node_r - 4:
            sx = hub_cx + ux*pos
            sy = hub_cy + uy*pos
            ex = hub_cx + ux*(pos+14)
            ey = hub_cy + uy*(pos+14)
            d.line([(sx, sy), (ex, ey)], fill=(70, 35, 120), width=2)
            # Moving dot
            mid = pos + 7
            mx_ = hub_cx + ux*mid; my_ = hub_cy + uy*mid
            d.ellipse([mx_-4, my_-4, mx_+4, my_+4], fill=PURPLE)
            pos += 22

        # Node outer glow
        lay = Image.new("RGBA", (W, H), (0,0,0,0))
        dl = ImageDraw.Draw(lay)
        for r in range(node_r+20, node_r, -2):
            a = int(40 * (1-(r-node_r)/20))
            dl.ellipse([nx-r, ny-r, nx+r, ny+r], fill=(*PURPLE, a))
        img = img.convert("RGBA"); img.alpha_composite(lay); img = img.convert("RGB")
        d = ImageDraw.Draw(img)

        # Node
        d.ellipse([nx-node_r, ny-node_r, nx+node_r, ny+node_r],
                  fill=(22, 10, 46), outline=(80, 40, 150), width=2)
        # Node label
        f_node = F("medium", 19)
        lines_n = label.split()
        for li, ln in enumerate(lines_n[:2]):
            lw = text_w(d, ln, f_node)
            d.text((nx-lw//2, ny-14+li*24), ln, font=f_node, fill=GRAY_BODY)

    # Hub glow
    for r in range(hub_r+60, hub_r-1, -4):
        a = int(55 * (1-(r-hub_r)/60) ** 1.2)
        lay2 = Image.new("RGBA", (W, H), (0,0,0,0))
        dl2 = ImageDraw.Draw(lay2)
        dl2.ellipse([hub_cx-r, hub_cy-r, hub_cx+r, hub_cy+r], fill=(*PURPLE, a))
        img = img.convert("RGBA"); img.alpha_composite(lay2); img = img.convert("RGB")
    d = ImageDraw.Draw(img)

    # Hub circle — gradient fill
    for xi in range(hub_cx-hub_r, hub_cx+hub_r):
        t = (xi-(hub_cx-hub_r))/(hub_r*2)
        c = lerp(PURPLE_LT, PINK, t)
        h_at = int(math.sqrt(max(0, hub_r**2-(xi-hub_cx)**2)))
        d.line([(xi, hub_cy-h_at), (xi, hub_cy+h_at)], fill=c)

    # PMI. in hub
    f_hub_main = F("black", 28)
    f_hub_sub  = F("medium", 15)
    pmi_w = text_w(d, "PMI", f_hub_main)
    dot_w = text_w(d, ".", f_hub_main)
    total = pmi_w + dot_w
    d.text((hub_cx-total//2, hub_cy-20), "PMI", font=f_hub_main, fill=WHITE)
    d.text((hub_cx-total//2+pmi_w, hub_cy-20), ".", font=f_hub_main, fill=(30, 12, 60))
    sm_w = text_w(d, "Social", f_hub_sub)
    d.text((hub_cx-sm_w//2, hub_cy+14), "Social", font=f_hub_sub, fill=WHITE)

    # ── Body + CTA ────────────────────────────────────────────────────────────
    y_body = hub_cy + spoke + node_r + 32
    f_body = F("regular", 27)
    body = "O plano Agency do PMI fecha tudo em um unico lugar — multiplos clientes, relatorios com sua marca, IA ilimitada e criativos para Meta Ads."
    y_body = draw_center(d, body, f_body, W, y_body, GRAY_BODY, max_w=W-112, leading=1.5)

    y_body += 22
    f_cta = F("bold", 24)
    cta = "Fale com a gente e monte sua operacao →"
    cw_btn = text_w(d, cta, f_cta) + 64
    bx = (W - cw_btn) // 2
    btn_solid(d, bx, y_body, cta, f_cta, color=PURPLE)
    y_body += text_h(d, cta, f_cta) + 36 + 32 + 22

    logo_center(d, W, y_body, size=34, on_dark=True)

    img.save(f"{OUT}/peca_04.png")
    print(f"✓ peca_04 — Pago C · Hub · 1080x1080")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 5 — STORY · 1080x1920 · GRADIENT
# ══════════════════════════════════════════════════════════════════════════════
def peca_05():
    W, H = 1080, 1920

    # Diagonal gradient bg
    img = grad_diag_bg(W, H, BLACK, (45, 10, 107))
    img = glow(img, W//2, H//2, 700, PURPLE, opacity=0.13)
    img = grid(img, PURPLE, opacity=0.04, spacing=88)
    img = vignette(img, strength=0.35)
    d = ImageDraw.Draw(img)

    # Top bar
    grad_h(d, 0, 0, W, 7, PURPLE_LT, PINK)

    # Logo top centered
    logo_center(d, W, 52, size=46, on_dark=True)

    # ── Headline ─────────────────────────────────────────────────────────────
    y = 210
    f_h = F("black", 114)
    for line in ["Tudo que sua", "agencia precisa."]:
        lw = text_w(d, line, f_h)
        d.text(((W-lw)//2, y), line, font=f_h, fill=WHITE)
        y += 128
    y += 10

    # Subtitle
    f_sub = F("regular", 38)
    for line in ["Agendamento. IA. Relatorios. Inbox.", "Uma plataforma. Zero baguna."]:
        lw = text_w(d, line, f_sub)
        d.text(((W-lw)//2, y), line, font=f_sub, fill=GRAY_BODY)
        y += 52
    y += 44

    # ── Phone mockup ──────────────────────────────────────────────────────────
    ph_w, ph_h = 440, 780
    ph_x = (W - ph_w) // 2
    ph_y = y
    ph_r  = 44

    # Phone glow
    lay = Image.new("RGBA", (W, H), (0,0,0,0))
    dl = ImageDraw.Draw(lay)
    for r in range(100, 0, -5):
        a = int(60 * (1-r/100))
        dl.rounded_rectangle([ph_x-r//2, ph_y-r//2, ph_x+ph_w+r//2, ph_y+ph_h+r//2],
                               radius=ph_r+r//3, outline=(*PURPLE, a), width=2)
    lay = lay.filter(ImageFilter.GaussianBlur(16))
    img = img.convert("RGBA"); img.alpha_composite(lay); img = img.convert("RGB")
    d = ImageDraw.Draw(img)

    # Phone shell
    d.rounded_rectangle([ph_x, ph_y, ph_x+ph_w, ph_y+ph_h],
                         radius=ph_r, fill=(16, 7, 34), outline=(85, 45, 155), width=3)

    # Camera notch
    d.ellipse([ph_x+ph_w//2-14, ph_y+12, ph_x+ph_w//2+14, ph_y+34], fill=(8, 4, 18))

    # Screen
    scr_pad = 16
    scr_x = ph_x + scr_pad
    scr_y = ph_y + scr_pad + 30
    scr_w = ph_w - scr_pad*2
    scr_h = ph_h - scr_pad*2 - 30
    grad_v(d, scr_x, scr_y, scr_x+scr_w, scr_y+scr_h, (22, 8, 52), (44, 6, 92))

    # Screen header gradient bar
    grad_h(d, scr_x, scr_y, scr_x+scr_w, scr_y+38, PURPLE_LT, PINK)
    d.text((scr_x+10, scr_y+9), "PMI Social Manager", font=F("bold", 15), fill=WHITE)

    # Metric mini-cards
    mc_y = scr_y + 48
    mc_w = (scr_w - 8) // 2
    mc_data = [("12","Contas"),("847","Posts"),("99%","Entrega"),("5h","Economizado")]
    for i, (val, lbl) in enumerate(mc_data):
        mx2 = scr_x + (i%2) * (mc_w+4)
        my2 = mc_y + (i//2) * 76
        d.rounded_rectangle([mx2, my2, mx2+mc_w, my2+66], radius=8, fill=(32, 12, 64))
        grad_h(d, mx2, my2, mx2+mc_w, my2+3, PURPLE_LT, PINK)
        d.text((mx2+8, my2+8), val, font=F("black", 22), fill=WHITE)
        d.text((mx2+8, my2+38), lbl, font=F("regular", 13), fill=(140, 120, 175))

    # Account rows
    row_y = mc_y + 162
    for i in range(5):
        ry = row_y + i*46
        c = lerp(PURPLE_LT, PINK, i/4)
        d.ellipse([scr_x+4, ry, scr_x+36, ry+32], fill=c)
        d.text((scr_x+44, ry+2),  f"@cliente_0{i+1}", font=F("medium", 14), fill=WHITE)
        d.text((scr_x+44, ry+22), "3 posts agendados", font=F("regular", 12), fill=(120,100,150))
        d.ellipse([scr_x+scr_w-22, ry+10, scr_x+scr_w-8, ry+24], fill=(30, 220, 100))

    # ── Below phone ──────────────────────────────────────────────────────────
    y_bot = ph_y + ph_h + 54
    f_tag = F("medium", 34)
    tag = "Para agencias e gestores de social media."
    lw = text_w(d, tag, f_tag)
    d.text(((W-lw)//2, y_bot), tag, font=f_tag, fill=GRAY_BODY)
    y_bot += 52

    # Feature pills
    pills = ["IA generativa", "Inbox unificado", "Relatorios white-label", "Meta Ads"]
    pill_x = 56
    pill_y = y_bot
    for pill in pills:
        f_pill = F("medium", 22)
        pw = text_w(d, pill, f_pill) + 30
        ph2 = text_h(d, pill, f_pill) + 14
        if pill_x + pw > W - 56:
            pill_x = 56
            pill_y += ph2 + 10
        d.rounded_rectangle([pill_x, pill_y, pill_x+pw, pill_y+ph2],
                             radius=20, outline=PURPLE, width=2, fill=(30, 10, 60))
        d.text((pill_x+15, pill_y+7), pill, font=f_pill, fill=WHITE)
        pill_x += pw + 12
    y_bot = pill_y + text_h(d, pills[0], F("medium", 22)) + 14 + 36

    # CTA gradient button
    f_cta = F("bold", 32)
    cta = "Conheca o PMI Social Manager"
    cw_btn = text_w(d, cta, f_cta) + 80
    bx = (W - cw_btn) // 2
    grad_h(d, bx, y_bot, bx+cw_btn, y_bot+58, PURPLE_LT, PINK)
    d.text((bx+40, y_bot+13), cta, font=f_cta, fill=WHITE)

    img.save(f"{OUT}/peca_05.png")
    print(f"✓ peca_05 — Story · 1080x1920")


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    peca_01()
    peca_02()
    peca_03()
    peca_04()
    peca_05()
    print(f"\nAll 5 pieces saved → {OUT}")
