#!/usr/bin/env python3
"""PMI Perry — Carrosseis IA e Viral. Auto-fit de fonte + bloco ancorado de baixo."""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os

W, H    = 1080, 1080
MARGIN  = 60          # margem lateral
MAX_W   = W - MARGIN*2
VIOLET  = (134, 0, 255)
VLT     = (160, 60, 255)
PINK    = (236, 72, 153)
WHITE   = (255, 255, 255)
GRAY    = (165, 168, 185)
RED     = (220, 38, 38)

R = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"
def F(style, size):
    return ImageFont.truetype({
        "black":   f"{R}/Roboto-Black.ttf",
        "bold":    f"{R}/Roboto-Bold.ttf",
        "medium":  f"{R}/Roboto-Medium.ttf",
        "regular": f"{R}/Roboto-Regular.ttf",
    }[style], size)

def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def tw(d, text, font):
    bb = d.textbbox((0,0), text, font=font); return bb[2]-bb[0]
def th(d, text, font):
    bb = d.textbbox((0,0), text, font=font); return bb[3]-bb[1]

def wrap(d, text, font, max_w=MAX_W):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if tw(d,test,font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ── Auto-fit fonte ─────────────────────────────────────────────────
def fit_font(d, lines, style, start=100, min_sz=52):
    """Reduz tamanho até todas as linhas caberem em MAX_W."""
    sz = start
    while sz >= min_sz:
        fnt = F(style, sz)
        if all(tw(d, ln, fnt) <= MAX_W for ln in lines):
            return sz, fnt
        sz -= 4
    return min_sz, F(style, min_sz)

# ── Overlay esfumaçado via GaussianBlur ───────────────────────────
def smoky_overlay(img, top_s=150, bot_s=252, top_r=270, bot_r=650, blur=56):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    dv = ImageDraw.Draw(ov)
    IW, IH = img.size
    for y in range(top_r):
        a = int(top_s * (1 - y/top_r)**1.8)
        dv.line([(0,y),(IW,y)], fill=(0,0,0,a))
    for y in range(IH-1, IH-bot_r-1, -1):
        dist = IH - 1 - y                          # 0 na borda, cresce subindo
        a = int(bot_s * (1 - dist / bot_r) ** 0.72)  # escuro embaixo, esfuma subindo
        dv.line([(0,y),(IW,y)], fill=(0,0,0,a))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    base = img.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

def load_bg(path, centering=(0.5,0.5)):
    img = Image.open(path).convert("RGB")
    return ImageOps.fit(img, (W,H), Image.LANCZOS, centering=centering)

# ── Logo PMI real ──────────────────────────────────────────────────
LOGO = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
def paste_logo(canvas, lh=54, x=52, y=42):
    logo = Image.open(LOGO).convert("RGBA")
    lw = int(logo.width * lh / logo.height)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    canvas.paste(logo, (x, y), logo)
    d = ImageDraw.Draw(canvas)
    d.rectangle([x, y+lh+8, x+lw, y+lh+12], fill=VIOLET)

# ── Gradiente no texto ─────────────────────────────────────────────
def grad_text(canvas, d, text, font, x, y, c1=VLT, c2=PINK):
    bb = d.textbbox((0,0), text, font=font)
    lw = bb[2] - bb[0]
    # Cobre os limites REAIS da tinta (bb[1]..bb[3]) não só th
    y0 = y + bb[1]; y1 = y + bb[3]
    lay  = Image.new("RGBA", canvas.size, (0,0,0,0))
    dl   = ImageDraw.Draw(lay); dl.text((x,y), text, font=font, fill=(*c1,255))
    tint = Image.new("RGBA", canvas.size, (0,0,0,0))
    dt   = ImageDraw.Draw(tint)
    for xi in range(x, x+lw):
        t = (xi-x)/max(1,lw-1)
        dt.line([(xi,y0),(xi,y1)], fill=(*lerp(c1,c2,t),255))
    _,_,_,ach = lay.split(); tint.putalpha(ach)
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(tint)
    return canvas.convert("RGB")

def darken_zone(canvas, y_top):
    """Segundo passe: escurece zona de texto para garantir legibilidade."""
    tz = Image.new("RGBA", canvas.size, (0,0,0,0))
    dz = ImageDraw.Draw(tz)
    t = max(y_top - 80, 0)
    IH = canvas.size[1]
    for iy in range(t, IH):
        a = int(210 * ((iy - t) / max(1, IH - t)) ** 0.55)
        dz.line([(0,iy),(canvas.size[0],iy)], fill=(0,0,0,a))
    tz = tz.filter(ImageFilter.GaussianBlur(36))
    base = canvas.convert("RGBA"); base.alpha_composite(tz)
    return base.convert("RGB")

def sep_line(d, y, w=56):
    x = (W-w)//2
    for xi in range(w):
        c = lerp(VLT, PINK, xi/max(1,w-1))
        d.line([(x+xi,y),(x+xi,y+5)], fill=c)
    return y+5

# ── Blocos de texto centrado ───────────────────────────────────────
def draw_sub(canvas, d, text, y, fnt_sz=27, color=GRAY):
    fnt = F("regular", fnt_sz)
    lh  = int(fnt_sz*1.5)
    for line in wrap(d, text, fnt):
        lw = tw(d,line,fnt)
        d.text(((W-lw)//2, y), line, font=fnt, fill=color)
        y += lh
    return y

# ── Slide genérico: headline (último gradiente) + sep + subtítulo ──
def make_slide(bg_path, headlines, subtitle, out_path,
               centering=(0.5,0.5), h_start=100,
               top_s=150, bot_s=252, top_r=270, bot_r=650, blur=56,
               extra_fn=None):
    """
    headlines: lista de str; a ÚLTIMA linha recebe gradiente.
    extra_fn(canvas, d, y) → y : chamada após subtítulo (botões, etc).
    """
    canvas = smoky_overlay(load_bg(bg_path, centering),
                           top_s, bot_s, top_r, bot_r, blur)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    # ── Auto-fit tamanho headline ──────────────────────────────────
    h_sz, fnt_h = fit_font(d, headlines, "black", h_start)
    lead = int(h_sz * 1.08)

    # ── Medir altura total do bloco ────────────────────────────────
    fnt_s  = F("regular", 27)
    sub_ls = wrap(d, subtitle, fnt_s)
    sub_h  = len(sub_ls) * int(27*1.5)

    extra_h = 80 if extra_fn else 0   # reserva para botões se houver

    block_h = lead*len(headlines) + 20 + 5 + 18 + sub_h + extra_h

    # ── Âncora: bloco cabe acima de y=H-100 ──────────────────────
    y = max(H - 100 - block_h, 460)

    # ── 2º passe: escurece zona de texto ──────────────────────────
    canvas = darken_zone(canvas, y)
    d = ImageDraw.Draw(canvas)          # recria d no canvas atualizado

    # ── Headlines ─────────────────────────────────────────────────
    for i, line in enumerate(headlines):
        lw = tw(d, line, fnt_h)
        x  = (W - lw) // 2
        if i == len(headlines)-1:           # última = gradiente
            canvas = grad_text(canvas, d, line, fnt_h, x, y)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((x, y), line, font=fnt_h, fill=WHITE)
        y += lead

    # ── Separador + subtítulo ──────────────────────────────────────
    y += 20
    y  = sep_line(d, y) + 18
    y  = draw_sub(canvas, d, subtitle, y)

    if extra_fn:
        extra_fn(canvas, d, y)

    canvas.save(out_path)
    print(f"✓ {os.path.basename(out_path)}")


OUT = "/home/user/WEB/carrossel-pmi/slides"
BG  = "/home/user/WEB/carrossel-pmi"
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
# CARROSSEL 1 — "A IA VAI MATAR SEU NEGÓCIO?"
# ══════════════════════════════════════════════════════════════════

def c1_slide01():
    make_slide(
        f"{BG}/bg_ia_slide01.png",
        ["A IA VAI", "MATAR SEU", "NEGÓCIO?"],
        "A resposta honesta que ninguém do mercado quer dar.",
        f"{OUT}/c1_slide01.png",
        h_start=112, top_r=260, bot_r=640,
    )

def c1_slide02():
    # Layout especial: "60%" hero + headline + sub
    canvas = smoky_overlay(load_bg(f"{BG}/bg_ia_slide02.png"),
                           120, 248, 240, 660, 60)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    # "60%" hero — calcular y_start antes do darken_zone
    headlines = ["DOS NEGÓCIOS JÁ USAM", "IA PARA CRIAR CONTEÚDO"]
    _, fnt_h = fit_font(d, headlines, "black", 72)
    fnt_big  = F("black", 160)
    lead_h   = int(fnt_h.size * 1.08)

    fnt_s   = F("regular", 27)
    sub_ls  = wrap(d, "Estão produzindo mais, mais rápido. E convertendo menos. Volume sem estratégia é ruído.", fnt_s)
    sub_h   = len(sub_ls)*int(27*1.5)

    num_h   = th(d,"60%",fnt_big)
    block_h = num_h + 12 + lead_h*len(headlines) + 20+5+18 + sub_h
    y = max(H-100-block_h, 400)
    canvas = darken_zone(canvas, y)
    d = ImageDraw.Draw(canvas)

    # "60%" gradiente
    nw = tw(d,"60%",fnt_big)
    canvas = grad_text(canvas, d, "60%", fnt_big, (W-nw)//2, y)
    d = ImageDraw.Draw(canvas)
    y += num_h + 12

    # Headlines
    for i, line in enumerate(headlines):
        lw = tw(d, line, fnt_h)
        if i == len(headlines)-1:
            canvas = grad_text(canvas, d, line, fnt_h, (W-lw)//2, y)
            d = ImageDraw.Draw(canvas)
        else:
            d.text(((W-lw)//2, y), line, font=fnt_h, fill=WHITE)
        y += lead_h

    y += 20; y = sep_line(d, y) + 18
    draw_sub(canvas, d, "Estão produzindo mais, mais rápido. E convertendo menos. Volume sem estratégia é ruído.", y)
    canvas.save(f"{OUT}/c1_slide02.png"); print("✓ c1_slide02")

def c1_slide03():
    make_slide(
        f"{BG}/bg_ia_slide03.png",
        ["A IA EXECUTA.", "ESTRATÉGIA É HUMANA."],
        "Ferramenta não diagnostica negócio. Não lê contexto de mercado. Não constrói posicionamento real.",
        f"{OUT}/c1_slide03.png",
        h_start=100, top_s=100, bot_r=580,
    )

def c1_slide04():
    make_slide(
        f"{BG}/bg_ia_slide04.png",
        ["O NEGÓCIO QUE VAI MORRER", "NÃO USA IA."],
        "É o que não sabe o que fazer com ela. O problema nunca foi a ferramenta. Foi sempre a falta de estratégia.",
        f"{OUT}/c1_slide04.png",
        h_start=100, top_r=250, bot_r=620,
    )

def c1_slide05():
    def extra(canvas, d, y):
        fnt_b  = F("bold", 28)
        labels = [("USE", VLT), ("MEDO", PINK)]
        btns   = [(lbl, col, tw(d,lbl,fnt_b)+52, th(d,lbl,fnt_b)+22)
                  for lbl, col in labels]
        total  = sum(b[2] for b in btns) + 20
        bx     = (W-total)//2
        y2 = y + 14
        for lbl, col, bw, bh in btns:
            d.rounded_rectangle([bx,y2,bx+bw,y2+bh], radius=10, fill=col)
            d.text((bx+(bw-tw(d,lbl,fnt_b))//2, y2+(bh-th(d,lbl,fnt_b))//2),
                   lbl, font=fnt_b, fill=WHITE)
            bx += bw+20
        draw_sub(canvas, d, "Comenta aqui. Vamos falar sobre isso.", y2+btns[0][3]+14)

    make_slide(
        f"{BG}/bg_ia_slide05.png",
        ["VOCÊ USA IA NO", "SEU NEGÓCIO?"],
        "",        # sub vazia: extra cuida do rodapé
        f"{OUT}/c1_slide05.png",
        h_start=100, top_r=240, bot_r=660,
        extra_fn=extra,
    )


# ══════════════════════════════════════════════════════════════════
# CARROSSEL 2 — "VIRAL ESTÁ MORTO"
# ══════════════════════════════════════════════════════════════════

def c2_slide01():
    # Especial: "VIRAL" com tachado + segunda linha gradiente
    canvas = smoky_overlay(load_bg(f"{BG}/bg_viral_slide01.png"),
                           140, 252, 260, 640, 58)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    headlines = ["VIRAL", "ESTÁ MORTO."]
    h_sz, fnt_h = fit_font(d, headlines, "black", 128)
    lead = int(h_sz*1.08)

    fnt_s   = F("regular", 27)
    sub_ls  = wrap(d, "E quem ainda corre atrás disso está perdendo tempo, dinheiro e posicionamento.", fnt_s)
    sub_h   = len(sub_ls)*int(27*1.5)
    block_h = lead*2 + 20+5+18 + sub_h
    y = max(H-100-block_h, 440)
    canvas = darken_zone(canvas, y)
    d = ImageDraw.Draw(canvas)

    # "VIRAL" branco + tachado vermelho
    lw1 = tw(d,"VIRAL",fnt_h); lh1 = th(d,"VIRAL",fnt_h)
    x1  = (W-lw1)//2
    d.text((x1, y), "VIRAL", font=fnt_h, fill=WHITE)
    mid = y + lh1//2
    d.line([(x1-6, mid),(x1+lw1+6, mid)], fill=RED, width=max(8, h_sz//14))
    y += lead

    # "ESTÁ MORTO." gradiente
    lw2 = tw(d,"ESTÁ MORTO.",fnt_h)
    canvas = grad_text(canvas, d, "ESTÁ MORTO.", fnt_h, (W-lw2)//2, y)
    d = ImageDraw.Draw(canvas)
    y += lead

    y += 20; y = sep_line(d, y) + 18
    draw_sub(canvas, d, "E quem ainda corre atrás disso está perdendo tempo, dinheiro e posicionamento.", y)
    canvas.save(f"{OUT}/c2_slide01.png"); print("✓ c2_slide01")

def c2_slide02():
    make_slide(
        f"{BG}/bg_viral_slide02.png",
        ["O ALGORITMO PAROU", "DE PREMIAR BARULHO"],
        "Em 2026 o Instagram virou curador de relevância. Conteúdo apelativo e sem substância perdeu alcance.",
        f"{OUT}/c2_slide02.png",
        h_start=92, top_s=120, bot_r=650,
    )

def c2_slide03():
    make_slide(
        f"{BG}/bg_viral_slide03.png",
        ["1 MILHÃO DE VIEWS DE QUEM", "NÃO COMPRA NÃO PAGA BOLETO."],
        "Alcance sem retenção é vaidade. Quem retém audiência qualificada vende. Quem viraliza pra nada, some.",
        f"{OUT}/c2_slide03.png",
        h_start=80, top_s=130, bot_r=620,
    )

def c2_slide04():
    make_slide(
        f"{BG}/bg_viral_slide04.png",
        ["O QUE REALMENTE", "FUNCIONA AGORA"],
        "Conteúdo que resolve. Que ensina. Que posiciona. Consistência bate viral eventual toda semana.",
        f"{OUT}/c2_slide04.png",
        h_start=104, top_s=110, bot_r=600,
    )

def c2_slide05():
    def extra(canvas, d, y):
        fnt_b  = F("bold", 28)
        labels = [("SIM", VIOLET), ("NÃO", PINK)]
        btns   = [(lbl, col, tw(d,lbl,fnt_b)+52, th(d,lbl,fnt_b)+22)
                  for lbl, col in labels]
        total  = sum(b[2] for b in btns) + 20
        bx     = (W-total)//2
        y2 = y + 14
        for lbl, col, bw, bh in btns:
            d.rounded_rectangle([bx,y2,bx+bw,y2+bh], radius=10, fill=col)
            d.text((bx+(bw-tw(d,lbl,fnt_b))//2, y2+(bh-th(d,lbl,fnt_b))//2),
                   lbl, font=fnt_b, fill=WHITE)
            bx += bw+20
        draw_sub(canvas, d, "Curioso pra saber a proporção.", y2+btns[0][3]+14)

    make_slide(
        f"{BG}/bg_viral_slide05.png",
        ["PARA DE PERSEGUIR VIRAL.", "CONSTRÓI AUTORIDADE."],
        "",
        f"{OUT}/c2_slide05.png",
        h_start=96, top_s=130, bot_r=650,
        extra_fn=extra,
    )


# ── Run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Carrossel 1: A IA vai matar seu negócio? ===")
    c1_slide01(); c1_slide02(); c1_slide03(); c1_slide04(); c1_slide05()
    print("\n=== Carrossel 2: Viral está morto ===")
    c2_slide01(); c2_slide02(); c2_slide03(); c2_slide04(); c2_slide05()
    print(f"\nDone → {OUT}")
