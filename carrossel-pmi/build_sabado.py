#!/usr/bin/env python3
"""Sábado PMI — Post A: TikTok Shop / Post B: ROI de Vaidade
Carrossel 1080×1350 — estilo full bleed ideia01
"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H   = 1080, 1350
C_BG   = (7, 6, 11)
C_WHT  = (255, 255, 255)
C_SUB  = (210, 200, 225)

FD   = '/home/user/WEB/carrossel-pmi/fonts'
LOGO = '/home/user/WEB/carrossel-pmi/logo_ritmodamarca.png'
BG   = '/home/user/WEB/carrossel-pmi/sabado_bg'
OUT  = '/home/user/WEB/carrossel-pmi/sabado'
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


def load_img(path, fade_h=120):
    canvas = Image.new('RGB', (W, H), C_BG)
    img = Image.open(path).convert('RGB')
    nh = int(img.height * W / img.width)
    img = img.resize((W, nh), Image.LANCZOS)
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


def add_logo(canvas, h=66):
    try:
        logo = Image.open(LOGO).convert('RGBA')
        lw = int(logo.width * h / logo.height)
        logo = logo.resize((lw, h), Image.LANCZOS)
        x = (W - lw) // 2
        y = H - h - 44
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
        if all(d.textbbox((0,0),ln,font=f)[2]-d.textbbox((0,0),ln,font=f)[0] <= max_w for ln in lines):
            return f, sz
        sz -= 2
    return F(style, min_sz), min_sz


def wrap_text(d, text, font, max_w):
    words = text.split()
    lines, line = [], ''
    for w in words:
        test = f'{line} {w}'.strip()
        bb = d.textbbox((0, 0), test, font=font)
        if bb[2] - bb[0] <= max_w:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines


def build(bg_file, hl_lines, sub_text, out_name,
          accent, hl_start=100, M=72, accent_idx=None):

    canvas = load_img(f'{BG}/{bg_file}')
    d = ImageDraw.Draw(canvas)
    MAX_W = W - M - 56

    if accent_idx is None:
        accent_idx = {len(hl_lines) - 1}

    hl_f, hl_sz = fit_font(d, hl_lines, 'mextrabold', hl_start, 38, MAX_W)
    sub_sz  = max(30, int(hl_sz * 0.36))
    sub_f   = F('isemibold', sub_sz)
    sub_lines = wrap_text(d, sub_text, sub_f, MAX_W)
    SUB_LEAD  = int(sub_sz * 1.28)

    GAP_HL = 18
    bbs_hl = [d.textbbox((0, 0), ln, font=hl_f) for ln in hl_lines]
    hl_h   = sum(b[3]-b[1] for b in bbs_hl) + GAP_HL * (len(hl_lines)-1)
    sub_h  = SUB_LEAD * len(sub_lines)

    LOGO_H  = 66
    LOGO_PAD = 44

    # bottom-up layout
    logo_top = H - LOGO_PAD - LOGO_H
    sub_top  = logo_top - 30 - sub_h
    hl_top   = sub_top - 22 - hl_h
    bar_y    = hl_top - 18 - 4

    # accent bar
    d.rectangle([M, bar_y, M + 80, bar_y + 4], fill=accent)

    # headline
    y = hl_top
    for i, ln in enumerate(hl_lines):
        bb = bbs_hl[i]
        ink_h = bb[3] - bb[1]
        color = accent if i in accent_idx else C_WHT
        d.text((M - bb[0], y - bb[1]), ln, font=hl_f, fill=color)
        y += ink_h + (GAP_HL if i < len(hl_lines) - 1 else 0)

    # subtitle
    y = sub_top
    for ln in sub_lines:
        bb = d.textbbox((0, 0), ln, font=sub_f)
        d.text((M - bb[0], y - bb[1]), ln, font=sub_f, fill=C_SUB)
        y += SUB_LEAD

    canvas = add_logo(canvas, LOGO_H)
    out = f'{OUT}/{out_name}'
    canvas.save(out, quality=95)
    print(f'  ✓ {out_name}')


# ── Cores de acento ──────────────────────────────────────────────────────────
PURPLE = (168, 85, 247)    # marca
TEAL   = (20, 220, 190)    # TikTok vibe
RED    = (239, 68, 68)     # urgência / vaidade

# ════════════════════════════════════════════════════════════════════════════
# POST A — TikTok Shop (5 slides)
# ════════════════════════════════════════════════════════════════════════════
print('=== POST A — TikTok Shop ===')

build('pa_s1_creator.jpg',
      ['ENQUANTO VOCÊ DEBATE', 'SE DEVE ENTRAR', 'NO TIKTOK SHOP,'],
      'seu concorrente já está vendendo ao vivo.',
      'pa_s1.png', TEAL, 90, accent_idx={2})

build('pa_s2_shopping.jpg',
      ['EM MENOS DE 1 ANO', 'O TIKTOK SHOP VIROU', 'O 3º MAIOR', 'MARKETPLACE DO BRASIL.'],
      'Atrás só de Mercado Livre e Shopee.',
      'pa_s2.png', TEAL, 90, accent_idx={2, 3})

build('pa_s3_money.jpg',
      ['O FATURAMENTO POR', 'LIVES CRESCEU', '96 VEZES', 'EM UM ANO.'],
      'Um negócio foi de R$ 4 mil para R$ 3,2 milhões vendendo ao vivo.',
      'pa_s3.png', TEAL, 94, accent_idx={2})

build('pa_s4_cityphone.jpg',
      ['VER. CONFIAR.', 'COMPRAR.', 'SEM SAIR DO APP.'],
      'O consumidor não quer clicar em link nem esperar página carregar.',
      'pa_s4.png', TEAL, 104, accent_idx={1})

build('pa_s5_glow.jpg',
      ['A PERGUNTA NÃO É', '"DEVO ENTRAR?"', 'É: QUANTO VOCÊ', 'JÁ PERDEU?'],
      'Segue @ritmodamarca e descobre como posicionar seu negócio agora.',
      'pa_s5.png', TEAL, 90, accent_idx={1, 3})

# ════════════════════════════════════════════════════════════════════════════
# POST B — ROI de Vaidade (4 slides)
# ════════════════════════════════════════════════════════════════════════════
print('\n=== POST B — ROI de Vaidade ===')

build('pb_s1_data.jpg',
      ['SEGUIR TODAS AS', 'TENDÊNCIAS CAIU', 'DE 54% PARA 16%', 'EM UM ANO.'],
      'O mercado finalmente acordou. Acabou a era do engajamento bonito sem resultado.',
      'pb_s1.png', RED, 88, accent_idx={2, 3})

build('pb_s2_likes.jpg',
      ['CURTIDA NÃO PAGA', 'BOLETO.', 'ALCANCE NÃO É', 'FATURAMENTO.'],
      'Quem ainda otimiza post para like em 2026 opera com mentalidade de 2019.',
      'pb_s2.png', RED, 92, accent_idx={1, 3})

build('pb_s3_dramatic.jpg',
      ['A PERGUNTA CERTA', 'É UMA SÓ:'],
      'Isso aqui gera cliente — ou só gera aplauso?',
      'pb_s3.png', RED, 110, accent_idx={1})

build('pb_s4_night.jpg',
      ['NA PMI A GENTE', 'SEMPRE DEFENDEU:', 'RESULTADO ACIMA', 'DE TREND.'],
      'Não é sobre ser bonito no feed. É sobre construir um negócio que vende de verdade.',
      'pb_s4.png', RED, 90, accent_idx={2, 3})

print(f'\nDone → {OUT}')
