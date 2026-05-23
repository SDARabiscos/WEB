#!/usr/bin/env python3
"""PMI — Posts sábado. Layouts variados: hero stat, split, left-align, lista, CTA."""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os

W, H   = 1080, 1350
MARGIN = 64
MAX_W  = W - MARGIN * 2

VIOLET = (134,   0, 255)
VLT    = (160,  60, 255)
PINK   = (236,  72, 153)
WHITE  = (255, 255, 255)
OFFWHT = (230, 225, 240)
DARK   = (  8,   6,  14)
CARD   = ( 22,  18,  34)
GRAY   = (160, 155, 175)

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

def tw(d, t, f): bb=d.textbbox((0,0),t,font=f); return bb[2]-bb[0]
def th(d, t, f): bb=d.textbbox((0,0),t,font=f); return bb[3]-bb[1]

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

def fit_font(d, lines, style, start=100, min_sz=44):
    sz = start
    while sz >= min_sz:
        f = F(style, sz)
        if all(tw(d, ln, f) <= MAX_W for ln in lines): return sz, f
        sz -= 4
    return min_sz, F(style, min_sz)

# ── Gradiente VLT → PINK num texto ───────────────────────────────
def grad_text(canvas, d, text, font, x, y, c1=VLT, c2=PINK):
    bb  = d.textbbox((0,0), text, font=font)
    lw  = bb[2]-bb[0]; y0 = y+bb[1]; y1 = y+bb[3]
    lay = Image.new("RGBA", canvas.size, (0,0,0,0))
    ImageDraw.Draw(lay).text((x,y), text, font=font, fill=(*c1,255))
    tint = Image.new("RGBA", canvas.size, (0,0,0,0))
    dt   = ImageDraw.Draw(tint)
    for xi in range(x, x+lw):
        c = lerp(c1, c2, (xi-x)/max(1,lw-1))
        dt.line([(xi,y0),(xi,y1)], fill=(*c,255))
    _,_,_,a = lay.split(); tint.putalpha(a)
    base = canvas.convert("RGBA"); base.alpha_composite(tint)
    return base.convert("RGB")

# ── Logo PMI topo esquerdo ────────────────────────────────────────
LOGO = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
def paste_logo(canvas, lh=48, x=52, y=44):
    logo = Image.open(LOGO).convert("RGBA")
    lw   = int(logo.width * lh / logo.height)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    canvas.paste(logo, (x, y), logo)
    ImageDraw.Draw(canvas).rectangle([x, y+lh+7, x+lw, y+lh+11], fill=VIOLET)

# ── Background IA com overlay esfumaçado ─────────────────────────
def load_smoky(path, centering=(0.5,0.5), top_s=140, bot_s=255,
               top_r=300, bot_r=900, blur=60):
    img = ImageOps.fit(Image.open(path).convert("RGB"), (W,H),
                       Image.LANCZOS, centering=centering)
    ov  = Image.new("RGBA", img.size, (0,0,0,0))
    dv  = ImageDraw.Draw(ov)
    IW, IH = img.size
    for y in range(top_r):
        a = int(top_s*(1-y/top_r)**2.0)
        dv.line([(0,y),(IW,y)], fill=(0,0,0,a))
    for y in range(IH-1, IH-bot_r-1, -1):
        a = int(bot_s*(1-(IH-1-y)/bot_r)**0.5)
        dv.line([(0,y),(IW,y)], fill=(0,0,0,a))
    ov  = ov.filter(ImageFilter.GaussianBlur(blur))
    base = img.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

