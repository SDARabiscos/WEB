#!/usr/bin/env python3
"""
Carousel builder - White/Clean Instagram style
Samuel Pereira / @segredosdaaudiencia
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ─── CANVAS ───────────────────────────────────────────────────────────────────
W, H = 1080, 1350          # Instagram 4:5
PHOTO_H = 570              # top photo area height
DIVIDER_Y = PHOTO_H
DIVIDER_H = 8
TEXT_START_Y = PHOTO_H + DIVIDER_H + 36
PAD_X = 58                 # horizontal padding
TEXT_W = W - PAD_X * 2
SIG_Y    = H - 148         # signature baseline
TEXT_MAX_Y = SIG_Y - 20   # body text must not exceed this

# ─── COLORS ───────────────────────────────────────────────────────────────────
GREEN       = (50, 180, 20)
BLACK       = (12, 12, 12)
DARK_GRAY   = (55, 55, 55)
WHITE_BG    = (255, 255, 255)
BLUE_VERIFY = (29, 155, 240)

# ─── FONTS ────────────────────────────────────────────────────────────────────
FONT_DIR    = Path("/usr/local/share/fonts/carousel")
ROBOTO_DIR  = Path("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF")

ANTON        = str(FONT_DIR / "Anton-Regular.ttf")
ROBOTO_REG   = str(ROBOTO_DIR / "Roboto-Regular.ttf")
ROBOTO_BOLD  = str(ROBOTO_DIR / "Roboto-Bold.ttf")
ROBOTO_BLK   = str(ROBOTO_DIR / "Roboto-Black.ttf")
NOTO_EMOJI   = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

AVATAR_PATH  = Path(__file__).parent / "avatar.png"
BADGE_PATH   = Path(__file__).parent / "verified_badge.png"
OUT_DIR      = Path(__file__).parent / "slides"
PHOTOS_DIR   = Path(__file__).parent / "photos"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def text_width(draw, text, f):
    bb = draw.textbbox((0, 0), text, font=f)
    return bb[2] - bb[0]


def text_height(draw, text, f):
    bb = draw.textbbox((0, 0), text, font=f)
    return bb[3] - bb[1]


def wrap(draw, text, f, max_w):
    """Wrap text into lines fitting max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        probe = (cur + " " + w).strip()
        if text_width(draw, probe, f) <= max_w:
            cur = probe
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines_centered(draw, lines, f, color, y, line_h):
    """Draw lines centered horizontally."""
    cy = y
    for line in lines:
        lw = text_width(draw, line, f)
        x = (W - lw) // 2
        draw.text((x, cy), line, font=f, fill=color)
        cy += line_h
    return cy


def draw_lines_left(draw, lines, f, color, y, line_h, x=PAD_X):
    cy = y
    for line in lines:
        draw.text((x, cy), line, font=f, fill=color)
        cy += line_h
    return cy


