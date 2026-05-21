#!/usr/bin/env python3
"""PMI Social Manager — 5 Ad Pieces. Versão corporativa com fotos AI e texto correto."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import math, os

OUT = "/home/user/WEB/pmi-social-ads/out"
BG  = "/home/user/WEB/pmi-social-ads/backgrounds"
os.makedirs(OUT, exist_ok=True)

# ── Brand Colors ──────────────────────────────────────────────────────────────
PURPLE    = (123, 47, 255)
PINK      = (236, 72, 153)
PURPLE_LT = (139, 92, 246)
BLACK     = (10, 10, 10)
WHITE     = (255, 255, 255)
GRAY_BG   = (248, 248, 248)
GRAY_TEXT = (80, 78, 90)
GRAY_BODY = (185, 180, 200)
TEXT_DARK = (17, 17, 17)
DARK_CARD = (20, 10, 42)
MID_DARK  = (28, 12, 58)

# ── Fonts ─────────────────────────────────────────────────────────────────────
R = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"
def F(style, size):
    return ImageFont.truetype({
        "black":   f"{R}/Roboto-Black.ttf",
        "bold":    f"{R}/Roboto-Bold.ttf",
        "medium":  f"{R}/Roboto-Medium.ttf",
        "regular": f"{R}/Roboto-Regular.ttf",
        "light":   f"{R}/Roboto-Light.ttf",
    }[style], size)

# ── Colour helpers ────────────────────────────────────────────────────────────
def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def grad_h(d, x1, y1, x2, y2, c1, c2):
    n = x2-x1
    for i in range(n):
        d.line([(x1+i,y1),(x1+i,y2)], fill=lerp(c1,c2,i/max(1,n-1)))

def grad_v(d, x1, y1, x2, y2, c1, c2):
    n = y2-y1
    for i in range(n):
        d.line([(x1,y1+i),(x2,y1+i)], fill=lerp(c1,c2,i/max(1,n-1)))

def grad_diag(W, H, c1, c2):
    img = Image.new("RGB",(W,H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        for x in range(0,W,3):
            d.line([(x,y),(min(x+3,W),y)], fill=lerp(c1,c2,x/W*0.35+y/H*0.65))
    return img

# ── Effects ───────────────────────────────────────────────────────────────────
def glow(img, cx, cy, radius, color, opacity=0.14):
    lay = Image.new("RGBA",img.size,(0,0,0,0))
    d = ImageDraw.Draw(lay)
    for i in range(28,0,-1):
        r = int(radius*i/28)
        a = int(opacity*255*(1-i/28)**0.5)
        d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(*color,a))
    lay = lay.filter(ImageFilter.GaussianBlur(radius//5))
    base = img.convert("RGBA"); base.alpha_composite(lay)
    return base.convert("RGB")

def dark_overlay(img, alpha=160):
    ov = Image.new("RGBA",img.size,(0,0,0,alpha))
    base = img.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

def grad_overlay_v(img, c1_alpha=0, c2_alpha=220):
    W,H = img.size
    lay = Image.new("RGBA",(W,H),(0,0,0,0))
    d = ImageDraw.Draw(lay)
    for y in range(H):
        a = int(c1_alpha + (c2_alpha-c1_alpha)*(y/H)**1.3)
        d.line([(0,y),(W,y)], fill=(0,0,0,a))
    base = img.convert("RGBA"); base.alpha_composite(lay)
    return base.convert("RGB")

def grid_lines(img, color=PURPLE, opacity=0.04, spacing=80):
    W,H = img.size
    lay = Image.new("RGBA",(W,H),(0,0,0,0))
    d = ImageDraw.Draw(lay)
    a = int(opacity*255)
    for x in range(0,W,spacing): d.line([(x,0),(x,H)], fill=(*color,a), width=1)
    for y in range(0,H,spacing): d.line([(0,y),(W,y)], fill=(*color,a), width=1)
    base = img.convert("RGBA"); base.alpha_composite(lay)
    return base.convert("RGB")

def fit_photo(path, W, H, centering=(0.5,0.4)):
    img = Image.open(path).convert("RGB")
    return ImageOps.fit(img,(W,H),Image.LANCZOS,centering=centering)

# ── Typography ────────────────────────────────────────────────────────────────
def tw(d,text,font):
    bb=d.textbbox((0,0),text,font=font); return bb[2]-bb[0]
def th(d,text,font):
    bb=d.textbbox((0,0),text,font=font); return bb[3]-bb[1]

def wrap_lines(d,text,font,max_w):
    words,lines,cur = text.split(),[],""
    for w in words:
        test=(cur+" "+w).strip()
        if tw(d,test,font)<=max_w: cur=test
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def block(d,text,font,x,y,max_w,color,leading=1.5,align="left",W_c=0):
    lines = wrap_lines(d,text,font,max_w)
    lh = int(font.size*leading)
    for line in lines:
        lw = tw(d,line,font)
        xp = ((W_c-lw)//2 if align=="center" else x)
        d.text((xp,y), line, font=font, fill=color)
        y += lh
    return y

# ── Logo ──────────────────────────────────────────────────────────────────────
def logo_tl(d,x,y,size=40,on_dark=True):
    fg  = WHITE if on_dark else TEXT_DARK
    sub = (155,148,172) if on_dark else (115,108,128)
    f,fs = F("black",size), F("medium",int(size*0.34))
    pw = tw(d,"PMI",f)
    d.text((x,y),"PMI",font=f,fill=fg)
    d.text((x+pw,y),".",font=f,fill=PURPLE)
    d.text((x,y+th(d,"PMI",f)+3),"Social Manager",font=fs,fill=sub)

def logo_c(d,W,y,size=38,on_dark=True):
    fg  = WHITE if on_dark else TEXT_DARK
    sub = (155,148,172) if on_dark else (115,108,128)
    f,fs = F("black",size), F("medium",int(size*0.34))
    pw=tw(d,"PMI",f); dw=tw(d,".",f)
    x=(W-pw-dw)//2
    d.text((x,y),"PMI",font=f,fill=fg)
    d.text((x+pw,y),".",font=f,fill=PURPLE)
    smw=tw(d,"Social Manager",fs)
    d.text(((W-smw)//2,y+th(d,"PMI",f)+3),"Social Manager",font=fs,fill=sub)

# ── Checkmark ────────────────────────────────────────────────────────────────
def checkmark(d,cx,cy,r=16,color=PURPLE):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=color)
    lw=max(2,r//6)
    d.line([(cx-r*0.36,cy+r*0.06),(cx-r*0.04,cy+r*0.44)],fill=WHITE,width=lw)
    d.line([(cx-r*0.04,cy+r*0.44),(cx+r*0.44,cy-r*0.32)],fill=WHITE,width=lw)

# ── Buttons ───────────────────────────────────────────────────────────────────
def btn_solid(d,x,y,text,font,color=PURPLE,px=36,py=14):
    bw=tw(d,text,font)+px*2; bh=th(d,text,font)+py*2
    d.rounded_rectangle([x,y,x+bw,y+bh],radius=10,fill=color)
    d.text((x+px,y+py),text,font=font,fill=WHITE)
    return y+bh

def btn_solid_c(d,W,y,text,font,color=PURPLE,px=40,py=16):
    bw=tw(d,text,font)+px*2; bh=th(d,text,font)+py*2
    x=(W-bw)//2
    d.rounded_rectangle([x,y,x+bw,y+bh],radius=10,fill=color)
    d.text((x+px,y+py),text,font=font,fill=WHITE)
    return y+bh

def btn_grad_c(d,W,y,text,font,px=44,py=16):
    bw=tw(d,text,font)+px*2; bh=th(d,text,font)+py*2
    x=(W-bw)//2
    grad_h(d,x,y,x+bw,y+bh,PURPLE_LT,PINK)
    d.text((x+px,y+py),text,font=font,fill=WHITE)
    return y+bh

def accent_bar(d,x,y,w=56,h=5,c1=PURPLE_LT,c2=PINK):
    grad_h(d,x,y,x+w,y+h,c1,c2)


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 1 — GRATUITO · LIGHT + FOTO · 1080×1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_01():
    W,H = 1080,1080
    MG  = 64

    # Background: foto workspace com overlay leve
    img = fit_photo(f"{BG}/bg_01.png", W, H, centering=(0.5,0.4))
    # Overlay branco para manter legibilidade (light mode)
    ov  = Image.new("RGBA",(W,H),(248,248,248,210))
    img = img.convert("RGBA"); img.alpha_composite(ov); img = img.convert("RGB")
    img = grid_lines(img, PURPLE, opacity=0.03, spacing=88)
    d   = ImageDraw.Draw(img)

    # Top bar
    grad_h(d,0,0,W,8,PURPLE_LT,PINK)

    # Logo
    logo_tl(d,MG,38,size=38,on_dark=False)

    # Badge
    f_b = F("bold",20); bt="GRATUITO"
    bw=tw(d,bt,f_b)+28; bh=th(d,bt,f_b)+12
    bx=W-MG-bw; by=42
    grad_h(d,bx,by,bx+bw,by+bh,PURPLE_LT,PINK)
    d.text((bx+14,by+6),bt,font=f_b,fill=WHITE)

    # Layout: texto esq. | card dir.
    CARD_W = 298
    cx0    = W-MG-CARD_W
    TW     = cx0-MG-40

    y = 132
    # Headline
    f_h = F("black",50)
    hl  = "Agências que crescem sem contratar mais ninguém têm uma coisa em comum."
    y   = block(d,hl,f_h,MG,y,TW,TEXT_DARK,leading=1.12)
    y  += 20

    accent_bar(d,MG,y)
    y += 22

    # Corpo
    f_body = F("regular",27); f_emph = F("bold",27)
    for txt,emph in [("Não é o número de clientes.",False),
                     ("Não é o time maior.",False),
                     ("É controle.",True)]:
        d.text((MG,y),txt,font=(f_emph if emph else f_body),
               fill=(PURPLE if emph else GRAY_TEXT))
        y += int(27*1.52)
    y += 8

    f_b2 = F("regular",25)
    y = block(d,"Relatórios que o cliente entende, conteúdo no horário certo e inbox sem mensagem perdida — sem planilha, sem post-it.",
              f_b2,MG,y,TW,GRAY_TEXT,leading=1.55)
    y += 16

    f_sub = F("medium",25)
    y = block(d,"Checklist gratuito para agências que querem atender mais com a mesma equipe.",
              f_sub,MG,y,TW,TEXT_DARK,leading=1.45)
    y += 26

    btn_solid(d,MG,y,"Ver onde sua agência perde tempo  →",F("bold",23),color=PURPLE)

    # Card
    ROW_H=60; cp=20
    items=["Relatórios automáticos","Agendamento inteligente","Inbox unificado",
           "IA para legendas","Aprovação de conteúdo","Dashboard por cliente"]
    c_y=132; c_h=len(items)*ROW_H+cp*2
    d.rounded_rectangle([cx0,c_y,cx0+CARD_W,c_y+c_h],radius=16,fill=WHITE)
    d.rounded_rectangle([cx0,c_y,cx0+CARD_W,c_y+c_h],radius=16,outline=(215,210,230),width=2)
    grad_h(d,cx0,c_y,cx0+CARD_W,c_y+6,PURPLE_LT,PINK)
    for i,item in enumerate(items):
        iy=c_y+cp+i*ROW_H+ROW_H//2
        checkmark(d,cx0+cp+16,iy,r=15,color=PURPLE)
        d.text((cx0+cp+42,iy-11),item,font=F("medium",20),fill=TEXT_DARK)

    img.save(f"{OUT}/peca_01.png"); print("✓ peca_01")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 2 — PAGO A · DARK + FOTO · 1080×1350
# ══════════════════════════════════════════════════════════════════════════════
def peca_02():
    W,H = 1080,1350
    MG  = 64

    # Metade superior: foto com overlay escuro
    PHOTO_H = 520
    photo   = fit_photo(f"{BG}/bg_02.png", W, PHOTO_H, centering=(0.5,0.3))
    photo   = dark_overlay(photo, alpha=110)
    # gradient escuro para baixo
    photo   = grad_overlay_v(photo, c1_alpha=0, c2_alpha=240)
    photo   = grid_lines(photo, PURPLE, opacity=0.04, spacing=72)

    img = Image.new("RGB",(W,H),BLACK)
    img.paste(photo,(0,0))
    img = glow(img,W//2,PHOTO_H,500,PURPLE,opacity=0.16)
    d   = ImageDraw.Draw(img)

    grad_h(d,0,0,W,7,PURPLE_LT,PINK)
    logo_tl(d,MG,36,size=40,on_dark=True)

    # Linha gradient accent (separador foto/texto)
    grad_h(d,0,PHOTO_H,W,PHOTO_H+4,PURPLE_LT,PINK)

    y = PHOTO_H + 44

    # Headline impactante
    f_h = F("black",70)
    d.text((MG,y),"Chega de gerenciar",font=f_h,fill=WHITE); y+=int(70*1.1)
    d.text((MG,y),"Instagram no grito.",font=f_h,fill=WHITE); y+=int(70*1.1)
    y += 8

    accent_bar(d,MG,y,w=64)
    y += 26

    # Corpo em blocos curtos
    f_body=F("regular",28)
    paras=["Agendar post. Responder DM. Gerar relatório. Criar legenda.",
           "Tudo isso todo dia. Para todo cliente.",
           "O PMI reúne tudo em um único lugar — o que tomava horas passa a tomar minutos."]
    for p in paras:
        y=block(d,p,f_body,MG,y,W-MG*2,GRAY_BODY,leading=1.52)
        y+=14

    y+=18
    btn_solid(d,MG,y,"Comece agora — teste sem risco  →",F("bold",25),color=PURPLE)

    img.save(f"{OUT}/peca_02.png"); print("✓ peca_02")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 3 — PAGO B · DARK + FOTO · 1080×1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_03():
    W,H = 1080,1080
    MG  = 64

    # Fundo: foto rede + overlay escuro forte
    img = fit_photo(f"{BG}/bg_03.png",W,H,centering=(0.5,0.5))
    img = dark_overlay(img,alpha=175)
    img = glow(img,W//2,H//2,560,PURPLE,opacity=0.18)
    img = grid_lines(img,PURPLE,opacity=0.04,spacing=90)
    d   = ImageDraw.Draw(img)

    y = 52
    f_h = F("black",46)
    hl  = "Quanto tempo você perde fazendo o que a IA faria em 10 segundos?"
    y   = block(d,hl,f_h,MG,y,W-MG*2,WHITE,leading=1.15,align="center",W_c=W)
    y  += 24

    sep_w=60; d.rectangle([(W-sep_w)//2,y,(W+sep_w)//2,y+4],fill=PURPLE)
    y += 20

    # 700+ hero com gradiente
    f_big=F("black",200); num="700+"
    nw=tw(d,num,f_big); nh=th(d,num,f_big)
    nx=(W-nw)//2; ny=y

    img = glow(img,W//2,ny+nh//2,300,PURPLE,opacity=0.22)
    d   = ImageDraw.Draw(img)

    num_lay = Image.new("RGBA",(W,H),(0,0,0,0))
    dn = ImageDraw.Draw(num_lay)
    dn.text((nx,ny),num,font=f_big,fill=(*PURPLE_LT,255))
    tint=Image.new("RGBA",(W,H),(0,0,0,0))
    dt =ImageDraw.Draw(tint)
    for xi in range(nx,nx+nw):
        t=(xi-nx)/max(1,nw)
        dt.line([(xi,ny),(xi,ny+nh)],fill=(*lerp(PURPLE_LT,PINK,t),255))
    _,_,_,a_ch=num_lay.split(); tint.putalpha(a_ch)
    img=img.convert("RGBA"); img.alpha_composite(tint); img=img.convert("RGB")
    d=ImageDraw.Draw(img)

    y=ny+nh-18
    f_lbl=F("medium",28)
    lbl="profissionais já economizam horas por semana com o PMI"
    y=block(d,lbl,f_lbl,MG,y,W-MG*2,GRAY_BODY,leading=1.2,align="center",W_c=W)
    y+=22

    # Avatares
    N=8; av_r=24; av_g=8; total=N*(av_r*2+av_g)-av_g; ax0=(W-total)//2
    av_cy=y+av_r; initials=list("ABCDEFGH")
    for i in range(N):
        ax=ax0+i*(av_r*2+av_g)+av_r; c=lerp(PURPLE_LT,PINK,i/(N-1))
        d.ellipse([ax-av_r-2,av_cy-av_r-2,ax+av_r+2,av_cy+av_r+2],fill=(10,5,20))
        d.ellipse([ax-av_r,av_cy-av_r,ax+av_r,av_cy+av_r],fill=c)
        iw=tw(d,initials[i],F("bold",17)); ih=th(d,initials[i],F("bold",17))
        d.text((ax-iw//2,av_cy-ih//2-2),initials[i],font=F("bold",17),fill=WHITE)
    y=av_cy+av_r+28

    f_body=F("regular",26)
    body="Gestores que usam o PMI criam a legenda de uma semana em menos de 5 minutos, automatizam respostas e entregam relatórios com a marca da agência."
    y=block(d,body,f_body,MG,y,W-MG*2,GRAY_BODY,leading=1.52,align="center",W_c=W)
    y+=28

    btn_grad_c(d,W,y,"Veja como funciona e comece hoje  →",F("bold",24))
    y+=th(d,"X",F("bold",24))+14+28+24

    logo_c(d,W,y,size=34,on_dark=True)
    img.save(f"{OUT}/peca_03.png"); print("✓ peca_03")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 4 — PAGO C · DARK + FOTO · HUB · 1080×1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_04():
    W,H = 1080,1080
    MG  = 64

    img = fit_photo(f"{BG}/bg_04.png",W,H,centering=(0.5,0.5))
    img = dark_overlay(img,alpha=178)
    img = glow(img,W//2,H//2,500,PURPLE,opacity=0.14)
    img = grid_lines(img,PURPLE,opacity=0.04,spacing=72)
    d   = ImageDraw.Draw(img)

    y=48
    f_h=F("black",50)
    for line in ["Sua agência usa uma ferramenta","diferente para cada coisa?"]:
        lw=tw(d,line,f_h)
        d.text(((W-lw)//2,y),line,font=f_h,fill=WHITE)
        y+=int(50*1.12)
    y+=14

    # Hub diagram
    hub_cx=W//2; hub_cy=y+210; hub_r=60; spoke=178; node_r=50

    tool_labels=[["Agendamento"],["Inbox"],["Relatório"],["Criativo"],["Legenda","IA"]]
    tool_angles=[270,342,54,126,198]

    for lns,ang in zip(tool_labels,tool_angles):
        rad=math.radians(ang)
        nx=hub_cx+int(spoke*math.cos(rad)); ny=hub_cy+int(spoke*math.sin(rad))
        dx=nx-hub_cx; dy=ny-hub_cy; ln=math.sqrt(dx*dx+dy*dy)
        ux,uy=dx/ln,dy/ln; pos=hub_r+6
        while pos<ln-node_r-6:
            sx=hub_cx+ux*pos; sy=hub_cy+uy*pos
            ex=hub_cx+ux*(pos+12); ey=hub_cy+uy*(pos+12)
            d.line([(sx,sy),(ex,ey)],fill=(65,32,115),width=2)
            mid=pos+6; mx_=hub_cx+ux*mid; my_=hub_cy+uy*mid
            d.ellipse([mx_-4,my_-4,mx_+4,my_+4],fill=PURPLE)
            pos+=20
        # Node glow
        lay=Image.new("RGBA",(W,H),(0,0,0,0)); dl=ImageDraw.Draw(lay)
        for r in range(node_r+18,node_r-1,-2):
            dl.ellipse([nx-r,ny-r,nx+r,ny+r],fill=(*PURPLE,int(32*(1-(r-node_r)/18))))
        img=img.convert("RGBA"); img.alpha_composite(lay); img=img.convert("RGB")
        d=ImageDraw.Draw(img)
        d.ellipse([nx-node_r,ny-node_r,nx+node_r,ny+node_r],fill=(20,9,42),outline=(78,38,148),width=2)
        f_nd=F("medium",18)
        for li,lt in enumerate(lns):
            ltw=tw(d,lt,f_nd)
            d.text((nx-ltw//2,ny-10+li*22),lt,font=f_nd,fill=GRAY_BODY)

    # Hub glow
    for r in range(hub_r+55,hub_r-1,-3):
        a=int(50*(1-(r-hub_r)/55)**1.2)
        lay2=Image.new("RGBA",(W,H),(0,0,0,0)); dl2=ImageDraw.Draw(lay2)
        dl2.ellipse([hub_cx-r,hub_cy-r,hub_cx+r,hub_cy+r],fill=(*PURPLE,a))
        img=img.convert("RGBA"); img.alpha_composite(lay2); img=img.convert("RGB")
    d=ImageDraw.Draw(img)

    for xi in range(hub_cx-hub_r,hub_cx+hub_r):
        t=(xi-(hub_cx-hub_r))/(hub_r*2); c=lerp(PURPLE_LT,PINK,t)
        hat=int(math.sqrt(max(0,hub_r**2-(xi-hub_cx)**2)))
        d.line([(xi,hub_cy-hat),(xi,hub_cy+hat)],fill=c)

    f_hub=F("black",26); pw=tw(d,"PMI",f_hub); dw2=tw(d,".",f_hub)
    d.text((hub_cx-(pw+dw2)//2,hub_cy-17),"PMI",font=f_hub,fill=WHITE)
    d.text((hub_cx-(pw+dw2)//2+pw,hub_cy-17),".",font=f_hub,fill=(28,10,56))
    smw=tw(d,"Social",F("medium",14))
    d.text((hub_cx-smw//2,hub_cy+12),"Social",font=F("medium",14),fill=WHITE)

    y_b=hub_cy+spoke+node_r+36
    f_body=F("regular",26)
    body="O plano Agency do PMI centraliza tudo — múltiplos clientes, relatórios white-label, IA ilimitada e criativos para Meta Ads."
    y_b=block(d,body,f_body,MG,y_b,W-MG*2,GRAY_BODY,leading=1.5,align="center",W_c=W)
    y_b+=24

    btn_solid_c(d,W,y_b,"Monte sua operação com a gente  →",F("bold",23),color=PURPLE)
    y_b+=th(d,"X",F("bold",23))+14+28+24
    logo_c(d,W,y_b,size=32,on_dark=True)

    img.save(f"{OUT}/peca_04.png"); print("✓ peca_04")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 5 — STORY · 1080×1920 · FOTO + GRADIENTE
# ══════════════════════════════════════════════════════════════════════════════
def peca_05():
    W,H = 1080,1920
    MG  = 72

    # Foto smartphone na metade inferior
    SPLIT = 960  # onde a foto começa
    img   = grad_diag(W, H, BLACK, (42,8,100))

    # Cola foto na parte inferior (device)
    photo  = fit_photo(f"{BG}/bg_05.png", W, H-SPLIT, centering=(0.5,0.3))
    photo  = dark_overlay(photo, alpha=60)
    photo  = grad_overlay_v(photo, c1_alpha=220, c2_alpha=60)  # escurece topo da foto
    img_ph = img.copy()
    img_ph.paste(photo,(0,SPLIT))
    img    = img_ph

    img = glow(img,W//2,H//2,700,PURPLE,opacity=0.13)
    img = grid_lines(img,PURPLE,opacity=0.04,spacing=92)
    d   = ImageDraw.Draw(img)

    grad_h(d,0,0,W,8,PURPLE_LT,PINK)

    # Logo centered top
    logo_c(d,W,52,size=44,on_dark=True)

    # Headline gigante
    y=210
    f_h=F("black",106)
    for line in ["Tudo que sua","agência precisa."]:
        lw=tw(d,line,f_h)
        d.text(((W-lw)//2,y),line,font=f_h,fill=WHITE)
        y+=int(106*1.08)
    y+=16

    # Subtítulo
    f_sub=F("regular",35)
    for line in ["Agendamento. IA. Relatórios. Inbox.","Uma plataforma. Zero bagunça."]:
        lw=tw(d,line,f_sub)
        d.text(((W-lw)//2,y),line,font=f_sub,fill=GRAY_BODY)
        y+=int(35*1.52)
    y+=32

    # Linha divisória gradiente
    grad_h(d,MG,y,W-MG,y+3,PURPLE_LT,PINK)
    y+=26

    # Feature pills (2 rows)
    pills=["IA Generativa","Inbox Unificado","Relatórios White-Label","Meta Ads"]
    f_pill=F("medium",22); pill_x=MG; pill_y=y; row_h=0
    for pill in pills:
        pw2=tw(d,pill,f_pill)+30; ph3=th(d,pill,f_pill)+14; row_h=max(row_h,ph3)
        if pill_x+pw2>W-MG: pill_x=MG; pill_y+=row_h+10; row_h=ph3
        d.rounded_rectangle([pill_x,pill_y,pill_x+pw2,pill_y+ph3],
                             radius=22,outline=PURPLE,width=2,fill=(26,6,54))
        d.text((pill_x+15,pill_y+7),pill,font=f_pill,fill=WHITE)
        pill_x+=pw2+10
    y=pill_y+row_h+40

    # Números de impacto (3 colunas)
    stats=[("700+","Profissionais"),("5h+","Economizadas/sem."),("99%","Taxa de entrega")]
    col_w=(W-MG*2)//3
    for i,(val,lbl) in enumerate(stats):
        cx=MG+i*col_w+col_w//2
        f_val=F("black",54); f_lbl=F("regular",22)
        vw=tw(d,val,f_val)
        # Gradiente no número
        num_lay=Image.new("RGBA",(W,H),(0,0,0,0))
        dn=ImageDraw.Draw(num_lay)
        dn.text((cx-vw//2,y),val,font=f_val,fill=(*PURPLE_LT,255))
        tint=Image.new("RGBA",(W,H),(0,0,0,0)); dt=ImageDraw.Draw(tint)
        for xi in range(cx-vw//2,cx+vw//2):
            t=(xi-(cx-vw//2))/max(1,vw)
            dt.line([(xi,y),(xi,y+th(d,val,f_val))],fill=(*lerp(PURPLE_LT,PINK,t),255))
        _,_,_,a_ch=num_lay.split(); tint.putalpha(a_ch)
        img=img.convert("RGBA"); img.alpha_composite(tint); img=img.convert("RGB")
        d=ImageDraw.Draw(img)
        lw=tw(d,lbl,f_lbl)
        d.text((cx-lw//2,y+th(d,val,f_val)+4),lbl,font=f_lbl,fill=GRAY_BODY)
    y+=th(d,stats[0][0],F("black",54))+th(d,stats[0][1],F("regular",22))+32

    # Separador
    grad_h(d,MG,y,W-MG,y+3,PURPLE_LT,PINK); y+=24

    # Tagline
    f_tag=F("medium",30); tag="Para agências e gestores de social media."
    lw=tw(d,tag,f_tag)
    d.text(((W-lw)//2,y),tag,font=f_tag,fill=GRAY_BODY); y+=int(30*1.5)+14

    # CTA
    btn_grad_c(d,W,y,"Conheça o PMI Social Manager",F("bold",32))

    img.save(f"{OUT}/peca_05.png"); print("✓ peca_05")


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    peca_01(); peca_02(); peca_03(); peca_04(); peca_05()
    print(f"\nAll 5 pieces → {OUT}")
