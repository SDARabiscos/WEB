#!/usr/bin/env python3
"""Tráfego Pago — 3 posts × 3 versões × 2 tamanhos = 18 criativos"""

from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

# ── Tamanhos ──────────────────────────────────────────────────────────────────
FEED    = (1080, 1350)   # 4:5
STORIES = (1080, 1920)   # 9:16

C_BG    = (6, 4, 10)
C_WHT   = (255, 255, 255)
C_SUB   = (210, 200, 225)

FD   = '/home/user/WEB/carrossel-pmi/fonts'
LOGO = '/home/user/WEB/carrossel-pmi/logo_ritmodamarca.png'
IMGS = '/home/user/WEB/carrossel-pmi'
OUT  = '/home/user/WEB/carrossel-pmi/trafego'
os.makedirs(OUT, exist_ok=True)


def F(style, size):
    m = {
        'mextrabold': 'Montserrat-ExtraBold.ttf',
        'mbold':      'Montserrat-Bold.ttf',
        'msemibold':  'Montserrat-SemiBold.ttf',
        'iregular':   'Inter-Regular.ttf',
        'isemibold':  'Inter-SemiBold.ttf',
    }
    return ImageFont.truetype(f'{FD}/{m[style]}', size)


# ── Fundo FEED: escala por largura, dark canvas embaixo ──────────────────────
def make_feed_canvas(path, W=1080, H=1350, fade_h=130):
    canvas = Image.new('RGB', (W, H), C_BG)
    img = Image.open(path).convert('RGB')
    nh = int(img.height * W / img.width)
    img = img.resize((W, nh), Image.LANCZOS)
    # fade bottom
    fade = Image.new('RGBA', (W, nh), (0, 0, 0, 0))
    fpx = fade.load()
    fs = max(0, nh - fade_h)
    for y in range(fs, nh):
        a = int(255 * (y - fs) / fade_h)
        for x in range(W):
            fpx[x, y] = (*C_BG, a)
    ir = img.convert('RGBA')
    ir.alpha_composite(fade)
    canvas.paste(ir.convert('RGB'), (0, 0))
    return canvas


# ── Fundo STORIES: full bleed, gradiente escuro na metade inferior ────────────
def make_stories_canvas(path, W=1080, H=1920, grad_start=0.42):
    img = ImageOps.fit(Image.open(path).convert('RGB'), (W, H),
                       Image.LANCZOS, centering=(0.5, 0.3))
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    opx = ov.load()
    sy = int(H * grad_start)
    for y in range(H):
        if y < sy:
            a = 30
        else:
            a = int(30 + 215 * ((y - sy) / (H - sy)) ** 1.3)
        a = min(a, 255)
        for x in range(W):
            opx[x, y] = (0, 0, 0, a)
    base = img.convert('RGBA')
    base.alpha_composite(ov)
    return base.convert('RGB')


def add_logo(canvas, W, H, h=60):
    try:
        logo = Image.open(LOGO).convert('RGBA')
        lw = int(logo.width * h / logo.height)
        logo = logo.resize((lw, h), Image.LANCZOS)
        x = (W - lw) // 2
        y = H - h - 48
        base = canvas.convert('RGBA')
        base.alpha_composite(logo, (x, y))
        return base.convert('RGB')
    except Exception as e:
        print(f'  logo err: {e}')
        return canvas


def fit_font(d, lines, style, start, min_sz, max_w):
    sz = start
    while sz >= min_sz:
        f = F(style, sz)
        bbs = [d.textbbox((0, 0), ln, font=f) for ln in lines]
        if all(bb[2] - bb[0] <= max_w for bb in bbs):
            return f, sz
        sz -= 2
    f = F(style, min_sz)
    return f, min_sz


def wrap_text(d, text, font, max_w):
    words = text.split()
    lines, line = [], ''
    for w in words:
        test = f'{line} {w}'.strip()
        bb = d.textbbox((0, 0), test, font=font)
        if bb[2] - bb[0] <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def render(canvas, W, H, hl_lines, sub_text, cta_text, accent,
           hl_start=110, M=72):
    d = ImageDraw.Draw(canvas)
    MAX_W = W - M - 60

    # fonts
    hl_f, hl_sz = fit_font(d, hl_lines, 'mextrabold', hl_start, 40, MAX_W)
    sub_sz = max(30, int(hl_sz * 0.36))
    sub_f = F('isemibold', sub_sz)
    cta_f = F('msemibold', max(26, int(hl_sz * 0.30)))

    sub_lines = wrap_text(d, sub_text, sub_f, MAX_W)
    SUB_LEAD = int(sub_sz * 1.28)

    # measure blocks
    GAP_HL = 16
    bbs_hl = [d.textbbox((0, 0), ln, font=hl_f) for ln in hl_lines]
    hl_block_h = sum(b[3]-b[1] for b in bbs_hl) + GAP_HL * (len(hl_lines)-1)
    sub_block_h = SUB_LEAD * len(sub_lines)

    cta_bb = d.textbbox((0, 0), cta_text, font=cta_f)
    cta_h  = cta_bb[3] - cta_bb[1]

    LOGO_H  = 60
    LOGO_PAD = 48

    # layout bottom-up
    logo_top  = H - LOGO_PAD - LOGO_H
    cta_top   = logo_top - 28 - cta_h
    sep_y     = cta_top - 20
    sub_top   = sep_y - 20 - sub_block_h
    hl_top    = sub_top - 22 - hl_block_h
    bar_y     = hl_top - 18 - 4

    # accent bar
    d.rectangle([M, bar_y, M + 80, bar_y + 4], fill=accent)

    # headline
    y = hl_top
    for i, ln in enumerate(hl_lines):
        bb = bbs_hl[i]
        ink_h = bb[3] - bb[1]
        # last line gets accent color
        color = accent if i == len(hl_lines) - 1 else C_WHT
        d.text((M - bb[0], y - bb[1]), ln, font=hl_f, fill=color)
        y += ink_h + (GAP_HL if i < len(hl_lines) - 1 else 0)

    # sub
    y = sub_top
    for ln in sub_lines:
        bb = d.textbbox((0, 0), ln, font=sub_f)
        d.text((M - bb[0], y - bb[1]), ln, font=sub_f, fill=C_SUB)
        y += SUB_LEAD

    # thin separator
    d.rectangle([M, sep_y, M + 48, sep_y + 2], fill=accent)

    # CTA
    cta_bb2 = d.textbbox((0, 0), cta_text, font=cta_f)
    d.text((M - cta_bb2[0], cta_top - cta_bb2[1]), cta_text, font=cta_f, fill=accent)

    return add_logo(canvas, W, H, LOGO_H)


