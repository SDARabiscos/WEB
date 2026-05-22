#!/usr/bin/env python3
"""PMI Social Manager — 5 Ad Pieces. Layout totalmente centralizado."""

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
GRAY_TEXT = (75, 72, 88)
GRAY_BODY = (188, 183, 205)
TEXT_DARK = (17, 17, 17)
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

# ── Colour ────────────────────────────────────────────────────────────────────
def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

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

def grad_overlay_v(img, a_top=0, a_bot=220):
    W,H = img.size
    lay = Image.new("RGBA",(W,H),(0,0,0,0))
    d = ImageDraw.Draw(lay)
    for y in range(H):
        a = int(a_top+(a_bot-a_top)*(y/H)**1.3)
        d.line([(0,y),(W,y)], fill=(0,0,0,a))
    base = img.convert("RGBA"); base.alpha_composite(lay)
    return base.convert("RGB")

def grid_lines(img, color=PURPLE, opacity=0.04, spacing=80):
    W,H = img.size
    lay = Image.new("RGBA",(W,H),(0,0,0,0))
    d = ImageDraw.Draw(lay)
    a = int(opacity*255)
    for x in range(0,W,spacing): d.line([(x,0),(x,H)], fill=(*color,a))
    for y in range(0,H,spacing): d.line([(0,y),(W,y)], fill=(*color,a))
    base = img.convert("RGBA"); base.alpha_composite(lay)
    return base.convert("RGB")

def fit_photo(path, W, H, centering=(0.5,0.4)):
    return ImageOps.fit(Image.open(path).convert("RGB"),(W,H),Image.LANCZOS,centering=centering)

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

