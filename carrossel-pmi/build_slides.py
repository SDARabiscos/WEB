#!/usr/bin/env python3
"""PMI Carousel — formato viral: foto dramática + texto massivo. Sem números de sequência."""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H        = 1080, 1350
PHOTO_H     = 675          # foto ocupa 50% do canvas
LINE_Y      = PHOTO_H
LINE_H      = 5
TEXT_Y      = LINE_Y + LINE_H
MARGIN      = 58
LOGO_H      = 43           # 30% menor
LOGO_PAD    = 32
# área segura para texto: de TEXT_Y+padding até acima do logo
TEXT_SAFE_BOTTOM = H - LOGO_PAD - LOGO_H - 12

# ── Cores PMI ────────────────────────────────────────────────────────────────
VIOLET      = (134, 0, 255)
VIOLET_LT   = (180, 90, 255)
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
GRAY        = (165, 168, 185)

# ── Fontes ────────────────────────────────────────────────────────────────────
R = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"

def F(style, size):
    paths = {
        "black":   f"{R}/Roboto-Black.ttf",
        "bold":    f"{R}/Roboto-Bold.ttf",
        "medium":  f"{R}/Roboto-Medium.ttf",
        "regular": f"{R}/Roboto-Regular.ttf",
        "light":   f"{R}/Roboto-Light.ttf",
    }
    return ImageFont.truetype(paths[style], size)


# ── Helpers ───────────────────────────────────────────────────────────────────
def crop_photo(path, w=W, h=PHOTO_H, centering=(0.5, 0.25)):
    img = Image.open(path).convert("RGB")
    return ImageOps.fit(img, (w, h), Image.LANCZOS, centering=centering)


