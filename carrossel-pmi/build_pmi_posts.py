#!/usr/bin/env python3
"""PMI — Posts sábado. Surreal + mixed light/dark layouts."""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os, statistics

W, H   = 1080, 1350
MARGIN = 64
MAX_W  = W - MARGIN * 2

VIOLET  = (134,   0, 255)
VLT     = (160,  60, 255)
PINK    = (236,  72, 153)
WHITE   = (255, 255, 255)
OFFWHT  = (235, 228, 245)
INK     = ( 10,   6,  18)   # texto escuro em fundos claros
INK2    = ( 55,  30,  90)   # subtítulo escuro
DARK    = (  8,   6,  14)
GRAY    = (160, 155, 175)
LGRAY   = (100,  80, 130)   # cinza sobre fundo claro

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

def tw(d,t,f): bb=d.textbbox((0,0),t,font=f); return bb[2]-bb[0]
def th(d,t,f): bb=d.textbbox((0,0),t,font=f); return bb[3]-bb[1]

def wrap(d, text, font, max_w=MAX_W):
    if not text: return []
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if tw(d,test,font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fit_font(d, lines, style, start=100, min_sz=44):
    sz = start
    while sz >= min_sz:
        f = F(style, sz)
        if all(tw(d,ln,f) <= MAX_W for ln in lines): return sz, f
        sz -= 4
    return min_sz, F(style, min_sz)

# ── Detecta se imagem é clara (True) ou escura ────────────────────
def is_light_bg(path, threshold=140):
    img  = Image.open(path).convert("L").resize((40,50))
    vals = list(img.getdata())
    return statistics.mean(vals) > threshold

# ── Gradiente VLT→PINK (escuro) ou VIOLET→PINK (claro) ───────────
def grad_text(canvas, d, text, font, x, y, light=False):
    c1 = VIOLET if light else VLT
    c2 = PINK
    bb  = d.textbbox((0,0), text, font=font)
    lw  = bb[2]-bb[0]; y0 = y+bb[1]; y1 = y+bb[3]
    lay = Image.new("RGBA", canvas.size, (0,0,0,0))
    ImageDraw.Draw(lay).text((x,y), text, font=font, fill=(*c1,255))
    tint = Image.new("RGBA", canvas.size, (0,0,0,0))
    dt   = ImageDraw.Draw(tint)
    for xi in range(x, x+lw):
        c = lerp(c1, c2, (xi-x)/max(1,lw-1))
        dt.line([(xi,y0),(xi,y1)], fill=(*c,255))
    _,_,_,a = lay.split(); tint.putalpha(a)
    base = canvas.convert("RGBA"); base.alpha_composite(tint)
    return base.convert("RGB")

# ── Overlay escuro esfumaçado ─────────────────────────────────────
def dark_overlay(img, strength=0.72):
    ov  = Image.new("RGBA", img.size, (0,0,0,0))
    dv  = ImageDraw.Draw(ov)
    IW, IH = img.size
    top_r, bot_r = 280, 900
    for y in range(top_r):
        a = int(150*(1-y/top_r)**2.0)
        dv.line([(0,y),(IW,y)], fill=(0,0,0,a))
    for y in range(IH-1, IH-bot_r-1, -1):
        a = int(int(255*strength)*(1-(IH-1-y)/bot_r)**0.5)
        dv.line([(0,y),(IW,y)], fill=(0,0,0,a))
    ov  = ov.filter(ImageFilter.GaussianBlur(55))
    base = img.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

# ── Overlay claro suave (para preservar cores do bg) ─────────────
def light_overlay(img, alpha=40):
    ov   = Image.new("RGBA", img.size, (255,255,255,alpha))
    base = img.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

def load_bg(path, centering=(0.5,0.5)):
    return ImageOps.fit(Image.open(path).convert("RGB"),
                        (W,H), Image.LANCZOS, centering=centering)

# ── Logo PMI ──────────────────────────────────────────────────────
LOGO = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
def paste_logo(canvas, light=False, lh=46, x=52, y=44):
    if light:
        # pílula escura atrás da logo em fundos claros
        d = ImageDraw.Draw(canvas)
        d.rounded_rectangle([x-10, y-8, x+180, y+lh+14], radius=12,
                             fill=(10,6,18,220))
    logo = Image.open(LOGO).convert("RGBA")
    lw   = int(logo.width * lh / logo.height)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    canvas.paste(logo, (x, y), logo)
    d = ImageDraw.Draw(canvas)
    d.rectangle([x, y+lh+7, x+lw, y+lh+11], fill=VIOLET)

# ── Tag de horário ────────────────────────────────────────────────
def paste_time(canvas, tag, light=False):
    d    = ImageDraw.Draw(canvas)
    fnt  = F("medium", 17)
    lw_  = tw(d, tag, fnt)
    bg   = (10,6,18,210) if light else (*VIOLET,180)
    d.rounded_rectangle([W-60-lw_, 38, W-44, 70], radius=8, fill=bg)
    d.text((W-52-lw_, 46), tag, font=fnt, fill=WHITE)

# ── Separador ─────────────────────────────────────────────────────
def sep(d, y, x=None, w=56):
    sx = (W-w)//2 if x is None else x
    for xi in range(w):
        c = lerp(VLT, PINK, xi/max(1,w-1))
        d.line([(sx+xi,y),(sx+xi,y+4)], fill=c)
    return y+4


BG  = "/home/user/WEB/carrossel-pmi"
OUT = "/home/user/WEB/carrossel-pmi/posts"
os.makedirs(OUT, exist_ok=True)


# ════════════════════════════════════════════════════════════════
# POST 1 — 10h30 — "Meta Ads ficou 12% mais caro"
# ════════════════════════════════════════════════════════════════

def p1_s01():
    """DARK SURREAL — homem de terno feito de notas. Hero '12%' gigante."""
    bg     = load_bg(f"{BG}/bg2_p1_s01.png")
    canvas = dark_overlay(bg, strength=0.68)
    paste_logo(canvas); paste_time(canvas, "10:30 • PMI")
    d = ImageDraw.Draw(canvas)

    fnt_num = F("black", 240)
    nw = tw(d,"12%",fnt_num)
    canvas = grad_text(canvas, d, "12%", fnt_num, (W-nw)//2, int(H*0.22))
    d = ImageDraw.Draw(canvas)

    bb     = d.textbbox((0,0),"12%",fnt_num)
    line_y = int(H*0.22) + bb[3] + 6
    for xi in range(W):
        d.line([(xi,line_y),(xi,line_y+3)], fill=lerp(VLT,PINK,xi/(W-1)))

    fnt_h = F("black", 64)
    lines = ["DO SEU INVESTIMENTO", "SUMIU SEM VOCÊ SABER."]
    y = line_y + 22
    for i,ln in enumerate(lines):
        _, fh = fit_font(d,[ln],"black",64)
        lw_ = tw(d,ln,fh); x=(W-lw_)//2
        if i==len(lines)-1:
            canvas = grad_text(canvas,d,ln,fh,x,y); d=ImageDraw.Draw(canvas)
        else:
            d.text((x,y),ln,font=fh,fill=WHITE)
        y += int(fh.size*1.1)

    fnt_s = F("light",27)
    sub   = "A Meta repassou PIS + COFINS + ISS direto pra você. Sem aviso. Arrasta."
    y += 14
    for ln in wrap(d,sub,fnt_s):
        lw_=tw(d,ln,fnt_s); d.text(((W-lw_)//2,y),ln,font=fnt_s,fill=OFFWHT); y+=int(27*1.5)

    canvas.save(f"{OUT}/p1_slide01.png"); print("✓ p1_01")


def p1_s02():
    """VIVID SPLIT — escritório normal vs em chamas. Contraste extremo."""
    bg     = load_bg(f"{BG}/bg2_p1_s02.png")
    canvas = light_overlay(bg, alpha=20)   # preserva as cores vivas
    paste_logo(canvas, light=True)
    d = ImageDraw.Draw(canvas)

    # Barra roxa topo
    for xi in range(W):
        d.line([(xi,0),(xi,5)], fill=lerp(VLT,PINK,xi/(W-1)))

    fnt_h = F("black", 72)
    lines = ["ANTES:", "RESULTADO IGUAL."]
    y = int(H*0.62)
    for i,ln in enumerate(lines):
        _, fh = fit_font(d,[ln],"black",72)
        lw_=tw(d,ln,fh); x=(W-lw_)//2
        if i==len(lines)-1:
            canvas = grad_text(canvas,d,ln,fh,x,y,light=True); d=ImageDraw.Draw(canvas)
        else:
            d.text((x,y),ln,font=fh,fill=INK)
        y += int(fh.size*1.1)

    y += 16; sep(d, y); y += 20
    fnt_s = F("bold",30)
    sub   = "DEPOIS: 12,15% a mais. Mesmo entrega."
    lw_=tw(d,sub,fnt_s); d.text(((W-lw_)//2,y),sub,font=fnt_s,fill=INK2)

    canvas.save(f"{OUT}/p1_slide02.png"); print("✓ p1_02")


def p1_s03():
    """BRIGHT EDITORIAL — Meta espremida. Texto escuro sobre fundo claro."""
    bg     = load_bg(f"{BG}/bg2_p1_s03.png", centering=(0.5,0.35))
    canvas = light_overlay(bg, alpha=15)
    paste_logo(canvas, light=True)
    d = ImageDraw.Draw(canvas)

    for xi in range(W):
        d.line([(xi,0),(xi,5)], fill=lerp(VLT,PINK,xi/(W-1)))

    fnt_h = F("black", 80)
    lines = ["A META", "REPASSOU", "OS IMPOSTOS."]
    _, fnt_h = fit_font(d, lines, "black", 80)
    y = int(H*0.60)
    for i,ln in enumerate(lines):
        lw_=tw(d,ln,fnt_h); x=(W-lw_)//2
        if i==len(lines)-1:
            canvas = grad_text(canvas,d,ln,fnt_h,x,y,light=True); d=ImageDraw.Draw(canvas)
        else:
            d.text((x,y),ln,font=fnt_h,fill=INK)
        y += int(fnt_h.size*1.08)

    y += 18; sep(d,y); y += 22
    fnt_s = F("regular",29)
    sub   = "Você pagou a conta. Sem aviso. Sem explicação."
    for ln in wrap(d,sub,fnt_s):
        lw_=tw(d,ln,fnt_s); d.text(((W-lw_)//2,y),ln,font=fnt_s,fill=INK2); y+=int(29*1.5)

    canvas.save(f"{OUT}/p1_slide03.png"); print("✓ p1_03")


def p1_s04():
    """BRIGHT EDITORIAL — pessoa minúscula com lupa. Lista 3 ações, texto escuro."""
    bg     = load_bg(f"{BG}/bg2_p1_s04.png", centering=(0.5,0.25))
    canvas = light_overlay(bg, alpha=30)
    paste_logo(canvas, light=True)
    d = ImageDraw.Draw(canvas)

    for xi in range(W):
        d.line([(xi,0),(xi,5)], fill=lerp(VLT,PINK,xi/(W-1)))

    fnt_t = F("black", 40)
    title = "COMO SE PROTEGER AGORA:"
    canvas = grad_text(canvas,d,title,fnt_t,(W-tw(d,title,fnt_t))//2,int(H*0.56),light=True)
    d = ImageDraw.Draw(canvas)
    sep(d, int(H*0.56)+52)

    items = [
        ("01","REAJUSTE O ORÇAMENTO","Some 12,15% ao valor atual."),
        ("02","PRIORIZE CONVERSÃO",  "Otimize para quem compra, não para quem vê."),
        ("03","REVISE O CRIATIVO",   "Criativo fraco com custo maior = prejuízo duplo."),
    ]
    fnt_n=F("black",46); fnt_hl=F("bold",28); fnt_ds=F("regular",22)
    y = int(H*0.56)+66
    for num,hl,ds in items:
        canvas = grad_text(canvas,d,num,fnt_n,64,y,light=True); d=ImageDraw.Draw(canvas)
        d.text((150,y+6),hl,font=fnt_hl,fill=INK)
        d.text((150,y+46),ds,font=fnt_ds,fill=LGRAY)
        line_y = y+80
        d.line([(64,line_y),(W-64,line_y)],fill=(*LGRAY,80))
        y = line_y+22

    canvas.save(f"{OUT}/p1_slide04.png"); print("✓ p1_04")


def p1_s05():
    """DARK NEON — mão atravessando tela. CTA final."""
    bg     = load_bg(f"{BG}/bg2_p1_s05.png")
    canvas = dark_overlay(bg, strength=0.65)
    paste_logo(canvas)
    d = ImageDraw.Draw(canvas)

    fnt_h = F("black", 86)
    lines = ["JÁ AJUSTOU SEU", "ORÇAMENTO?"]
    _, fnt_h = fit_font(d,lines,"black",86)
    block_h = int(fnt_h.size*1.08)*len(lines)
    y = (H-block_h)//2 - 50
    for i,ln in enumerate(lines):
        lw_=tw(d,ln,fnt_h); x=(W-lw_)//2
        if i==len(lines)-1:
            canvas=grad_text(canvas,d,ln,fnt_h,x,y); d=ImageDraw.Draw(canvas)
        else:
            d.text((x,y),ln,font=fnt_h,fill=WHITE)
        y += int(fnt_h.size*1.08)

    y+=24; sep(d,y); y+=22
    fnt_s=F("regular",29)
    for ln in wrap(d,"Comenta aqui. A gente calcula o impacto no seu investimento.",fnt_s):
        lw_=tw(d,ln,fnt_s); d.text(((W-lw_)//2,y),ln,font=fnt_s,fill=OFFWHT); y+=int(29*1.5)

    canvas.save(f"{OUT}/p1_slide05.png"); print("✓ p1_05")


# ════════════════════════════════════════════════════════════════
# POST 2 — 16h — "82% usam IA. Quase nenhum tem estratégia."
# ════════════════════════════════════════════════════════════════

def p2_s01():
    """DARK NEON — robô de puzzle. Hero '82%' gigante."""
    bg     = load_bg(f"{BG}/bg2_p2_s01.png")
    canvas = dark_overlay(bg, strength=0.65)
    paste_logo(canvas); paste_time(canvas,"16:00 • PMI")
    d = ImageDraw.Draw(canvas)

    fnt_num = F("black", 250)
    nw = tw(d,"82%",fnt_num)
    canvas = grad_text(canvas,d,"82%",fnt_num,(W-nw)//2,int(H*0.20))
    d = ImageDraw.Draw(canvas)

    bb     = d.textbbox((0,0),"82%",fnt_num)
    line_y = int(H*0.20)+bb[3]+6
    for xi in range(W):
        d.line([(xi,line_y),(xi,line_y+3)],fill=lerp(PINK,VLT,xi/(W-1)))

    fnt_h=F("black",56); y=line_y+24
    lines=["DOS NEGÓCIOS USAM IA.","QUASE NENHUM TEM ESTRATÉGIA."]
    for i,ln in enumerate(lines):
        _,fh=fit_font(d,[ln],"black",56); lw_=tw(d,ln,fh); x=(W-lw_)//2
        if i==len(lines)-1:
            canvas=grad_text(canvas,d,ln,fh,x,y); d=ImageDraw.Draw(canvas)
        else:
            d.text((x,y),ln,font=fh,fill=WHITE)
        y+=int(fh.size*1.1)

    fnt_s=F("light",27); y+=14
    for ln in wrap(d,"Isso separa quem escala de quem só produz ruído. Arrasta.",fnt_s):
        lw_=tw(d,ln,fnt_s); d.text(((W-lw_)//2,y),ln,font=fnt_s,fill=OFFWHT); y+=int(27*1.5)

    canvas.save(f"{OUT}/p2_slide01.png"); print("✓ p2_01")


def p2_s02():
    """VIVID MAGENTA/BLUE — robô eficiente vs explosão. Split extremo."""
    bg     = load_bg(f"{BG}/bg2_p2_s02.png")
    canvas = light_overlay(bg, alpha=15)
    paste_logo(canvas, light=True)
    d = ImageDraw.Draw(canvas)

    for xi in range(W):
        d.line([(xi,0),(xi,5)],fill=lerp(PINK,VLT,xi/(W-1)))

    fnt_h=F("black",70)
    lines=["IA AUTOMATIZA.","ESTRATÉGIA","DEFINE O QUE."]
    _,fnt_h=fit_font(d,lines,"black",70)
    y=int(H*0.60)
    for i,ln in enumerate(lines):
        lw_=tw(d,ln,fnt_h); x=(W-lw_)//2
        if i==len(lines)-1:
            canvas=grad_text(canvas,d,ln,fnt_h,x,y,light=True); d=ImageDraw.Draw(canvas)
        else:
            d.text((x,y),ln,font=fnt_h,fill=WHITE)
        y+=int(fnt_h.size*1.08)

    y+=16; sep(d,y); y+=20
    fnt_s=F("bold",28)
    sub="Sem estratégia você só automatiza o desperdício."
    lw_=tw(d,sub,fnt_s); d.text(((W-lw_)//2,y),sub,font=fnt_s,fill=WHITE)

    canvas.save(f"{OUT}/p2_slide02.png"); print("✓ p2_02")


def p2_s03():
    """DREAMY PASTEL — xadrez em nuvens. Texto escuro, left-aligned."""
    bg     = load_bg(f"{BG}/bg2_p2_s03.png", centering=(0.5,0.3))
    canvas = light_overlay(bg, alpha=35)
    paste_logo(canvas, light=True)
    d = ImageDraw.Draw(canvas)

    for xi in range(W):
        d.line([(xi,0),(xi,5)],fill=lerp(VLT,PINK,xi/(W-1)))

    lx=64; y=int(H*0.55)
    fnt_h=F("black",84)
    lines=["FERRAMENTA","NAS MÃOS","ERRADAS É","DESPERDÍCIO."]
    _,fnt_h=fit_font(d,lines,"black",84)
    for i,ln in enumerate(lines):
        if i==len(lines)-1:
            canvas=grad_text(canvas,d,ln,fnt_h,lx,y,light=True); d=ImageDraw.Draw(canvas)
        else:
            d.text((lx,y),ln,font=fnt_h,fill=INK)
        y+=int(fnt_h.size*1.06)

    y+=20; sep(d,y,x=lx,w=50); y+=22
    fnt_s=F("regular",27)
    for ln in wrap(d,"IA na mão certa escala. Na errada, só escala o custo.",fnt_s,max_w=520):
        d.text((lx,y),ln,font=fnt_s,fill=INK2); y+=int(27*1.55)

    canvas.save(f"{OUT}/p2_slide03.png"); print("✓ p2_03")


def p2_s04():
    """BRIGHT EDITORIAL — cérebro vs circuito. Lista '3 coisas que IA não faz'."""
    bg     = load_bg(f"{BG}/bg2_p2_s04.png", centering=(0.5,0.25))
    canvas = light_overlay(bg, alpha=25)
    paste_logo(canvas, light=True)
    d = ImageDraw.Draw(canvas)

    for xi in range(W):
        d.line([(xi,0),(xi,5)],fill=lerp(VLT,PINK,xi/(W-1)))

    fnt_t=F("black",38)
    title="O QUE IA NÃO FAZ POR VOCÊ:"
    canvas=grad_text(canvas,d,title,fnt_t,(W-tw(d,title,fnt_t))//2,int(H*0.54),light=True)
    d=ImageDraw.Draw(canvas); sep(d,int(H*0.54)+50)

    items=[
        ("01","POSICIONAR SUA MARCA","Quem você é e pra quem fala — isso é seu."),
        ("02","ENTENDER SEU CLIENTE","IA processa dados. Você lê comportamento real."),
        ("03","DEFINIR ONDE CRESCER","A escolha de canal e estratégia ainda é humana."),
    ]
    fnt_n=F("black",44); fnt_hl=F("bold",26); fnt_ds=F("regular",21)
    y=int(H*0.54)+64
    for num,hl,ds in items:
        canvas=grad_text(canvas,d,num,fnt_n,64,y,light=True); d=ImageDraw.Draw(canvas)
        d.text((148,y+6),hl,font=fnt_hl,fill=INK)
        d.text((148,y+44),ds,font=fnt_ds,fill=LGRAY)
        line_y=y+76; d.line([(64,line_y),(W-64,line_y)],fill=(*LGRAY,70)); y=line_y+24

    canvas.save(f"{OUT}/p2_slide04.png"); print("✓ p2_04")


def p2_s05():
    """BRIGHT WARM — cabeça de lâmpada. CTA salva esse post."""
    bg     = load_bg(f"{BG}/bg2_p2_s05.png", centering=(0.5,0.3))
    canvas = light_overlay(bg, alpha=20)
    paste_logo(canvas, light=True)
    d = ImageDraw.Draw(canvas)

    for xi in range(W):
        d.line([(xi,0),(xi,5)],fill=lerp(VLT,PINK,xi/(W-1)))

    fnt_h=F("black",78)
    lines=["SALVA ESSE POST.","SEGUNDA A","CONVERSA MUDA."]
    _,fnt_h=fit_font(d,lines,"black",78)
    block_h=int(fnt_h.size*1.08)*len(lines)
    y=int(H*0.57)
    for i,ln in enumerate(lines):
        lw_=tw(d,ln,fnt_h); x=(W-lw_)//2
        if i==len(lines)-1:
            canvas=grad_text(canvas,d,ln,fnt_h,x,y,light=True); d=ImageDraw.Draw(canvas)
        else:
            d.text((x,y),ln,font=fnt_h,fill=INK)
        y+=int(fnt_h.size*1.08)

    y+=24; sep(d,y); y+=22
    fnt_s=F("regular",28)
    sub="Você usa IA com estratégia ou no piloto automático?"
    for ln in wrap(d,sub,fnt_s):
        lw_=tw(d,ln,fnt_s); d.text(((W-lw_)//2,y),ln,font=fnt_s,fill=INK2); y+=int(28*1.55)

    canvas.save(f"{OUT}/p2_slide05.png"); print("✓ p2_05")


if __name__ == "__main__":
    print("=== POST 1 — 10h30 ===")
    p1_s01(); p1_s02(); p1_s03(); p1_s04(); p1_s05()
    print("\n=== POST 2 — 16h ===")
    p2_s01(); p2_s02(); p2_s03(); p2_s04(); p2_s05()
    print(f"\nDone → {OUT}")
