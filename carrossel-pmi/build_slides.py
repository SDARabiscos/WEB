#!/usr/bin/env python3
"""PMI Carousel Builder — dark navy + grid + violet accent."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1080, 1350

# ── Brand colors ──────────────────────────────────────────────────────────────
BG          = (8,  10, 22)      # deep navy
GRID_LINE   = (20, 24, 50)      # subtle grid
ACCENT      = (134, 0, 255)     # violet #8600FF
ACCENT_GLOW = (80,  0, 160)     # darker violet for glow layers
WHITE       = (255, 255, 255)
GRAY        = (160, 160, 185)
LIGHT_GRAY  = (210, 210, 225)

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_DIR_ROBOTO = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"
FONT_DIR_COND   = "/usr/share/fonts/truetype/roboto/unhinted"

def font(name, size):
    paths = {
        "black":   f"{FONT_DIR_ROBOTO}/Roboto-Black.ttf",
        "bold":    f"{FONT_DIR_ROBOTO}/Roboto-Bold.ttf",
        "medium":  f"{FONT_DIR_ROBOTO}/Roboto-Medium.ttf",
        "regular": f"{FONT_DIR_ROBOTO}/Roboto-Regular.ttf",
        "light":   f"{FONT_DIR_ROBOTO}/Roboto-Light.ttf",
        "cond_bold": f"{FONT_DIR_COND}/RobotoCondensed-Bold.ttf",
    }
    return ImageFont.truetype(paths[name], size)


# ── Background helpers ─────────────────────────────────────────────────────────
def make_background():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # dot-grid pattern
    spacing = 54
    for x in range(0, W + spacing, spacing):
        for y in range(0, H + spacing, spacing):
            d.ellipse([x-1, y-1, x+1, y+1], fill=GRID_LINE)

    # subtle violet radial glow — top-left corner
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    dg = ImageDraw.Draw(glow)
    for r in range(600, 0, -30):
        alpha = int(18 * (1 - r / 600))
        c = tuple(min(255, v + alpha) for v in BG)
        dg.ellipse([-r + 80, -r + 80, r + 80, r + 80], fill=c)
    # tint with accent
    glow_tint = Image.new("RGB", (W, H), (0, 0, 0))
    dtint = ImageDraw.Draw(glow_tint)
    for r in range(500, 0, -25):
        alpha = int(25 * (1 - r / 500))
        c = (min(255, ACCENT[0] * alpha // 255 + BG[0]),
             min(255, ACCENT[1] * alpha // 255 + BG[1]),
             min(255, ACCENT[2] * alpha // 255 + BG[2]))
        dtint.ellipse([-r + 60, -r + 60, r + 60, r + 60], fill=c)
    img = Image.blend(img, glow_tint, 0.18)

    # bottom-right glow
    glow2 = Image.new("RGB", (W, H), BG)
    dg2 = ImageDraw.Draw(glow2)
    for r in range(700, 0, -35):
        alpha = int(20 * (1 - r / 700))
        c = (min(255, ACCENT[0] * alpha // 255 + BG[0]),
             min(255, ACCENT[1] * alpha // 255 + BG[1]),
             min(255, ACCENT[2] * alpha // 255 + BG[2]))
        dg2.ellipse([W - r - 100, H - r - 100, W + r - 100, H + r - 100], fill=c)
    img = Image.blend(img, glow2, 0.12)

    # redraw dots on top of glow
    d2 = ImageDraw.Draw(img)
    for x in range(0, W + spacing, spacing):
        for y in range(0, H + spacing, spacing):
            d2.ellipse([x-1, y-1, x+1, y+1], fill=GRID_LINE)

    return img


def add_logo(img, logo_path, margin=48, height=60):
    """Place logo bottom-center."""
    logo = Image.open(logo_path).convert("RGBA")
    ratio = height / logo.height
    new_w = int(logo.width * ratio)
    logo = logo.resize((new_w, height), Image.LANCZOS)
    x = (W - new_w) // 2
    y = H - margin - height
    # paste with alpha
    img.paste(logo, (x, y), logo)
    return img


def add_counter(d, current, total, size=28):
    """Slide counter top-right."""
    f = font("regular", size)
    txt = f"{current:02d} / {total:02d}"
    bbox = d.textbbox((0, 0), txt, font=f)
    tw = bbox[2] - bbox[0]
    x = W - 64 - tw
    y = 60
    d.text((x, y), txt, font=f, fill=GRAY)


def add_accent_line(d, y, x_start=64, x_end=W - 64, thickness=2):
    """Thin violet horizontal rule."""
    d.rectangle([x_start, y, x_end, y + thickness], fill=ACCENT)


def wrap_text(text, fnt, max_width, draw):
    """Word-wrap text to fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=fnt)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_tag(d, text, x, y, fnt, bg_color=ACCENT, text_color=WHITE, pad_x=18, pad_y=8):
    """Draw a filled pill/rectangle tag."""
    bbox = d.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    rx1, ry1 = x, y
    rx2, ry2 = x + tw + pad_x * 2, y + th + pad_y * 2
    d.rounded_rectangle([rx1, ry1, rx2, ry2], radius=6, fill=bg_color)
    d.text((rx1 + pad_x, ry1 + pad_y), text, font=fnt, fill=text_color)
    return rx2, ry2  # bottom-right corner


