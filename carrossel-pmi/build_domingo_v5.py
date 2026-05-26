#!/usr/bin/env python3
"""Domingo v5 — Full bleed, texto editorial sobre imagem. Estilo @ritmodamarca / @brandsdecoded__"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
OUT = "/home/user/WEB/carrossel-pmi/domingo_v5"
BG  = "/home/user/WEB/carrossel-pmi"
FD  = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"
LOGO = f"{BG}/logo_pmi_transparent.png"

os.makedirs(OUT, exist_ok=True)

FONTS = {
    "black":   "Roboto-Black.ttf",
    "bold":    "Roboto-Bold.ttf",
    "medium":  "Roboto-Medium.ttf",
    "regular": "Roboto-Regular.ttf",
    "light":   "Roboto-Light.ttf",
}

def F(style, size):
    return ImageFont.truetype(f"{FD}/{FONTS[style]}", size)

def tw(d, text, font):
    bb = d.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]

def load_bg(name):
    img = Image.open(f"{BG}/{name}").convert("RGB")
    r = img.width / img.height
    if r > W / H:
        nw, nh = int(H * r), H
    else:
        nw, nh = W, int(W / r)
    img = img.resize((nw, nh), Image.LANCZOS)
    return img.crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))

def gradient_overlay(canvas, start_pct=0.28, top_a=45, bot_a=225):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = ov.load()
    sy = int(H * start_pct)
    for y in range(H):
        a = top_a if y < sy else int(top_a + (bot_a - top_a) * (y - sy) / (H - sy))
        for x in range(W):
            px[x, y] = (0, 0, 0, min(a, 255))
    base = canvas.convert("RGBA")
    base.alpha_composite(ov)
    return base.convert("RGB")

def fit_headline(d, lines, max_w, max_h, start=130, min_sz=52):
    sz = start
    while sz >= min_sz:
        f = F("black", sz)
        lead = int(sz * 1.10)
        if all(tw(d, ln, f) <= max_w for ln in lines) and lead * len(lines) <= max_h:
            return f, lead
        sz -= 2
    f = F("black", min_sz)
    return f, int(min_sz * 1.10)

def add_logo(canvas, h=38):
    try:
        logo = Image.open(LOGO).convert("RGBA")
        lw = int(logo.width * h / logo.height)
        logo = logo.resize((lw, h), Image.LANCZOS)
        base = canvas.convert("RGBA")
        base.alpha_composite(logo, (72, 52))
        return base.convert("RGB")
    except:
        return canvas

def build(data, path):
    canvas = load_bg(data["bg"])
    canvas = gradient_overlay(canvas,
                               start_pct=data.get("grad_start", 0.28),
                               top_a=data.get("top_a", 45),
                               bot_a=data.get("bot_a", 225))

    M = 72          # left margin
    MAX_W = W - M - 60   # right breathing room

    d = ImageDraw.Draw(canvas)

    # ── Sub text ────────────────────────────────────────────────────────────
    sub_sz = 36
    sub_f = F("regular", sub_sz)
    sub_lead = int(sub_sz * 1.28)

    # wrap sub
    words = data["sub"].split()
    sub_lines, line = [], ""
    for w in words:
        test = f"{line} {w}".strip()
        if tw(d, test, sub_f) <= MAX_W:
            line = test
        else:
            if line:
                sub_lines.append(line)
            line = w
    if line:
        sub_lines.append(line)

    sub_block_h = sub_lead * len(sub_lines)

    # ── Headline ─────────────────────────────────────────────────────────────
    hl_lines = data["headline"]
    hl_max_h = int(H * 0.44)
    hl_f, hl_lead = fit_headline(d, hl_lines, MAX_W, hl_max_h)
    hl_block_h = hl_lead * len(hl_lines)

    # ── Vertical layout (bottom-up) ──────────────────────────────────────────
    HANDLE_Y  = 1295          # handle baseline
    GAP_SUB   = 20            # gap between sub and handle
    SEP_H     = 4             # accent separator bar
    GAP_SEP   = 18            # gap above separator
    GAP_HL    = 28            # gap between headline and separator

    sub_top   = HANDLE_Y - sub_block_h - GAP_SUB
    sep_y     = sub_top  - GAP_SEP - SEP_H
    hl_top    = sep_y    - GAP_HL  - hl_block_h

    accent = data["accent"]
    accent_idx = set(data.get("accent_lines", []))

    # draw headline lines
    for i, ln in enumerate(hl_lines):
        color = accent if i in accent_idx else (255, 255, 255)
        bb = d.textbbox((0, 0), ln, font=hl_f)
        d.text((M, hl_top + i * hl_lead - bb[1]), ln, font=hl_f, fill=color)

    # accent separator bar
    d.rectangle([M, sep_y, M + 72, sep_y + SEP_H], fill=accent)

    # draw sub lines
    sub_color = (210, 200, 225)
    for i, ln in enumerate(sub_lines):
        bb = d.textbbox((0, 0), ln, font=sub_f)
        d.text((M, sub_top + i * sub_lead - bb[1]), ln, font=sub_f, fill=sub_color)

    # handle
    hf = F("medium", 26)
    hnd = "@pmiconsultoria"
    hbb = d.textbbox((0, 0), hnd, font=hf)
    d.text((M, HANDLE_Y - hbb[1]), hnd, font=hf, fill=(170, 160, 190))

    canvas = add_logo(canvas)
    canvas.save(path, quality=95)
    print(f"  ✓ {os.path.basename(path)}")


# ════════════════════════════════════════════════════════════════════════════
# CARROSSEL A — IA Saturou o Feed
# ════════════════════════════════════════════════════════════════════════════
ACC_A = (175, 80, 255)

SLIDES_A = [
    dict(
        bg="bg_v2_v2_a_s01.png",
        headline=["O ROBÔ NÃO", "CRIA.", "ELE COPIA."],
        accent_lines=[1, 2],
        accent=ACC_A,
        sub="Seu cliente já percebeu. A questão é: você ainda faz diferença?",
    ),
    dict(
        bg="bg_v2_v2_a_s02.png",
        headline=["SEU CONTEÚDO É", "ORIGINAL", "OU SÓ MAIS UM?"],
        accent_lines=[1],
        accent=ACC_A,
        sub="A IA produziu bilhões de textos iguais ao seu. O que só você tem?",
    ),
    dict(
        bg="bg_v2_v2_a_s03.png",
        headline=["VOCÊ", "OU O", "ALGORITMO?"],
        accent_lines=[2],
        accent=ACC_A,
        sub="Quem está por trás da sua marca de verdade?",
    ),
    dict(
        bg="bg_v2_v2_a_s04.png",
        headline=["ESCREVER COMO", "MÁQUINA É FÁCIL.", "SER LEMBRADO,", "NÃO."],
        accent_lines=[3],
        accent=ACC_A,
        sub="Humanidade vende mais que velocidade.",
    ),
    dict(
        bg="bg_v2_v2_a_s05.png",
        headline=["O PRÓXIMO", "PASSO É", "SEU."],
        accent_lines=[2],
        accent=ACC_A,
        sub="Parece IA demais. Humanize antes que seja tarde.",
    ),
]

# ════════════════════════════════════════════════════════════════════════════
# CARROSSEL B — Viral Morreu
# ════════════════════════════════════════════════════════════════════════════
ACC_B = (255, 200, 0)

SLIDES_B = [
    dict(
        bg="bg_v2_v2_b_s01.png",
        headline=["VIRAL NÃO", "PAGA CONTA."],
        accent_lines=[0],
        accent=ACC_B,
        sub="Comunidade sim. Repense o que você está construindo.",
    ),
    dict(
        bg="bg_v2_v2_b_s02.png",
        headline=["1 MILHÃO DE VIEWS.", "ZERO CLIENTES."],
        accent_lines=[0],
        accent=(255, 140, 0),
        sub="Alcance sem conversão é só barulho.",
    ),
    dict(
        bg="bg_v2_v2_b_s03.png",
        headline=["1.000 PESSOAS", "QUE COMPRAM", "VALEM MAIS."],
        accent_lines=[0],
        accent=ACC_B,
        sub="Do que 1 milhão que só passam o dedo.",
    ),
    dict(
        bg="bg_v2_v2_b_s04.png",
        headline=["VOCÊ BUSCA ALCANCE.", "O MERCADO QUER", "CONFIANÇA."],
        accent_lines=[2],
        accent=ACC_B,
        sub="São métricas que não aparecem no relatório de likes.",
    ),
    dict(
        bg="bg_v2_v2_b_s05.png",
        headline=["PARE DE CORRER", "ATRÁS DO VIRAL.", "CONSTRUA ALGO", "REAL."],
        accent_lines=[3],
        accent=(255, 140, 0),
        sub="O que dura não é o que explode. É o que conecta.",
    ),
]

# ════════════════════════════════════════════════════════════════════════════
# CARROSSEL C — 47M Empreendedores
# ════════════════════════════════════════════════════════════════════════════
ACC_C = (220, 55, 95)

SLIDES_C = [
    dict(
        bg="bg_domingo_dom_c_s01.png",
        headline=["47 MILHÕES DE", "EMPREENDEDORES.", "UM MERCADO SÓ."],
        accent_lines=[0],
        accent=ACC_C,
        sub="A maioria vende o mesmo do mesmo jeito.",
        grad_start=0.22, top_a=35, bot_a=220,
    ),
    dict(
        bg="bg_domingo_dom_c_s02.png",
        headline=["SEU CONCORRENTE", "PARECE COM", "VOCÊ."],
        accent_lines=[2],
        accent=ACC_C,
        sub="Esse é o maior problema do seu negócio hoje.",
        grad_start=0.22, top_a=35, bot_a=220,
    ),
    dict(
        bg="bg_domingo_dom_c_s03.png",
        headline=["DIFERENCIAÇÃO", "NÃO É PREÇO.", "É CORAGEM."],
        accent_lines=[0],
        accent=ACC_C,
        sub="É posicionamento. É escolha. É identidade própria.",
        grad_start=0.22, top_a=35, bot_a=220,
    ),
    dict(
        bg="bg_domingo_dom_c_s04.png",
        headline=["47 MILHÕES", "DISPUTANDO", "ATENÇÃO."],
        accent_lines=[0],
        accent=ACC_C,
        sub="Quem tem identidade própria já saiu na frente.",
        grad_start=0.22, top_a=35, bot_a=220,
    ),
    dict(
        bg="bg_domingo_dom_c_s05.png",
        headline=["O MERCADO NÃO", "ESTÁ SATURADO.", "ESTÁ CHEIO", "DE IGUAIS."],
        accent_lines=[3],
        accent=ACC_C,
        sub="Esse é o espaço que a PMI ajuda você a ocupar.",
        grad_start=0.22, top_a=35, bot_a=220,
    ),
]

if __name__ == "__main__":
    print("=== A — IA Saturou o Feed ===")
    for i, s in enumerate(SLIDES_A, 1):
        build(s, f"{OUT}/a_slide{i:02d}.png")

    print("\n=== B — Viral Morreu ===")
    for i, s in enumerate(SLIDES_B, 1):
        build(s, f"{OUT}/b_slide{i:02d}.png")

    print("\n=== C — 47M Empreendedores ===")
    for i, s in enumerate(SLIDES_C, 1):
        build(s, f"{OUT}/c_slide{i:02d}.png")

    print(f"\nDone → {OUT}")
