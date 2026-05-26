#!/usr/bin/env python3
"""Post 3 — Diferença Famoso e Rico (7 slides)"""

from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1080, 1350
FD   = '/home/user/WEB/carrossel-pmi/fonts'
LOGO = '/home/user/WEB/carrossel-pmi/logo_ritmodamarca.png'
OUT  = '/home/user/WEB/carrossel-pmi/post3'
os.makedirs(OUT, exist_ok=True)

# ── Brand colors ─────────────────────────────────────────────────────────
C_DARK   = (26,  5, 51)    # #1a0533
C_VIB    = (110, 0, 212)   # #6e00d4
C_MED    = (168, 85, 247)  # #a855f7
C_WHITE  = (255, 255, 255)
C_SOFT   = (243, 232, 255) # #f3e8ff
C_GREEN  = (34, 197, 94)
C_RED    = (239, 68, 68)

def F(style, size):
    m = {
        'mblack':    'Montserrat-Black.ttf',
        'mextrabold':'Montserrat-ExtraBold.ttf',
        'mbold':     'Montserrat-Bold.ttf',
        'msemibold': 'Montserrat-SemiBold.ttf',
        'mregular':  'Montserrat-Regular.ttf',
        'iregular':  'Inter-Regular.ttf',
        'isemibold': 'Inter-SemiBold.ttf',
    }
    return ImageFont.truetype(f'{FD}/{m[style]}', size)

def tw(d, t, f):
    bb = d.textbbox((0,0), t, font=f); return bb[2]-bb[0]

def th(d, t, f):
    bb = d.textbbox((0,0), t, font=f); return bb[3]-bb[1]

def draw_text(d, text, font, x, y, fill, anchor='lt'):
    bb = d.textbbox((0,0), text, font=font)
    if anchor == 'center':
        x = x - (bb[2]-bb[0])//2
    d.text((x - bb[0], y - bb[1]), text, font=font, fill=fill)
    return bb[3] - bb[1]

def wrap(d, text, font, max_w):
    words = text.split(); lines, line = [], ''
    for w in words:
        test = f'{line} {w}'.strip()
        bb = d.textbbox((0,0), test, font=font)
        if bb[2]-bb[0] <= max_w: line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

def add_logo(canvas, y=None, h=56, bg=None):
    logo = Image.open(LOGO).convert('RGBA')
    lw = int(logo.width * h / logo.height)
    logo = logo.resize((lw, h), Image.LANCZOS)
    if y is None: y = H - h - 40
    x = (W - lw) // 2
    base = canvas.convert('RGBA'); base.alpha_composite(logo, (x, y))
    return base.convert('RGB')

def gradient_bg(c1, c2, direction='v'):
    img = Image.new('RGB', (W, H))
    px = img.load()
    for y in range(H):
        for x in range(W):
            if direction == 'v':
                t = y / H
            else:
                t = x / W
            r = int(c1[0] + (c2[0]-c1[0])*t)
            g = int(c1[1] + (c2[1]-c1[1])*t)
            b = int(c1[2] + (c2[2]-c1[2])*t)
            px[x,y] = (r,g,b)
    return img

