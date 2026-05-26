#!/usr/bin/env python3
"""Post 3 — Famoso vs Rico (7 slides) — full bleed ideia01 style"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H    = 1080, 1350
C_BG    = (7, 6, 11)
C_VIB   = (110, 0, 212)
C_MED   = (168, 85, 247)
C_WHT   = (255, 255, 255)
C_SUB   = (210, 200, 225)
FADE_H  = 120

FD   = '/home/user/WEB/carrossel-pmi/fonts'
LOGO = '/home/user/WEB/carrossel-pmi/logo_ritmodamarca.png'
IMGS = '/home/user/WEB/carrossel-pmi'
OUT  = '/home/user/WEB/carrossel-pmi/post3'
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


def load_img(path):
    """Scale photo to canvas width, paste on dark canvas, fade bottom edge."""
    canvas = Image.new('RGB', (W, H), C_BG)
    img = Image.open(path).convert('RGB')
    nh = int(img.height * W / img.width)
    img = img.resize((W, nh), Image.LANCZOS)
    # soft fade from image bottom into dark canvas
    fade = Image.new('RGBA', (W, nh), (0, 0, 0, 0))
    fpx = fade.load()
    fade_start = max(0, nh - FADE_H)
    for y in range(fade_start, nh):
        a = int(255 * (y - fade_start) / FADE_H)
        for x in range(W):
            fpx[x, y] = (*C_BG, a)
    ir = img.convert('RGBA')
    ir.alpha_composite(fade)
    canvas.paste(ir.convert('RGB'), (0, 0))
    return canvas


def add_logo(canvas, h=70):
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
        print(f'  logo error: {e}')
        return canvas


def fit_font(d, lines, style, start=110, min_sz=44, max_w=None):
    if max_w is None:
        max_w = W - 132
    sz = start
    while sz >= min_sz:
        f = F(style, sz)
        bbs = [d.textbbox((0, 0), ln, font=f) for ln in lines]
        if all(bb[2] - bb[0] <= max_w for bb in bbs):
            return f
        sz -= 2
    return F(style, min_sz)


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


def build(bg_path, hl_lines, sub_text, out_path,
          accent_idx=None, hl_size_start=110, M=72):

    canvas = load_img(bg_path)
    d = ImageDraw.Draw(canvas)
    MAX_W = W - M - 60

    hl_f = fit_font(d, hl_lines, 'mextrabold', hl_size_start, 44, MAX_W)
    sub_sz = 36
    sub_f = F('isemibold', sub_sz)
    sub_lines = wrap_text(d, sub_text, sub_f, MAX_W)

    GAP_HL  = 18
    SUB_LEAD = int(sub_sz * 1.30)
    LOGO_H  = 70
    LOGO_PAD = 44

    # measure headline block
    bbs_hl = [d.textbbox((0, 0), ln, font=hl_f) for ln in hl_lines]
    hl_block_h = (sum(bb[3] - bb[1] for bb in bbs_hl)
                  + GAP_HL * (len(hl_lines) - 1))
    sub_block_h = SUB_LEAD * len(sub_lines)

    # layout bottom-up
    logo_top  = H - LOGO_PAD - LOGO_H
    sub_top   = logo_top - 32 - sub_block_h
    hl_top    = sub_top - 24 - hl_block_h
    accent_y  = hl_top - 20 - 4

    # accent bar
    d.rectangle([M, accent_y, M + 72, accent_y + 4], fill=C_VIB)

    # headline
    if accent_idx is None:
        accent_idx = set()
    y = hl_top
    for i, ln in enumerate(hl_lines):
        bb = bbs_hl[i]
        ink_h = bb[3] - bb[1]
        color = C_MED if i in accent_idx else C_WHT
        d.text((M - bb[0], y - bb[1]), ln, font=hl_f, fill=color)
        y += ink_h + (GAP_HL if i < len(hl_lines) - 1 else 0)

    # subtitle
    y = sub_top
    for ln in sub_lines:
        bb = d.textbbox((0, 0), ln, font=sub_f)
        d.text((M - bb[0], y - bb[1]), ln, font=sub_f, fill=C_SUB)
        y += SUB_LEAD

    canvas = add_logo(canvas, LOGO_H)
    canvas.save(out_path, quality=95)
    print(f'  ✓ {os.path.basename(out_path)}')


# ── Slides ───────────────────────────────────────────────────────────────────

SLIDES = [
    dict(
        bg='fp_p3_s1.jpg',
        hl_lines=['CONHEÇO PERFIS', 'COM 500K', 'QUE FATURAM', 'MENOS.'],
        sub='Do que quem tem 2k. Quer saber por quê?',
        accent_idx={2, 3},
        hl_size_start=100,
    ),
    dict(
        bg='fp_p3_s2.jpg',
        hl_lines=['O ERRO MAIS CARO', 'DO INSTAGRAM'],
        sub='Confundir visibilidade com autoridade.',
        accent_idx={1},
        hl_size_start=104,
    ),
    dict(
        bg='fp_p3_s3.jpg',
        hl_lines=['SEGUIDORES', 'NÃO PAGAM', 'BOLETO.'],
        sub='Cliente paga. E cliente vem de posicionamento, não de número.',
        accent_idx={2},
        hl_size_start=110,
    ),
    dict(
        bg='fp_p3_s4.jpg',
        hl_lines=['O QUE CRIA', 'AUTORIDADE REAL?'],
        sub='Clareza de nicho · Consistência · Prova · Especialidade.',
        accent_idx={1},
        hl_size_start=110,
    ),
    dict(
        bg='fp_p3_s5.jpg',
        hl_lines=['O QUE CRIA SÓ', 'SEGUIDORES', 'SEM VENDA?'],
        sub='Trends · Virais · Dancinha. Engajamento vazio não converte.',
        accent_idx={2},
        hl_size_start=104,
    ),
    dict(
        bg='fp_p3_s6.jpg',
        hl_lines=['VOCÊ QUER', 'SER FAMOSO', 'OU QUER', 'CLIENTES?'],
        sub='Essa pergunta muda tudo.',
        accent_idx={1, 3},
        hl_size_start=110,
    ),
    dict(
        bg='fp_p3_s7.jpg',
        hl_lines=['SALVA', 'ESSE POST.'],
        sub='Para mostrar para quem precisa ouvir isso.',
        accent_idx={1},
        hl_size_start=130,
    ),
]

if __name__ == '__main__':
    print('=== Post 3 — Famoso vs Rico ===')
    for i, s in enumerate(SLIDES, 1):
        build(
            bg_path=f'{IMGS}/{s["bg"]}',
            hl_lines=s['hl_lines'],
            sub_text=s['sub'],
            out_path=f'{OUT}/slide{i:02d}.png',
            accent_idx=s.get('accent_idx'),
            hl_size_start=s.get('hl_size_start', 110),
        )
    print(f'\nDone → {OUT}')
