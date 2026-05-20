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


def draw_headline(d, lines, y, size, color=WHITE, leading=None):
    """Desenha headline com auto-wrap se a linha não couber. Retorna y após a última linha."""
    fnt = F("black", size)
    if leading is None:
        leading = int(size * 1.1)
    max_w = W - MARGIN * 2
    for line in lines:
        # Quebra automática caso a linha seja larga demais
        words = line.split()
        cur_line = ""
        for word in words:
            test = (cur_line + " " + word).strip()
            bb = d.textbbox((0, 0), test, font=fnt)
            if bb[2] - bb[0] <= max_w:
                cur_line = test
            else:
                if cur_line:
                    d.text((MARGIN, y), cur_line, font=fnt, fill=color)
                    y += leading
                cur_line = word
        if cur_line:
            d.text((MARGIN, y), cur_line, font=fnt, fill=color)
            y += leading
    return y


def draw_subtitle_parts(d, parts, y, size=34):
    """
    parts: lista de (texto, destaque).
    Renderiza word-by-word com wrap, respeitando TEXT_SAFE_BOTTOM.
    """
    fnt_reg = F("regular", size)
    fnt_bld = F("bold", size)
    max_x   = W - MARGIN
    line_h  = int(size * 1.48)

    tokens = []
    for text, highlight in parts:
        for word in text.split():
            tokens.append((word, highlight))

    x, cur_y = MARGIN, y

    for word, highlight in tokens:
        # Para se ultrapassar a área segura
        if cur_y + line_h > TEXT_SAFE_BOTTOM:
            break
        fnt   = fnt_bld if highlight else fnt_reg
        color = VIOLET_LT if highlight else GRAY
        bb    = d.textbbox((0, 0), word + " ", font=fnt)
        ww    = bb[2] - bb[0]

        if x + ww > max_x and x > MARGIN:
            x = MARGIN
            cur_y += line_h
            if cur_y + line_h > TEXT_SAFE_BOTTOM:
                break

        d.text((x, cur_y), word, font=fnt, fill=color)
        x += ww

    return cur_y + line_h


def add_logo(img, h=LOGO_H, bottom=LOGO_PAD):
    lg = Image.open("/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png").convert("RGBA")
    ratio = h / lg.height
    nw = int(lg.width * ratio)
    lg = lg.resize((nw, h), Image.LANCZOS)
    x = (W - nw) // 2
    y = H - bottom - h
    img.paste(lg, (x, y), lg)


def make_slide(photo_path, headline_lines, headline_size=75,
               subtitle_parts=None, out_path="", photo_centering=(0.5, 0.25)):

    # 1. canvas preto
    canvas = Image.new("RGB", (W, H), BLACK)

    # 2. foto com gradiente
    photo = crop_photo(photo_path, centering=photo_centering)
    photo = gradient_overlay(photo)
    canvas.paste(photo, (0, 0))

    # 3. linha accent violet
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, LINE_Y, W, LINE_Y + LINE_H], fill=VIOLET)

    # 4. headline
    text_y = TEXT_Y + 30
    text_y = draw_headline(d, headline_lines, text_y, headline_size)

    # 5. subtítulo
    text_y += 14
    draw_subtitle_parts(d, subtitle_parts, text_y, size=36)

    # 6. logo PMI
    add_logo(canvas)

    canvas.save(out_path)
    print(f"✓ {os.path.basename(out_path)}")


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
        ("Diagnóstico →", True),
        ("Estratégia →", False),
        ("Execução →", True),
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
        ("A PMI faz um diagnóstico", False),
        ("100% gratuito", True),
        ("do seu cenário.", False),
        ("Sem compromisso. Sem pitch.", False),
        ("Comenta", True),
        ("@perrymarketingintegrado", False),
    ],
    out_path       = f"{OUT}/slide_05.png",
    photo_centering= (0.5, 0.25),
)

print(f"\nDone → {OUT}")