def text_c(d, text, font, W, y, color, max_w=None, leading=1.45):
    """Renderiza texto CENTRALIZADO. Retorna y após última linha."""
    lines = wrap_lines(d,text,font,max_w or W-128)
    lh = int(font.size*leading)
    for line in lines:
        lw = tw(d,line,font)
        d.text(((W-lw)//2, y), line, font=font, fill=color)
        y += lh
    return y

def text_l(d, text, font, x, y, color, max_w=900, leading=1.45):
    """Renderiza texto alinhado à esquerda."""
    lines = wrap_lines(d,text,font,max_w)
    lh = int(font.size*leading)
    for line in lines:
        d.text((x,y), line, font=font, fill=color)
        y += lh
    return y

# ── Logo ──────────────────────────────────────────────────────────────────────
def logo_tl(d, x, y, size=40, on_dark=True):
    fg  = WHITE if on_dark else TEXT_DARK
    sub = (152,145,170) if on_dark else (112,105,125)
    f,fs = F("black",size), F("medium",int(size*0.34))
    pw = tw(d,"PMI",f)
    d.text((x,y),"PMI",font=f,fill=fg)
    d.text((x+pw,y),".",font=f,fill=PURPLE)
    d.text((x,y+th(d,"PMI",f)+3),"Social Manager",font=fs,fill=sub)

def logo_c(d, W, y, size=38, on_dark=True):
    fg  = WHITE if on_dark else TEXT_DARK
    sub = (152,145,170) if on_dark else (112,105,125)
    f,fs = F("black",size), F("medium",int(size*0.34))
    pw=tw(d,"PMI",f); dw=tw(d,".",f)
    x=(W-pw-dw)//2
    d.text((x,y),"PMI",font=f,fill=fg)
    d.text((x+pw,y),".",font=f,fill=PURPLE)
    smw=tw(d,"Social Manager",fs)
    d.text(((W-smw)//2,y+th(d,"PMI",f)+4),"Social Manager",font=fs,fill=sub)

# ── Helpers ───────────────────────────────────────────────────────────────────
def sep_c(d, W, y, w=64, h=5):
    """Linha separadora centralizada com gradiente."""
    x=(W-w)//2
    grad_h(d,x,y,x+w,y+h,PURPLE_LT,PINK)
    return y+h

def checkmark(d, cx, cy, r=16, color=PURPLE):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=color)
    lw=max(2,r//6)
    d.line([(cx-r*0.36,cy+r*0.06),(cx-r*0.04,cy+r*0.44)],fill=WHITE,width=lw)
    d.line([(cx-r*0.04,cy+r*0.44),(cx+r*0.44,cy-r*0.32)],fill=WHITE,width=lw)

def btn_c(d, W, y, text, font, color=PURPLE, px=44, py=16):
    """Botão centralizado sólido."""
    bw=tw(d,text,font)+px*2; bh=th(d,text,font)+py*2
    x=(W-bw)//2
    d.rounded_rectangle([x,y,x+bw,y+bh],radius=10,fill=color)
    d.text((x+px,y+py),text,font=font,fill=WHITE)
    return y+bh

def btn_grad_c(d, W, y, text, font, px=44, py=16):
    """Botão centralizado gradiente."""
    bw=tw(d,text,font)+px*2; bh=th(d,text,font)+py*2
    x=(W-bw)//2
    grad_h(d,x,y,x+bw,y+bh,PURPLE_LT,PINK)
    d.text((x+px,y+py),text,font=font,fill=WHITE)
    return y+bh

def badge_c(d, W, y, text, font, gap_top=0):
    """Badge centralizado com gradiente."""
    bw=tw(d,text,font)+28; bh=th(d,text,font)+12
    x=(W-bw)//2
    grad_h(d,x,y,x+bw,y+bh,PURPLE_LT,PINK)
    d.text((x+14,y+6),text,font=font,fill=WHITE)
    return y+bh

def num_gradient(img, d, W, nx, ny, num, font):
    """Renderiza número grande com gradiente PURPLE→PINK."""
    nw=tw(d,num,font); nh=th(d,num,font)
    lay=Image.new("RGBA",(W,img.size[1]),(0,0,0,0))
    dn=ImageDraw.Draw(lay)
    dn.text((nx,ny),num,font=font,fill=(*PURPLE_LT,255))
    tint=Image.new("RGBA",(W,img.size[1]),(0,0,0,0))
    dt=ImageDraw.Draw(tint)
    for xi in range(nx,nx+nw):
        t=(xi-nx)/max(1,nw)
        dt.line([(xi,ny),(xi,ny+nh)],fill=(*lerp(PURPLE_LT,PINK,t),255))
    _,_,_,a_ch=lay.split(); tint.putalpha(a_ch)
    img=img.convert("RGBA"); img.alpha_composite(tint)
    return img.convert("RGB"), ny+nh


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 1 — GRATUITO · LIGHT · CENTRALIZADA · 1080×1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_01():
    W,H = 1080,1080
    MG  = 72

    img = fit_photo(f"{BG}/bg_01.png",W,H,(0.5,0.4))
    ov  = Image.new("RGBA",(W,H),(248,248,248,205))
    img = img.convert("RGBA"); img.alpha_composite(ov); img = img.convert("RGB")
    img = grid_lines(img,PURPLE,opacity=0.03,spacing=90)
    d   = ImageDraw.Draw(img)

    # Topo
    grad_h(d,0,0,W,8,PURPLE_LT,PINK)
    logo_tl(d,MG,36,size=38,on_dark=False)

    # Conteúdo — tudo centralizado
    y = 136
    y = badge_c(d,W,y,"GRATUITO",F("bold",22))
    y += 24

    y = text_c(d,"Agências que crescem sem contratar mais ninguém têm uma coisa em comum.",
               F("black",52),W,y,TEXT_DARK,max_w=W-MG*2,leading=1.12)
    y += 22
    y = sep_c(d,W,y,w=60)
    y += 22

    # 3 pontos de contraste
    for txt,emph in [("Não é o número de clientes.",False),
                     ("Não é o time maior.",False),
                     ("É controle.",True)]:
        lw=tw(d,txt,(F("bold",30) if emph else F("regular",30)))
        d.text(((W-lw)//2,y),txt,
               font=(F("bold",30) if emph else F("regular",30)),
               fill=(PURPLE if emph else GRAY_TEXT))
        y+=int(30*1.5)
    y+=10

    y = text_c(d,"Relatórios que o cliente entende, conteúdo no horário certo e inbox sem mensagem perdida — sem planilha, sem post-it.",
               F("regular",26),W,y,GRAY_TEXT,max_w=W-MG*2,leading=1.52)
    y+=18

    y = text_c(d,"Checklist gratuito para agências que querem atender mais com a mesma equipe.",
               F("medium",26),W,y,TEXT_DARK,max_w=W-MG*2,leading=1.45)
    y+=28

    # Checklist 2 colunas centralizadas
    items=["Relatórios automáticos","Agendamento inteligente","Inbox unificado",
           "IA para legendas","Aprovação de conteúdo","Dashboard por cliente"]
    f_item=F("medium",22); ROW=52; COL_W=360; COL_GAP=40
    total_w=COL_W*2+COL_GAP; start_x=(W-total_w)//2
    for i,item in enumerate(items):
        col=i%2; row=i//2
        ix=start_x+col*(COL_W+COL_GAP); iy=y+row*ROW
        checkmark(d,ix+16,iy+ROW//2,r=14,color=PURPLE)
        d.text((ix+38,iy+ROW//2-11),item,font=f_item,fill=TEXT_DARK)
    y+=3*ROW+24

    btn_grad_c(d,W,y,"Ver onde sua agência perde tempo  →",F("bold",24))

    img.save(f"{OUT}/peca_01.png"); print("✓ peca_01")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 2 — PAGO A · DARK · CENTRALIZADA · 1080×1350
# ══════════════════════════════════════════════════════════════════════════════
def peca_02():
    W,H  = 1080,1350
    MG   = 72
    PH   = 500  # altura da foto

    photo = fit_photo(f"{BG}/bg_02.png",W,PH,(0.5,0.3))
    photo = dark_overlay(photo,alpha=105)
    photo = grad_overlay_v(photo,a_top=0,a_bot=245)
    photo = grid_lines(photo,PURPLE,opacity=0.04,spacing=72)

    img = Image.new("RGB",(W,H),BLACK)
    img.paste(photo,(0,0))
    img = glow(img,W//2,PH,480,PURPLE,opacity=0.16)
    d   = ImageDraw.Draw(img)

    grad_h(d,0,0,W,7,PURPLE_LT,PINK)
    logo_tl(d,MG,36,size=40,on_dark=True)
    grad_h(d,0,PH,W,PH+5,PURPLE_LT,PINK)

    # Dashboard mockup centralizado
    mx=MG; mw=W-MG*2; my=130; mh=340
    for pw in range(4,0,-1):
        d.rounded_rectangle([mx-pw*5,my-pw*5,mx+mw+pw*5,my+mh+pw*5],
                              radius=18+pw*3,outline=(*PURPLE,14*pw),width=2)
    d.rounded_rectangle([mx,my,mx+mw,my+mh],radius=14,fill=(18,8,36),outline=(72,36,148),width=2)
    grad_h(d,mx,my,mx+mw,my+44,PURPLE_LT,PINK)
    d.text((mx+16,my+11),"PMI Social Manager",font=F("bold",20),fill=WHITE)
    for i,c in enumerate([(255,80,80),(255,200,50),(60,220,90)]):
        d.ellipse([mx+mw-68+i*22,my+16,mx+mw-50+i*22,my+34],fill=c)
    N=4; cpad=8; cw=(mw-(N+1)*cpad)//N
    for i,(val,lbl) in enumerate([("12","Contas"),("847","Posts"),("99%","Entrega"),("5h+","Economizado")]):
        cx=mx+cpad+i*(cw+cpad); cy=my+54
        d.rounded_rectangle([cx,cy,cx+cw,cy+82],radius=9,fill=MID_DARK)
        grad_h(d,cx,cy,cx+cw,cy+4,PURPLE_LT,PINK)
        d.text((cx+12,cy+10),val,font=F("black",28),fill=WHITE)
        d.text((cx+12,cy+48),lbl,font=F("regular",15),fill=(148,136,172))
    r0=my+148
    for i in range(4):
        ry=r0+i*46; c=lerp(PURPLE_LT,PINK,i/3)
        d.ellipse([mx+cpad,ry+4,mx+cpad+32,ry+36],fill=c)
        d.text((mx+cpad+42,ry+2),f"@cliente_0{i+1}",font=F("medium",17),fill=WHITE)
        d.text((mx+cpad+42,ry+24),"Ativo  ·  3 posts agendados",font=F("regular",13),fill=(128,116,152))
        d.ellipse([mx+mw-26,ry+12,mx+mw-12,ry+28],fill=(36,218,100))

    # Texto — tudo centralizado
    y = PH+50
    y = text_c(d,"Chega de gerenciar",F("black",70),W,y,WHITE,max_w=W-MG*2,leading=1.1)
    y = text_c(d,"Instagram no grito.",F("black",70),W,y,WHITE,max_w=W-MG*2,leading=1.1)
    y+=14; y=sep_c(d,W,y,w=72); y+=24

    paras=["Agendar post. Responder DM. Gerar relatório. Criar legenda.",
           "Tudo isso todo dia. Para todo cliente.",
           "O PMI reúne tudo em um único lugar — o que tomava horas passa a tomar minutos."]
    for p in paras:
        y=text_c(d,p,F("regular",28),W,y,GRAY_BODY,max_w=W-MG*2,leading=1.5)
        y+=10
    y+=24

    btn_c(d,W,y,"Comece agora — teste sem risco  →",F("bold",25),color=PURPLE)
    img.save(f"{OUT}/peca_02.png"); print("✓ peca_02")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 3 — PAGO B · DARK · CENTRALIZADA · 1080×1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_03():
    W,H = 1080,1080
    MG  = 72

    img = fit_photo(f"{BG}/bg_03.png",W,H,(0.5,0.5))
    img = dark_overlay(img,alpha=175)
    img = glow(img,W//2,H//2,560,PURPLE,opacity=0.18)
    img = grid_lines(img,PURPLE,opacity=0.04,spacing=90)
    d   = ImageDraw.Draw(img)

    y=52
    y=text_c(d,"Quanto tempo você perde fazendo o que",F("black",48),W,y,WHITE,max_w=W-MG*2,leading=1.12)
    y=text_c(d,"a IA faria em 10 segundos?",F("black",48),W,y,WHITE,max_w=W-MG*2,leading=1.12)
    y+=20; y=sep_c(d,W,y); y+=20

    # 700+ hero
    f_big=F("black",200); num="700+"
    nw=tw(d,num,f_big); nh=th(d,num,f_big); nx=(W-nw)//2; ny=y
    img=glow(img,W//2,ny+nh//2,300,PURPLE,opacity=0.22)
    d=ImageDraw.Draw(img)
    img,y=num_gradient(img,d,W,nx,ny,num,f_big)
    d=ImageDraw.Draw(img)
    y-=16

    y=text_c(d,"profissionais já economizam horas por semana com o PMI",
             F("medium",27),W,y,GRAY_BODY,max_w=W-MG*2,leading=1.3)
    y+=20

    # Avatares
    N=8; av_r=24; av_g=8; total=N*(av_r*2+av_g)-av_g; ax0=(W-total)//2
    av_cy=y+av_r; initials=list("ABCDEFGH")
    for i in range(N):
        ax=ax0+i*(av_r*2+av_g)+av_r; c=lerp(PURPLE_LT,PINK,i/(N-1))
        d.ellipse([ax-av_r-2,av_cy-av_r-2,ax+av_r+2,av_cy+av_r+2],fill=(10,5,20))
        d.ellipse([ax-av_r,av_cy-av_r,ax+av_r,av_cy+av_r],fill=c)
        iw=tw(d,initials[i],F("bold",17)); ih=th(d,initials[i],F("bold",17))
        d.text((ax-iw//2,av_cy-ih//2-2),initials[i],font=F("bold",17),fill=WHITE)
    y=av_cy+av_r+26

    y=text_c(d,"Gestores que usam o PMI criam a legenda de uma semana em menos de 5 minutos, automatizam respostas e entregam relatórios com a marca da agência.",
             F("regular",26),W,y,GRAY_BODY,max_w=W-MG*2,leading=1.5)
    y+=26

    y=btn_grad_c(d,W,y,"Veja como funciona e comece hoje  →",F("bold",24))
    y+=26
    logo_c(d,W,y,size=34,on_dark=True)
    img.save(f"{OUT}/peca_03.png"); print("✓ peca_03")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 4 — PAGO C · HUB · CENTRALIZADA · 1080×1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_04():
    W,H = 1080,1080
    MG  = 72

    img = fit_photo(f"{BG}/bg_04.png",W,H,(0.5,0.5))
    img = dark_overlay(img,alpha=180)
    img = glow(img,W//2,H//2,500,PURPLE,opacity=0.14)
    img = grid_lines(img,PURPLE,opacity=0.04,spacing=72)
    d   = ImageDraw.Draw(img)

    y=48
    y=text_c(d,"Sua agência usa uma ferramenta diferente",F("black",50),W,y,WHITE,max_w=W-MG*2,leading=1.12)
    y=text_c(d,"para cada coisa?",F("black",50),W,y,WHITE,max_w=W-MG*2,leading=1.12)
    y+=16

    # Hub diagram
    hub_cx=W//2; hub_cy=y+218; hub_r=60; spoke=178; node_r=50
    for lns,ang in zip([["Agendamento"],["Inbox"],["Relatório"],["Criativo"],["Legenda","IA"]],
                        [270,342,54,126,198]):
        rad=math.radians(ang)
        nx=hub_cx+int(spoke*math.cos(rad)); ny=hub_cy+int(spoke*math.sin(rad))
        dx=nx-hub_cx; dy=ny-hub_cy; ln=math.sqrt(dx*dx+dy*dy)
        ux,uy=dx/ln,dy/ln; pos=hub_r+6
        while pos<ln-node_r-6:
            sx=hub_cx+ux*pos; sy=hub_cy+uy*pos
            ex=hub_cx+ux*(pos+12); ey=hub_cy+uy*(pos+12)
            d.line([(sx,sy),(ex,ey)],fill=(65,32,115),width=2)
            mid=pos+6
            d.ellipse([hub_cx+ux*mid-4,hub_cy+uy*mid-4,hub_cx+ux*mid+4,hub_cy+uy*mid+4],fill=PURPLE)
            pos+=20
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

    # Hub com glow + gradiente
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
    y_b=text_c(d,"O plano Agency do PMI centraliza tudo — múltiplos clientes, relatórios white-label, IA ilimitada e criativos para Meta Ads.",
               F("regular",26),W,y_b,GRAY_BODY,max_w=W-MG*2,leading=1.5)
    y_b+=24
    y_b=btn_c(d,W,y_b,"Monte sua operação com a gente  →",F("bold",23),color=PURPLE)
    y_b+=26
    logo_c(d,W,y_b,size=32,on_dark=True)
    img.save(f"{OUT}/peca_04.png"); print("✓ peca_04")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 5 — STORY · CENTRALIZADA · 1080×1920
# ══════════════════════════════════════════════════════════════════════════════
def peca_05():
    W,H  = 1080,1920
    MG   = 72
    SPLIT= 980

    img  = grad_diag(W,H,BLACK,(42,8,100))
    photo= fit_photo(f"{BG}/bg_05.png",W,H-SPLIT,(0.5,0.3))
    photo= dark_overlay(photo,alpha=55)
    photo= grad_overlay_v(photo,a_top=230,a_bot=60)
    img.paste(photo,(0,SPLIT))
    img  = glow(img,W//2,H//2,700,PURPLE,opacity=0.13)
    img  = grid_lines(img,PURPLE,opacity=0.04,spacing=92)
    d    = ImageDraw.Draw(img)

    grad_h(d,0,0,W,8,PURPLE_LT,PINK)
    logo_c(d,W,52,size=44,on_dark=True)

    y=215
    y=text_c(d,"Tudo que sua",F("black",106),W,y,WHITE,leading=1.08)
    y=text_c(d,"agência precisa.",F("black",106),W,y,WHITE,leading=1.08)
    y+=16; y=sep_c(d,W,y,w=72); y+=16

    for line in ["Agendamento. IA. Relatórios. Inbox.","Uma plataforma. Zero bagunça."]:
        y=text_c(d,line,F("regular",34),W,y,GRAY_BODY,leading=1.5)
    y+=32

    # Linha divisória
    grad_h(d,MG,y,W-MG,y+3,PURPLE_LT,PINK); y+=22

    # Feature pills (2 linhas, centralizadas)
    pills=["IA Generativa","Inbox Unificado","Relatórios White-Label","Meta Ads"]
    f_pill=F("medium",22)
    # Pre-calc total width por linha para centralizar
    rows=[[pills[0],pills[1]],[pills[2],pills[3]]]
    pill_h=th(d,pills[0],f_pill)+14
    for row in rows:
        widths=[tw(d,p,f_pill)+30 for p in row]
        total_w=sum(widths)+10*(len(row)-1)
        px=(W-total_w)//2
        for p,pw2 in zip(row,widths):
            d.rounded_rectangle([px,y,px+pw2,y+pill_h],radius=22,
                                 outline=PURPLE,width=2,fill=(26,6,54))
            d.text((px+15,y+7),p,font=f_pill,fill=WHITE)
            px+=pw2+10
        y+=pill_h+10
    y+=24

    # Métricas (3 colunas centralizadas)
    stats=[("700+","Profissionais"),("5h+","Economizadas/sem."),("99%","Taxa de entrega")]
    col_w=(W-MG*2)//3
    f_val=F("black",52); f_lbl=F("regular",21)
    val_h=th(d,stats[0][0],f_val)
    for i,(val,lbl) in enumerate(stats):
        cx=MG+i*col_w+col_w//2
        vw=tw(d,val,f_val)
        img=glow(img,cx,y+val_h//2,80,PURPLE,opacity=0.20)
        d=ImageDraw.Draw(img)
        img,_ = num_gradient(img,d,W,cx-vw//2,y,val,f_val)
        d=ImageDraw.Draw(img)
        lw=tw(d,lbl,f_lbl)
        d.text((cx-lw//2,y+val_h+4),lbl,font=f_lbl,fill=GRAY_BODY)
    y+=val_h+th(d,stats[0][1],f_lbl)+32

    grad_h(d,MG,y,W-MG,y+3,PURPLE_LT,PINK); y+=24

    y=text_c(d,"Para agências e gestores de social media.",F("medium",30),W,y,GRAY_BODY,leading=1.5)
    y+=18
    btn_grad_c(d,W,y,"Conheça o PMI Social Manager",F("bold",32))

    img.save(f"{OUT}/peca_05.png"); print("✓ peca_05")


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    peca_01(); peca_02(); peca_03(); peca_04(); peca_05()
    print(f"\nAll 5 pieces → {OUT}")