def build(bg_path, hl_lines, sub_text, cta_text, accent, name,
          hl_start=110):
    W_F, H_F = FEED
    W_S, H_S = STORIES

    # Feed
    c_feed = make_feed_canvas(bg_path, W_F, H_F)
    c_feed = render(c_feed, W_F, H_F, hl_lines, sub_text, cta_text, accent, hl_start)
    out_f = f'{OUT}/{name}_feed.png'
    c_feed.save(out_f, quality=95)
    print(f'  ✓ {os.path.basename(out_f)}')

    # Stories
    c_stor = make_stories_canvas(bg_path, W_S, H_S)
    c_stor = render(c_stor, W_S, H_S, hl_lines, sub_text, cta_text, accent,
                    int(hl_start * 1.1))
    out_s = f'{OUT}/{name}_stories.png'
    c_stor.save(out_s, quality=95)
    print(f'  ✓ {os.path.basename(out_s)}')


# ── Paleta de acentos contrastantes ──────────────────────────────────────────
PURPLE = (168, 85, 247)    # #a855f7 — marca
YELLOW = (251, 191,  36)   # âmbar quente — contraste máximo
CORAL  = (251,  99,  64)   # coral/laranja — energia, urgência

# ════════════════════════════════════════════════════════════════════════════
# POST 1 — Dependência de indicação
# ════════════════════════════════════════════════════════════════════════════
HL1 = ['SE O SEU NEGÓCIO', 'DEPENDE DE', 'INDICAÇÃO PARA VENDER,']
SB1 = 'você não tem uma empresa. Tem um emprego disfarçado.'
CT1 = '→ Segue @ritmodamarca'

print('=== POST 1 — Indicação ===')
build(f'{IMGS}/fp_t1_v1.jpg', HL1, SB1, CT1, PURPLE, 'p1_v1', 90)
build(f'{IMGS}/fp_t1_v2.jpg', HL1, SB1, CT1, YELLOW, 'p1_v2', 90)
build(f'{IMGS}/fp_t1_v3.jpg', HL1, SB1, CT1, CORAL,  'p1_v3', 90)

# ════════════════════════════════════════════════════════════════════════════
# POST 2 — Tráfego sem retorno
# ════════════════════════════════════════════════════════════════════════════
HL2 = ['VOCÊ INVESTE EM', 'ANÚNCIO TODO MÊS.', 'AS VENDAS NÃO APARECEM.']
SB2 = 'Os relatórios parecem bons. Isso tem nome: gargalo de conversão.'
CT2 = '→ Segue @ritmodamarca'

print('\n=== POST 2 — Tráfego ===')
build(f'{IMGS}/fp_t2_v1.jpg', HL2, SB2, CT2, PURPLE, 'p2_v1', 86)
build(f'{IMGS}/fp_t2_v2.jpg', HL2, SB2, CT2, YELLOW, 'p2_v2', 86)
build(f'{IMGS}/fp_t2_v3.jpg', HL2, SB2, CT2, CORAL,  'p2_v3', 86)

# ════════════════════════════════════════════════════════════════════════════
# POST 3 — Cobrar mais caro
# ════════════════════════════════════════════════════════════════════════════
HL3 = ['VOCÊ NÃO PRECISA', 'DE MAIS CLIENTES.']
SB3 = 'Você precisa de clientes que pagam o que você vale.'
CT3 = '→ Segue @ritmodamarca'

print('\n=== POST 3 — Cobrar Mais ===')
build(f'{IMGS}/fp_t3_v1.jpg', HL3, SB3, CT3, PURPLE, 'p3_v1', 104)
build(f'{IMGS}/fp_t3_v2.jpg', HL3, SB3, CT3, YELLOW, 'p3_v2', 104)
build(f'{IMGS}/fp_t3_v3.jpg', HL3, SB3, CT3, CORAL,  'p3_v3', 104)

print(f'\nDone → {OUT}')