# ════════════════════════════════════════════════════════════════════════
# SLIDE 1 — CAPA
# ════════════════════════════════════════════════════════════════════════
def slide1():
    canvas = gradient_bg(C_DARK, (18, 2, 38))
    d = ImageDraw.Draw(canvas)
    M = 80

    # top accent bar
    d.rectangle([M, 90, M+60, 96], fill=C_VIB)

    # label tag
    f_tag = F('msemibold', 24)
    draw_text(d, 'POST 3 · FAMOSO vs RICO', f_tag, M, 112, C_MED)

    # Main text
    lines = [
        'Conheço perfis',
        'com 500k que',
        'faturam MENOS',
        'do que quem tem 2k.',
    ]
    f_hl = F('mextrabold', 86)
    f_hl2 = F('mextrabold', 86)

    # fit font
    sz = 86
    while sz >= 40:
        f = F('mextrabold', sz)
        if all(tw(d, ln, f) <= W - 2*M for ln in lines): break
        sz -= 2
    f_hl = F('mextrabold', sz)

    y = 210
    for i, ln in enumerate(lines):
        bb = d.textbbox((0,0), ln, font=f_hl)
        ink_h = bb[3]-bb[1]
        color = C_MED if 'MENOS' in ln else C_WHITE
        d.text((M-bb[0], y-bb[1]), ln, font=f_hl, fill=color)
        y += ink_h + 14

    # sub
    f_sub = F('isemibold', 38)
    sub = 'Quer saber por quê?'
    bb = d.textbbox((0,0), sub, font=f_sub)
    d.text((M-bb[0], y+28-bb[1]), sub, font=f_sub, fill=C_SOFT)

    # like vs $ icons (drawn)
    icon_y = y + 120
    # Like icon (thumb up simplified)
    d.rounded_rectangle([M, icon_y, M+90, icon_y+90], radius=18, fill=C_VIB)
    f_icon = F('mextrabold', 44)
    bb = d.textbbox((0,0), '♥', font=f_icon)
    d.text((M+45-(bb[2]-bb[0])//2-bb[0], icon_y+45-(bb[3]-bb[1])//2-bb[1]), '♥', font=f_icon, fill=C_WHITE)

    d.rounded_rectangle([M+110, icon_y, M+200, icon_y+90], radius=18, fill=(50,12,100))
    bb = d.textbbox((0,0), '$', font=f_icon)
    d.text((M+155-(bb[2]-bb[0])//2-bb[0], icon_y+45-(bb[3]-bb[1])//2-bb[1]), '$', font=f_icon, fill=C_GREEN)

    # swipe arrow at bottom
    arrow_y = H - 130
    f_arr = F('msemibold', 26)
    arrow_txt = 'Deslize para ver →'
    bb = d.textbbox((0,0), arrow_txt, font=f_arr)
    cx = W//2
    d.text((cx-(bb[2]-bb[0])//2-bb[0], arrow_y-bb[1]), arrow_txt, font=f_arr, fill=C_MED)

    # dots
    for i in range(7):
        color = C_VIB if i == 0 else (80, 40, 120)
        d.ellipse([cx-60+i*20-4, arrow_y+40, cx-60+i*20+4, arrow_y+48], fill=color)

    canvas = add_logo(canvas, y=H-90, h=48)
    canvas.save(f'{OUT}/slide01.png', quality=95)
    print('✓ slide01')

# ════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Visibilidade vs Autoridade
# ════════════════════════════════════════════════════════════════════════
def slide2():
    canvas = gradient_bg(C_DARK, (22, 4, 45))
    d = ImageDraw.Draw(canvas)
    M = 72

    # header
    f_label = F('msemibold', 22)
    draw_text(d, 'O ERRO MAIS CARO DO INSTAGRAM', f_label, M, 80, C_MED)
    d.rectangle([M, 114, W-M, 117], fill=C_VIB)

    # headline
    f_hl = F('mextrabold', 68)
    lines = ['Confundir', 'VISIBILIDADE', 'com AUTORIDADE.']
    sz = 68
    while sz >= 36:
        f = F('mextrabold', sz)
        if all(tw(d,ln,f) <= W-2*M for ln in lines): break
        sz -= 2
    f_hl = F('mextrabold', sz)

    y = 148
    for ln in lines:
        bb = d.textbbox((0,0), ln, font=f_hl)
        color = C_MED if ln in ('VISIBILIDADE', 'AUTORIDADE.') else C_WHITE
        d.text((M-bb[0], y-bb[1]), ln, font=f_hl, fill=color)
        y += (bb[3]-bb[1]) + 12

    # sub
    f_sub = F('iregular', 34)
    draw_text(d, 'São completamente diferentes.', f_sub, M, y+20, C_SOFT)

    # divider
    div_y = int(H * 0.52)
    d.rectangle([0, div_y, W, div_y+2], fill=(60, 20, 100))

    # left panel — VISIBILIDADE
    lx = W//4
    # eye circle
    eye_y = div_y + 90
    r = 75
    d.ellipse([lx-r, eye_y-r, lx+r, eye_y+r], fill=(40, 10, 80))
    d.ellipse([lx-r, eye_y-r, lx+r, eye_y+r], outline=C_MED, width=3)
    # eye shape
    d.ellipse([lx-30, eye_y-18, lx+30, eye_y+18], fill=C_MED)
    d.ellipse([lx-10, eye_y-10, lx+10, eye_y+10], fill=C_DARK)

    f_card = F('mbold', 28)
    f_card_sub = F('iregular', 22)
    bb = d.textbbox((0,0), 'VISIBILIDADE', font=f_card)
    d.text((lx-(bb[2]-bb[0])//2-bb[0], eye_y+r+24-bb[1]), 'VISIBILIDADE', font=f_card, fill=C_WHITE)
    bb2 = d.textbbox((0,0), 'Ser visto', font=f_card_sub)
    d.text((lx-(bb2[2]-bb2[0])//2-bb2[0], eye_y+r+66-bb2[1]), 'Ser visto', font=f_card_sub, fill=C_MED)

    # ≠ in center
    f_neq = F('mextrabold', 72)
    cx = W//2
    bb = d.textbbox((0,0), '≠', font=f_neq)
    d.text((cx-(bb[2]-bb[0])//2-bb[0], eye_y-bb[1]), '≠', font=f_neq, fill=C_VIB)

    # right panel — AUTORIDADE
    rx = 3*W//4
    # trophy
    tr_y = div_y + 90
    # cup body
    d.ellipse([rx-r, tr_y-r, rx+r, tr_y+r], fill=(40, 10, 80))
    d.ellipse([rx-r, tr_y-r, rx+r, tr_y+r], outline=C_MED, width=3)
    f_trophy = F('mextrabold', 60)
    bb = d.textbbox((0,0), '🏆', font=f_trophy)
    # fallback since emoji might not render
    f_t = F('mbold', 52)
    bb = d.textbbox((0,0), '★', font=f_t)
    d.text((rx-(bb[2]-bb[0])//2-bb[0], tr_y-(bb[3]-bb[1])//2-bb[1]), '★', font=f_t, fill=C_MED)

    bb = d.textbbox((0,0), 'AUTORIDADE', font=f_card)
    d.text((rx-(bb[2]-bb[0])//2-bb[0], tr_y+r+24-bb[1]), 'AUTORIDADE', font=f_card, fill=C_WHITE)
    bb2 = d.textbbox((0,0), 'Ser escolhido', font=f_card_sub)
    d.text((rx-(bb2[2]-bb2[0])//2-bb2[0], tr_y+r+66-bb2[1]), 'Ser escolhido', font=f_card_sub, fill=C_MED)

    canvas = add_logo(canvas, h=44)
    canvas.save(f'{OUT}/slide02.png', quality=95)
    print('✓ slide02')

# ════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Seguidores vs Cliente (bar chart)
# ════════════════════════════════════════════════════════════════════════
def slide3():
    canvas = gradient_bg(C_DARK, (15, 1, 32))
    d = ImageDraw.Draw(canvas)
    M = 72

    f_label = F('msemibold', 22)
    draw_text(d, 'SEGUIDORES NÃO PAGAM BOLETO', f_label, M, 80, C_MED)
    d.rectangle([M, 114, W-M, 117], fill=C_VIB)

    f_hl = F('mextrabold', 56)
    lines = ['Cliente paga.', 'E cliente vem de', 'POSICIONAMENTO,', 'não de número.']
    sz = 56
    while sz >= 32:
        f = F('mextrabold', sz)
        if all(tw(d,ln,f) <= W-2*M for ln in lines): break
        sz -= 2
    f_hl = F('mextrabold', sz)

    y = 148
    for ln in lines:
        bb = d.textbbox((0,0), ln, font=f_hl)
        color = C_MED if 'POSICIONAMENTO' in ln else C_WHITE
        d.text((M-bb[0], y-bb[1]), ln, font=f_hl, fill=color)
        y += (bb[3]-bb[1]) + 10

    # Chart area
    chart_top = y + 48
    chart_bot = H - 160
    chart_h = chart_bot - chart_top
    bar_w = 180
    gap = 100

    col_a_x = W//2 - gap//2 - bar_w   # left bar center
    col_b_x = W//2 + gap//2            # right bar center

    # Column A: 500k seguidores — small revenue bar
    rev_a = int(chart_h * 0.22)
    fol_a = int(chart_h * 0.90)

    # Column B: 2k seguidores — big revenue bar
    rev_b = int(chart_h * 0.85)
    fol_b = int(chart_h * 0.12)

    # draw bars
    def bar(x, top_y, bh, color, label_top, label_bot):
        d.rounded_rectangle([x, chart_bot-bh, x+bar_w, chart_bot], radius=12, fill=color)
        f_val = F('mextrabold', 28)
        bb = d.textbbox((0,0), label_top, font=f_val)
        d.text((x+bar_w//2-(bb[2]-bb[0])//2-bb[0], chart_bot-bh-44-bb[1]), label_top, font=f_val, fill=C_WHITE)
        f_bot = F('iregular', 22)
        bb2 = d.textbbox((0,0), label_bot, font=f_bot)
        d.text((x+bar_w//2-(bb2[2]-bb2[0])//2-bb2[0], chart_bot+12-bb2[1]), label_bot, font=f_bot, fill=C_SOFT)

    bar(col_a_x, chart_top, rev_a, (80, 30, 130), 'R$ baixo', '500k')
    bar(col_b_x, chart_top, rev_b, C_VIB, 'R$ alto', '2k')

    # follower mini bars (ghost)
    d.rounded_rectangle([col_a_x+10, chart_bot-fol_a, col_a_x+bar_w-10, chart_bot], radius=8, outline=(80,40,120), width=2)
    d.rounded_rectangle([col_b_x+10, chart_bot-fol_b, col_b_x+bar_w-10, chart_bot], radius=8, outline=(80,40,120), width=2)

    # labels
    f_leg = F('iregular', 20)
    d.text((col_a_x, chart_bot+55), '□ seguidores', font=f_leg, fill=(120,80,180))
    d.rectangle([col_a_x, chart_bot+63, col_a_x+14, chart_bot+71], fill=(80,40,120))

    # chart title
    f_ct = F('msemibold', 22)
    bb = d.textbbox((0,0), 'Faturamento ↑', font=f_ct)
    d.text((M-bb[0], chart_top-bb[1]), 'Faturamento ↑', font=f_ct, fill=C_MED)

    canvas = add_logo(canvas, h=40)
    canvas.save(f'{OUT}/slide03.png', quality=95)
    print('✓ slide03')

# ════════════════════════════════════════════════════════════════════════
# SLIDE 4 — O que cria autoridade (checklist verde)
# ════════════════════════════════════════════════════════════════════════
def slide4():
    canvas = Image.new('RGB', (W,H), (30, 8, 58))
    d = ImageDraw.Draw(canvas)
    M = 72

    f_label = F('msemibold', 22)
    draw_text(d, 'O QUE CRIA AUTORIDADE REAL?', f_label, M, 80, C_GREEN)
    d.rectangle([M, 114, W-M, 117], fill=C_GREEN)

    f_hl = F('mextrabold', 58)
    draw_text(d, 'Isso constrói', f_hl, M, 148, C_WHITE)
    draw_text(d, 'clientes.', f_hl, M, 148+68, C_GREEN)

    items = [
        ('◎', 'Clareza do nicho',         'Para quem você fala e qual problema resolve'),
        ('◎', 'Consistência de mensagem',  'Mesmo tom, toda semana, em todo canal'),
        ('◎', 'Prova de transformação',    'Resultados reais de quem você já ajudou'),
        ('◎', 'Especialidade demonstrada', 'Conteúdo que prova o que você sabe fazer'),
    ]

    f_item  = F('mbold', 34)
    f_desc  = F('iregular', 24)
    start_y = 360
    gap_item = 24

    for icon, title, desc in items:
        # green check circle
        cx_i, cy_i = M+26, start_y+26
        d.ellipse([M, start_y, M+52, start_y+52], fill=C_GREEN)
        f_ck = F('mbold', 26)
        bb = d.textbbox((0,0), '✓', font=f_ck)
        d.text((cx_i-(bb[2]-bb[0])//2-bb[0], cy_i-(bb[3]-bb[1])//2-bb[1]), '✓', font=f_ck, fill=(10,40,10))

        # title
        tx = M + 70
        bb_t = d.textbbox((0,0), title, font=f_item)
        d.text((tx-bb_t[0], start_y-bb_t[1]), title, font=f_item, fill=C_WHITE)
        # desc
        bb_d = d.textbbox((0,0), desc, font=f_desc)
        d.text((tx-bb_d[0], start_y+(bb_t[3]-bb_t[1])+6-bb_d[1]), desc, font=f_desc, fill=C_MED)

        item_h = (bb_t[3]-bb_t[1]) + 6 + (bb_d[3]-bb_d[1])
        start_y += max(item_h, 56) + gap_item
        # separator line
        d.rectangle([M+70, start_y-gap_item//2, W-M, start_y-gap_item//2+1], fill=(60,20,100))

    canvas = add_logo(canvas, h=44)
    canvas.save(f'{OUT}/slide04.png', quality=95)
    print('✓ slide04')

# ════════════════════════════════════════════════════════════════════════
# SLIDE 5 — O que cria só seguidores (checklist vermelho)
# ════════════════════════════════════════════════════════════════════════
def slide5():
    canvas = Image.new('RGB', (W,H), (30, 8, 58))
    d = ImageDraw.Draw(canvas)
    M = 72

    f_label = F('msemibold', 22)
    draw_text(d, 'O QUE CRIA SÓ SEGUIDORES SEM VENDA?', f_label, M, 80, C_RED)
    d.rectangle([M, 114, W-M, 117], fill=C_RED)

    f_hl = F('mextrabold', 58)
    draw_text(d, 'Isso afasta', f_hl, M, 148, C_WHITE)
    draw_text(d, 'clientes.', f_hl, M, 148+68, C_RED)

    items = [
        ('✗', 'Trends sem contexto',              'Você vira entretenimento, não referência'),
        ('✗', 'Virais desconectados do negócio',  'Alcance sem propósito não converte'),
        ('✗', 'Dancinha sem posicionamento',       'Engajamento vazio não paga conta'),
    ]

    f_item  = F('mbold', 34)
    f_desc  = F('iregular', 24)
    start_y = 360

    for icon, title, desc in items:
        cx_i, cy_i = M+26, start_y+26
        d.ellipse([M, start_y, M+52, start_y+52], fill=C_RED)
        f_ck = F('mbold', 28)
        bb = d.textbbox((0,0), '✗', font=f_ck)
        d.text((cx_i-(bb[2]-bb[0])//2-bb[0], cy_i-(bb[3]-bb[1])//2-bb[1]), '✗', font=f_ck, fill=(80,5,5))

        tx = M + 70
        bb_t = d.textbbox((0,0), title, font=f_item)
        d.text((tx-bb_t[0], start_y-bb_t[1]), title, font=f_item, fill=C_WHITE)
        bb_d = d.textbbox((0,0), desc, font=f_desc)
        d.text((tx-bb_d[0], start_y+(bb_t[3]-bb_t[1])+6-bb_d[1]), desc, font=f_desc, fill=C_MED)

        item_h = (bb_t[3]-bb_t[1]) + 6 + (bb_d[3]-bb_d[1])
        start_y += max(item_h, 56) + 28
        d.rectangle([M+70, start_y-14, W-M, start_y-13], fill=(80,20,40))

    # contrast note
    f_note = F('isemibold', 26)
    note = '← Compare com o slide anterior'
    bb = d.textbbox((0,0), note, font=f_note)
    d.text((W//2-(bb[2]-bb[0])//2-bb[0], H-200-bb[1]), note, font=f_note, fill=(160,80,100))

    canvas = add_logo(canvas, h=44)
    canvas.save(f'{OUT}/slide05.png', quality=95)
    print('✓ slide05')

# ════════════════════════════════════════════════════════════════════════
# SLIDE 6 — A pergunta que muda tudo (minimalista)
# ════════════════════════════════════════════════════════════════════════
def slide6():
    canvas = Image.new('RGB', (W,H), C_DARK)
    d = ImageDraw.Draw(canvas)

    # subtle center glow
    glow = Image.new('RGBA', (W,H), (0,0,0,0))
    gpx = glow.load()
    cx, cy = W//2, H//2
    for y in range(H):
        for x in range(W):
            dist = math.sqrt((x-cx)**2 + (y-cy)**2)
            a = max(0, int(40 * (1 - dist/600)))
            gpx[x,y] = (110, 0, 212, a)
    base = canvas.convert('RGBA'); base.alpha_composite(glow)
    canvas = base.convert('RGB')
    d = ImageDraw.Draw(canvas)

    # top label
    f_label = F('msemibold', 22)
    bb = d.textbbox((0,0), 'A PERGUNTA QUE MUDA TUDO', font=f_label)
    draw_text(d, 'A PERGUNTA QUE MUDA TUDO', f_label, W//2-bb[2]//2, 88, C_MED)

    # thin line
    d.rectangle([W//2-40, 124, W//2+40, 127], fill=C_VIB)

    # big question — Montserrat ExtraBold
    q1 = 'Você quer'
    q2 = 'ser famoso'
    q3 = 'ou quer clientes'
    q4 = 'que pagam bem'
    q5 = 'por você?'
    q_lines = [q1, q2, q3, q4, q5]

    sz = 88
    M = 72
    while sz >= 40:
        f = F('mextrabold', sz)
        if all(tw(d,ln,f) <= W-2*M for ln in q_lines): break
        sz -= 2
    fq = F('mextrabold', sz)

    total_h = 0
    bbs_q = [d.textbbox((0,0), ln, font=fq) for ln in q_lines]
    for bb in bbs_q: total_h += bb[3]-bb[1]
    total_h += 16 * (len(q_lines)-1)

    y = (H - total_h) // 2 - 30
    for i, ln in enumerate(q_lines):
        bb = bbs_q[i]
        color = C_MED if i in (1, 3) else C_WHITE
        cx_txt = W//2 - (bb[2]-bb[0])//2
        d.text((cx_txt-bb[0], y-bb[1]), ln, font=fq, fill=color)
        y += (bb[3]-bb[1]) + 16

    canvas = add_logo(canvas, h=44)
    canvas.save(f'{OUT}/slide06.png', quality=95)
    print('✓ slide06')

# ════════════════════════════════════════════════════════════════════════
# SLIDE 7 — CTA
# ════════════════════════════════════════════════════════════════════════
def slide7():
    canvas = Image.new('RGB', (W,H), C_VIB)
    d = ImageDraw.Draw(canvas)

    # subtle texture dots
    import random
    rng = random.Random(99)
    for _ in range(600):
        x = rng.randint(0, W); y = rng.randint(0, H)
        r = rng.randint(1,3)
        a_val = rng.randint(15,40)
        dot = Image.new('RGBA',(W,H),(0,0,0,0))
        dd = ImageDraw.Draw(dot)
        dd.ellipse([x-r,y-r,x+r,y+r], fill=(255,255,255,a_val))
        base = canvas.convert('RGBA'); base.alpha_composite(dot)
        canvas = base.convert('RGB')
        d = ImageDraw.Draw(canvas)

    # big logo centered top
    logo = Image.open(LOGO).convert('RGBA')
    lh = 110; lw = int(logo.width * lh / logo.height)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    base = canvas.convert('RGBA')
    base.alpha_composite(logo, ((W-lw)//2, 140))
    canvas = base.convert('RGB')
    d = ImageDraw.Draw(canvas)

    # divider
    d.rectangle([W//2-60, 280, W//2+60, 283], fill=(255,255,255,120))

    # CTA text
    f_cta1 = F('mextrabold', 92)
    f_cta2 = F('msemibold', 40)
    f_sub  = F('iregular', 30)

    line1 = 'Salva'
    line2 = 'esse post.'
    line3 = 'Para mostrar para quem'
    line4 = 'precisa ouvir isso.'

    y = 340
    for ln, fnt, gap in [(line1,f_cta1,8),(line2,f_cta1,48),(line3,f_cta2,4),(line4,f_cta2,60)]:
        bb = d.textbbox((0,0), ln, font=fnt)
        cx_t = W//2-(bb[2]-bb[0])//2
        d.text((cx_t-bb[0], y-bb[1]), ln, font=fnt, fill=C_WHITE)
        y += (bb[3]-bb[1]) + gap

    # final line
    f_fin = F('msemibold', 26)
    fin = '→ @ritmodamarca'
    bb = d.textbbox((0,0), fin, font=f_fin)
    d.text((W//2-(bb[2]-bb[0])//2-bb[0], y+20-bb[1]), fin, font=f_fin, fill=C_SOFT)

    canvas.save(f'{OUT}/slide07.png', quality=95)
    print('✓ slide07')

if __name__ == '__main__':
    print('=== Post 3 — Diferença Famoso e Rico ===')
    slide1(); slide2(); slide3(); slide4()
    slide5(); slide6(); slide7()
    print(f'Done → {OUT}')
