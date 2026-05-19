#!/usr/bin/env python3
"""
Carousel builder - White/Clean style
Samuel Pereira / @segredosdaaudiencia
"""
import os
import sys
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ─── CONFIG ───────────────────────────────────────────────────────────────────
W, H = 1080, 1350
PHOTO_H = int(H * 0.555)
DIVIDER_Y = PHOTO_H + 6
DIVIDER_H = 6
TEXT_Y_START = PHOTO_H + DIVIDER_H + 18
TEXT_X = 54
TEXT_W = W - TEXT_X * 2

GREEN = (76, 187, 23)
BLACK = (10, 10, 10)
DARK_GRAY = (50, 50, 50)
WHITE_BG = (255, 255, 255)

FONT_DIR = Path("/usr/local/share/fonts/carousel")
ANTON = str(FONT_DIR / "Anton-Regular.ttf")
ROBOTO_BOLD = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf"
ROBOTO = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf"
ROBOTO_BLACK = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Black.ttf"

AVATAR_PATH = Path(__file__).parent / "avatar.png"
OUT_DIR = Path(__file__).parent / "slides"
PHOTOS_DIR = Path(__file__).parent / "photos"


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_headline(draw, number_str, title_str, y, font_size=88):
    """Draw number in green + title in black, same line style, wrapping."""
    f_title = load_font(ANTON, font_size)
    f_num = load_font(ANTON, font_size)
    line_h = int(font_size * 1.08)

    if number_str:
        num_bbox = draw.textbbox((0, 0), number_str + " ", font=f_num)
        num_w = num_bbox[2] - num_bbox[0]
    else:
        num_w = 0

    avail = TEXT_W - num_w if number_str else TEXT_W
    words = title_str.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=f_title)
        if bbox[2] - bbox[0] <= avail:
            current = test
        else:
            if current:
                lines.append(current)
            avail = TEXT_W
            current = word
    if current:
        lines.append(current)

    cy = y
    for i, line in enumerate(lines):
        if i == 0 and number_str:
            draw.text((TEXT_X, cy), number_str + " ", font=f_num, fill=GREEN)
            draw.text((TEXT_X + num_w, cy), line, font=f_title, fill=BLACK)
        else:
            draw.text((TEXT_X, cy), line, font=f_title, fill=BLACK)
        cy += line_h

    return cy + 8


def draw_body_with_highlight(draw, text, y, highlight_last=True, font_size=44):
    """Draw body text; last sentence in green bold if highlight_last."""
    f_body = load_font(ROBOTO, font_size)
    f_bold = load_font(ROBOTO_BOLD, font_size)
    line_h = int(font_size * 1.45)

    # Split on '. ' to find last sentence
    if highlight_last and '. ' in text:
        idx = text.rfind('. ', 0, len(text) - 2)
        if idx != -1:
            normal_part = text[:idx + 2].strip()
            highlight_part = text[idx + 2:].strip()
        else:
            normal_part = ""
            highlight_part = text
    else:
        normal_part = text
        highlight_part = ""

    cy = y
    tmp_draw = draw

    def render_lines(txt, font, color, cy):
        lines = wrap_text(txt, font, TEXT_W, tmp_draw)
        for line in lines:
            draw.text((TEXT_X, cy), line, font=font, fill=color)
            cy += line_h
        return cy

    if normal_part:
        cy = render_lines(normal_part, f_body, DARK_GRAY, cy)
    if highlight_part:
        cy = render_lines(highlight_part, f_bold, GREEN, cy)

    return cy


