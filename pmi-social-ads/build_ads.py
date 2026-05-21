#!/usr/bin/env python3
"""PMI Social Manager — 5 Ad Pieces. Fixed proportions & readability."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

OUT = "/home/user/WEB/pmi-social-ads/out"
os.makedirs(OUT, exist_ok=True)

# ── Brand Colors ──────────────────────────────────────────────────────────────
PURPLE    = (123, 47, 255)
PINK      = (236, 72, 153)
PURPLE_LT = (139, 92, 246)
BLACK     = (10, 10, 10)
WHITE     = (255, 255, 255)
GRAY_BG   = (248, 248, 248)
GRAY_TEXT = (90, 90, 90)
GRAY_BODY = (180, 175, 195)
TEXT_DARK = (17, 17, 17)
DARK_CARD = (22, 12, 48)
MID_DARK  = (30, 14, 62)

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
        d.line([(x1+i, y1),(x1+i, y2)], fill=lerp(c1, c2, i/max(1,n-1)))

def grad_v(d, x1, y1, x2, y2, c1, c2):
    n = y2-y1
    for i in range(n):
        d.line([(x1, y1+i),(x2, y1+i)], fill=lerp(c1, c2, i/max(1,n-1)))

def grad_diag(W, H, c1, c2):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        for x in range(0, W, 3):
            t = x/W*0.35 + y/H*0.65
            d.line([(x,y),(min(x+3,W),y)], fill=lerp(c1,c2,t))
    return img

# ── Effects ───────────────────────────────────────────────────────────────────
def glow(img, cx, cy, radius, color, opacity=0.13):
    lay = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(lay)
    steps = 28
    for i in range(steps, 0, -1):
        r = int(radius*i/steps)
        a = int(opacity*255*(1-i/steps)**0.55)
        d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(*color,a))
    lay = lay.filter(ImageFilter.GaussianBlur(radius//5))
    base = img.convert("RGBA"); base.alpha_composite(lay)
    return base.convert("RGB")

def grid_lines(img, color=PURPLE, opacity=0.045, spacing=80):
    W,H = img.size
    lay = Image.new("RGBA",(W,H),(0,0,0,0))
    d = ImageDraw.Draw(lay)
    a = int(opacity*255)
    for x in range(0,W,spacing): d.line([(x,0),(x,H)], fill=(*color,a), width=1)
    for y in range(0,H,spacing): d.line([(0,y),(W,y)], fill=(*color,a), width=1)
    base = img.convert("RGBA"); base.alpha_composite(lay)
    return base.convert("RGB")

def vignette(img, strength=0.35):
    W,H = img.size
    lay = Image.new("RGBA",(W,H),(0,0,0,0))
    d = ImageDraw.Draw(lay)
    for i in range(30,0,-1):
        rw,rh = int(W*i/30), int(H*i/30)
        a = int(strength*255*(1-i/30)**1.6)
        d.rectangle([W//2-rw,H//2-rh,W//2+rw,H//2+rh], outline=(0,0,0,a), width=4)
    lay = lay.filter(ImageFilter.GaussianBlur(40))
    base = img.convert("RGBA"); base.alpha_composite(lay)
    return base.convert("RGB")

# ── Typography ────────────────────────────────────────────────────────────────
def tw(d, text, font):
    bb = d.textbbox((0,0), text, font=font)
    return bb[2]-bb[0]

def th(d, text, font):
    bb = d.textbbox((0,0), text, font=font)
    return bb[3]-bb[1]

def wrap_lines(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if tw(d, test, font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def text_block_h(d, text, font, max_w, leading):
    """Returns total pixel height of a text block."""
    lines = wrap_lines(d, text, font, max_w)
    return len(lines) * int(font.size * leading)

def draw_block(d, text, font, x, y, max_w, color, leading=1.5, align="left", W_canvas=0):
    lines = wrap_lines(d, text, font, max_w)
    lh = int(font.size * leading)
    for line in lines:
        lw = tw(d, line, font)
        if align == "center":
            xp = (W_canvas - lw) // 2
        elif align == "right":
            xp = x + max_w - lw
        else:
            xp = x
        d.text((xp, y), line, font=font, fill=color)
        y += lh
    return y  # returns y after last line

# ── Logo ──────────────────────────────────────────────────────────────────────
def logo_tl(d, x, y, size=40, on_dark=True):
    fg = WHITE if on_dark else TEXT_DARK
    sub = (155,148,172) if on_dark else (115,108,128)
    f, fs = F("black",size), F("medium",int(size*0.35))
    pw = tw(d,"PMI",f)
    d.text((x,y),"PMI",font=f,fill=fg)
    d.text((x+pw,y),".",font=f,fill=PURPLE)
    d.text((x,y+th(d,"PMI",f)+3),"Social Manager",font=fs,fill=sub)

def logo_c(d, W, y, size=38, on_dark=True):
    fg = WHITE if on_dark else TEXT_DARK
    sub = (155,148,172) if on_dark else (115,108,128)
    f, fs = F("black",size), F("medium",int(size*0.35))
    pw = tw(d,"PMI",f); dw = tw(d,".",f)
    x = (W - pw - dw)//2
    d.text((x,y),"PMI",font=f,fill=fg)
    d.text((x+pw,y),".",font=f,fill=PURPLE)
    smw = tw(d,"Social Manager",fs)
    d.text(((W-smw)//2, y+th(d,"PMI",f)+3),"Social Manager",font=fs,fill=sub)

# ── Checkmark ────────────────────────────────────────────────────────────────
def checkmark(d, cx, cy, r=17, color=PURPLE):
    d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=color)
    lw = max(2, r//6)
    d.line([(cx-r*0.36,cy+r*0.06),(cx-r*0.04,cy+r*0.44)], fill=WHITE, width=lw)
    d.line([(cx-r*0.04,cy+r*0.44),(cx+r*0.44,cy-r*0.32)], fill=WHITE, width=lw)

# ── Button helpers ────────────────────────────────────────────────────────────
def btn_solid_c(d, W, y, text, font, color=PURPLE, px=40, py=16):
    """Centered solid button. Returns y after button."""
    bw = tw(d,text,font)+px*2; bh = th(d,text,font)+py*2
    x = (W-bw)//2
    d.rounded_rectangle([x,y,x+bw,y+bh], radius=10, fill=color)
    d.text((x+px,y+py), text, font=font, fill=WHITE)
    return y+bh

def btn_grad_c(d, W, y, text, font, px=40, py=16):
    """Centered gradient button. Returns y after button."""
    bw = tw(d,text,font)+px*2; bh = th(d,text,font)+py*2
    x = (W-bw)//2
    grad_h(d,x,y,x+bw,y+bh, PURPLE_LT, PINK)
    d.text((x+px,y+py), text, font=font, fill=WHITE)
    return y+bh

def btn_solid_l(d, x, y, text, font, color=PURPLE, px=36, py=14):
    """Left-anchored solid button. Returns y after button."""
    bw = tw(d,text,font)+px*2; bh = th(d,text,font)+py*2
    d.rounded_rectangle([x,y,x+bw,y+bh], radius=10, fill=color)
    d.text((x+px,y+py), text, font=font, fill=WHITE)
    return y+bh


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 1 — GRATUITO · LIGHT · 1080×1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_01():
    W, H = 1080, 1080
    MG = 64  # margin

    img = Image.new("RGB",(W,H), GRAY_BG)
    d = ImageDraw.Draw(img)

    # Top bar
    grad_h(d,0,0,W,7, PURPLE_LT, PINK)

    # Subtle bg glow bottom-right
    lay = Image.new("RGBA",(W,H),(0,0,0,0))
    dl = ImageDraw.Draw(lay)
    for r in range(460,0,-20):
        a = int(16*(1-r/460)**0.8)
        dl.ellipse([W-r+80,H-r+80,W+r+80,H+r+80], fill=(*PURPLE_LT,a))
    lay = lay.filter(ImageFilter.GaussianBlur(45))
    img = img.convert("RGBA"); img.alpha_composite(lay); img = img.convert("RGB")
    d = ImageDraw.Draw(img)

    # ── Logo top-left ─────────────────────────────────────────────────────────
    logo_tl(d, MG, 36, size=38, on_dark=False)

    # ── GRATUITO badge top-right ──────────────────────────────────────────────
    f_badge = F("bold", 20)
    btext = "GRATUITO"
    bw = tw(d,btext,f_badge)+28; bh = th(d,btext,f_badge)+12
    bx = W - MG - bw; by = 40
    grad_h(d,bx,by,bx+bw,by+bh, PURPLE_LT, PINK)
    d.text((bx+14,by+6), btext, font=f_badge, fill=WHITE)

    # ── Layout: left column (text) | right column (card) ─────────────────────
    CARD_W  = 296
    card_x  = W - MG - CARD_W
    text_w_max = card_x - MG - 40

    y = 130

    # Headline
    f_h = F("black", 52)
    hl  = "Agencias que crescem sem contratar mais ninguem tem uma coisa em comum."
    y   = draw_block(d, hl, f_h, MG, y, text_w_max, TEXT_DARK, leading=1.12)
    y  += 18

    # Thin accent line
    d.rectangle([MG, y, MG+52, y+4], fill=PURPLE)
    y += 22

    # Body — 4 short punchy lines
    f_body = F("regular", 28)
    f_emph = F("bold",    28)
    body_items = [
        ("Nao e o numero de clientes.", False),
        ("Nao e o time maior.", False),
        ("E controle.", True),
    ]
    for text, emph in body_items:
        fc = PURPLE if emph else GRAY_TEXT
        ff = f_emph if emph else f_body
        d.text((MG,y), text, font=ff, fill=fc)
        y += int(28*1.5)
    y += 8

    # Secondary body
    f_b2 = F("regular", 26)
    body2 = "Relatorios que o cliente entende, conteudo no horario certo e inbox sem mensagem perdida — sem planilha, sem post-it."
    y = draw_block(d, body2, f_b2, MG, y, text_w_max, GRAY_TEXT, leading=1.55)
    y += 16

    # Sub-headline
    f_sub = F("medium", 26)
    sub = "Checklist gratuito para agencias que querem atender mais com a mesma equipe."
    y = draw_block(d, sub, f_sub, MG, y, text_w_max, TEXT_DARK, leading=1.45)
    y += 26

    # CTA button (left-anchored, concise)
    btn_solid_l(d, MG, y, "Ver onde sua agencia perde tempo  →", F("bold",24), color=PURPLE)

    # ── Right card ────────────────────────────────────────────────────────────
    items = [
        "Relatorios automaticos",
        "Agendamento inteligente",
        "Inbox unificado",
        "IA para legendas",
        "Aprovacao de conteudo",
        "Dashboard por cliente",
    ]
    ROW_H  = 62
    c_pad  = 20
    c_y    = 130
    c_h    = len(items)*ROW_H + c_pad*2

    # Card
    d.rounded_rectangle([card_x, c_y, card_x+CARD_W, c_y+c_h],
                         radius=16, fill=WHITE)
    d.rounded_rectangle([card_x, c_y, card_x+CARD_W, c_y+c_h],
                         radius=16, outline=(220,215,235), width=2)
    # Card top bar
    grad_h(d, card_x, c_y, card_x+CARD_W, c_y+6, PURPLE_LT, PINK)

    for i, item in enumerate(items):
        iy = c_y + c_pad + i*ROW_H + ROW_H//2
        checkmark(d, card_x+c_pad+17, iy, r=15, color=PURPLE)
        d.text((card_x+c_pad+42, iy-11), item, font=F("medium",20), fill=TEXT_DARK)

    img.save(f"{OUT}/peca_01.png")
    print("✓ peca_01")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 2 — PAGO A · DARK · 1080×1350
# ══════════════════════════════════════════════════════════════════════════════
def peca_02():
    W, H  = 1080, 1350
    MG    = 64
    SAFE  = H - 64  # nothing below this

    img = Image.new("RGB",(W,H), BLACK)
    img = glow(img, W//2, int(H*0.3), 560, PURPLE, opacity=0.12)
    img = grid_lines(img, PURPLE, opacity=0.045, spacing=72)
    d = ImageDraw.Draw(img)

    grad_h(d,0,0,W,6, PURPLE_LT, PINK)
    logo_tl(d, MG, 36, size=40, on_dark=True)

    # ── Dashboard mockup ──────────────────────────────────────────────────────
    mx, my = MG, 138
    mw, mh = W-MG*2, 370

    # Glow around frame
    for pw in range(3,0,-1):
        d.rounded_rectangle([mx-pw*6,my-pw*6,mx+mw+pw*6,my+mh+pw*6],
                              radius=20+pw*4, outline=(*PURPLE, 18*pw), width=2)

    d.rounded_rectangle([mx,my,mx+mw,my+mh], radius=14,
                         fill=(18,8,36), outline=(72,36,148), width=2)

    # Header bar
    grad_h(d,mx,my,mx+mw,my+44, PURPLE_LT, PINK)
    d.text((mx+16,my+11),"PMI Social Manager", font=F("bold",20), fill=WHITE)
    for i,c in enumerate([(255,80,80),(255,200,50),(60,220,90)]):
        d.ellipse([mx+mw-68+i*22,my+16,mx+mw-50+i*22,my+34], fill=c)

    # Metric cards (4 columns)
    N, cpad = 4, 8
    cw = (mw - (N+1)*cpad)//N
    ch = 82
    metrics = [("12","Contas"),("847","Posts agend."),("99%","Entrega"),("5h+","Economizado")]
    for i,(val,lbl) in enumerate(metrics):
        cx = mx+cpad+i*(cw+cpad); cy = my+54
        d.rounded_rectangle([cx,cy,cx+cw,cy+ch], radius=9, fill=MID_DARK)
        grad_h(d,cx,cy,cx+cw,cy+4, PURPLE_LT, PINK)
        d.text((cx+12,cy+10),  val, font=F("black",28), fill=WHITE)
        d.text((cx+12,cy+48),  lbl, font=F("regular",15), fill=(148,136,172))

    # Account rows
    ry0 = my+148
    for i in range(4):
        ry = ry0+i*48
        c  = lerp(PURPLE_LT, PINK, i/3)
        d.ellipse([mx+cpad,ry+5,mx+cpad+32,ry+37], fill=c)
        d.text((mx+cpad+42,ry+3),   f"@cliente_0{i+1}", font=F("medium",17), fill=WHITE)
        d.text((mx+cpad+42,ry+25),  "Ativo  ·  3 posts agendados", font=F("regular",13), fill=(128,116,152))
        d.ellipse([mx+mw-26,ry+12,mx+mw-12,ry+28], fill=(36,218,100))

    # ── Text content ──────────────────────────────────────────────────────────
    y = my + mh + 52

    # Headline (2 lines, large)
    f_h = F("black", 68)
    for line in ["Chega de gerenciar", "Instagram no grito."]:
        d.text((MG,y), line, font=f_h, fill=WHITE)
        y += int(68*1.1)
    y += 14

    # Thin accent
    d.rectangle([MG,y,MG+56,y+4], fill=PURPLE)
    y += 24

    # Body — short paragraphs, generous leading
    f_body = F("regular", 29)
    paras = [
        "Agendar post. Responder DM. Gerar relatorio. Criar legenda.",
        "Tudo isso todo dia. Pra todo cliente.",
        "O PMI reune tudo em um unico lugar — o que tomava horas passa a tomar minutos.",
    ]
    for para in paras:
        y = draw_block(d, para, f_body, MG, y, W-MG*2, GRAY_BODY, leading=1.5)
        y += 12

    y += 20
    btn_solid_l(d, MG, y, "Comece agora — teste sem risco  →", F("bold",24), color=PURPLE)

    img.save(f"{OUT}/peca_02.png")
    print("✓ peca_02")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 3 — PAGO B · DARK GRADIENT · 1080×1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_03():
    W, H = 1080, 1080
    MG   = 64

    img = Image.new("RGB",(W,H))
    d0  = ImageDraw.Draw(img)
    grad_v(d0,0,0,W,H, (14,6,30),(6,3,14))
    img = glow(img, W//2, H//2, 580, PURPLE, opacity=0.15)
    img = grid_lines(img, PURPLE, opacity=0.04, spacing=88)
    d = ImageDraw.Draw(img)

    # ── Headline ──────────────────────────────────────────────────────────────
    y = 52
    f_h = F("black", 46)
    hl  = "Quanto tempo voce perde fazendo o que a IA faria em 10 segundos?"
    y   = draw_block(d, hl, f_h, MG, y, W-MG*2, WHITE, leading=1.15, align="center", W_canvas=W)
    y  += 28

    # Thin separator
    sep_w = 60
    d.rectangle([(W-sep_w)//2, y, (W+sep_w)//2, y+4], fill=PURPLE)
    y += 22

    # ── 700+ hero ─────────────────────────────────────────────────────────────
    f_big = F("black", 200)
    num   = "700+"
    nw_   = tw(d, num, f_big)
    nh_   = th(d, num, f_big)
    nx    = (W-nw_)//2
    ny    = y

    # Glow
    img = glow(img, W//2, ny+nh_//2, 320, PURPLE, opacity=0.20)
    d   = ImageDraw.Draw(img)

    # Gradient number via tint layer
    num_lay = Image.new("RGBA",(W,H),(0,0,0,0))
    dn = ImageDraw.Draw(num_lay)
    dn.text((nx,ny), num, font=f_big, fill=(*PURPLE_LT,255))
    # colour tint mask
    tint = Image.new("RGBA",(W,H),(0,0,0,0))
    dt   = ImageDraw.Draw(tint)
    for xi in range(nx, nx+nw_):
        t = (xi-nx)/max(1,nw_)
        dt.line([(xi,ny),(xi,ny+nh_)], fill=(*lerp(PURPLE_LT,PINK,t),255))
    _,_,_,a_ch = num_lay.split()
    tint.putalpha(a_ch)
    img = img.convert("RGBA"); img.alpha_composite(tint); img = img.convert("RGB")
    d = ImageDraw.Draw(img)

    y = ny + nh_ - 16

    # Sub-label
    f_lbl = F("medium", 28)
    lbl   = "profissionais ja economizam horas por semana com o PMI"
    y     = draw_block(d, lbl, f_lbl, MG, y, W-MG*2, GRAY_BODY, leading=1.2, align="center", W_canvas=W)
    y    += 20

    # ── Avatars ───────────────────────────────────────────────────────────────
    N_av  = 8; av_r = 24; av_gap = 8
    total = N_av*(av_r*2+av_gap)-av_gap
    ax0   = (W-total)//2
    av_cy = y + av_r
    initials = list("ABCDEFGH")
    for i in range(N_av):
        ax = ax0 + i*(av_r*2+av_gap) + av_r
        c  = lerp(PURPLE_LT, PINK, i/(N_av-1))
        d.ellipse([ax-av_r-2,av_cy-av_r-2,ax+av_r+2,av_cy+av_r+2], fill=(12,6,22))
        d.ellipse([ax-av_r,  av_cy-av_r,  ax+av_r,  av_cy+av_r  ], fill=c)
        iw = tw(d,initials[i],F("bold",18)); ih = th(d,initials[i],F("bold",18))
        d.text((ax-iw//2,av_cy-ih//2-2), initials[i], font=F("bold",18), fill=WHITE)
    y = av_cy + av_r + 30

    # ── Body ──────────────────────────────────────────────────────────────────
    f_body = F("regular", 27)
    body   = "Gestores que usam o PMI criam a legenda de uma semana em menos de 5 minutos, automatizam respostas e entregam relatorios com a marca da agencia."
    y      = draw_block(d, body, f_body, MG, y, W-MG*2, GRAY_BODY, leading=1.52, align="center", W_canvas=W)
    y     += 28

    # CTA
    btn_grad_c(d, W, y, "Veja como funciona e comece hoje  →", F("bold",24))
    y += th(d,"X",F("bold",24)) + 32 + 28

    # Logo
    logo_c(d, W, y, size=34, on_dark=True)

    img.save(f"{OUT}/peca_03.png")
    print("✓ peca_03")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 4 — PAGO C · DARK · HUB · 1080×1080
# ══════════════════════════════════════════════════════════════════════════════
def peca_04():
    W, H  = 1080, 1080
    MG    = 64

    img = Image.new("RGB",(W,H), BLACK)
    img = glow(img, W//2, H//2, 520, PURPLE, opacity=0.11)
    img = grid_lines(img, PURPLE, opacity=0.045, spacing=72)
    d = ImageDraw.Draw(img)

    # ── Headline ──────────────────────────────────────────────────────────────
    y = 48
    f_h = F("black", 50)
    for line in ["Sua agencia usa uma ferramenta", "diferente pra cada coisa?"]:
        lw = tw(d,line,f_h)
        d.text(((W-lw)//2, y), line, font=f_h, fill=WHITE)
        y += int(50*1.12)
    y += 12

    # ── Hub diagram (compact, centred) ────────────────────────────────────────
    hub_cx = W//2
    hub_cy = y + 220
    hub_r  = 60
    spoke  = 180
    node_r = 48

    tool_angles = [270, 342, 54, 126, 198]
    tool_labels = [["Agendamento"], ["Inbox"], ["Relatorio"], ["Criativo"], ["Legenda","IA"]]

    for label_lines, ang in zip(tool_labels, tool_angles):
        rad = math.radians(ang)
        nx  = hub_cx + int(spoke*math.cos(rad))
        ny  = hub_cy + int(spoke*math.sin(rad))

        # Spoke (dashed)
        dx = nx-hub_cx; dy = ny-hub_cy
        length = math.sqrt(dx*dx+dy*dy)
        ux, uy = dx/length, dy/length
        pos = hub_r+6
        while pos < length-node_r-6:
            sx=hub_cx+ux*pos; sy=hub_cy+uy*pos
            ex=hub_cx+ux*(pos+12); ey=hub_cy+uy*(pos+12)
            d.line([(sx,sy),(ex,ey)], fill=(65,32,115), width=2)
            mid=pos+6; mx_=hub_cx+ux*mid; my_=hub_cy+uy*mid
            d.ellipse([mx_-4,my_-4,mx_+4,my_+4], fill=PURPLE)
            pos += 20

        # Node glow
        lay = Image.new("RGBA",(W,H),(0,0,0,0))
        dl  = ImageDraw.Draw(lay)
        for r in range(node_r+18,node_r-1,-2):
            a = int(35*(1-(r-node_r)/18))
            dl.ellipse([nx-r,ny-r,nx+r,ny+r], fill=(*PURPLE,a))
        img = img.convert("RGBA"); img.alpha_composite(lay); img = img.convert("RGB")
        d = ImageDraw.Draw(img)

        # Node
        d.ellipse([nx-node_r,ny-node_r,nx+node_r,ny+node_r],
                  fill=(20,9,42), outline=(78,38,148), width=2)
        f_nd = F("medium",18)
        for li,lt in enumerate(label_lines):
            ltw = tw(d,lt,f_nd)
            d.text((nx-ltw//2, ny-10+li*22), lt, font=f_nd, fill=GRAY_BODY)

    # Hub glow
    for r in range(hub_r+55,hub_r-1,-3):
        a = int(50*(1-(r-hub_r)/55)**1.2)
        lay2 = Image.new("RGBA",(W,H),(0,0,0,0))
        dl2  = ImageDraw.Draw(lay2)
        dl2.ellipse([hub_cx-r,hub_cy-r,hub_cx+r,hub_cy+r], fill=(*PURPLE,a))
        img = img.convert("RGBA"); img.alpha_composite(lay2); img = img.convert("RGB")
    d = ImageDraw.Draw(img)

    # Hub gradient fill
    for xi in range(hub_cx-hub_r, hub_cx+hub_r):
        t = (xi-(hub_cx-hub_r))/(hub_r*2)
        c = lerp(PURPLE_LT, PINK, t)
        hat = int(math.sqrt(max(0, hub_r**2-(xi-hub_cx)**2)))
        d.line([(xi,hub_cy-hat),(xi,hub_cy+hat)], fill=c)

    # PMI in hub
    f_hub = F("black",26)
    pw = tw(d,"PMI",f_hub); dw2 = tw(d,".",f_hub)
    d.text((hub_cx-(pw+dw2)//2, hub_cy-17),"PMI",  font=f_hub, fill=WHITE)
    d.text((hub_cx-(pw+dw2)//2+pw, hub_cy-17),".", font=f_hub, fill=(28,10,56))
    f_sm = F("medium",14)
    smw = tw(d,"Social",f_sm)
    d.text((hub_cx-smw//2, hub_cy+12),"Social", font=f_sm, fill=WHITE)

    # ── Text below hub ────────────────────────────────────────────────────────
    y_b = hub_cy + spoke + node_r + 36
    f_body = F("regular", 26)
    body   = "O plano Agency do PMI centraliza tudo — multiplos clientes, relatorios white-label, IA ilimitada e criativos para Meta Ads."
    y_b    = draw_block(d, body, f_body, MG, y_b, W-MG*2, GRAY_BODY, leading=1.5, align="center", W_canvas=W)
    y_b   += 24

    btn_solid_c(d, W, y_b, "Monte sua operacao com a gente  →", F("bold",23), color=PURPLE)
    y_b += th(d,"X",F("bold",23))+14+28+24

    logo_c(d, W, y_b, size=32, on_dark=True)

    img.save(f"{OUT}/peca_04.png")
    print("✓ peca_04")


# ══════════════════════════════════════════════════════════════════════════════
# PEÇA 5 — STORY · 1080×1920 · GRADIENT
# ══════════════════════════════════════════════════════════════════════════════
def peca_05():
    W, H = 1080, 1920
    MG   = 72

    img  = grad_diag(W, H, BLACK, (45,10,107))
    img  = glow(img, W//2, H//2, 700, PURPLE, opacity=0.12)
    img  = grid_lines(img, PURPLE, opacity=0.04, spacing=90)
    img  = vignette(img, strength=0.30)
    d    = ImageDraw.Draw(img)

    grad_h(d,0,0,W,7, PURPLE_LT, PINK)

    # Logo centered top
    logo_c(d, W, 52, size=44, on_dark=True)

    # ── Headline ──────────────────────────────────────────────────────────────
    y = 210
    f_h = F("black", 108)
    for line in ["Tudo que sua", "agencia precisa."]:
        lw = tw(d,line,f_h)
        d.text(((W-lw)//2, y), line, font=f_h, fill=WHITE)
        y += int(108*1.08)
    y += 14

    # Subtitle (2 lines, readable)
    f_sub = F("regular", 36)
    for line in ["Agendamento. IA. Relatorios. Inbox.", "Uma plataforma. Zero baguna."]:
        lw = tw(d,line,f_sub)
        d.text(((W-lw)//2, y), line, font=f_sub, fill=GRAY_BODY)
        y += int(36*1.5)
    y += 40

    # ── Phone mockup ──────────────────────────────────────────────────────────
    ph_w, ph_h = 420, 740
    ph_x = (W-ph_w)//2
    ph_y = y
    ph_r = 40

    # Phone glow
    lay = Image.new("RGBA",(W,H),(0,0,0,0))
    dl  = ImageDraw.Draw(lay)
    for rp in range(90,0,-5):
        a = int(55*(1-rp/90))
        dl.rounded_rectangle([ph_x-rp//2,ph_y-rp//2,ph_x+ph_w+rp//2,ph_y+ph_h+rp//2],
                               radius=ph_r+rp//3, outline=(*PURPLE,a), width=2)
    lay = lay.filter(ImageFilter.GaussianBlur(14))
    img = img.convert("RGBA"); img.alpha_composite(lay); img = img.convert("RGB")
    d = ImageDraw.Draw(img)

    # Phone body
    d.rounded_rectangle([ph_x,ph_y,ph_x+ph_w,ph_y+ph_h], radius=ph_r,
                         fill=(16,6,32), outline=(82,42,152), width=3)
    # Camera
    d.ellipse([ph_x+ph_w//2-12,ph_y+10,ph_x+ph_w//2+12,ph_y+30], fill=(8,4,18))

    # Screen
    sp = 14; sy0 = ph_y+sp+28
    sx0 = ph_x+sp; sw = ph_w-sp*2; sh = ph_h-sp*2-28
    grad_v(d, sx0,sy0, sx0+sw,sy0+sh, (22,8,50),(42,6,88))

    # Screen header
    grad_h(d, sx0,sy0, sx0+sw,sy0+36, PURPLE_LT, PINK)
    d.text((sx0+10,sy0+9), "PMI Social Manager", font=F("bold",13), fill=WHITE)

    # Metric mini-cards (2×2)
    mc_y = sy0+46; mc_w2 = (sw-6)//2
    for i,(val,lbl) in enumerate([("12","Contas"),("847","Posts"),("99%","Entrega"),("5h","Economizado")]):
        mx2 = sx0+(i%2)*(mc_w2+6); my2 = mc_y+(i//2)*68
        d.rounded_rectangle([mx2,my2,mx2+mc_w2,my2+60], radius=7, fill=MID_DARK)
        grad_h(d,mx2,my2,mx2+mc_w2,my2+3, PURPLE_LT, PINK)
        d.text((mx2+8,my2+7),  val, font=F("black",20), fill=WHITE)
        d.text((mx2+8,my2+34), lbl, font=F("regular",12), fill=(138,118,170))

    # Account rows
    rr_y = mc_y+148
    for i in range(4):
        ry=rr_y+i*44; c=lerp(PURPLE_LT,PINK,i/3)
        d.ellipse([sx0+4,ry,sx0+32,ry+30], fill=c)
        d.text((sx0+40,ry+2),  f"@cliente_0{i+1}", font=F("medium",13), fill=WHITE)
        d.text((sx0+40,ry+20), "3 posts agendados", font=F("regular",11), fill=(118,98,148))
        d.ellipse([sx0+sw-20,ry+8,sx0+sw-8,ry+22], fill=(30,218,95))

    # ── Content below phone ───────────────────────────────────────────────────
    y_b = ph_y + ph_h + 52

    f_tag = F("medium",32)
    tag   = "Para agencias e gestores de social media."
    lw    = tw(d,tag,f_tag)
    d.text(((W-lw)//2, y_b), tag, font=f_tag, fill=GRAY_BODY)
    y_b  += int(32*1.5) + 8

    # Feature pills (wrap to 2 rows)
    pills    = ["IA generativa", "Inbox unificado", "Relatorios white-label", "Meta Ads"]
    f_pill   = F("medium",20)
    pill_x   = MG; pill_y2 = y_b; row_h = 0
    for pill in pills:
        pw2 = tw(d,pill,f_pill)+28; ph3 = th(d,pill,f_pill)+12
        row_h = max(row_h, ph3)
        if pill_x+pw2 > W-MG: pill_x=MG; pill_y2+=row_h+10; row_h=ph3
        d.rounded_rectangle([pill_x,pill_y2,pill_x+pw2,pill_y2+ph3],
                             radius=20, outline=PURPLE, width=2, fill=(28,8,56))
        d.text((pill_x+14,pill_y2+6), pill, font=f_pill, fill=WHITE)
        pill_x += pw2+10
    y_b = pill_y2 + row_h + 36

    # CTA gradient button
    btn_grad_c(d, W, y_b, "Conheca o PMI Social Manager", F("bold",30))

    img.save(f"{OUT}/peca_05.png")
    print("✓ peca_05")


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    peca_01()
    peca_02()
    peca_03()
    peca_04()
    peca_05()
    print(f"\nAll 5 pieces → {OUT}")