# ─── HEADLINE RENDERER ────────────────────────────────────────────────────────
def draw_headline(draw, number, title, y, fs=86):
    """
    Numbered slides: number (green) + title (black), left-aligned.
    Insight slides (number=""): title centered.
    """
    f = font(ANTON, fs)
    lh = int(fs * 1.10)

    if number:
        # Measure number prefix
        num_text = number + " "
        num_w = text_width(draw, num_text, f)
        avail = TEXT_W - num_w

        # Wrap title into lines given available width first line
        words = title.split()
        lines, cur = [], ""
        first = True
        for w in words:
            probe = (cur + " " + w).strip()
            limit = avail if first else TEXT_W
            if text_width(draw, probe, f) <= limit:
                cur = probe
            else:
                if cur:
                    lines.append(cur)
                    first = False
                cur = w
        if cur:
            lines.append(cur)

        cy = y
        for i, line in enumerate(lines):
            if i == 0:
                draw.text((PAD_X, cy), num_text, font=f, fill=GREEN)
                draw.text((PAD_X + num_w, cy), line, font=f, fill=BLACK)
            else:
                draw.text((PAD_X, cy), line, font=f, fill=BLACK)
            cy += lh
        return cy + 6

    else:
        # Centered
        lines = wrap(draw, title, f, TEXT_W)
        cy = y
        for line in lines:
            lw = text_width(draw, line, f)
            draw.text(((W - lw) // 2, cy), line, font=f, fill=BLACK)
            cy += lh
        return cy + 6


# ─── BODY RENDERER ────────────────────────────────────────────────────────────
EMOJI_RANGES = [
    (0x1F000, 0x1FFFF),  # Most emoji
    (0x2190,  0x27BF),   # Arrows + misc symbols + dingbats (↗ 0x2197, ❤ 0x2764)
    (0x2300,  0x23FF),   # Misc technical
    (0xFE00,  0xFE0F),   # Variation selectors
    (0x200D,  0x200D),   # ZWJ
]


def _is_emoji_cp(cp):
    for lo, hi in EMOJI_RANGES:
        if lo <= cp <= hi:
            return True
    return False


def has_emoji(text):
    return any(_is_emoji_cp(ord(ch)) for ch in text)


def split_emoji(text):
    """Split text into (segment, is_emoji) pairs."""
    segments = []
    buf, buf_emoji = "", False
    for ch in text:
        is_e = _is_emoji_cp(ord(ch))
        if is_e == buf_emoji:
            buf += ch
        else:
            if buf:
                segments.append((buf, buf_emoji))
            buf, buf_emoji = ch, is_e
    if buf:
        segments.append((buf, buf_emoji))
    return segments


def draw_mixed_line(draw, img, line, f_text, f_emoji, color, x, y, centered, emoji_size=44):
    """Draw a line with mixed text/emoji, handling emoji font separately."""
    segs = split_emoji(line)
    # measure total width
    total_w = 0
    widths = []
    for seg, is_e in segs:
        if is_e:
            w = emoji_size
        else:
            bb = draw.textbbox((0, 0), seg, font=f_text)
            w = bb[2] - bb[0]
        widths.append(w)
        total_w += w

    cx = (W - total_w) // 2 if centered else x
    for (seg, is_e), w in zip(segs, widths):
        if is_e:
            try:
                # NotoColorEmoji only works at bitmap size 109; scale after render
                f_em = ImageFont.truetype(NOTO_EMOJI, 109)
                # render emoji onto temp RGBA image then scale to desired size
                tmp = Image.new("RGBA", (109 * len(seg) + 20, 140), (255, 255, 255, 0))
                td = ImageDraw.Draw(tmp)
                td.text((0, 0), seg, font=f_em, embedded_color=True)
                # crop to content
                bbox = tmp.getbbox()
                if bbox:
                    tmp = tmp.crop(bbox)
                    scale = emoji_size / tmp.height if tmp.height else 1
                    nw = max(1, int(tmp.width * scale))
                    nh = max(1, emoji_size)
                    tmp = tmp.resize((nw, nh), Image.LANCZOS)
                    # paste onto main image
                    img.paste(tmp, (cx, y + 4), tmp)
                    w = nw
            except Exception:
                draw.text((cx, y), seg, font=f_text, fill=color)
        else:
            draw.text((cx, y), seg, font=f_text, fill=color)
        cx += w


def draw_body(draw, text, y, fs=44, highlight_last=True, centered=True, img=None):
    """
    Body text centered. Last sentence in green bold if highlight_last.
    """
    f_reg  = font(ROBOTO_REG, fs)
    f_bold = font(ROBOTO_BOLD, fs)
    lh = int(fs * 1.52)

    if highlight_last and ". " in text:
        idx = text.rfind(". ", 0, len(text) - 2)
        if idx != -1:
            normal = text[:idx + 2].strip()
            green  = text[idx + 2:].strip()
        else:
            normal, green = "", text
    else:
        normal, green = text, ""

    cy = y

    def render(txt, f, color):
        nonlocal cy
        lines = wrap(draw, txt, f, TEXT_W)
        for line in lines:
            if cy + lh > TEXT_MAX_Y:
                break
            if has_emoji(line):
                draw_mixed_line(draw, img, line, f, None, color, PAD_X, cy, centered, emoji_size=fs)
            elif centered:
                lw = text_width(draw, line, f)
                draw.text(((W - lw) // 2, cy), line, font=f, fill=color)
            else:
                draw.text((PAD_X, cy), line, font=f, fill=color)
            cy += lh

    if normal:
        render(normal, f_reg, DARK_GRAY)
    if green:
        render(green, f_bold, GREEN)

    return cy


# ─── SIGNATURE ────────────────────────────────────────────────────────────────
def draw_signature(img):
    draw = ImageDraw.Draw(img)
    f_name   = font(ROBOTO_BOLD, 38)
    f_handle = font(ROBOTO_REG,  34)

    name   = "Samuel Pereira"
    handle = "@segredosdaaudiencia"

    av_size = 96
    gap     = 16
    name_w  = text_width(draw, name, f_name)
    hdl_w   = text_width(draw, handle, f_handle)
    v_sz    = 26

    text_block_w = max(name_w, hdl_w + v_sz + 6)
    total_w      = av_size + gap + text_block_w
    start_x      = (W - total_w) // 2

    av_x = start_x
    av_y = SIG_Y

    # ── Avatar ──
    if AVATAR_PATH.exists():
        try:
            av = Image.open(AVATAR_PATH).convert("RGBA")
            av = ImageOps.fit(av, (av_size, av_size), method=Image.LANCZOS)
            # circular mask
            mask = Image.new("L", (av_size, av_size), 0)
            from PIL import ImageDraw as _ID
            _ID.Draw(mask).ellipse((0, 0, av_size - 1, av_size - 1), fill=255)
            # white circle border
            border = 3
            bc = Image.new("RGBA", (av_size + border * 2, av_size + border * 2), (255, 255, 255, 0))
            _ID.Draw(bc).ellipse((0, 0, av_size + border * 2 - 1, av_size + border * 2 - 1),
                                  fill=(220, 220, 220, 255))
            img.paste(bc.convert("RGB"), (av_x - border, av_y - border),
                      bc.split()[3] if bc.mode == "RGBA" else None)
            img.paste(av, (av_x, av_y), mask)
        except Exception as e:
            draw.ellipse((av_x, av_y, av_x + av_size, av_y + av_size), fill=(120, 120, 120))
    else:
        draw.ellipse((av_x, av_y, av_x + av_size, av_y + av_size), fill=(120, 120, 120))

    tx   = av_x + av_size + gap
    ty_n = av_y + (av_size - 38 - 34 - 8) // 2 + 4
    ty_h = ty_n + 46

    draw.text((tx, ty_n), name,   font=f_name,   fill=BLACK)
    draw.text((tx, ty_h), handle, font=f_handle, fill=DARK_GRAY)

    # verified badge — real Meta/Instagram badge image
    vx = tx + hdl_w + 6
    vy = ty_h + 2
    if BADGE_PATH.exists():
        try:
            badge = Image.open(BADGE_PATH).convert("RGBA")
            badge = badge.resize((v_sz + 4, v_sz + 4), Image.LANCZOS)
            # make checkerboard (transparent) background white
            bg = Image.new("RGBA", badge.size, (255, 255, 255, 255))
            badge = Image.alpha_composite(bg, badge).convert("RGB")
            # paste with white bg blend
            img.paste(badge, (vx, vy))
        except Exception:
            draw.ellipse((vx, vy, vx + v_sz, vy + v_sz), fill=BLUE_VERIFY)


# ─── SLIDE BUILDER ────────────────────────────────────────────────────────────
def build_slide(photo_path, number, title, body, output_path,
                highlight_last=True, fs_title=86, fs_body=44, text_y_offset=0, photo_centering=(0.5, 0.3)):

    img  = Image.new("RGB", (W, H), WHITE_BG)
    draw = ImageDraw.Draw(img)

    # ── Photo (cover fill, no black bars) ──
    p = Path(photo_path)
    if p.exists():
        photo = Image.open(p).convert("RGB")
        photo = ImageOps.fit(photo, (W, PHOTO_H), method=Image.LANCZOS, centering=photo_centering)
        img.paste(photo, (0, 0))
    else:
        draw.rectangle((0, 0, W, PHOTO_H), fill=(200, 200, 200))
        draw.text((W // 2, PHOTO_H // 2), "FOTO", fill=(160, 160, 160),
                  font=font(ANTON, 80), anchor="mm")

    # ── Green divider ──
    draw.rectangle((0, DIVIDER_Y, W, DIVIDER_Y + DIVIDER_H), fill=GREEN)

    # ── Headline ──
    y = TEXT_START_Y + text_y_offset
    if title:
        y = draw_headline(draw, number, title, y, fs=fs_title)
        y += 14

    # ── Body ──
    if body:
        y = draw_body(draw, body, y, fs=fs_body,
                      highlight_last=highlight_last, centered=True, img=img)

    # ── Signature ──
    draw_signature(img)

    img.save(output_path, "PNG")
    print(f"  ✓ {Path(output_path).name}")
    return output_path


# ─── SLIDE DATA ───────────────────────────────────────────────────────────────
SLIDES = [
    {
        "id": "01-capa",
        "photo": "photo-01-capa.png",
        "number": "",
        "title": "A PANINI VAI FATURAR R$700 MILHÕES NO BRASIL. COM PAPEL.",
        "body": "E a maioria das pessoas nem percebeu o que está sendo vendido de verdade.",
        "highlight_last": False,
        "fs_title": 80,
        "fs_body": 46,
        "photo_centering": (0.5, 0.38),
        "text_y_offset": 36,
    },
    {
        "id": "02-221pct",
        "photo": "photo-02-bancas.png",
        "number": "1.",
        "title": "TICKET MÉDIO SUBIU 221% EM 7 DIAS",
        "body": "Em 2022, o gasto médio por cliente era R$24. Em 2026, passou para R$55 — sem nenhuma promoção, sem desconto, sem influencer pago. As pessoas simplesmente quiseram mais.",
        "highlight_last": True,
        "fs_title": 86,
        "fs_body": 42,
    },
    {
        "id": "03-r16mil",
        "photo": "photo-03-neymar.png",
        "number": "2.",
        "title": "UMA BANCA FATUROU R$16 MIL EM UM DIA",
        "body": "Em São Paulo, bancas comuns registraram entre R$10 mil e R$16 mil em vendas num único dia. Vendendo pacotinhos de R$3,50. Isso é mais que muita loja de roupa fatura no mês.",
        "highlight_last": True,
        "fs_title": 82,
        "fs_body": 42,
    },
    {
        "id": "04-produto",
        "photo": "photo-04-album.png",
        "number": "",
        "title": "O QUE VOCÊ ACHA QUE ESTÁ COMPRANDO NÃO É O QUE VOCÊ ESTÁ COMPRANDO",
        "body": "Ninguém compra figurinha. Compram a antecipação de abrir o pacote. A dopamina da surpresa. O ritual que faz um adulto de 35 anos se sentir criança de novo. A figurinha é só a desculpa.",
        "highlight_last": True,
        "fs_title": 66,
        "fs_body": 39,
        "text_y_offset": 30,
    },
    {
        "id": "05-conexao",
        "photo": "photo-05-amigos.png",
        "number": "3.",
        "title": "CRIOU COMUNIDADE FÍSICA EM 2026. SEM APP. SEM GRUPO NO WHATSAPP.",
        "body": "Filas em bancas. Trocas entre desconhecidos no elevador. Crianças parando adultos na rua. 40 milhões de álbuns distribuídos no Brasil. Nenhum aplicativo de rede social fez isso esse ano.",
        "highlight_last": True,
        "fs_title": 74,
        "fs_body": 41,
    },
    {
        "id": "06-falta",
        "photo": "photo-06-estadio.png",
        "number": "4.",
        "title": "O MODELO DE NEGÓCIO DEPENDE DE VOCÊ NÃO COMPLETAR",
        "body": "São 670 figurinhas no total. A chance de completar comprando só pacotes é estatisticamente próxima de zero. Cada espaço vazio é uma missão incompleta. E missão incompleta vende o próximo pacote.",
        "highlight_last": True,
        "fs_title": 76,
        "fs_body": 41,
    },
    {
        "id": "07-preco",
        "photo": "photo-07-pacotes.png",
        "number": "5.",
        "title": "SUBIRAM 75% O PREÇO. A DEMANDA TRIPLICOU.",
        "body": "De R$2,00 em 2022 para R$3,50 em 2026. Aumento de 75%. Resultado? Filas maiores. Mais cobertura espontânea na mídia. Mais desejo. Preço alto não afastou ninguém. Sinalizou que valia ainda mais.",
        "highlight_last": True,
        "fs_title": 82,
        "fs_body": 41,
    },
    {
        "id": "08-viral",
        "photo": "photo-08-celular.png",
        "number": "6.",
        "title": "CONTEÚDO VIRAL NÃO NASCE DE INFORMAÇÃO. NASCE DE IDENTIDADE.",
        "body": "Ninguém compartilhou o álbum porque é útil. Compartilharam porque diz quem a pessoa é: alguém que completa o que começa. Alguém que valoriza o ritual. Esse é o gatilho por trás de todo post que você já viu explodir sem motivo aparente.",
        "highlight_last": True,
        "fs_title": 70,
        "fs_body": 36,
    },
    {
        "id": "09-publico",
        "photo": "photo-09-instagram.png",
        "number": "7.",
        "title": "SEU SEGUIDOR NÃO TE SEGUE PELO QUE VOCÊ SABE",
        "body": "A Panini tem concorrentes com produto mais barato. Ninguém liga. Porque o que ela vende não é figurinha — é familiaridade, é ritual, é pertencimento. Audiência real não é construída com informação. É construída com identificação.",
        "highlight_last": True,
        "fs_title": 76,
        "fs_body": 39,
    },
    {
        "id": "10-atencao",
        "photo": "photo-10-estadio2.png",
        "number": "",
        "title": "UM PACOTINHO DE R$3,50 DEU UMA AULA SOBRE ATENÇÃO HUMANA",
        "body": "R$700 milhões em faturamento. 40 milhões de álbuns. Viral orgânico em todo país. Filas de 2 horas. Sem Meta Ads. Sem influencer. Com papel e cola. O segredo? Venderam dopamina disfarçada de figurinha.",
        "highlight_last": True,
        "fs_title": 70,
        "fs_body": 39,
        "text_y_offset": 30,
    },
    {
        "id": "11-cta",
        "photo": "photo-11-cta.png",
        "number": "",
        "title": 'COMENTA "COPA" AQUI EMBAIXO',
        "body": "Eu te mando no direct os 7 gatilhos psicológicos que fazem qualquer conteúdo virar obsessão coletiva — os mesmos que a Panini usou sem você perceber. 🔖❤️💬↗️",
        "highlight_last": False,
        "fs_title": 88,
        "fs_body": 43,
    },
]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--slide", help="Only build this slide id")
    ap.add_argument("--skip-photos", action="store_true")
    args = ap.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    PHOTOS_DIR.mkdir(exist_ok=True)

    if not args.skip_photos:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        sys.path.insert(0, str(Path.home() / ".claude/skills/nano-banana-pro/scripts"))
        from generate_image import generate_image
        for slide in SLIDES:
            fname = PHOTOS_DIR / slide["photo"]
            if fname.exists():
                print(f"  Skip photo: {slide['photo']}")
                continue
            print(f"  Generating photo: {slide['photo']}")
            try:
                generate_image(prompt=slide["photo"], filename=str(fname), api_key=api_key)
            except Exception as e:
                print(f"  FAILED: {e}")

    print("── Building slides ──")
    for s in SLIDES:
        if args.slide and s["id"] != args.slide:
            continue
        build_slide(
            photo_path=str(PHOTOS_DIR / s["photo"]),
            number=s["number"],
            title=s["title"],
            body=s["body"],
            output_path=str(OUT_DIR / f"slide-{s['id']}.png"),
            highlight_last=s["highlight_last"],
            fs_title=s["fs_title"],
            fs_body=s["fs_body"],
            text_y_offset=s.get("text_y_offset", 0),
            photo_centering=s.get("photo_centering", (0.5, 0.3)),
        )
    print("\nDone.")
