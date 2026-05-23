#!/usr/bin/env python3
"""PMI — 5 modelos de layout para escolha. Mesmo conteúdo, estruturas diferentes."""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os

W, H = 1080, 1350

VIOLET = (134,   0, 255)
VLT    = (160,  60, 255)
PINK   = (236,  72, 153)
GREEN  = ( 57, 255,  20)   # neon ref
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
DARK   = (  8,   6,  14)
OFFWHT = (230, 225, 240)
GRAY   = (160, 155, 175)

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

def tw(d,t,f): bb=d.textbbox((0,0),t,font=f); return bb[2]-bb[0]
def th(d,t,f): bb=d.textbbox((0,0),t,font=f); return bb[3]-bb[1]

def wrap(d, text, font, max_w=900):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if tw(d,test,font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fit_font(d, lines, style, start=120, min_sz=44, max_w=960):
    sz = start
    while sz >= min_sz:
        f = F(style, sz)
        if all(tw(d,ln,f) <= max_w for ln in lines): return sz, f
        sz -= 4
    return min_sz, F(style, min_sz)

def grad_line(d, y, h=5, c1=VLT, c2=PINK):
    for xi in range(W):
        d.line([(xi,y),(xi,y+h)], fill=lerp(c1,c2,xi/(W-1)))

LOGO = "/home/user/WEB/carrossel-pmi/logo_pmi_transparent.png"
def paste_logo(canvas, x=52, y=None, lh=42, light=False):
    if y is None: y = H - 80
    if light:
        ImageDraw.Draw(canvas).rounded_rectangle(
            [x-10, y-8, x+190, y+lh+12], radius=10, fill=(10,6,18,210))
    logo = Image.open(LOGO).convert("RGBA")
    lw   = int(logo.width * lh / logo.height)
    logo = logo.resize((lw,lh), Image.LANCZOS)
    canvas.paste(logo, (x,y), logo)

BG1 = "/home/user/WEB/carrossel-pmi/bg2_p1_s01.png"   # dark surreal
BG2 = "/home/user/WEB/carrossel-pmi/bg2_p2_s03.png"   # dreamy pastel
OUT = "/home/user/WEB/carrossel-pmi/modelos"
os.makedirs(OUT, exist_ok=True)

HEADLINE = ["META ADS FICOU", "12% MAIS CARO."]
SUBTITLE = "E a maioria dos negócios ainda não ajustou nada."
ACCENT   = "Entenda o que mudou e como se proteger."


# ════════════════════════════════════════════════════════════════
# MODELO 1 — "Split Limpo" (inspirado na referência viral)
# Imagem limpa topo · linha de cor · fundo sólido escuro embaixo
# ════════════════════════════════════════════════════════════════
def modelo1():
    cut  = int(H * 0.52)   # onde a imagem termina
    line = 6               # espessura da linha colorida

    # imagem no topo (sem overlay)
    img    = ImageOps.fit(Image.open(BG1).convert("RGB"),(W,cut),Image.LANCZOS)
    canvas = Image.new("RGB",(W,H),DARK)
    canvas.paste(img,(0,0))

    d = ImageDraw.Draw(canvas)
    # linha gradiente violeta→rosa
    grad_line(d, cut, h=line)

    # bloco de texto no fundo sólido
    ty = cut + line + 48
    _, fnt_h = fit_font(d, HEADLINE, "black", 110)
    lead = int(fnt_h.size * 1.06)
    for i, ln in enumerate(HEADLINE):
        lw_ = tw(d, ln, fnt_h)
        x   = (W - lw_) // 2
        if i == len(HEADLINE)-1:
            # última linha: gradiente
            bb  = d.textbbox((0,0),ln,font=fnt_h)
            lay = Image.new("RGBA",canvas.size,(0,0,0,0))
            ImageDraw.Draw(lay).text((x,ty),ln,font=fnt_h,fill=(*VLT,255))
            tint = Image.new("RGBA",canvas.size,(0,0,0,0))
            dt   = ImageDraw.Draw(tint)
            lw2  = bb[2]-bb[0]
            for xi in range(x,x+lw2):
                c = lerp(VLT,PINK,(xi-x)/max(1,lw2-1))
                dt.line([(xi,ty+bb[1]),(xi,ty+bb[3])],fill=(*c,255))
            _,_,_,a = lay.split(); tint.putalpha(a)
            canvas = canvas.convert("RGBA"); canvas.alpha_composite(tint)
            canvas = canvas.convert("RGB"); d = ImageDraw.Draw(canvas)
        else:
            d.text((x,ty), ln, font=fnt_h, fill=WHITE)
        ty += lead

    ty += 16
    fnt_s = F("regular", 30)
    for ln in wrap(d, SUBTITLE, fnt_s):
        lw_ = tw(d,ln,fnt_s)
        d.text(((W-lw_)//2, ty), ln, font=fnt_s, fill=GRAY)
        ty += int(30*1.5)

    paste_logo(canvas, y=H-76)

    # label modelo
    fnt_l = F("bold",22)
    d = ImageDraw.Draw(canvas)
    d.text((W-200, H-40), "MODELO 1", font=fnt_l, fill=(*VLT,180))

    canvas.save(f"{OUT}/modelo1.png"); print("✓ modelo1 — Split Limpo")


# ════════════════════════════════════════════════════════════════
# MODELO 2 — "Faixa Neon"
# Imagem full + faixa roxa larga no centro com texto dentro
# ════════════════════════════════════════════════════════════════
def modelo2():
    img    = ImageOps.fit(Image.open(BG1).convert("RGB"),(W,H),Image.LANCZOS)
    # overlay suave para escurecer geral
    ov  = Image.new("RGBA",img.size,(0,0,0,110))
    base = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")

    # faixa sólida no centro-baixo
    faixa_h = int(H * 0.40)
    faixa_y = H - faixa_h
    faixa   = Image.new("RGBA",(W,H),(0,0,0,0))
    df      = ImageDraw.Draw(faixa)
    df.rectangle([0,faixa_y,W,H], fill=(8,6,14,240))
    faixa = faixa.filter(ImageFilter.GaussianBlur(0))
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(faixa)
    canvas = canvas.convert("RGB")
    d = ImageDraw.Draw(canvas)

    # linha neon no topo da faixa
    for xi in range(W):
        d.line([(xi,faixa_y),(xi,faixa_y+4)], fill=lerp(PINK,VLT,xi/(W-1)))

    ty = faixa_y + 36
    _, fnt_h = fit_font(d, HEADLINE, "black", 108)
    lead = int(fnt_h.size*1.06)
    for ln in HEADLINE:
        lw_ = tw(d,ln,fnt_h)
        d.text(((W-lw_)//2, ty), ln, font=fnt_h, fill=WHITE)
        ty += lead

    # acento de cor na palavra-chave
    ty += 12
    fnt_s = F("bold", 30)
    for ln in wrap(d, SUBTITLE, fnt_s):
        lw_ = tw(d,ln,fnt_s)
        d.text(((W-lw_)//2, ty), ln, font=fnt_s, fill=PINK)
        ty += int(30*1.5)

    paste_logo(canvas, y=H-72)
    d = ImageDraw.Draw(canvas)
    d.text((W-200,H-40),"MODELO 2",font=F("bold",22),fill=(*VLT,180))
    canvas.save(f"{OUT}/modelo2.png"); print("✓ modelo2 — Faixa Neon")


# ════════════════════════════════════════════════════════════════
# MODELO 3 — "Invertido" (texto sólido topo · imagem embaixo)
# ════════════════════════════════════════════════════════════════
def modelo3():
    cut = int(H * 0.48)

    canvas = Image.new("RGB",(W,H),DARK)
    d = ImageDraw.Draw(canvas)

    # bloco de texto no topo
    _, fnt_h = fit_font(d, HEADLINE, "black", 108)
    lead = int(fnt_h.size * 1.06)
    block_h = lead * len(HEADLINE)
    ty = (cut - block_h) // 2 - 20

    # glow roxo sutil no topo
    glow = Image.new("RGBA",(W,H),(0,0,0,0))
    dg   = ImageDraw.Draw(glow)
    for r in range(300,0,-4):
        a = int(40*(1-r/300)**2)
        dg.ellipse([W//2-r,0,W//2+r,r*2],fill=(*VLT,a))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(glow)
    canvas = canvas.convert("RGB"); d = ImageDraw.Draw(canvas)

    for ln in HEADLINE:
        lw_=tw(d,ln,fnt_h); d.text(((W-lw_)//2,ty),ln,font=fnt_h,fill=WHITE); ty+=lead
    ty += 14
    grad_line(d, ty, h=4)
    ty += 20
    fnt_s = F("regular",30)
    for ln in wrap(d,SUBTITLE,fnt_s):
        lw_=tw(d,ln,fnt_s); d.text(((W-lw_)//2,ty),ln,font=fnt_s,fill=GRAY); ty+=int(30*1.5)

    # imagem embaixo
    img = ImageOps.fit(Image.open(BG1).convert("RGB"),(W,H-cut),Image.LANCZOS,centering=(0.5,0.3))
    # linha separadora
    grad_line(d, cut-4, h=5)
    canvas.paste(img,(0,cut))

    paste_logo(canvas, y=H-76)
    d = ImageDraw.Draw(canvas)
    d.text((W-200,H-40),"MODELO 3",font=F("bold",22),fill=(*VLT,180))
    canvas.save(f"{OUT}/modelo3.png"); print("✓ modelo3 — Invertido")


# ════════════════════════════════════════════════════════════════
# MODELO 4 — "Card Glassmorphism"
# Imagem full + card central semi-transparente com texto
# ════════════════════════════════════════════════════════════════
def modelo4():
    img    = ImageOps.fit(Image.open(BG2).convert("RGB"),(W,H),Image.LANCZOS)
    # overlay mais forte para não competir com card
    ov  = Image.new("RGBA",img.size,(0,0,0,80))
    base = img.convert("RGBA"); base.alpha_composite(ov)
    canvas = base.convert("RGB")

    # card glass
    card_x, card_w = 52, W-104
    card_y, card_h = int(H*0.50), int(H*0.42)
    card = Image.new("RGBA",(W,H),(0,0,0,0))
    dc   = ImageDraw.Draw(card)
    dc.rounded_rectangle([card_x,card_y,card_x+card_w,card_y+card_h],
                         radius=24, fill=(8,6,14,215))
    # borda gradiente
    for xi in range(card_x, card_x+card_w):
        t = (xi-card_x)/(card_w-1)
        c = lerp(VLT,PINK,t)
        dc.line([(xi,card_y),(xi,card_y+4)],fill=(*c,255))
        dc.line([(xi,card_y+card_h-4),(xi,card_y+card_h)],fill=(*c,120))

    card = card.filter(ImageFilter.GaussianBlur(0))
    canvas = canvas.convert("RGBA"); canvas.alpha_composite(card)
    canvas = canvas.convert("RGB"); d = ImageDraw.Draw(canvas)

    ty = card_y + 44
    _, fnt_h = fit_font(d,HEADLINE,"black",96,max_w=card_w-60)
    lead = int(fnt_h.size*1.06)
    for i,ln in enumerate(HEADLINE):
        lw_=tw(d,ln,fnt_h); x=card_x+30+(card_w-60-lw_)//2
        if i==len(HEADLINE)-1:
            # gradiente última linha
            bb=d.textbbox((0,0),ln,font=fnt_h); lw2=bb[2]-bb[0]
            lay=Image.new("RGBA",canvas.size,(0,0,0,0))
            ImageDraw.Draw(lay).text((x,ty),ln,font=fnt_h,fill=(*VLT,255))
            tint=Image.new("RGBA",canvas.size,(0,0,0,0)); dt=ImageDraw.Draw(tint)
            for xi in range(x,x+lw2):
                c=lerp(VLT,PINK,(xi-x)/max(1,lw2-1))
                dt.line([(xi,ty+bb[1]),(xi,ty+bb[3])],fill=(*c,255))
            _,_,_,a=lay.split(); tint.putalpha(a)
            canvas=canvas.convert("RGBA"); canvas.alpha_composite(tint)
            canvas=canvas.convert("RGB"); d=ImageDraw.Draw(canvas)
        else:
            d.text((x,ty),ln,font=fnt_h,fill=WHITE)
        ty+=lead

    ty+=14
    fnt_s=F("regular",27)
    for ln in wrap(d,SUBTITLE,fnt_s,max_w=card_w-60):
        lw_=tw(d,ln,fnt_s); d.text((card_x+30+(card_w-60-lw_)//2,ty),ln,font=fnt_s,fill=GRAY)
        ty+=int(27*1.5)

    paste_logo(canvas, y=H-76)
    d=ImageDraw.Draw(canvas)
    d.text((W-200,H-40),"MODELO 4",font=F("bold",22),fill=(*VLT,180))
    canvas.save(f"{OUT}/modelo4.png"); print("✓ modelo4 — Card Glass")


# ════════════════════════════════════════════════════════════════
# MODELO 5 — "Stat + Imagem" (número hero no topo, imagem embaixo)
# ════════════════════════════════════════════════════════════════
def modelo5():
    cut = int(H * 0.46)

    canvas = Image.new("RGB",(W,H),DARK)
    d = ImageDraw.Draw(canvas)

    # glow roxo
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); dg=ImageDraw.Draw(glow)
    for r in range(350,0,-5):
        a=int(35*(1-r/350)**2.2)
        dg.ellipse([W//2-r,50,W//2+r,50+r*2],fill=(*VIOLET,a))
    glow=glow.filter(ImageFilter.GaussianBlur(70))
    canvas=canvas.convert("RGBA"); canvas.alpha_composite(glow)
    canvas=canvas.convert("RGB"); d=ImageDraw.Draw(canvas)

    # stat grande
    fnt_num = F("black",180)
    num     = "12%"
    nw = tw(d,num,fnt_num)
    ny = 80
    # gradiente no número
    bb=d.textbbox((0,0),num,font=fnt_num); lw2=bb[2]-bb[0]
    lay=Image.new("RGBA",canvas.size,(0,0,0,0))
    ImageDraw.Draw(lay).text(((W-nw)//2,ny),num,font=fnt_num,fill=(*VLT,255))
    tint=Image.new("RGBA",canvas.size,(0,0,0,0)); dt=ImageDraw.Draw(tint)
    x0=(W-nw)//2
    for xi in range(x0,x0+lw2):
        c=lerp(VLT,PINK,(xi-x0)/max(1,lw2-1))
        dt.line([(xi,ny+bb[1]),(xi,ny+bb[3])],fill=(*c,255))
    _,_,_,a=lay.split(); tint.putalpha(a)
    canvas=canvas.convert("RGBA"); canvas.alpha_composite(tint)
    canvas=canvas.convert("RGB"); d=ImageDraw.Draw(canvas)

    ty = ny + bb[3] + 8
    grad_line(d, ty, h=4)
    ty += 20

    _, fnt_h = fit_font(d,HEADLINE,"black",72)
    lead = int(fnt_h.size*1.06)
    for ln in HEADLINE:
        lw_=tw(d,ln,fnt_h); d.text(((W-lw_)//2,ty),ln,font=fnt_h,fill=WHITE); ty+=lead

    ty+=10
    fnt_s=F("regular",26)
    for ln in wrap(d,SUBTITLE,fnt_s):
        lw_=tw(d,ln,fnt_s); d.text(((W-lw_)//2,ty),ln,font=fnt_s,fill=GRAY); ty+=int(26*1.5)

    # linha separadora antes da imagem
    grad_line(d, cut-5, h=5)

    # imagem no terço inferior
    img=ImageOps.fit(Image.open(BG1).convert("RGB"),(W,H-cut),Image.LANCZOS,centering=(0.5,0.4))
    canvas.paste(img,(0,cut))

    paste_logo(canvas, y=H-72)
    d=ImageDraw.Draw(canvas)
    d.text((W-200,H-40),"MODELO 5",font=F("bold",22),fill=(*VLT,180))
    canvas.save(f"{OUT}/modelo5.png"); print("✓ modelo5 — Stat + Imagem")


if __name__ == "__main__":
    modelo1(); modelo2(); modelo3(); modelo4(); modelo5()
    print(f"\n5 modelos → {OUT}")