def draw_signature(img, avatar_path):
    """Draw centered signature at bottom."""
    draw = ImageDraw.Draw(img)
    f_name = load_font(ROBOTO_BOLD, 36)
    f_handle = load_font(ROBOTO, 32)

    name = "Samuel Pereira"
    handle = "@segredosdaaudiencia"

    name_bbox = draw.textbbox((0, 0), name, font=f_name)
    handle_bbox = draw.textbbox((0, 0), handle, font=f_handle)
    name_w = name_bbox[2] - name_bbox[0]
    handle_w = handle_bbox[2] - handle_bbox[0]

    avatar_size = 90
    gap = 14
    verified_size = 28

    text_block_w = max(name_w, handle_w + verified_size + 4)
    total_w = avatar_size + gap + text_block_w
    start_x = (W - total_w) // 2

    sig_y = H - 130
    av_x = start_x
    av_y = sig_y

    # Avatar
    if avatar_path.exists():
        try:
            av = Image.open(avatar_path).convert("RGBA").resize((avatar_size, avatar_size))
            mask = Image.new("L", (avatar_size, avatar_size), 0)
            from PIL import ImageDraw as ID2
            d = ID2.Draw(mask)
            d.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            img.paste(av, (av_x, av_y), mask)
        except Exception:
            draw.ellipse((av_x, av_y, av_x + avatar_size, av_y + avatar_size), fill=(100, 100, 100))
    else:
        draw.ellipse((av_x, av_y, av_x + avatar_size, av_y + avatar_size), fill=(80, 80, 80))

    tx = av_x + avatar_size + gap
    ty_name = av_y + 8
    ty_handle = ty_name + 42

    draw.text((tx, ty_name), name, font=f_name, fill=BLACK)
    draw.text((tx, ty_handle), handle, font=f_handle, fill=DARK_GRAY)

    # Verified checkmark (blue circle with white tick)
    vx = tx + handle_w + 6
    vy = ty_handle + 4
    draw.ellipse((vx, vy, vx + verified_size, vy + verified_size), fill=(29, 155, 240))
    # simple tick
    draw.text((vx + 5, vy + 1), "✓", font=load_font(ROBOTO_BOLD, 20), fill=(255, 255, 255))


def build_slide(photo_path, number_str, title_str, body_text, output_path,
                highlight_last=True, font_size_title=88, font_size_body=44,
                center_title=False):
    img = Image.new("RGB", (W, H), WHITE_BG)

    # ── Top photo ──
    if photo_path and Path(photo_path).exists():
        photo = Image.open(photo_path).convert("RGB")
        # Crop to fill top area
        pw, ph = photo.size
        target_ratio = W / PHOTO_H
        src_ratio = pw / ph
        if src_ratio > target_ratio:
            new_w = int(ph * target_ratio)
            offset = (pw - new_w) // 2
            photo = photo.crop((offset, 0, offset + new_w, ph))
        else:
            new_h = int(pw / target_ratio)
            offset = (ph - new_h) // 2
            photo = photo.crop((0, offset, pw, offset + new_h))
        photo = photo.resize((W, PHOTO_H), Image.LANCZOS)
        img.paste(photo, (0, 0))
    else:
        # Placeholder
        draw_ph = ImageDraw.Draw(img)
        draw_ph.rectangle((0, 0, W, PHOTO_H), fill=(200, 200, 200))
        draw_ph.text((W // 2, PHOTO_H // 2), "FOTO", fill=(150, 150, 150),
                     font=load_font(ANTON, 80), anchor="mm")

    # ── Green divider ──
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, PHOTO_H, W, PHOTO_H + DIVIDER_H), fill=GREEN)

    # ── Text area ──
    y = TEXT_Y_START

    if title_str or number_str:
        y = draw_headline(draw, number_str, title_str, y, font_size=font_size_title)
        y += 12

    if body_text:
        y = draw_body_with_highlight(draw, body_text, y,
                                     highlight_last=highlight_last,
                                     font_size=font_size_body)

    # ── Signature ──
    draw_signature(img, AVATAR_PATH)

    img.save(output_path, "PNG", quality=95)
    print(f"  Saved: {output_path}")
    return output_path


