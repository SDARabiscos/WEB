#!/usr/bin/env python3
"""Tráfego Pago V2 — backgrounds conceituais fora da caixinha
3 posts × 3 conceitos × 2 tamanhos = 18 criativos
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

FEED    = (1080, 1350)
STORIES = (1080, 1920)

C_BG  = (6, 4, 10)
C_WHT = (255, 255, 255)
C_SUB = (210, 200, 225)
C_ACC = (168, 85, 247)    # roxo marca — #a855f7

FD   = '/home/user/WEB/carrossel-pmi/fonts'
LOGO = '/home/user/WEB/carrossel-pmi/logo_ritmodamarca.png'
BG   = '/home/user/WEB/carrossel-pmi/trafego_bg'
OUT  = '/home/user/WEB/carrossel-pmi/trafego2'
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


# ── Canvas feed: escala por largura → dark canvas natural embaixo ─────────────
def make_feed(path, W=1080, H=1350, fade_h=110, centering=(0.5, 0.35)):
    img = Image.open(path).convert('RGB')
    # se imagem for mais larga que 3:1, usa fit para cobrir verticalmente
    ratio = img.width / img.height
    if ratio > 2.5:
        # imagem ultra-wide: fit para cobrir o topo com drama
        target_h = max(300, int(W / ratio))
        img = ImageOps.fit(img, (W, target_h), Image.LANCZOS, centering=centering)
        nh = target_h
    else:
        nh = int(img.height * W / img.width)
        img = img.resize((W, nh), Image.LANCZOS)

    canvas = Image.new('RGB', (W, H), C_BG)
    # fade bottom da imagem para dark canvas
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


# ── Canvas stories: full bleed, gradiente escuro forte na metade inferior ─────
def make_stories(path, W=1080, H=1920, grad_start=0.40, centering=(0.5, 0.3)):
    img = ImageOps.fit(
        Image.open(path).convert('RGB'), (W, H),
        Image.LANCZOS, centering=centering
    )
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    opx = ov.load()
    sy = int(H * grad_start)
    for y in range(H):
        if y < sy:
            a = 25
        else:
            t = (y - sy) / (H - sy)
            a = int(25 + 220 * (t ** 1.4))
        a = min(255, a)
        for x in range(W):
            opx[x, y] = (0, 0, 0, a)
    base = img.convert('RGBA')
    base.alpha_composite(ov)
    return base.convert('RGB')


def add_logo(canvas, W, H, h=62):
    try:
        logo = Image.open(LOGO).convert('RGBA')
        lw = int(logo.width * h / logo.height)
        logo = logo.resize((lw, h), Image.LANCZOS)
        x = (W - lw) // 2
        y = H - h - 46
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


def render(canvas, W, H, hl_lines, sub_text, cta_text,
           hl_start=104, M=72, accent=C_ACC):
    d = ImageDraw.Draw(canvas)
    MAX_W = W - M - 56

    hl_f, hl_sz = fit_font(d, hl_lines, 'mextrabold', hl_start, 38, MAX_W)
    sub_sz  = max(28, int(hl_sz * 0.355))
    cta_sz  = max(24, int(hl_sz * 0.295))
    sub_f   = F('isemibold', sub_sz)
    cta_f   = F('msemibold', cta_sz)

    sub_lines = wrap_text(d, sub_text, sub_f, MAX_W)
    SUB_LEAD  = int(sub_sz * 1.30)

    GAP_HL = 16
    bbs_hl = [d.textbbox((0, 0), ln, font=hl_f) for ln in hl_lines]
    hl_h   = sum(b[3]-b[1] for b in bbs_hl) + GAP_HL * (len(hl_lines)-1)
    sub_h  = SUB_LEAD * len(sub_lines)
    cta_bb = d.textbbox((0, 0), cta_text, font=cta_f)
    cta_h  = cta_bb[3] - cta_bb[1]

    LOGO_H  = 62
    LOGO_PAD = 46

    # layout bottom-up
    logo_top = H - LOGO_PAD - LOGO_H
    cta_top  = logo_top - 26 - cta_h
    sep_y    = cta_top - 18
    sub_top  = sep_y - 18 - sub_h
    hl_top   = sub_top - 20 - hl_h
    bar_y    = hl_top - 16 - 4

    # barra de acento
    d.rectangle([M, bar_y, M + 80, bar_y + 4], fill=accent)

    # headline — última linha em cor de acento
    y = hl_top
    for i, ln in enumerate(hl_lines):
        bb = bbs_hl[i]
        ink_h = bb[3] - bb[1]
        color = accent if i == len(hl_lines) - 1 else C_WHT
        d.text((M - bb[0], y - bb[1]), ln, font=hl_f, fill=color)
        y += ink_h + (GAP_HL if i < len(hl_lines) - 1 else 0)

    # subtítulo
    y = sub_top
    for ln in sub_lines:
        bb = d.textbbox((0, 0), ln, font=sub_f)
        d.text((M - bb[0], y - bb[1]), ln, font=sub_f, fill=C_SUB)
        y += SUB_LEAD

    # separador fino
    d.rectangle([M, sep_y, M + 48, sep_y + 2], fill=accent)

    # CTA
    bb = d.textbbox((0, 0), cta_text, font=cta_f)
    d.text((M - bb[0], cta_top - bb[1]), cta_text, font=cta_f, fill=accent)

    return add_logo(canvas, W, H, LOGO_H)


def build(name, bg_file, hl_lines, sub_text, cta_text,
          hl_start=104, centering=(0.5, 0.35)):
    W_F, H_F = FEED
    W_S, H_S = STORIES
    path = f'{BG}/{bg_file}'

    c = make_feed(path, W_F, H_F, centering=centering)
    c = render(c, W_F, H_F, hl_lines, sub_text, cta_text, hl_start)
    out = f'{OUT}/{name}_feed.png'
    c.save(out, quality=95)
    print(f'  ✓ {os.path.basename(out)}')

    c = make_stories(path, W_S, H_S, centering=centering)
    c = render(c, W_S, H_S, hl_lines, sub_text, cta_text, int(hl_start * 1.12))
    out = f'{OUT}/{name}_stories.png'
    c.save(out, quality=95)
    print(f'  ✓ {os.path.basename(out)}')


# ════════════════════════════════════════════════════════════════════════════
# POST 1 — Dependência de indicação
# ════════════════════════════════════════════════════════════════════════════
HL1 = ['SE O SEU NEGÓCIO', 'DEPENDE DE', 'INDICAÇÃO PARA VENDER,']
SB1 = 'você não tem uma empresa. Tem um emprego disfarçado.'
CT1 = '→ Segue @ritmodamarca'

print('=== POST 1 — Indicação ===')
build('p1_casino',    'p1_casino.jpg',    HL1, SB1, CT1, 96,  (0.5, 0.40))
build('p1_corda',     'p1_corda.jpg',     HL1, SB1, CT1, 96,  (0.5, 0.30))
build('p1_correntes', 'p1_correntes.jpg', HL1, SB1, CT1, 96,  (0.5, 0.35))

# ════════════════════════════════════════════════════════════════════════════
# POST 2 — Tráfego sem retorno
# ════════════════════════════════════════════════════════════════════════════
HL2 = ['VOCÊ INVESTE EM', 'ANÚNCIO TODO MÊS.', 'AS VENDAS NÃO APARECEM.']
SB2 = 'Os relatórios parecem bons. Isso tem nome: gargalo de conversão.'
CT2 = '→ Segue @ritmodamarca'

print('\n=== POST 2 — Tráfego ===')
build('p2_fogo',      'p2_fogo.jpg',      HL2, SB2, CT2, 86, (0.5, 0.40))
build('p2_torneira',  'p2_torneira.jpg',  HL2, SB2, CT2, 86, (0.5, 0.50))
build('p2_ampulheta', 'p2_ampulheta.jpg', HL2, SB2, CT2, 86, (0.5, 0.35))

# ════════════════════════════════════════════════════════════════════════════
# POST 3 — Cobrar mais caro
# ════════════════════════════════════════════════════════════════════════════
HL3 = ['VOCÊ NÃO PRECISA', 'DE MAIS CLIENTES.']
SB3 = 'Você precisa de clientes que pagam o que você vale.'
CT3 = '→ Segue @ritmodamarca'

print('\n=== POST 3 — Cobrar Mais ===')
build('p3_diamante', 'p3_diamante.jpg', HL3, SB3, CT3, 108, (0.5, 0.50))
build('p3_alvo',     'p3_alvo.jpg',     HL3, SB3, CT3, 108, (0.5, 0.45))
build('p3_cidade',   'p3_cidade.jpg',   HL3, SB3, CT3, 108, (0.5, 0.40))

print(f'\nDone → {OUT}')
