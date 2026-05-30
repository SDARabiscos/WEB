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
C_VIB  = (110, 0, 212)    # #6e00d4
C_MED  = (168, 85, 247)   # #a855f7

FD   = '/home/user/WEB/carrossel-pmi/fonts'
LOGO = '/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png'
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


# ── Cores de acento — paleta da marca ────────────────────────────────────────
PURPLE = (168, 85, 247)   # #a855f7 roxo médio
VIBRANT = (110, 0, 212)   # #6e00d4 roxo vibrante

# ════════════════════════════════════════════════════════════════════════════
# POST A — TikTok Shop (5 slides)
# ════════════════════════════════════════════════════════════════════════════
print('=== POST A — TikTok Shop ===')

build('pa_s1_creator.jpg',
      ['SEU CONCORRENTE', 'JA ESTA VENDENDO', 'AO VIVO.'],
      'Voce ainda esta debatendo se deve entrar no TikTok Shop.',
      'pa_s1.png', PURPLE, 96, accent_idx={1, 2})

build('pa_s2_shopping.jpg',
      ['EM MENOS DE 1 ANO', 'O TIKTOK SHOP SE TORNOU', 'O 3 MAIOR', 'MARKETPLACE DO BRASIL.'],
      'Atras so de Mercado Livre e Shopee. Nao e tendencia. E mercado.',
      'pa_s2.png', PURPLE, 84, accent_idx={2, 3})

build('pa_s3_money.jpg',
      ['UM NEGOCIO', 'FOI DE R$ 4 MIL', 'A R$ 3,2 MILHOES', 'VENDENDO AO VIVO.'],
      'O faturamento por lives cresceu 96 vezes em um ano no Brasil.',
      'pa_s3.png', PURPLE, 90, accent_idx={2, 3})

build('pa_s4_cityphone.jpg',
      ['O CONSUMIDOR', 'QUER VER,', 'CONFIAR E COMPRAR', 'EM 30 SEGUNDOS.'],
      'Sem clicar em link. Sem esperar carregar pagina. Tudo dentro do app.',
      'pa_s4.png', PURPLE, 90, accent_idx={2})

build('pa_s5_glow.jpg',
      ['A QUESTAO', 'NAO E SE VOCE', 'DEVE ENTRAR.'],
      'E quanto voce ja perdeu esperando a hora certa. Siga @perrymarketingintegrado.',
      'pa_s5.png', PURPLE, 96, accent_idx={2})

# ════════════════════════════════════════════════════════════════════════════
# POST B — ROI de Vaidade (4 slides)
# ════════════════════════════════════════════════════════════════════════════
print('\n=== POST B — ROI de Vaidade ===')

build('pb_s1_data.jpg',
      ['QUEM AINDA POSTA', 'SÓ PARA CURTIDA', 'ESTA ATRASADO', '7 ANOS.'],
      'Seguir todas as tendencias caiu de 54 para 16 porcento em um ano. O mercado cresceu.',
      'pb_s1.png', VIBRANT, 88, accent_idx={2, 3})

build('pb_s2_likes.jpg',
      ['CURTIDA NAO', 'PAGA BOLETO.', 'ALCANCE NAO E', 'FATURAMENTO.'],
      'Engajamento sem conversao e so barulho. O mercado cobrou resultado e ganhou.',
      'pb_s2.png', VIBRANT, 90, accent_idx={0, 2})

build('pb_s3_dramatic.jpg',
      ['ANTES DE POSTAR,', 'RESPONDA:', 'ISSO GERA CLIENTE', 'OU SO APLAUSO?'],
      'Se a resposta demorar mais de 5 segundos, voce tem um problema de posicionamento.',
      'pb_s3.png', VIBRANT, 88, accent_idx={2, 3})

build('pb_s4_night.jpg',
      ['NAO E SOBRE', 'SER BONITO', 'NO FEED.'],
      'E sobre construir um negocio que vende todo dia. A PMI sempre defendeu isso.',
      'pb_s4.png', VIBRANT, 104, accent_idx={1, 2})

print(f'\nDone → {OUT}')
