#!/usr/bin/env python3
"""
PMI — Carrosseis Domingo V3. Layouts densos, sem espaço morto.
  A: SPLIT BRUTALISTA  — metade cor pura / metade imagem, texto preenchendo todo espaço
  B: POSTER PUNK       — fundo escuro + acento AMARELO QUENTE, sem LIME
  C: EDITORIAL CLARO   — imagem topo + zona CREME com dados gigantes
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os

W, H   = 1080, 1350
M      = 52   # margem padrão

# ── Paleta A — Split Brutalista ───────────────────────────────────
A_PUR  = (130,  40, 220)   # roxo sólido (mais saturado que VLT)
A_WHT  = (255, 255, 255)
A_BLK  = (  0,   0,   0)
A_PNK  = (236,  72, 153)
A_GRY  = (200, 185, 225)   # cinza lilás

# ── Paleta B — Poster Punk ────────────────────────────────────────
B_BG   = (  6,   4,  12)   # quase preto
B_YEL  = (255, 210,   0)   # amarelo quente (não LIME)
B_RED  = (220,  40,  60)   # vermelho acento
B_WHT  = (245, 240, 255)
B_GRY  = (120, 110, 140)
B_VLT  = (160,  60, 255)

# ── Paleta C — Editorial Claro ────────────────────────────────────
C_CLAY = (238, 228, 210)   # bege/creme
C_INK  = ( 16,  10,  22)   # preto quase roxo
C_PLUM = ( 90,  15, 130)   # roxo escuro
C_RSE  = (200,  55, 100)   # rosa forte
C_MID  = (140, 120, 100)   # cinza bege

R = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"
def F(style, size):
    return ImageFont.truetype({
        "black":   f"{R}/Roboto-Black.ttf",
        "bold":    f"{R}/Roboto-Bold.ttf",
        "medium":  f"{R}/Roboto-Medium.ttf",
        "regular": f"{R}/Roboto-Regular.ttf",
        "light":   f"{R}/Roboto-Light.ttf",
    }[style], size)

def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def tw(d, t, f):
    bb = d.textbbox((0,0), t, font=f); return bb[2]-bb[0]
def tb(d, t, f):
    return d.textbbox((0,0), t, font=f)

def wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if tw(d, test, font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fit_font(d, lines, style, start=140, min_sz=32, max_w=W-M*2):
    sz = start
    while sz >= min_sz:
        f = F(style, sz)
        if all(tw(d,ln,f) <= max_w for ln in lines): return sz, f
        sz -= 2
    return min_sz, F(style, min_sz)

def load_bg(path, ctr=(0.5,0.5)):
    return ImageOps.fit(Image.open(path).convert("RGB"), (W,H),
                        Image.LANCZOS, centering=ctr)

def overlay(canvas, color, alpha):
    ov   = Image.new("RGBA", canvas.size, (*color, alpha))
    base = canvas.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

def fill_rect(canvas, x, y, w, h, color, alpha=255):
    lay = Image.new("RGBA", canvas.size, (0,0,0,0))
    ImageDraw.Draw(lay).rectangle([x,y,x+w,y+h], fill=(*color,alpha))
    base = canvas.convert("RGBA"); base.alpha_composite(lay)
    return base.convert("RGB")

def hline(d, y, h=6, c1=(160,60,255), c2=(236,72,153), x0=0, x1=W):
    for xi in range(x0, x1):
        d.line([(xi,y),(xi,y+h)], fill=lerp(c1,c2,(xi-x0)/max(1,x1-x0-1)))

def grad_text(canvas, d, text, font, x, y, c1, c2):
    bb  = tb(d,text,font); lw_=bb[2]-bb[0]; y0=y+bb[1]; y1=y+bb[3]
    lay = Image.new("RGBA",canvas.size,(0,0,0,0))
    ImageDraw.Draw(lay).text((x,y),text,font=font,fill=(*c1,255))
    tint= Image.new("RGBA",canvas.size,(0,0,0,0)); dt=ImageDraw.Draw(tint)
    for xi in range(x,x+lw_):
        c=lerp(c1,c2,(xi-x)/max(1,lw_-1))
        dt.line([(xi,y0),(xi,y1)],fill=(*c,255))
    _,_,_,a=lay.split(); tint.putalpha(a)
    base=canvas.convert("RGBA"); base.alpha_composite(tint)
    return base.convert("RGB")

def border(canvas, color=A_BLK, thick=7):
    ImageDraw.Draw(canvas).rectangle([0,0,W-1,H-1], outline=color, width=thick)

LOGO = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
def paste_logo(canvas, x=M, y=38, lh=38, bg_color=None):
    if bg_color:
        ImageDraw.Draw(canvas).rounded_rectangle(
            [x-8,y-6,x+180,y+lh+8], radius=10, fill=(*bg_color, 230))
    logo = Image.open(LOGO).convert("RGBA")
    lw   = int(logo.width*lh/logo.height)
    logo = logo.resize((lw,lh), Image.LANCZOS)
    canvas.paste(logo, (x,y), logo)

BG  = "/home/user/WEB/carrossel-pmi"
OUT = "/home/user/WEB/carrossel-pmi/domingo_v3"
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
# CAROUSEL A — SPLIT BRUTALISTA
# Metade esquerda: cor pura com texto; Metade direita: imagem
# Texto preenche TODA a zona colorida sem espaço vazio
# ══════════════════════════════════════════════════════════════════

SPLIT = int(W * 0.50)   # divisória exatamente no meio

def a_make(bg_path, lines_top, lines_bot, sub, out, ctr=(0.5,0.5),
           color=A_PUR, accent=A_PNK, img_side="right"):
    """
    lines_top: lista de strings, fonte GIGANTE (preenche zona superior)
    lines_bot: lista de strings, fonte GRANDE (preenche zona inferior)
    sub: string, fonte pequena
    """
    img    = load_bg(bg_path, ctr=ctr)
    canvas = img.copy()

    # bloco de cor sólida (esquerda ou direita)
    if img_side == "right":
        canvas = fill_rect(canvas, 0, 0, SPLIT, H, color)
        txt_x0, txt_x1 = 0, SPLIT
        img_x0 = SPLIT
    else:
        canvas = fill_rect(canvas, SPLIT, 0, W-SPLIT, H, color)
        txt_x0, txt_x1 = SPLIT, W
        img_x0 = 0

    d      = ImageDraw.Draw(canvas)
    zone_w = SPLIT - 16   # largura disponível para texto

    # divisória preta grossa
    d.rectangle([SPLIT-4, 0, SPLIT+4, H], fill=A_BLK)

    # ── Bloco superior: texto enorme que preenche a zona ──────────
    # calcula fonte máxima que cabe em zone_w
    top_text = " ".join(lines_top)   # para estimar
    sz = 160
    while sz >= 48:
        f = F("black", sz)
        if all(tw(d,ln,f) <= zone_w-8 for ln in lines_top): break
        sz -= 2
    fnt_top  = F("black", sz)
    lead_top = int(sz * 1.0)
    block_top_h = lead_top * len(lines_top)

    # ── Bloco inferior: texto grande ──────────────────────────────
    sz2 = sz - 28
    while sz2 >= 36:
        f = F("black", sz2)
        if all(tw(d,ln,f) <= zone_w-8 for ln in lines_bot): break
        sz2 -= 2
    fnt_bot  = F("black", sz2)
    lead_bot = int(sz2 * 1.0)
    block_bot_h = lead_bot * len(lines_bot)

    # ── Fonte para sub ────────────────────────────────────────────
    fnt_sub  = F("bold", min(32, max(22, sz//5)))
    sub_lines= wrap(d, sub, fnt_sub, zone_w-8)
    sub_h    = int(fnt_sub.size * 1.4) * len(sub_lines)

    # ── Distribuição vertical — sem espaço morto ──────────────────
    # Reserva: logo 90px topo + margem 20px bot
    available = H - 90 - 30
    sep_h     = 10   # separador grosso
    total_h   = block_top_h + sep_h + block_bot_h + sep_h + sub_h
    gap       = max(12, (available - total_h) // 3)

    ty = 90 + gap

    # topo
    for ln in lines_top:
        d.text((txt_x0+6, ty), ln, font=fnt_top, fill=A_WHT)
        ty += lead_top

    # separador grosso
    ty += 4
    d.rectangle([txt_x0+6, ty, txt_x0+zone_w-6, ty+sep_h], fill=A_BLK)
    ty += sep_h + gap//2

    # inferior (última linha com acento)
    for i, ln in enumerate(lines_bot):
        if i == len(lines_bot)-1:
            canvas = grad_text(canvas, d, ln, fnt_bot, txt_x0+6, ty, accent, A_WHT)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((txt_x0+6, ty), ln, font=fnt_bot, fill=A_WHT)
        ty += lead_bot

    # sub
    ty += gap//2
    for ln in sub_lines:
        d.text((txt_x0+6, ty), ln, font=fnt_sub, fill=A_GRY)
        ty += int(fnt_sub.size*1.4)

    # borda brutalista
    border(canvas)
    paste_logo(canvas, x=txt_x0+M, bg_color=color)
    canvas.save(out); print(f"✓ {os.path.basename(out)}")


def a_s01():
    a_make(f"{BG}/bg_v2_v2_a_s01.png",
           lines_top=["SEU", "CONTEÚDO"],
           lines_bot=["PARECE FEITO", "POR ROBÔ."],
           sub="Porque parece mesmo.",
           out=f"{OUT}/a_slide01.png", ctr=(0.7,0.5))

def a_s02():
    a_make(f"{BG}/bg_v2_v2_a_s02.png",
           lines_top=["TODO", "MUNDO USA", "IA."],
           lines_bot=["TODO MUNDO", "SONA IGUAL."],
           sub="O feed virou uma fábrica sem dono.",
           out=f"{OUT}/a_slide02.png", color=(80,10,160))

def a_s03():
    a_make(f"{BG}/bg_v2_v2_a_s03.png",
           lines_top=["O QUE", "DIFERENCIA"],
           lines_bot=["NÃO É A", "FERRAMENTA."],
           sub="É a VOZ. E voz não se automatiza.",
           out=f"{OUT}/a_slide03.png", color=A_BLK, accent=A_PUR, img_side="right")

def a_s04():
    a_make(f"{BG}/bg_v2_v2_a_s04.png",
           lines_top=["É", "A VOZ."],
           lines_bot=["NUNCA FOI", "A FERRAMENTA."],
           sub="Quem usa IA sem voz própria não é insubstituível.",
           out=f"{OUT}/a_slide04.png", color=(100,0,180), ctr=(0.4,0.5))

def a_s05():
    a_make(f"{BG}/bg_v2_v2_a_s05.png",
           lines_top=["VOCÊ", "AINDA SENTE"],
           lines_bot=["SUA VOZ", "NOS POSTS?"],
           sub="Responde nos comentários.",
           out=f"{OUT}/a_slide05.png", color=A_PUR, img_side="left", ctr=(0.3,0.5))


# ══════════════════════════════════════════════════════════════════
# CAROUSEL B — POSTER PUNK
# Fundo quase preto + acento AMARELO QUENTE (não LIME)
# Texto denso, sem espaço vazio, estética de pôster de rua
# ══════════════════════════════════════════════════════════════════

def b_make(bg_path, big_word, strikethrough=False, lines_mid=None,
           lines_bot=None, sub=None, out=None, ctr=(0.5,0.5), overlay_alpha=155):
    img    = load_bg(bg_path, ctr=ctr)
    canvas = overlay(img, B_BG, overlay_alpha)
    d      = ImageDraw.Draw(canvas)

    # faixa amarela topo (7px)
    for xi in range(W):
        d.line([(xi,0),(xi,7)], fill=lerp(B_YEL,(255,160,0),xi/(W-1)))

    ty = 28

    # palavra gigante centralizada
    if big_word:
        sz = 170
        while sz >= 60:
            f = F("black", sz)
            if tw(d, big_word, f) <= W-20: break
            sz -= 2
        fnt_big = F("black", sz)
        lw_ = tw(d, big_word, fnt_big)
        x_w = (W-lw_)//2
        d.text((x_w, ty), big_word, font=fnt_big, fill=B_WHT)

        if strikethrough:
            bb   = tb(d, big_word, fnt_big)
            txt_h= bb[3]-bb[1]
            mid_y= ty+bb[1]+txt_h//2
            lh   = max(16, txt_h//7)
            # risca tripla: amarelo + vermelho + amarelo
            d.rectangle([x_w-6, mid_y-lh//2-3, x_w+lw_+6, mid_y-lh//2+3], fill=B_YEL)
            d.rectangle([x_w-6, mid_y-lh//2,   x_w+lw_+6, mid_y+lh//2],   fill=B_RED)
            d.rectangle([x_w-6, mid_y+lh//2-3, x_w+lw_+6, mid_y+lh//2+3], fill=B_YEL)

        ty += int(fnt_big.size * 0.98)

    # faixa separadora
    for xi in range(W):
        d.line([(xi,ty),(xi,ty+8)], fill=lerp(B_YEL,(255,100,0),xi/(W-1)))
    ty += 20

    # linhas do meio
    if lines_mid:
        sz2 = 92
        while sz2 >= 40:
            f = F("black", sz2)
            if all(tw(d,ln,f) <= W-M*2 for ln in lines_mid): break
            sz2 -= 2
        fnt_mid = F("black", sz2)
        for ln in lines_mid:
            lw_ = tw(d,ln,fnt_mid); d.text(((W-lw_)//2,ty),ln,font=fnt_mid,fill=B_WHT)
            ty += int(sz2*1.04)
        ty += 6

    # linhas inferiores (com destaque amarelo na última)
    if lines_bot:
        sz3 = 74
        while sz3 >= 36:
            f = F("black", sz3)
            if all(tw(d,ln,f) <= W-M*2 for ln in lines_bot): break
            sz3 -= 2
        fnt_bot = F("black", sz3)
        for i, ln in enumerate(lines_bot):
            lw_ = tw(d,ln,fnt_bot)
            if i == len(lines_bot)-1:
                canvas = grad_text(canvas,d,ln,fnt_bot,(W-lw_)//2,ty,B_YEL,(255,160,0))
                d = ImageDraw.Draw(canvas)
            else:
                d.text(((W-lw_)//2,ty),ln,font=fnt_bot,fill=B_WHT)
            ty += int(sz3*1.04)
        ty += 8

    # subtítulo
    if sub:
        for xi in range(W):
            d.line([(xi,ty),(xi,ty+5)], fill=lerp(B_VLT,A_PNK,xi/(W-1)))
        ty += 14
        fnt_s = F("regular", 30)
        for ln in wrap(d, sub, fnt_s, W-M*2):
            lw_ = tw(d,ln,fnt_s); d.text(((W-lw_)//2,ty),ln,font=fnt_s,fill=B_GRY)
            ty += int(fnt_s.size*1.5)

    paste_logo(canvas, bg_color=B_BG)
    canvas.save(out); print(f"✓ {os.path.basename(out)}")


def b_s01():
    b_make(f"{BG}/bg_v2_v2_b_s01.png",
           big_word="VIRALIZAR", strikethrough=True,
           lines_mid=["NÃO É MAIS O OBJETIVO."],
           lines_bot=["NA VERDADE,", "NUNCA FOI."],
           sub="Viral é pico. Comunidade é renda.",
           out=f"{OUT}/b_slide01.png")

def b_s02():
    b_make(f"{BG}/bg_v2_v2_b_s02.png",
           big_word=None,
           lines_mid=["200 MIL CURTIDAS.", "ZERO VENDAS."],
           lines_bot=["ISSO ACONTECE", "TODO DIA."],
           sub="Alcance que não converte é vaidade. Não é negócio.",
           out=f"{OUT}/b_slide02.png", ctr=(0.5,0.3))

def b_s03():
    b_make(f"{BG}/bg_v2_v2_b_s03.png",
           big_word="VIRAL",
           lines_mid=["É EGO."],
           lines_bot=["COMUNIDADE", "É NEGÓCIO."],
           sub="As marcas que mais vendem têm comunidade pequena e lista de espera.",
           out=f"{OUT}/b_slide03.png")

def b_s04():
    b_make(f"{BG}/bg_v2_v2_b_s04.png",
           big_word=None,
           lines_mid=["EM QUAL LADO", "VOCÊ ESTÁ", "APOSTANDO?"],
           lines_bot=["VIRAL", "OU COMUNIDADE?"],
           sub="O que explode some. O que serve fica.",
           out=f"{OUT}/b_slide04.png", ctr=(0.5,0.4))

def b_s05():
    b_make(f"{BG}/bg_v2_v2_b_s05.png",
           big_word=None,
           lines_mid=["QUAL O TAMANHO", "DO SEU PÚBLICO", "MAIS FIEL?"],
           lines_bot=["NEM PRECISA SER GRANDE.", "PRECISA SER SEU."],
           sub="Comenta aqui o número.",
           out=f"{OUT}/b_slide05.png", ctr=(0.5,0.4), overlay_alpha=120)


# ══════════════════════════════════════════════════════════════════
# CAROUSEL C — EDITORIAL CLARO
# Imagem ocupa topo 44% | linha separadora | zona creme com dados
# Texto PRETO, dado gigante, sub em roxo escuro — sem espaço morto
# ══════════════════════════════════════════════════════════════════

CUT = int(H * 0.44)   # linha de corte imagem/creme

def c_make(bg_path, stat=None, stat_label=None, lines_h=None,
           sub=None, out=None, ctr=(0.5,0.35)):
    img     = load_bg(bg_path, ctr=ctr)
    img_top = img.crop((0, 0, W, CUT))

    canvas  = Image.new("RGB", (W,H), C_CLAY)
    canvas.paste(img_top, (0,0))

    d = ImageDraw.Draw(canvas)
    # linha separadora PLUM grossa
    d.rectangle([0, CUT, W, CUT+10], fill=C_PLUM)

    # ── Zona de texto: de CUT+10 até H ───────────────────────────
    zone_h   = H - CUT - 10
    ty       = CUT + 10 + 20
    zone_w   = W - M*2

    if stat:
        # número/stat gigante — preenche a largura
        sz = 240
        while sz >= 80:
            f = F("black", sz)
            if tw(d, stat, f) <= zone_w: break
            sz -= 4
        fnt_stat = F("black", sz)
        lw_ = tw(d, stat, fnt_stat)
        d.text(((W-lw_)//2, ty), stat, font=fnt_stat, fill=C_INK)
        ty += int(fnt_stat.size * 0.88)

        if stat_label:
            fnt_lbl = F("bold", min(40, max(26, sz//6)))
            for ln in wrap(d, stat_label, fnt_lbl, zone_w):
                lw_ = tw(d,ln,fnt_lbl)
                d.text(((W-lw_)//2,ty),ln,font=fnt_lbl,fill=C_PLUM)
                ty += int(fnt_lbl.size*1.15)
        ty += 8
        # linha separadora fina
        d.rectangle([M, ty, W-M, ty+5], fill=C_PLUM)
        ty += 16

    if lines_h:
        sz2 = 96
        while sz2 >= 36:
            f = F("black", sz2)
            if all(tw(d,ln,f) <= zone_w for ln in lines_h): break
            sz2 -= 2
        fnt_h = F("black", sz2)
        for i, ln in enumerate(lines_h):
            lw_ = tw(d,ln,fnt_h)
            col = C_RSE if i == len(lines_h)-1 else C_INK
            d.text(((W-lw_)//2,ty),ln,font=fnt_h,fill=col)
            ty += int(sz2*1.04)
        ty += 8

    if sub:
        fnt_s = F("regular", 30)
        for ln in wrap(d, sub, fnt_s, zone_w):
            lw_ = tw(d,ln,fnt_s)
            d.text(((W-lw_)//2,ty),ln,font=fnt_s,fill=C_MID)
            ty += int(fnt_s.size*1.5)

    paste_logo(canvas, bg_color=C_CLAY)
    canvas.save(out); print(f"✓ {os.path.basename(out)}")


def c_s01():
    c_make(f"{BG}/bg_domingo_dom_c_s01.png",
           stat="47M",
           stat_label="de empreendedores no Brasil.",
           lines_h=["A MAIORIA NÃO SABE", "O QUE ESTÁ VENDENDO."],
           sub="Não é falta de produto. É falta de clareza.",
           out=f"{OUT}/c_slide01.png")

def c_s02():
    c_make(f"{BG}/bg_domingo_dom_c_s02.png",
           stat=None,
           lines_h=["NÃO É FALTA", "DE PRODUTO.", "É FALTA DE CLAREZA."],
           sub="Sobre o que você vende, para quem, e por que você.",
           out=f"{OUT}/c_slide02.png", ctr=(0.5,0.4))

def c_s03():
    c_make(f"{BG}/bg_domingo_dom_c_s03.png",
           stat=None,
           lines_h=["FALAR ALTO", "NÃO É SER OUVIDO."],
           sub="Quem fala para todos não fala com ninguém. Clareza atrai, volume cansa.",
           out=f"{OUT}/c_slide03.png")

def c_s04():
    c_make(f"{BG}/bg_domingo_dom_c_s04.png",
           stat=None,
           lines_h=["POSICIONAMENTO", "CLARO VENDE MAIS", "QUE CRIATIVIDADE."],
           sub="Sempre vendeu. Só ninguém falava isso abertamente.",
           out=f"{OUT}/c_slide04.png")

def c_s05():
    c_make(f"{BG}/bg_domingo_dom_c_s05.png",
           stat=None,
           lines_h=["ESCREVE O QUE VOCÊ", "VENDE EM UMA FRASE.", "SEM 'SOLUÇÃO'."],
           sub="Quem consegue está no caminho. Quem trava, a gente conversa.",
           out=f"{OUT}/c_slide05.png", ctr=(0.5,0.4))


if __name__ == "__main__":
    print("=== A — SPLIT BRUTALISTA ===")
    a_s01(); a_s02(); a_s03(); a_s04(); a_s05()
    print("\n=== B — POSTER PUNK ===")
    b_s01(); b_s02(); b_s03(); b_s04(); b_s05()
    print("\n=== C — EDITORIAL CLARO ===")
    c_s01(); c_s02(); c_s03(); c_s04(); c_s05()
    print(f"\nDone → {OUT}")