# ─── SLIDE DEFINITIONS ────────────────────────────────────────────────────────
SLIDES = [
    {
        "id": "01-capa",
        "photo": "photo-01-capa.png",
        "number": "",
        "title": "A PANINI VAI FATURAR R$700 MILHÕES NO BRASIL. COM PAPEL.",
        "body": "E a maioria das pessoas nem percebeu o que está sendo vendido de verdade.",
        "highlight_last": False,
        "font_title": 80,
        "font_body": 46,
    },
    {
        "id": "02-221pct",
        "photo": "photo-02-bancas.png",
        "number": "1.",
        "title": "TICKET MÉDIO SUBIU 221% EM 7 DIAS",
        "body": "Em 2022, o gasto médio era R$24. Em 2026, passou para R$55 — sem promoção, sem desconto, sem influencer pago. As pessoas simplesmente quiseram mais.",
        "highlight_last": True,
        "font_title": 88,
        "font_body": 42,
    },
    {
        "id": "03-r16mil",
        "photo": "photo-03-neymar.png",
        "number": "2.",
        "title": "UMA BANCA FATUROU R$16 MIL EM UM DIA",
        "body": "Em São Paulo, bancas comuns registraram entre R$10 mil e R$16 mil em vendas num único dia. Vendendo pacotinhos de R$3,50. Isso é mais que muita loja de roupa fatura no mês.",
        "highlight_last": True,
        "font_title": 82,
        "font_body": 42,
    },
    {
        "id": "04-produto",
        "photo": "photo-04-album.png",
        "number": "",
        "title": "O QUE VOCÊ ACHA QUE ESTÁ COMPRANDO NÃO É O QUE ESTÁ COMPRANDO",
        "body": "Ninguém compra figurinha. Compram a antecipação de abrir o pacote. A dopamina da surpresa. O ritual que faz um adulto de 35 anos se sentir criança de novo. A figurinha é só a desculpa.",
        "highlight_last": True,
        "font_title": 72,
        "font_body": 42,
    },
    {
        "id": "05-conexao",
        "photo": "photo-05-amigos.png",
        "number": "3.",
        "title": "CRIOU COMUNIDADE FÍSICA. SEM APP. SEM WHATSAPP.",
        "body": "Filas em bancas. Trocas entre desconhecidos no elevador. Crianças parando adultos na rua. 40 milhões de álbuns distribuídos no Brasil. Nenhum aplicativo fez isso esse ano.",
        "highlight_last": True,
        "font_title": 82,
        "font_body": 42,
    },
    {
        "id": "06-falta",
        "photo": "photo-06-estadio.png",
        "number": "4.",
        "title": "ELA LUCRA COM O QUE VOCÊ AINDA NÃO TEM",
        "body": "São 670 figurinhas no total. A chance de completar comprando só pacotes é próxima de zero. Cada espaço vazio é uma missão incompleta. E missão incompleta vende o próximo pacote.",
        "highlight_last": True,
        "font_title": 84,
        "font_body": 42,
    },
    {
        "id": "07-preco",
        "photo": "photo-07-pacotes.png",
        "number": "5.",
        "title": "SUBIRAM 75% O PREÇO. A DEMANDA TRIPLICOU.",
        "body": "De R$2,00 em 2022 para R$3,50 em 2026. Aumento de 75%. Resultado? Filas maiores. Mais cobertura espontânea na mídia. Mais desejo. Preço alto não afastou ninguém. Sinalizou que valia ainda mais.",
        "highlight_last": True,
        "font_title": 82,
        "font_body": 40,
    },
    {
        "id": "08-viral",
        "photo": "photo-08-celular.png",
        "number": "6.",
        "title": "VIRAL NÃO NASCE DE INFORMAÇÃO. NASCE DE IDENTIDADE.",
        "body": "Ninguém compartilhou o álbum porque é útil. Compartilharam porque diz quem a pessoa é. Esse é o gatilho por trás de todo post que você já viu explodir sem motivo aparente.",
        "highlight_last": True,
        "font_title": 78,
        "font_body": 42,
    },
    {
        "id": "09-publico",
        "photo": "photo-09-instagram.png",
        "number": "7.",
        "title": "SEU SEGUIDOR NÃO TE SEGUE PELO QUE VOCÊ SABE",
        "body": "A Panini tem concorrentes com produto mais barato. Ninguém liga. Porque o que ela vende não é figurinha — é familiaridade, ritual, pertencimento. Audiência real não se constrói com informação. Constrói-se com identificação.",
        "highlight_last": True,
        "font_title": 78,
        "font_body": 40,
    },
    {
        "id": "10-atencao",
        "photo": "photo-10-estadio2.png",
        "number": "",
        "title": "UM PACOTINHO DE R$3,50 DEU UMA AULA SOBRE ATENÇÃO HUMANA",
        "body": "R$700 milhões em faturamento. 40 milhões de álbuns. Viral orgânico em todo o país. Filas de 2 horas. Sem Meta Ads. Sem influencer. Com papel e cola. O segredo? Venderam dopamina disfarçada de figurinha.",
        "highlight_last": True,
        "font_title": 74,
        "font_body": 42,
    },
    {
        "id": "11-cta",
        "photo": "photo-11-cta.png",
        "number": "",
        "title": 'COMENTA "COPA" AQUI EMBAIXO',
        "body": "Eu te mando no direct os 7 gatilhos psicológicos que fazem qualquer conteúdo virar obsessão coletiva — os mesmos que a Panini usou sem você perceber. 🔖❤️💬↗️",
        "highlight_last": False,
        "font_title": 90,
        "font_body": 44,
    },
]