# ── Fundo escuro PIL com glow roxo ────────────────────────────────
def dark_canvas(accent_y=None):
    c  = Image.new("RGB", (W,H), DARK)
    gl = Image.new("RGBA", (W,H), (0,0,0,0))
    dg = ImageDraw.Draw(gl)
    cy = accent_y or H//2
    for r in range(600, 0, -5):
        a = int(45*(1-r/600)**2.0)
        dg.ellipse([W//2-r, cy-r, W//2+r, cy+r], fill=(*VLT, a))
    gl = gl.filter(ImageFilter.GaussianBlur(80))
    c  = c.convert("RGBA"); c.alpha_composite(gl)
    return c.convert("RGB")

# ── Separador ─────────────────────────────────────────────────────
def sep(d, x, y, w=56, left=False):
    sx = x if left else (W-w)//2
    for xi in range(w):
        c = lerp(VLT, PINK, xi/max(1,w-1))
        d.line([(sx+xi,y),(sx+xi,y+4)], fill=c)
    return y+4

BG  = "/home/user/WEB/carrossel-pmi"
OUT = "/home/user/WEB/carrossel-pmi/posts"
os.makedirs(OUT, exist_ok=True)


# ════════════════════════════════════════════════════════════════
# POST 1 — 10h30 — "Meta Ads ficou 12% mais caro"
# ════════════════════════════════════════════════════════════════

def p1_s01():
    """LAYOUT: hero stat — '12%' gigante + hook. Imagem de fundo."""
    canvas = load_smoky(f"{BG}/bg_p1_s01.png", bot_r=1000)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    # "10:30" topo direito em tag
    fnt_tag = F("medium", 17)
    tag = "10:30 • PMI"
    tw_ = tw(d, tag, fnt_tag)
    d.rounded_rectangle([W-60-tw_, 38, W-44, 70], radius=8, fill=(*VIOLET,180))
    d.text((W-52-tw_, 46), tag, font=fnt_tag, fill=WHITE)

    # "12%" centro — tamanho máximo que cabe
    fnt_num = F("black", 260)
    num = "12%"
    nw = tw(d, num, fnt_num)
    ny = int(H*0.26)
    canvas = grad_text(canvas, d, num, fnt_num, (W-nw)//2, ny)
    d = ImageDraw.Draw(canvas)

    # linha fina abaixo do número
    bb = d.textbbox((0,0), num, font=fnt_num)
    line_y = ny + bb[3] + 10
    for xi in range(W):
        c = lerp(VLT, PINK, xi/(W-1))
        d.line([(xi,line_y),(xi,line_y+3)], fill=c)

    # headline abaixo da linha
    fnt_h = F("black", 68)
    lines = ["DO SEU INVESTIMENTO", "SUMIU SEM VOCÊ SABER."]
    y = line_y + 28
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h)
        x   = (W-lw_)//2
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, x, y)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((x, y), ln, font=fnt_h, fill=WHITE)
        y += int(68*1.1)

    # subtítulo
    fnt_s = F("regular", 28)
    sub   = "A Meta aumentou 12,15% o custo de todos os anúncios no Brasil. Arrasta."
    y += 18
    for ln in wrap(d, sub, fnt_s):
        lw_ = tw(d, ln, fnt_s)
        d.text(((W-lw_)//2, y), ln, font=fnt_s, fill=OFFWHT)
        y += int(28*1.5)

    canvas.save(f"{OUT}/p1_slide01.png"); print("✓ p1_slide01")


def p1_s02():
    """LAYOUT: split comparativo — PIL puro, sem foto. Antes vs Depois."""
    canvas = dark_canvas(accent_y=H//2)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    # título topo centralizado
    fnt_t = F("bold", 32)
    title = "O MESMO RESULTADO AGORA CUSTA MAIS."
    lw_   = tw(d, title, fnt_t)
    d.text(((W-lw_)//2, 130), title, font=fnt_t, fill=GRAY)

    sep(d, 0, 182)

    # divisória vertical central
    div_x = W//2
    for yi in range(300, H-200):
        ratio = abs(yi-(H//2)) / max(1, H//2-300)
        a = int(120 * max(0.0, 1-ratio)**0.5)
        d.line([(div_x, yi),(div_x+1, yi)], fill=(*GRAY, max(0,a)))

    # CARD ESQUERDO — ANTES
    card_pad = 52
    fnt_lab  = F("medium", 18)
    fnt_val  = F("black", 72)
    fnt_desc = F("regular", 24)

    # label "ANTES"
    lbl = "ANTES"
    d.text((card_pad, 240), lbl, font=fnt_lab, fill=GRAY)
    sep(d, card_pad, 272, w=40, left=True)

    # valor
    val = "R$5.000"
    canvas = grad_text(canvas, d, val, fnt_val, card_pad, 290, c1=WHITE, c2=OFFWHT)
    d = ImageDraw.Draw(canvas)
    d.text((card_pad, 390), "por mês", font=fnt_desc, fill=GRAY)

    # descrição
    fnt_b = F("regular", 22)
    for i, ln in enumerate(["Investia isso e", "recebia X resultado."]):
        d.text((card_pad, 460+i*34), ln, font=fnt_b, fill=GRAY)

    # CARD DIREITO — DEPOIS
    rx = div_x + card_pad

    d.text((rx, 240), "DEPOIS", font=fnt_lab, fill=PINK)
    sep(d, rx, 272, w=40, left=True)

    canvas = grad_text(canvas, d, "R$5.607", fnt_val, rx, 290)
    d = ImageDraw.Draw(canvas)
    d.text((rx, 390), "por mês", font=fnt_desc, fill=GRAY)

    for i, ln in enumerate(["Investe mais e", "entrega o mesmo."]):
        d.text((rx, 460+i*34), ln, font=fnt_b, fill=OFFWHT)

    # ícone seta central
    fnt_arr = F("bold", 48)
    d.text(((W-tw(d,"→",fnt_arr))//2, 310), "→", font=fnt_arr, fill=VIOLET)

    # frase âncora embaixo
    fnt_anc = F("black", 38)
    anc = "12,15% A MAIS. MESMO RESULTADO."
    lw_ = tw(d, anc, fnt_anc)
    canvas = grad_text(canvas, d, anc, fnt_anc, (W-lw_)//2, H-200)
    d = ImageDraw.Draw(canvas)

    fnt_ss = F("regular", 26)
    note   = "PIS + COFINS + ISS agora são seus."
    lw_    = tw(d, note, fnt_ss)
    d.text(((W-lw_)//2, H-142), note, font=fnt_ss, fill=GRAY)

    canvas.save(f"{OUT}/p1_slide02.png"); print("✓ p1_slide02")


def p1_s03():
    """LAYOUT: texto LEFT-ALIGNED + imagem. Declaração direta, sem centralizar."""
    canvas = load_smoky(f"{BG}/bg_p1_s02.png", centering=(0.3, 0.5))
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    # painel escuro à esquerda
    pan = Image.new("RGBA", (W,H), (0,0,0,0))
    dp  = ImageDraw.Draw(pan)
    for xi in range(W):
        a = int(220*(1-xi/(W*0.85))**0.7) if xi < W*0.85 else 0
        a = max(0, min(255, a))
        dp.line([(xi,0),(xi,H)], fill=(0,0,0,a))
    pan = pan.filter(ImageFilter.GaussianBlur(30))
    base = canvas.convert("RGBA"); base.alpha_composite(pan)
    canvas = base.convert("RGB")
    d = ImageDraw.Draw(canvas)

    lx = 64   # margem esquerda
    y  = 340

    fnt_h = F("black", 88)
    lines = ["A META", "REPASSOU", "OS IMPOSTOS."]
    for i, ln in enumerate(lines):
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, lx, y)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((lx, y), ln, font=fnt_h, fill=WHITE)
        y += int(88*1.05)

    y += 18
    sep(d, lx, y, w=50, left=True)
    y += 24

    fnt_s = F("regular", 28)
    for ln in wrap(d, "Você pagou a conta. Sem aviso. Sem explicação.", fnt_s, max_w=500):
        d.text((lx, y), ln, font=fnt_s, fill=OFFWHT)
        y += int(28*1.55)

    canvas.save(f"{OUT}/p1_slide03.png"); print("✓ p1_slide03")


def p1_s04():
    """LAYOUT: lista numerada em PIL puro — 3 ações concretas."""
    canvas = dark_canvas(accent_y=int(H*0.55))
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_t = F("black", 46)
    title = "COMO SE PROTEGER AGORA:"
    lw_   = tw(d, title, fnt_t)
    canvas = grad_text(canvas, d, title, fnt_t, (W-lw_)//2, 160)
    d = ImageDraw.Draw(canvas)
    sep(d, 0, 230)

    items = [
        ("01", "REAJUSTE O ORÇAMENTO",
               "Some 12,15% ao valor atual\npara manter o mesmo alcance."),
        ("02", "PRIORIZE CONVERSÃO",
               "Menos alcance, mais resultado.\nOtimize para quem compra, não para quem vê."),
        ("03", "REVISE O CRIATIVO",
               "Com custo maior, criativo fraco\ncusta o dobro. Teste antes de escalar."),
    ]

    fnt_n  = F("black",  52)
    fnt_hl = F("bold",   32)
    fnt_ds = F("regular",24)

    y = 290
    for num, headline, desc in items:
        # número em gradiente
        canvas = grad_text(canvas, d, num, fnt_n, 64, y)
        d = ImageDraw.Draw(canvas)

        # headline branco
        d.text((152, y+6), headline, font=fnt_hl, fill=WHITE)

        # descrição em GRAY, 2 linhas
        dy = y + 52
        for ln in desc.split("\n"):
            d.text((152, dy), ln, font=fnt_ds, fill=GRAY)
            dy += int(24*1.45)

        # linha divisória
        line_y = dy + 14
        d.line([(64, line_y),(W-64, line_y)], fill=(*CARD, 255))
        y = line_y + 30

    canvas.save(f"{OUT}/p1_slide04.png"); print("✓ p1_slide04")


def p1_s05():
    """LAYOUT: imagem de fundo + CTA centralizado bold."""
    canvas = load_smoky(f"{BG}/bg_p1_s03.png", bot_r=950)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_h = F("black", 88)
    lines = ["JÁ AJUSTOU", "SEU ORÇAMENTO?"]
    block_h = int(88*1.08)*len(lines)
    y = (H - block_h)//2 - 40
    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h)
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, (W-lw_)//2, y)
            d = ImageDraw.Draw(canvas)
        else:
            d.text(((W-lw_)//2, y), ln, font=fnt_h, fill=WHITE)
        y += int(88*1.08)

    y += 24
    sep(d, 0, y)
    y += 24

    fnt_s = F("regular", 30)
    sub   = "Comenta aqui. A gente calcula o impacto no seu investimento."
    for ln in wrap(d, sub, fnt_s):
        lw_ = tw(d, ln, fnt_s)
        d.text(((W-lw_)//2, y), ln, font=fnt_s, fill=OFFWHT)
        y += int(30*1.55)

    canvas.save(f"{OUT}/p1_slide05.png"); print("✓ p1_slide05")


# ════════════════════════════════════════════════════════════════
# POST 2 — 16h — "82% usam IA. Quase nenhum tem estratégia."
# ════════════════════════════════════════════════════════════════

def p2_s01():
    """LAYOUT: '82%' ocupa 60% do frame. Hook visual extremo."""
    canvas = load_smoky(f"{BG}/bg_p2_s01.png", bot_r=1000)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    # tag horário
    fnt_tag = F("medium", 17)
    tag = "16:00 • PMI"
    tw_ = tw(d, tag, fnt_tag)
    d.rounded_rectangle([W-60-tw_, 38, W-44, 70], radius=8, fill=(*VIOLET,180))
    d.text((W-52-tw_, 46), tag, font=fnt_tag, fill=WHITE)

    # "82%" hero — enorme
    fnt_num = F("black", 280)
    num = "82%"
    nw  = tw(d, num, fnt_num)
    ny  = int(H*0.18)
    canvas = grad_text(canvas, d, num, fnt_num, (W-nw)//2, ny)
    d = ImageDraw.Draw(canvas)

    # linha divisória
    bb     = d.textbbox((0,0), num, font=fnt_num)
    line_y = ny + bb[3] + 8
    for xi in range(W):
        c = lerp(PINK, VLT, xi/(W-1))
        d.line([(xi,line_y),(xi,line_y+3)], fill=c)

    # headline
    fnt_h  = F("black", 60)
    lines  = ["DOS NEGÓCIOS JÁ USAM IA.", "QUASE NENHUM TEM ESTRATÉGIA."]
    y      = line_y + 28
    for i, ln in enumerate(lines):
        _, fnt_fit = fit_font(d, [ln], "black", 60)
        lw_ = tw(d, ln, fnt_fit)
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_fit, (W-lw_)//2, y)
            d = ImageDraw.Draw(canvas)
        else:
            d.text(((W-lw_)//2, y), ln, font=fnt_fit, fill=WHITE)
        y += int(fnt_fit.size*1.1)

    fnt_s = F("light", 28)
    sub   = "E é exatamente isso que separa quem escala de quem só produz ruído."
    y += 16
    for ln in wrap(d, sub, fnt_s):
        lw_ = tw(d, ln, fnt_s)
        d.text(((W-lw_)//2, y), ln, font=fnt_s, fill=OFFWHT)
        y += int(28*1.5)

    canvas.save(f"{OUT}/p2_slide01.png"); print("✓ p2_slide01")


def p2_s02():
    """LAYOUT: slide PIL dividido em 2 halves — contraste visual forte."""
    canvas = dark_canvas(accent_y=H//2)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    mid = H//2

    # metade superior — "IA AUTOMATIZA."
    fnt_top = F("black", 92)
    txt_top = "IA AUTOMATIZA."
    lw_     = tw(d, txt_top, fnt_top)
    y_top   = mid//2 - int(fnt_top.size*1.08)//2
    d.text(((W-lw_)//2, y_top), txt_top, font=fnt_top, fill=WHITE)

    fnt_st  = F("light", 28)
    sub_top = "Conteúdo. Anúncios. Respostas. Relatórios."
    lw_     = tw(d, sub_top, fnt_st)
    d.text(((W-lw_)//2, y_top+int(fnt_top.size*1.1)+12),
           sub_top, font=fnt_st, fill=GRAY)

    # linha divisória central
    for xi in range(W):
        c = lerp(VLT, PINK, xi/(W-1))
        d.line([(xi, mid-2),(xi, mid+2)], fill=c)

    # metade inferior — "ESTRATÉGIA DEFINE O QUE AUTOMATIZAR."
    fnt_bot = F("black", 68)
    lines_b = ["ESTRATÉGIA DEFINE", "O QUE AUTOMATIZAR."]
    y_bot   = mid + 60
    for i, ln in enumerate(lines_b):
        _, fnt_fit = fit_font(d, [ln], "black", 68)
        lw_ = tw(d, ln, fnt_fit)
        if i == len(lines_b)-1:
            canvas = grad_text(canvas, d, ln, fnt_fit, (W-lw_)//2, y_bot)
            d = ImageDraw.Draw(canvas)
        else:
            d.text(((W-lw_)//2, y_bot), ln, font=fnt_fit, fill=WHITE)
        y_bot += int(fnt_fit.size*1.1)

    fnt_sb  = F("light", 28)
    sub_bot = "Sem isso, você só automatiza o desperdício."
    lw_     = tw(d, sub_bot, fnt_sb)
    d.text(((W-lw_)//2, y_bot+14), sub_bot, font=fnt_sb, fill=GRAY)

    canvas.save(f"{OUT}/p2_slide02.png"); print("✓ p2_slide02")


def p2_s03():
    """LAYOUT: LEFT-ALIGNED, imagem de xadrez ao fundo."""
    canvas = load_smoky(f"{BG}/bg_p2_s02.png", centering=(0.7, 0.5))
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    # painel escuro à esquerda
    pan = Image.new("RGBA", (W,H), (0,0,0,0))
    dp  = ImageDraw.Draw(pan)
    for xi in range(W):
        a = int(235*(1-xi/(W*0.9))**0.6) if xi < W*0.9 else 0
        dp.line([(xi,0),(xi,H)], fill=(0,0,0,max(0,min(255,a))))
    pan = pan.filter(ImageFilter.GaussianBlur(28))
    base = canvas.convert("RGBA"); base.alpha_composite(pan)
    canvas = base.convert("RGB")
    d = ImageDraw.Draw(canvas)

    lx = 64
    y  = 320

    fnt_h = F("black", 84)
    lines = ["FERRAMENTA", "NAS MÃOS", "ERRADAS É", "DESPERDÍCIO."]
    _, fnt_h = fit_font(d, lines, "black", 84)
    for i, ln in enumerate(lines):
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, lx, y)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((lx, y), ln, font=fnt_h, fill=WHITE)
        y += int(fnt_h.size*1.06)

    y += 20
    sep(d, lx, y, w=50, left=True)
    y += 24

    fnt_s = F("regular", 27)
    for ln in wrap(d, "IA na mão certa escala negócio. Na errada, escala custo.", fnt_s, max_w=520):
        d.text((lx, y), ln, font=fnt_s, fill=OFFWHT)
        y += int(27*1.55)

    canvas.save(f"{OUT}/p2_slide03.png"); print("✓ p2_slide03")


def p2_s04():
    """LAYOUT: lista — 'O que IA NÃO FAZ por você' — PIL puro."""
    canvas = dark_canvas(accent_y=int(H*0.5))
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_t = F("black", 42)
    title = "O QUE IA NÃO FAZ POR VOCÊ:"
    lw_   = tw(d, title, fnt_t)
    canvas = grad_text(canvas, d, title, fnt_t, (W-lw_)//2, 160)
    d = ImageDraw.Draw(canvas)
    sep(d, 0, 222)

    items = [
        ("01", "POSICIONAR SUA MARCA",
               "Quem você é, pra quem fala e por que\nalguém deveria te escolher — isso é seu."),
        ("02", "ENTENDER SEU CLIENTE",
               "IA processa dados. Você interpreta\no comportamento de gente real."),
        ("03", "DEFINIR ONDE CRESCER",
               "Meta, Google, TikTok, WhatsApp.\nEstrategia é sua. Execução pode ser dela."),
    ]

    fnt_n  = F("black",  52)
    fnt_hl = F("bold",   30)
    fnt_ds = F("regular",23)
    y = 272

    for num, headline, desc in items:
        canvas = grad_text(canvas, d, num, fnt_n, 64, y)
        d = ImageDraw.Draw(canvas)
        d.text((152, y+8), headline, font=fnt_hl, fill=WHITE)
        dy = y + 50
        for ln in desc.split("\n"):
            d.text((152, dy), ln, font=fnt_ds, fill=GRAY)
            dy += int(23*1.45)
        line_y = dy + 12
        d.line([(64, line_y),(W-64, line_y)], fill=(*CARD,255))
        y = line_y + 28

    canvas.save(f"{OUT}/p2_slide04.png"); print("✓ p2_slide04")


def p2_s05():
    """LAYOUT: imagem + pergunta direta. CTA de save."""
    canvas = load_smoky(f"{BG}/bg_p2_s03.png", bot_r=950)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_h  = F("black", 78)
    lines  = ["SALVA ESSE POST.", "SEGUNDA A", "CONVERSA MUDA."]
    _, fnt_h = fit_font(d, lines, "black", 78)
    block_h  = int(fnt_h.size*1.08) * len(lines)
    y = (H - block_h)//2 - 60

    for i, ln in enumerate(lines):
        lw_ = tw(d, ln, fnt_h)
        if i == len(lines)-1:
            canvas = grad_text(canvas, d, ln, fnt_h, (W-lw_)//2, y)
            d = ImageDraw.Draw(canvas)
        else:
            d.text(((W-lw_)//2, y), ln, font=fnt_h, fill=WHITE)
        y += int(fnt_h.size*1.08)

    y += 26
    sep(d, 0, y)
    y += 24

    fnt_s = F("regular", 29)
    sub   = "Você usa IA com estratégia ou no piloto automático?"
    for ln in wrap(d, sub, fnt_s):
        lw_ = tw(d, ln, fnt_s)
        d.text(((W-lw_)//2, y), ln, font=fnt_s, fill=OFFWHT)
        y += int(29*1.55)

    canvas.save(f"{OUT}/p2_slide05.png"); print("✓ p2_slide05")


if __name__ == "__main__":
    print("=== POST 1 — 10h30: Meta Ads 12% mais caro ===")
    p1_s01(); p1_s02(); p1_s03(); p1_s04(); p1_s05()
    print("\n=== POST 2 — 16h: 82% usam IA sem estratégia ===")
    p2_s01(); p2_s02(); p2_s03(); p2_s04(); p2_s05()
    print(f"\nDone → {OUT}")