def gradient_overlay(photo):
    """Gradiente escuro na base da foto para fundir com a área de texto."""
    grad = Image.new("RGBA", (W, PHOTO_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(grad)
    fade_start = PHOTO_H - 180
    for y in range(fade_start, PHOTO_H):
        alpha = int(230 * ((y - fade_start) / (PHOTO_H - fade_start)) ** 1.4)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    photo = photo.convert("RGBA")
    photo.paste(grad, mask=grad.split()[3])
    return photo.convert("RGB")


def wrap_headline_lines(d, lines, fnt, max_w):
    """Quebra cada linha do headline se ultrapassar max_w."""
    out = []
    for line in lines:
        words = line.split()
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if d.textbbox((0, 0), test, font=fnt)[2] <= max_w:
                cur = test
            else:
                if cur:
                    out.append(cur)
                cur = w
        if cur:
            out.append(cur)
    return out


def layout_subtitle_lines(d, parts, fnt_reg, fnt_bld, max_w):
    """
    Distribui as palavras em linhas; cada linha é uma lista de
    (word, font, color) já com larguras pré-calculadas.
    Retorna: [ [(word, fnt, color, width), ...], ... ], line_height
    """
    tokens = []
    for text, highlight in parts:
        for word in text.split():
            tokens.append((word, highlight))

    space_w = d.textbbox((0, 0), " ", font=fnt_reg)[2]
    lines = [[]]
    cur_w = 0

    for word, highlight in tokens:
        fnt   = fnt_bld if highlight else fnt_reg
        color = VIOLET_LT if highlight else GRAY
        ww    = d.textbbox((0, 0), word, font=fnt)[2]
        add_w = ww + (space_w if lines[-1] else 0)

        if cur_w + add_w > max_w and lines[-1]:
            lines.append([])
            cur_w = ww
            lines[-1].append((word, fnt, color, ww))
        else:
            lines[-1].append((word, fnt, color, ww))
            cur_w += add_w

    return lines, space_w


def draw_centered_headline(d, lines, y, size, color=WHITE):
    fnt = F("black", size)
    leading = int(size * 1.08)
    for line in lines:
        bb = d.textbbox((0, 0), line, font=fnt)
        tw = bb[2] - bb[0]
        x = (W - tw) // 2
        d.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def draw_centered_subtitle(d, lines, y, size, space_w):
    line_h = int(size * 1.42)
    for line in lines:
        total_w = sum(ww for _, _, _, ww in line) + space_w * (len(line) - 1)
        x = (W - total_w) // 2
        for word, fnt, color, ww in line:
            d.text((x, y), word, font=fnt, fill=color)
            x += ww + space_w
        y += line_h
    return y


def add_logo(img, h=LOGO_H, bottom=LOGO_PAD):
    lg = Image.open("/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png").convert("RGBA")
    ratio = h / lg.height
    nw = int(lg.width * ratio)
    lg = lg.resize((nw, h), Image.LANCZOS)
    x = (W - nw) // 2
    y = H - bottom - h
    img.paste(lg, (x, y), lg)


def make_slide(photo_path, headline_lines, subtitle_parts,
               out_path, headline_size=85, subtitle_size=34,
               photo_centering=(0.5, 0.25)):

    canvas = Image.new("RGB", (W, H), BLACK)

    # Foto + gradiente
    photo = crop_photo(photo_path, centering=photo_centering)
    photo = gradient_overlay(photo)
    canvas.paste(photo, (0, 0))

    d = ImageDraw.Draw(canvas)

    # Linha violet accent
    d.rectangle([0, LINE_Y, W, LINE_Y + LINE_H], fill=VIOLET)

    # Auto-fit do headline: se com 85px ele estourar a largura, reduz progressivamente
    max_w = W - MARGIN * 2
    h_size = headline_size
    while h_size > 50:
        fnt = F("black", h_size)
        wrapped = wrap_headline_lines(d, headline_lines, fnt, max_w)
        # Se o número de linhas pós-wrap é igual ao input, ok
        if len(wrapped) == len(headline_lines):
            break
        h_size -= 4
    fnt_h = F("black", h_size)
    wrapped_h = wrap_headline_lines(d, headline_lines, fnt_h, max_w)
    h_leading = int(h_size * 1.08)
    h_total = h_leading * len(wrapped_h)

    # Auto-fit do subtítulo: reduz se ultrapassar área
    fnt_sub_reg = F("regular", subtitle_size)
    fnt_sub_bld = F("bold", subtitle_size)
    sub_lines, space_w = layout_subtitle_lines(d, subtitle_parts,
                                                fnt_sub_reg, fnt_sub_bld, max_w)
    s_leading = int(subtitle_size * 1.42)
    s_total = s_leading * len(sub_lines)

    # Espaço total disponível
    area_top    = LINE_Y + LINE_H
    area_bottom = TEXT_SAFE_BOTTOM
    area_h      = area_bottom - area_top

    gap = 28
    block_h = h_total + gap + s_total

    # Se não couber, reduz o subtítulo
    while block_h > area_h - 20 and subtitle_size > 24:
        subtitle_size -= 2
        fnt_sub_reg = F("regular", subtitle_size)
        fnt_sub_bld = F("bold", subtitle_size)
        sub_lines, space_w = layout_subtitle_lines(d, subtitle_parts,
                                                    fnt_sub_reg, fnt_sub_bld, max_w)
        s_leading = int(subtitle_size * 1.42)
        s_total = s_leading * len(sub_lines)
        block_h = h_total + gap + s_total

    # Centraliza verticalmente
    start_y = area_top + (area_h - block_h) // 2

    # Renderiza
    y_after_h = draw_centered_headline(d, wrapped_h, start_y, h_size)
    draw_centered_subtitle(d, sub_lines, y_after_h + gap, subtitle_size, space_w)

    add_logo(canvas)
    canvas.save(out_path)
    print(f"✓ {os.path.basename(out_path)}  (headline {h_size}px, sub {subtitle_size}px)")


# ── Slides ────────────────────────────────────────────────────────────────────
OUT = "/home/user/WEB/carrossel-pmi/slides"
os.makedirs(OUT, exist_ok=True)
PH  = "/home/user/WEB/carrossel-pmi/photos"


# SLIDE 01 — hook de abertura
make_slide(
    photo_path     = f"{PH}/photo_01.png",
    headline_lines = ["MARKETING É UM", "AMPLIFICADOR"],
    subtitle_parts = [
        ("Não é milagre. Não salva o que", False),
        ("está quebrado.", True),
        ("Mas com base sólida,", False),
        ("transforma presença em resultado.", True),
    ],
    out_path       = f"{OUT}/slide_01.png",
    photo_centering= (0.5, 0.3),
)

# SLIDE 02 — problema / conflito
make_slide(
    photo_path     = f"{PH}/photo_02.png",
    headline_lines = ["O ERRO MAIS CARO", "DO MERCADO"],
    subtitle_parts = [
        ("Investir em campanhas antes de resolver o", False),
        ("produto", True),
        ("é o desperdício que ninguém fala.", False),
    ],
    out_path       = f"{OUT}/slide_02.png",
    photo_centering= (0.5, 0.4),
)

# SLIDE 03 — revelação / verdade
make_slide(
    photo_path     = f"{PH}/photo_03.png",
    headline_lines = ["ELE AMPLIFICA O", "QUE JÁ EXISTE"],
    subtitle_parts = [
        ("Base sólida + estratégia integrada =", False),
        ("8x mais resultado.", True),
        ("Base fraca + marketing = colapso acelerado.", False),
    ],
    out_path       = f"{OUT}/slide_03.png",
    photo_centering= (0.5, 0.2),
)

# SLIDE 04 — método / solução
make_slide(
    photo_path     = f"{PH}/photo_04.png",
    headline_lines = ["4 ETAPAS QUE", "MUDAM O JOGO"],
    subtitle_parts = [
        ("Diagnóstico ·", True),
        ("Estratégia ·", False),
        ("Execução ·", True),
        ("Crescimento.", False),
        ("Sem surpresas. Sem pacotes genéricos.", False),
    ],
    out_path       = f"{OUT}/slide_04.png",
    photo_centering= (0.5, 0.3),
)

# SLIDE 05 — CTA
make_slide(
    photo_path     = f"{PH}/photo_05.png",
    headline_lines = ["PRONTO PARA", "ESCALAR DE", "VERDADE?"],
    subtitle_parts = [
        ("Diagnóstico", False),
        ("100% gratuito", True),
        ("do seu cenário.", False),
        ("Sem compromisso. Sem pitch.", False),
        ("Comenta abaixo.", True),
    ],
    out_path       = f"{OUT}/slide_05.png",
    photo_centering= (0.5, 0.25),
)

print(f"\nDone → {OUT}")