PHOTO_PROMPTS = {
    "photo-01-capa.png": (
        "Photorealistic photo: a happy Brazilian boy around 8 years old wearing a yellow Brazil national football jersey, "
        "holding up a shiny Neymar Jr. FIFA World Cup 2026 Panini sticker with both hands, big smile, excited expression. "
        "Warm bokeh background with colorful blurred lights. Natural photography style, DSLR quality, NOT obviously AI-generated. "
        "4:5 vertical portrait."
    ),
    "photo-02-bancas.png": (
        "Photorealistic photo: long excited queue of Brazilian people in yellow and green jerseys outside a newspaper kiosk "
        "in São Paulo at golden hour, holding Panini FIFA World Cup 2026 sticker packs, raising fists in celebration. "
        "Street photography style, natural light, candid feel. 4:5 vertical."
    ),
    "photo-03-neymar.png": (
        "Photorealistic photo: a young adult Brazilian man in casual clothes holding the FIFA World Cup 2026 Panini sticker album "
        "open, showing completed pages, excited smile, bright indoor lighting. Clean background. "
        "DSLR portrait quality. 4:5 vertical."
    ),
    "photo-04-album.png": (
        "Close-up photorealistic photo of child's hands carefully placing a shiny FIFA World Cup 2026 Panini sticker into a "
        "nearly-complete album page. Warm natural light, shallow depth of field. "
        "Cozy home setting. 4:5 vertical."
    ),
    "photo-05-amigos.png": (
        "Photorealistic photo: four young Brazilian friends sitting on the floor indoors, laughing and trading Panini FIFA World Cup "
        "2026 stickers, some wearing Brazil jerseys, stickers spread on the floor between them. "
        "Natural window light, candid moment. 4:5 vertical."
    ),
    "photo-06-estadio.png": (
        "Photorealistic aerial wide-angle photo of a packed football stadium at night filled with Brazilian fans in yellow jerseys, "
        "dramatic floodlights, green pitch visible, electric atmosphere. "
        "Sports photography style. 4:5 vertical."
    ),
    "photo-07-pacotes.png": (
        "Clean product photo: a fan of multiple Panini FIFA World Cup 2026 sticker packets held in one hand against a pure white "
        "background. Studio lighting, sharp focus, minimal style. 4:5 vertical."
    ),
    "photo-08-celular.png": (
        "Photorealistic photo: diverse group of five young adults sitting together laughing while looking at smartphones, "
        "casual indoor setting with warm lighting. Candid natural moment, DSLR quality. 4:5 vertical."
    ),
    "photo-09-instagram.png": (
        "Photorealistic photo: a young woman's hands holding a smartphone showing an Instagram profile page, "
        "cozy cafe setting with coffee cup and notebook on wooden table, warm natural window light. "
        "4:5 vertical."
    ),
    "photo-10-estadio2.png": (
        "Dramatic AI-generated illustration: massive stadium packed with Brazilian fans in yellow and green, "
        "colorful fireworks exploding over the stadium at night, giant golden FIFA World Cup trophy standing "
        "in the center of the pitch, epic cinematic lighting. 4:5 vertical."
    ),
    "photo-11-cta.png": (
        "Photorealistic photo: crowd of jubilant Brazilian fans in a stadium, arms raised, holding Panini FIFA World Cup 2026 "
        "sticker albums, confetti falling, stadium lights blazing, pure celebration atmosphere. "
        "Wide angle, epic moment. 4:5 vertical."
    ),
}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-photos", action="store_true", help="Skip photo generation")
    parser.add_argument("--slide", type=str, help="Generate only this slide id")
    args = parser.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    PHOTOS_DIR.mkdir(exist_ok=True)

    api_key = os.environ.get("GEMINI_API_KEY", "")

    if not args.skip_photos:
        print("── Generating photos ──")
        sys.path.insert(0, str(Path.home() / ".claude/skills/nano-banana-pro/scripts"))
        try:
            from generate_image import generate_image
        except ImportError:
            print("ERROR: nano-banana-pro script not found")
            sys.exit(1)

        for fname, prompt in PHOTO_PROMPTS.items():
            out = PHOTOS_DIR / fname
            if out.exists():
                print(f"  Skip (exists): {fname}")
                continue
            print(f"  Generating: {fname}")
            try:
                generate_image(prompt, str(out), resolution="2K", api_key=api_key)
            except Exception as e:
                print(f"  FAILED {fname}: {e}")

    print("\n── Building slides ──")
    for slide in SLIDES:
        if args.slide and slide["id"] != args.slide:
            continue
        out = OUT_DIR / f"slide-{slide['id']}.png"
        photo = PHOTOS_DIR / slide["photo"]
        build_slide(
            photo_path=str(photo),
            number_str=slide["number"],
            title_str=slide["title"],
            body_text=slide["body"],
            output_path=str(out),
            highlight_last=slide["highlight_last"],
            font_size_title=slide["font_title"],
            font_size_body=slide["font_body"],
        )

    print("\nDone.")
