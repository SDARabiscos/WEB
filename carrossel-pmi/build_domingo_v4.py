#!/usr/bin/env python3
"""
PMI — Carrosseis Domingo V4. Grid correto baseado em pesquisa.

Grid 1080x1350:
  Margem lateral : 72px
  Logo           : y=40, altura=44px
  Conteúdo início: y=160 (após zona de UI do Instagram 120px + 40px respiro)
  Conteúdo fim   : y=1230
  CTA/sub ancora : y=1240 (base fixa)
  Zona útil      : 1230-160 = 1070px
  Espaçamentos   : múltiplos de 8px (8,16,24,32,48,64)
  Centro óptico  : y=607 (45%)
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os

W, H   = 1080, 1350
M      = 72    # margem lateral

# ── Grid fixo ────────────────────────────────────────────────────
LOGO_Y    = 40     # logo topo
LOGO_H    = 44     # altura logo
TOP_SAFE  = 160    # conteúdo começa aqui
BOT_SAFE  = 1230   # conteúdo termina aqui
CTA_Y     = 1248   # subtítulo ancora base
CONTENT_H = BOT_SAFE - TOP_SAFE   # 1070px disponíveis

# ── Paleta A — Split Brutalista ───────────────────────────────────
A_PUR  = (120,  30, 210)
A_DRK  = (  6,   0,  18)
A_WHT  = (255, 255, 255)
A_BLK  = (  0,   0,   0)
A_PNK  = (236,  72, 153)
A_GRY  = (195, 175, 220)
A_ACC  = (200, 140, 255)   # lilás claro para acento

# ── Paleta B — Poster Punk ────────────────────────────────────────
B_BG   = (  6,   4,  12)
B_YEL  = (255, 205,   0)
B_AMB  = (255, 140,   0)
B_RED  = (215,  35,  55)
B_WHT  = (248, 242, 255)
B_GRY  = (130, 118, 150)
B_VLT  = (160,  55, 255)

# ── Paleta C — Editorial Claro ────────────────────────────────────
C_CLAY = (238, 228, 210)
C_INK  = ( 16,  10,  22)
C_PLUM = ( 88,  14, 128)
C_RSE  = (198,  50,  95)
C_MID  = (138, 118,  98)

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

def tw(d, t, f):  bb=d.textbbox((0,0),t,font=f); return bb[2]-bb[0]
def tb(d, t, f):  return d.textbbox((0,0),t,font=f)

def wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test=(cur+" "+w).strip()
        if tw(d,test,font)<=max_w: cur=test
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def fit_font(d, lines, style, max_h, max_w, start=160, min_sz=28):
    """Reduz até o bloco caber tanto em largura quanto em altura."""
    sz = start
    while sz >= min_sz:
        f    = F(style, sz)
        lead = int(sz * 1.08)
        total_h = lead * len(lines)
        if all(tw(d,ln,f)<=max_w for ln in lines) and total_h<=max_h:
            return sz, f, lead
        sz -= 2
    f    = F(style, min_sz)
    lead = int(min_sz * 1.08)
    return min_sz, f, lead

def load_bg(path, ctr=(0.5,0.5)):
    return ImageOps.fit(Image.open(path).convert("RGB"),(W,H),
                        Image.LANCZOS,centering=ctr)

def overlay(canvas, color, alpha):
    ov=Image.new("RGBA",canvas.size,(*color,alpha))
    base=canvas.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

def fill_rect(canvas, x, y, w, h, color, alpha=255):
    lay=Image.new("RGBA",canvas.size,(0,0,0,0))
    ImageDraw.Draw(lay).rectangle([x,y,x+w,y+h],fill=(*color,alpha))
    base=canvas.convert("RGBA"); base.alpha_composite(lay)
    return base.convert("RGB")

def hbar(d, y, h=6, c1=B_VLT, c2=A_PNK, x0=0, x1=W):
    for xi in range(x0,x1):
        d.line([(xi,y),(xi,y+h)],fill=lerp(c1,c2,(xi-x0)/max(1,x1-x0-1)))

def grad_text(canvas, d, text, font, x, y, c1, c2):
    bb=tb(d,text,font); lw_=bb[2]-bb[0]; y0=y+bb[1]; y1=y+bb[3]
    lay=Image.new("RGBA",canvas.size,(0,0,0,0))
    ImageDraw.Draw(lay).text((x,y),text,font=font,fill=(*c1,255))
    tint=Image.new("RGBA",canvas.size,(0,0,0,0)); dt=ImageDraw.Draw(tint)
    for xi in range(x,x+lw_):
        c=lerp(c1,c2,(xi-x)/max(1,lw_-1))
        dt.line([(xi,y0),(xi,y1)],fill=(*c,255))
    _,_,_,a=lay.split(); tint.putalpha(a)
    base=canvas.convert("RGBA"); base.alpha_composite(tint)
    return base.convert("RGB")

LOGO="/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
def paste_logo(canvas, x=M, y=LOGO_Y, lh=LOGO_H, pill=None):
    """pill: cor de fundo (tuple RGB) ou None"""
    if pill:
        ImageDraw.Draw(canvas).rounded_rectangle(
            [x-10,y-8,x+192,y+lh+10],radius=12,fill=(*pill,235))
    logo=Image.open(LOGO).convert("RGBA")
    lw=int(logo.width*lh/logo.height)
    logo=logo.resize((lw,lh),Image.LANCZOS)
    canvas.paste(logo,(x,y),logo)

BG  = "/home/user/WEB/carrossel-pmi"
OUT = "/home/user/WEB/carrossel-pmi/domingo_v4"
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
# CAROUSEL A — SPLIT BRUTALISTA
# ─ Esquerda: bloco de cor sólida com texto
# ─ Direita: fotografia
# ─ Grid: logo y=40 | headline y=180 | separador | sub | CTA y=1240
# ══════════════════════════════════════════════════════════════════

SPLIT = 540   # exatamente metade

def a_slide(bg_path, headline, body, sub, out, color=A_PUR,
            img_side="right", ctr=(0.5,0.5)):
    img    = load_bg(bg_path, ctr=ctr)
    canvas = img.copy()

    # bloco de cor sólida
    cx0 = 0 if img_side=="right" else SPLIT
    canvas = fill_rect(canvas, cx0, 0, SPLIT, H, color)
    d      = ImageDraw.Draw(canvas)

    # divisória preta (8px)
    d.rectangle([SPLIT-4,0,SPLIT+4,H], fill=A_BLK)

    # zona de texto dentro do bloco colorido
    txt_x = cx0 + 24           # 24px de margem interna
    txt_w = SPLIT - 48         # largura texto = SPLIT - 48

    # ── LOGO ─────────────────────────────────────────────────────
    paste_logo(canvas, x=cx0+24, pill=color)

    # ── HEADLINE: ocupa topo da zona de conteúdo (TOP_SAFE → ~55%) ─
    hl_zone_h = int(CONTENT_H * 0.55)   # 588px para headline
    sz_h, fnt_h, lead_h = fit_font(d, headline, "black",
                                    max_h=hl_zone_h, max_w=txt_w, start=148)
    hl_block_h = lead_h * len(headline)

    # centraliza o bloco de headline verticalmente na zona superior
    hl_y_start = TOP_SAFE + (hl_zone_h - hl_block_h) // 2

    ty = hl_y_start
    for ln in headline:
        d.text((txt_x, ty), ln, font=fnt_h, fill=A_WHT)
        ty += lead_h

    # ── SEPARADOR (8px, múltiplo) ─────────────────────────────────
    sep_y = TOP_SAFE + hl_zone_h + 16
    d.rectangle([txt_x, sep_y, txt_x+txt_w-8, sep_y+8], fill=A_BLK)

    # ── BODY: abaixo do separador ─────────────────────────────────
    body_zone_h = int(CONTENT_H * 0.28)   # 300px para body
    body_y_start = sep_y + 24
    sz_b, fnt_b, lead_b = fit_font(d, body, "black",
                                    max_h=body_zone_h, max_w=txt_w, start=sz_h-20)
    ty = body_y_start
    for i, ln in enumerate(body):
        if i == len(body)-1:
            canvas = grad_text(canvas,d,ln,fnt_b,txt_x,ty,A_PNK,A_ACC)
            d = ImageDraw.Draw(canvas)
        else:
            d.text((txt_x, ty), ln, font=fnt_b, fill=A_WHT)
        ty += lead_b

    # ── SUB: ancorado na base (CTA_Y) ────────────────────────────
    fnt_s = F("regular", 28)
    sub_lines = wrap(d, sub, fnt_s, txt_w)
    sub_total = int(28*1.5) * len(sub_lines)
    sub_y = CTA_Y - sub_total
    for ln in sub_lines:
        d.text((txt_x, sub_y), ln, font=fnt_s, fill=A_GRY)
        sub_y += int(28*1.5)

    canvas.save(out); print(f"✓ {os.path.basename(out)}")


def a_s01():
    a_slide(f"{BG}/bg_v2_v2_a_s01.png",
            headline=["SEU", "CONTEÚDO"],
            body=["PARECE FEITO", "POR ROBÔ."],
            sub="Porque parece mesmo. Desliza.",
            out=f"{OUT}/a_slide01.png", ctr=(0.65,0.5))

def a_s02():
    a_slide(f"{BG}/bg_v2_v2_a_s02.png",
            headline=["TODO MUNDO", "USA IA."],
            body=["TODO MUNDO", "SONA IGUAL."],
            sub="O feed virou uma fábrica sem dono.",
            out=f"{OUT}/a_slide02.png", color=(70,5,155))

def a_s03():
    a_slide(f"{BG}/bg_v2_v2_a_s03.png",
            headline=["O QUE", "DIFERENCIA"],
            body=["NÃO É A", "FERRAMENTA."],
            sub="É a VOZ. E voz não se automatiza.",
            out=f"{OUT}/a_slide03.png", color=A_DRK,
            img_side="left", ctr=(0.6,0.5))

def a_s04():
    a_slide(f"{BG}/bg_v2_v2_a_s04.png",
            headline=["É", "A VOZ."],
            body=["NUNCA FOI", "A FERRAMENTA."],
            sub="Quem usa IA sem voz própria não é insubstituível.",
            out=f"{OUT}/a_slide04.png", color=(95,0,175), ctr=(0.4,0.5))

def a_s05():
    a_slide(f"{BG}/bg_v2_v2_a_s05.png",
            headline=["VOCÊ AINDA", "SENTE SUA VOZ", "NOS POSTS?"],
            body=["RESPONDE", "NOS COMENTÁRIOS."],
            sub="Sua resposta pode mudar sua estratégia.",
            out=f"{OUT}/a_slide05.png", color=A_PUR,
            img_side="left", ctr=(0.3,0.5))


# ══════════════════════════════════════════════════════════════════
# CAROUSEL B — POSTER PUNK
# ─ Full frame: fundo escuro + imagem
# ─ Grid: faixa 8px topo | logo y=40 | headline y=180 | sep | body | CTA ancora
# ══════════════════════════════════════════════════════════════════

def b_slide(bg_path, big=None, strikethrough=False,
            headline=None, body=None, sub=None, out=None,
            ctr=(0.5,0.5), ov_alpha=155):
    img    = load_bg(bg_path, ctr=ctr)
    canvas = overlay(img, B_BG, ov_alpha)
    d      = ImageDraw.Draw(canvas)

    # faixa amarela 8px no topo
    for xi in range(W):
        d.line([(xi,0),(xi,8)],fill=lerp(B_YEL,B_AMB,xi/(W-1)))

    paste_logo(canvas, pill=B_BG)

    ty = TOP_SAFE   # conteúdo começa em y=160

    # ── BIG WORD ─────────────────────────────────────────────────
    if big:
        sz=170
        while sz>=60:
            f=F("black",sz)
            if tw(d,big,f)<=W-M*2: break
            sz-=2
        fnt_big=F("black",sz)
        lw_=tw(d,big,fnt_big); x_w=(W-lw_)//2
        d.text((x_w,ty),big,font=fnt_big,fill=B_WHT)

        if strikethrough:
            bb=tb(d,big,fnt_big); txt_h=bb[3]-bb[1]
            mid_y=ty+bb[1]+txt_h//2; lh=max(18,txt_h//6)
            d.rectangle([x_w-8,mid_y-lh//2-4,x_w+lw_+8,mid_y-lh//2+4],fill=B_YEL)
            d.rectangle([x_w-8,mid_y-lh//2,  x_w+lw_+8,mid_y+lh//2],  fill=B_RED)
            d.rectangle([x_w-8,mid_y+lh//2-4,x_w+lw_+8,mid_y+lh//2+4],fill=B_YEL)

        ty += int(sz*1.0) + 16

        # separador 8px
        for xi in range(W):
            d.line([(xi,ty),(xi,ty+8)],fill=lerp(B_YEL,B_AMB,xi/(W-1)))
        ty += 24

    # ── HEADLINE ─────────────────────────────────────────────────
    if headline:
        avail_h = (CTA_Y - 80) - ty
        sz2,fnt_hl,lead_hl = fit_font(d,headline,"black",
                                       max_h=int(avail_h*0.52),
                                       max_w=W-M*2, start=96)
        for ln in headline:
            lw_=tw(d,ln,fnt_hl); d.text(((W-lw_)//2,ty),ln,font=fnt_hl,fill=B_WHT)
            ty+=lead_hl
        ty += 24

        # separador fino
        hbar(d, ty, h=5, c1=B_VLT, c2=A_PNK)
        ty += 24

    # ── BODY ─────────────────────────────────────────────────────
    if body:
        avail_h2 = (CTA_Y - 80) - ty
        sz3,fnt_bd,lead_bd = fit_font(d,body,"black",
                                       max_h=int(avail_h2*0.85),
                                       max_w=W-M*2, start=80)
        for i,ln in enumerate(body):
            lw_=tw(d,ln,fnt_bd)
            if i==len(body)-1:
                canvas=grad_text(canvas,d,ln,fnt_bd,(W-lw_)//2,ty,B_YEL,B_AMB)
                d=ImageDraw.Draw(canvas)
            else:
                d.text(((W-lw_)//2,ty),ln,font=fnt_bd,fill=B_WHT)
            ty+=lead_bd

    # ── SUB ancorado na base ──────────────────────────────────────
    if sub:
        fnt_s=F("regular",29)
        sub_lines=wrap(d,sub,fnt_s,W-M*2)
        sub_h=int(29*1.5)*len(sub_lines)
        sy=CTA_Y-sub_h
        for ln in sub_lines:
            lw_=tw(d,ln,fnt_s); d.text(((W-lw_)//2,sy),ln,font=fnt_s,fill=B_GRY)
            sy+=int(29*1.5)

    canvas.save(out); print(f"✓ {os.path.basename(out)}")


def b_s01():
    b_slide(f"{BG}/bg_v2_v2_b_s01.png",
            big="VIRALIZAR", strikethrough=True,
            headline=["NÃO É MAIS O OBJETIVO."],
            body=["NA VERDADE,","NUNCA FOI."],
            sub="Viral é pico. Comunidade é renda.",
            out=f"{OUT}/b_slide01.png")

def b_s02():
    b_slide(f"{BG}/bg_v2_v2_b_s02.png",
            headline=["200 MIL CURTIDAS.","ZERO VENDAS."],
            body=["ISSO ACONTECE","TODO DIA."],
            sub="Alcance que não converte é vaidade. Não é negócio.",
            out=f"{OUT}/b_slide02.png", ctr=(0.5,0.3))

def b_s03():
    b_slide(f"{BG}/bg_v2_v2_b_s03.png",
            big="VIRAL", strikethrough=False,
            headline=["É EGO."],
            body=["COMUNIDADE","É NEGÓCIO."],
            sub="As marcas que mais vendem têm comunidade pequena e lista de espera.",
            out=f"{OUT}/b_slide03.png")

def b_s04():
    b_slide(f"{BG}/bg_v2_v2_b_s04.png",
            headline=["EM QUAL LADO","VOCÊ ESTÁ","APOSTANDO?"],
            body=["VIRAL","OU COMUNIDADE?"],
            sub="O que explode some. O que serve fica.",
            out=f"{OUT}/b_slide04.png", ctr=(0.5,0.4))

def b_s05():
    b_slide(f"{BG}/bg_v2_v2_b_s05.png",
            headline=["QUAL O TAMANHO","DO SEU PÚBLICO","MAIS FIEL?"],
            body=["NEM PRECISA SER GRANDE.","PRECISA SER SEU."],
            sub="Comenta aqui o número.",
            out=f"{OUT}/b_slide05.png", ctr=(0.5,0.4), ov_alpha=110)


# ══════════════════════════════════════════════════════════════════
# CAROUSEL C — EDITORIAL CLARO
# ─ Imagem topo 42% | linha PLUM | zona creme 58%
# ─ Grid: stat gigante se houver | headline | sub ancora base
# ══════════════════════════════════════════════════════════════════

C_CUT = int(H * 0.42)   # y=567 — exatamente o centro óptico

def c_slide(bg_path, stat=None, stat_lbl=None,
            headline=None, sub=None, out=None, ctr=(0.5,0.3)):
    img     = load_bg(bg_path, ctr=ctr)
    img_top = img.crop((0,0,W,C_CUT))

    canvas  = Image.new("RGB",(W,H),C_CLAY)
    canvas.paste(img_top,(0,0))
    d       = ImageDraw.Draw(canvas)

    # linha PLUM 10px
    d.rectangle([0,C_CUT,W,C_CUT+10],fill=C_PLUM)

    # logo sobre a imagem (com pílula creme)
    paste_logo(canvas, pill=C_CLAY)

    # zona de texto: C_CUT+10 a H
    zone_top = C_CUT + 10 + 32   # 32px de respiro após linha
    zone_h   = H - zone_top - 80  # 80px de margem base
    zone_w   = W - M*2

    ty = zone_top

    if stat:
        # stat gigante: ocupa até 38% da zona
        stat_max_h = int(zone_h * 0.38)
        sz=220
        while sz>=64:
            f=F("black",sz)
            bb=tb(d,stat,f)
            if tw(d,stat,f)<=zone_w and (bb[3]-bb[1])<=stat_max_h: break
            sz-=4
        fnt_stat=F("black",sz)
        lw_=tw(d,stat,fnt_stat)
        bb=tb(d,stat,fnt_stat)
        d.text(((W-lw_)//2,ty),stat,font=fnt_stat,fill=C_INK)
        ty += bb[3]-bb[1]+8

        if stat_lbl:
            fnt_lbl=F("bold",min(38,max(24,sz//6)))
            for ln in wrap(d,stat_lbl,fnt_lbl,zone_w):
                lw_=tw(d,ln,fnt_lbl)
                d.text(((W-lw_)//2,ty),ln,font=fnt_lbl,fill=C_PLUM)
                ty+=int(fnt_lbl.size*1.2)
        ty += 16
        d.rectangle([M,ty,W-M,ty+6],fill=C_PLUM)
        ty += 24

    if headline:
        avail_h = (H-80) - ty
        sz2,fnt_h,lead_h = fit_font(d,headline,"black",
                                     max_h=int(avail_h*0.72),
                                     max_w=zone_w, start=96)
        for i,ln in enumerate(headline):
            lw_=tw(d,ln,fnt_h)
            col=C_RSE if i==len(headline)-1 else C_INK
            d.text(((W-lw_)//2,ty),ln,font=fnt_h,fill=col)
            ty+=lead_h

    if sub:
        fnt_s=F("regular",30)
        sub_lines=wrap(d,sub,fnt_s,zone_w)
        sub_h=int(30*1.5)*len(sub_lines)
        sy=H-72-sub_h
        for ln in sub_lines:
            lw_=tw(d,ln,fnt_s)
            d.text(((W-lw_)//2,sy),ln,font=fnt_s,fill=C_MID)
            sy+=int(30*1.5)

    canvas.save(out); print(f"✓ {os.path.basename(out)}")


def c_s01():
    c_slide(f"{BG}/bg_domingo_dom_c_s01.png",
            stat="47M",
            stat_lbl="de empreendedores no Brasil.",
            headline=["A MAIORIA NÃO SABE","O QUE ESTÁ VENDENDO."],
            sub="Não é falta de produto. É falta de clareza.",
            out=f"{OUT}/c_slide01.png")

def c_s02():
    c_slide(f"{BG}/bg_domingo_dom_c_s02.png",
            headline=["NÃO É FALTA DE PRODUTO.","NÃO É FALTA DE CLIENTE.","É FALTA DE CLAREZA."],
            sub="Sobre o que você vende, para quem, e por que você.",
            out=f"{OUT}/c_slide02.png", ctr=(0.5,0.4))

def c_s03():
    c_slide(f"{BG}/bg_domingo_dom_c_s03.png",
            headline=["FALAR ALTO","NÃO É SER OUVIDO."],
            sub="Quem fala para todos não fala com ninguém. Clareza atrai, volume cansa.",
            out=f"{OUT}/c_slide03.png")

def c_s04():
    c_slide(f"{BG}/bg_domingo_dom_c_s04.png",
            headline=["POSICIONAMENTO CLARO","VENDE MAIS","QUE CRIATIVIDADE."],
            sub="Sempre vendeu. Só ninguém falava isso abertamente.",
            out=f"{OUT}/c_slide04.png")

def c_s05():
    c_slide(f"{BG}/bg_domingo_dom_c_s05.png",
            headline=["ESCREVE O QUE VOCÊ","VENDE EM UMA FRASE.","SEM 'SOLUÇÃO'."],
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