LOGO_PATH = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
OUT_DIR   = "/home/user/WEB/carrossel-pmi/slides"
os.makedirs(OUT_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 01 — Capa
# ══════════════════════════════════════════════════════════════════════════════
def slide_01():
    img = make_background()
    d = ImageDraw.Draw(img)
    add_counter(d, 1, 5)

    # Tag "POSICIONAMENTO & AUTORIDADE"
    f_tag = font("bold", 24)
    draw_tag(d, "POSICIONAMENTO & AUTORIDADE", 64, 130, f_tag)

    # Main headline
    y = 240
    f_h1 = font("black", 100)
    f_h2 = font("black", 100)
    d.text((64, y), "Marketing é", font=f_h1, fill=WHITE)
    y += 115
    d.text((64, y), "amplificador.", font=f_h2, fill=ACCENT)
    y += 130

    add_accent_line(d, y)
    y += 30

    # Negative statement
    f_neg = font("bold", 46)
    d.text((64, y), "Não é milagre.", font=f_neg, fill=LIGHT_GRAY)
    y += 60
    d.text((64, y), "Não salva o que", font=f_neg, fill=LIGHT_GRAY)
    y += 60
    d.text((64, y), "está quebrado.", font=f_neg, fill=LIGHT_GRAY)
    y += 90

    # Body paragraph
    f_body = font("regular", 34)
    body = "Mas quando a base do negócio é sólida, marketing integrado transforma presença em resultado real e escalável."
    lines = wrap_text(body, f_body, W - 128, d)
    for line in lines:
        d.text((64, y), line, font=f_body, fill=GRAY)
        y += 46

    y += 20
    f_cta = font("medium", 32)
    d.text((64, y), "Arrasta para entender →", font=f_cta, fill=ACCENT)

    add_logo(img, LOGO_PATH)
    img.save(f"{OUT_DIR}/slide_01.png")
    print("✓ slide_01")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 02 — O Mito
# ══════════════════════════════════════════════════════════════════════════════
def slide_02():
    img = make_background()
    d = ImageDraw.Draw(img)
    add_counter(d, 2, 5)

    # Overline
    f_over = font("bold", 24)
    draw_tag(d, "ERRO MAIS CARO DO MERCADO", 64, 130, f_over, bg_color=(60, 0, 120))

    y = 230
    add_accent_line(d, y)
    y += 24

    # X tag
    f_xtag = font("black", 22)
    draw_tag(d, "✗  O MITO", 64, y, f_xtag, bg_color=(180, 0, 60))
    y += 68

    # Big quote
    f_quote = font("black", 68)
    quote_lines = [
        '"O marketing vai',
        "resolver o problema",
        'do nosso produto."',
    ]
    for line in quote_lines:
        d.text((64, y), line, font=f_quote, fill=WHITE)
        y += 82

    y += 10
    add_accent_line(d, y)
    y += 30

    # Body
    f_body = font("regular", 33)
    body = "Investir em campanhas antes de resolver o produto, a entrega ou a proposta de valor é o erro mais caro que uma empresa pode cometer."
    lines = wrap_text(body, f_body, W - 128, d)
    for line in lines:
        d.text((64, y), line, font=f_body, fill=GRAY)
        y += 46

    y += 20
    f_cta = font("medium", 32)
    d.text((64, y), "Continua no próximo slide →", font=f_cta, fill=ACCENT)

    add_logo(img, LOGO_PATH)
    img.save(f"{OUT_DIR}/slide_02.png")
    print("✓ slide_02")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 03 — A Verdade
# ══════════════════════════════════════════════════════════════════════════════
def slide_03():
    img = make_background()
    d = ImageDraw.Draw(img)
    add_counter(d, 3, 5)

    y = 120

    # Left diagram area: two rows Base Sólida / Base Fraca
    f_label = font("bold", 30)
    f_small = font("regular", 26)
    col_x = 64

    # Divider
    add_accent_line(d, y, x_start=64, x_end=W - 64)
    y += 24

    # "NEGÓCIO" header
    d.text((col_x, y), "NEGÓCIO", font=font("bold", 22), fill=GRAY)
    d.text((col_x + 340, y), "MARKETING INTEGRADO", font=font("bold", 22), fill=GRAY)
    y += 36

    # Row: Base sólida
    d.rounded_rectangle([col_x, y, col_x + 290, y + 52], radius=8,
                         fill=(20, 100, 60), outline=(0, 200, 100), width=2)
    d.text((col_x + 14, y + 12), "Base sólida →", font=f_label, fill=(0, 230, 120))
    arrow_x = col_x + 300
    d.text((arrow_x, y + 12), "──────────→", font=font("regular", 28), fill=ACCENT)
    y += 64

    # Row: Base fraca
    d.rounded_rectangle([col_x, y, col_x + 290, y + 52], radius=8,
                         fill=(100, 10, 20), outline=(220, 40, 60), width=2)
    d.text((col_x + 14, y + 12), "Base fraca →", font=f_label, fill=(240, 80, 90))
    d.text((arrow_x, y + 12), "──────────→", font=font("regular", 28), fill=(180, 30, 50))
    y += 80

    add_accent_line(d, y)
    y += 30

    # ROI metric — big callout
    f_big_num = font("black", 110)
    f_big_label = font("bold", 30)
    d.text((col_x, y), "x8", font=f_big_num, fill=ACCENT)
    roi_y = y + 28
    d.text((col_x + 190, roi_y), "ROI MÉDIO PMI", font=f_big_label, fill=WHITE)
    d.text((col_x + 190, roi_y + 44), "quando bem aplicado", font=font("regular", 26), fill=GRAY)
    y += 140

    add_accent_line(d, y)
    y += 24

    # "A VERDADE" tag + headline
    draw_tag(d, "✓  A VERDADE", 64, y, font("bold", 22), bg_color=(0, 130, 80))
    y += 60

    f_truth = font("black", 52)
    d.text((64, y), "Marketing amplifica", font=f_truth, fill=WHITE)
    y += 62
    d.text((64, y), "o que já existe –", font=f_truth, fill=WHITE)
    y += 62
    d.text((64, y), "o bom e o ruim.", font=f_truth, fill=ACCENT)
    y += 82

    f_body = font("regular", 30)
    body = "Com base sólida, estratégia integrada multiplica resultado. Com base fraca, ela acelera o colapso."
    lines = wrap_text(body, f_body, W - 128, d)
    for line in lines:
        d.text((64, y), line, font=f_body, fill=GRAY)
        y += 42

    y += 10
    d.text((64, y), "Continua no próximo slide →", font=font("medium", 30), fill=ACCENT)

    add_logo(img, LOGO_PATH)
    img.save(f"{OUT_DIR}/slide_03.png")
    print("✓ slide_03")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 04 — Método PMI
# ══════════════════════════════════════════════════════════════════════════════
def slide_04():
    img = make_background()
    d = ImageDraw.Draw(img)
    add_counter(d, 4, 5)

    y = 110
    add_accent_line(d, y)
    y += 24

    # Tag
    draw_tag(d, "⚡  MÉTODO PMI", 64, y, font("bold", 24), bg_color=ACCENT)
    y += 68

    # Big headline
    f_h = font("black", 72)
    d.text((64, y), "Do diagnóstico ao", font=f_h, fill=WHITE)
    y += 85
    d.text((64, y), "crescimento em", font=f_h, fill=WHITE)
    y += 85
    d.text((64, y), "4 etapas claras.", font=f_h, fill=ACCENT)
    y += 100

    add_accent_line(d, y)
    y += 30

    # 4 steps
    steps = [
        ("01", "Diagnóstico", "Entender antes de agir. Sem pacote, sem pitch, sem atalho."),
        ("02", "Estratégia",  "Plano sob medida integrando todos os canais com meta clara."),
        ("03", "Execução",    "Estratégia em prática com dados em tempo real. Ajuste contínuo."),
        ("04", "Crescimento", "Resultado previsível. Marca consolidada. Escala real."),
    ]

    f_num  = font("black", 36)
    f_step = font("bold", 34)
    f_desc = font("regular", 27)

    for num, title, desc in steps:
        # Number bubble
        d.ellipse([64, y + 2, 64 + 46, y + 2 + 46], fill=ACCENT)
        bbox = d.textbbox((0, 0), num, font=f_num)
        nx = 64 + (46 - (bbox[2] - bbox[0])) // 2
        ny = y + 2 + (46 - (bbox[3] - bbox[1])) // 2
        d.text((nx, ny), num, font=f_num, fill=WHITE)

        tx = 64 + 64
        d.text((tx, y), title, font=f_step, fill=WHITE)
        y += 40
        desc_lines = wrap_text(desc, f_desc, W - tx - 64, d)
        for line in desc_lines:
            d.text((tx, y), line, font=f_desc, fill=GRAY)
            y += 36
        y += 16

    y += 4
    body = "Sem surpresas. Sem pacotes genéricos. Cada etapa com meta definida e resultado previsível."
    f_body = font("regular", 28)
    lines = wrap_text(body, f_body, W - 128, d)
    for line in lines:
        d.text((64, y), line, font=f_body, fill=GRAY)
        y += 38

    y += 8
    d.text((64, y), "Último slide →", font=font("medium", 30), fill=ACCENT)

    add_logo(img, LOGO_PATH)
    img.save(f"{OUT_DIR}/slide_04.png")
    print("✓ slide_04")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 05 — CTA
# ══════════════════════════════════════════════════════════════════════════════
def slide_05():
    img = make_background()
    d = ImageDraw.Draw(img)
    add_counter(d, 5, 5)

    y = 130

    # "DIAGNÓSTICO" tag
    draw_tag(d, "DIAGNÓSTICO", 64, y, font("bold", 26), bg_color=ACCENT)
    y += 80

    add_accent_line(d, y)
    y += 28

    # Free tag
    f_free = font("bold", 28)
    draw_tag(d, "CONSULTORIA 100% GRATUITA", 64, y, f_free, bg_color=(20, 100, 60))
    y += 72

    # Big headline
    f_h = font("black", 82)
    d.text((64, y), "Pronto para", font=f_h, fill=WHITE)
    y += 95
    d.text((64, y), "escalar o seu", font=f_h, fill=WHITE)
    y += 95
    d.text((64, y), "negócio", font=f_h, fill=WHITE)
    y += 95
    d.text((64, y), "de verdade?", font=f_h, fill=ACCENT)
    y += 110

    add_accent_line(d, y)
    y += 28

    # Body
    f_body = font("regular", 32)
    body = "A PMI analisa seu cenário, identifica gargalos reais e mostra o caminho mais curto para o resultado. Sem compromisso. Sem pitch."
    lines = wrap_text(body, f_body, W - 128, d)
    for line in lines:
        d.text((64, y), line, font=f_body, fill=GRAY)
        y += 44

    y += 20
    # CTA button style
    draw_tag(d, "COMENTA ABAIXO", 64, y, font("black", 34), bg_color=ACCENT, pad_x=30, pad_y=14)
    y += 80

    # Handle
    d.text((64, y), "@perrymarketingintegrado", font=font("medium", 30), fill=LIGHT_GRAY)

    add_logo(img, LOGO_PATH)
    img.save(f"{OUT_DIR}/slide_05.png")
    print("✓ slide_05")


if __name__ == "__main__":
    slide_01()
    slide_02()
    slide_03()
    slide_04()
    slide_05()
    print("\nDone — slides saved to", OUT_DIR)
