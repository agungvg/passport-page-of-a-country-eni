#!/usr/bin/env python3
"""
The Passport Page of a Country That Isn't There
================================================
Draws one invented passport spread and writes it to /output/entry.png
(or ./output/entry.png when run locally).

The country: the Republic of Velmara (Lýðveldið Velmara), a small
North Atlantic island republic. Capital and only deep-water port:
Ternvik. The island is reached by ferry and by a tidal causeway,
the Tidal Road, which floods at high tide; its hot springs are
taxed at the border. The holder, Ingrid Sólveig Halvorsdóttir,
born 14 June 1982 in Ternvik, is a cod boat captain.

Everything on the spread agrees with everything else:
  * Passport VM 0417826, issued 12 MAR 2024 in Ternvik,
    expiring 12 MAR 2034.
  * Six stamps, all dated after the issue date and in
    chronological order: Bergen 28 MAY 2024, Reykjavik
    09 JUN 2024, Lerwick 17 SEP 2025, Tórshavn 30 OCT 2025,
    Copenhagen 03 FEB 2026, and the return home to Ternvik
    21 FEB 2026 on the ferry MV Sætern.
  * The machine-readable zone is built with real ICAO 9303
    check digits, computed in code and self-checked.
  * The telling paperwork detail is the purple border-control
    condition stamp: TIDAL ROAD ONLY, no overland crossing
    at low tide, geothermal bath tax 450 kr paid.

The portrait is a photographic portrait made in-session
(portrait.jpg, shipped beside this file) and pasted in at
passport-photo size. No face is drawn in code. No network
is used. All randomness is seeded, so two runs produce the
same file byte for byte.
"""

import hashlib
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SEED = 20261121
W, H = 1024, 724

# ---------------------------------------------------------------- palette
INK = (30, 36, 50)             # near-black document ink
INK_SOFT = (62, 68, 82)
RULE = (98, 106, 124)          # hairline rules
PAGE_L = (248, 244, 231)       # left page: warm cream
PAGE_R = (243, 239, 225)       # right page: a shade cooler
DESK = (54, 58, 66)            # table the passport lies on
TEAL = (18, 74, 84)            # Velmara state teal
TEAL_DEEP = (11, 48, 58)
TEAL_FAINT = (218, 226, 222)   # guilloche wash
GOLD = (176, 138, 62)
BLUE = (32, 66, 138)
GREEN = (28, 96, 70)
RED = (146, 44, 44)
PURPLE = (104, 52, 128)
FAINT = (122, 130, 142)

HERE = Path(__file__).resolve().parent
OUT = Path("/output/entry.png") if Path("/output").is_dir() else HERE / "output" / "entry.png"

FONT_DIR = Path("/usr/share/fonts/truetype")


def font(name, size):
    """First usable font from the candidate list, else PIL default."""
    for cand in (FONT_DIR / name,):
        if cand.exists():
            try:
                return ImageFont.truetype(str(cand), size)
            except OSError:
                pass
    return ImageFont.load_default()


SERIF = "liberation/LiberationSerif-Regular.ttf"
SERIF_B = "liberation/LiberationSerif-Bold.ttf"
SERIF_I = "liberation/LiberationSerif-Italic.ttf"
SANS = "liberation/LiberationSans-Regular.ttf"
SANS_B = "liberation/LiberationSans-Bold.ttf"
MONO_B = "dejavu/DejaVuSansMono-Bold.ttf"

rng = random.Random(SEED)


# ---------------------------------------------------------------- ICAO 9303
def _val(ch):
    if ch.isdigit():
        return int(ch)
    if ch == "<":
        return 0
    return ord(ch) - ord("A") + 10


def check_digit(field):
    """ICAO 9303 check digit: weights 7, 3, 1 repeating."""
    total = 0
    for i, ch in enumerate(field):
        total += _val(ch) * (7, 3, 1)[i % 3]
    return str(total % 10)


def transliterate(text):
    """ICAO transliteration for the MRZ (Latin letters only)."""
    table = {
        "Á": "A", "À": "A", "Ä": "A", "Å": "A", "Æ": "AE",
        "É": "E", "È": "E", "Ë": "E", "Í": "I", "Ì": "I",
        "Ó": "O", "Ò": "O", "Ö": "O", "Ø": "O", "Ú": "U",
        "Ù": "U", "Ü": "U", "Ý": "Y", "Ð": "D", "Þ": "TH",
        "Ñ": "N", "Ç": "C", "Š": "S", "Ž": "Z", "Č": "C",
    }
    return "".join(table.get(c, c) for c in text.upper())


def build_mrz():
    """Two 44-character MRZ lines with computed check digits."""
    surname = transliterate("HALVORSDÓTTIR")
    given = transliterate("INGRID SÓLVEIG").replace(" ", "<")
    line1 = ("P<VLM" + surname + "<<" + given).ljust(44, "<")[:44]

    doc = "VM0417826"
    dob = "820614"          # 14 JUN 1982
    expiry = "340312"       # 12 MAR 2034
    personal = "<" * 14
    personal_cd = check_digit(personal)
    composite = (
        doc + check_digit(doc) + dob + check_digit(dob)
        + expiry + check_digit(expiry) + personal + personal_cd
    )
    line2 = (
        doc + check_digit(doc) + "VLM" + dob + check_digit(dob)
        + "F" + expiry + check_digit(expiry) + personal + personal_cd
        + check_digit(composite)
    )
    assert len(line1) == 44 and len(line2) == 44
    # Self-check: every embedded check digit verifies.
    assert check_digit(doc) == line2[9]
    assert check_digit(dob) == line2[19]
    assert check_digit(expiry) == line2[27]
    assert check_digit(personal) == line2[42]
    assert check_digit(composite) == line2[43]
    return line1, line2


# ---------------------------------------------------------------- helpers
def text(draw, xy, s, fnt, fill=INK, anchor="la"):
    if isinstance(fnt, tuple):
        fnt = font(*fnt)
    draw.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def centred(draw, cx, y, s, fnt, fill=INK):
    if isinstance(fnt, tuple):
        fnt = font(*fnt)
    draw.text((cx, y), s, font=fnt, fill=fill, anchor="ma")


def label_value(draw, x, y, label, value, vsize=15, label_size=8):
    """A small-caps grey label over a serif value, with a hairline."""
    text(draw, (x, y), label, (SANS_B, label_size), fill=FAINT)
    text(draw, (x, y + 11), value, (SERIF, vsize), fill=INK)
    return y + 11 + vsize + 6


def rotated_stamp(base, box, angle, draw_fn):
    """Draw a stamp on its own layer, rotate it a touch, paste it."""
    w, h = box[2] - box[0], box[3] - box[1]
    layer = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d, 12, 12, w, h)
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (box[0] - 12, box[1] - 12))


def puffin(draw, cx, cy, s, ink=TEAL_DEEP, beak=(214, 110, 44)):
    """Stylised puffin emblem: dark body, white cheek, orange beak."""
    # body
    draw.ellipse([cx - 0.42 * s, cy - 0.55 * s, cx + 0.42 * s, cy + 0.55 * s], fill=ink)
    # white breast
    draw.ellipse([cx - 0.30 * s, cy - 0.05 * s, cx + 0.30 * s, cy + 0.52 * s], fill=(250, 248, 242))
    # white cheek
    draw.ellipse([cx - 0.34 * s, cy - 0.48 * s, cx + 0.02 * s, cy - 0.08 * s], fill=(250, 248, 242))
    # eye
    draw.ellipse([cx - 0.10 * s, cy - 0.36 * s, cx - 0.01 * s, cy - 0.27 * s], fill=ink)
    # beak: orange triangle pointing right
    draw.polygon(
        [(cx + 0.02 * s, cy - 0.44 * s), (cx + 0.52 * s, cy - 0.28 * s), (cx + 0.02 * s, cy - 0.14 * s)],
        fill=beak,
    )
    # feet
    draw.line([cx - 0.16 * s, cy + 0.55 * s, cx - 0.16 * s, cy + 0.68 * s], fill=beak, width=max(2, int(s * 0.05)))
    draw.line([cx + 0.16 * s, cy + 0.55 * s, cx + 0.16 * s, cy + 0.68 * s], fill=beak, width=max(2, int(s * 0.05)))
    # three waves below
    for i in range(3):
        y = cy + (0.82 + i * 0.16) * s
        draw.arc([cx - 0.55 * s, y - 0.10 * s, cx + 0.55 * s, y + 0.10 * s],
                 start=200, end=340, fill=TEAL, width=max(2, int(s * 0.045)))


def guilloche(draw, x0, y0, x1, y1, cx, cy):
    """Faint concentric arcs, a security-print wash low on the page."""
    for r in range(80, 430, 34):
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=195, end=345,
                 fill=TEAL_FAINT, width=1)


# ---------------------------------------------------------------- left page
def draw_left(base, x0, y0, x1, y1):
    page = Image.new("RGBA", (x1 - x0, y1 - y0), PAGE_L + (255,))
    d = ImageDraw.Draw(page)
    w, h = x1 - x0, y1 - y0

    guilloche(d, 0, 0, w, h, w // 2, h + 80)

    # header: emblem + state name
    puffin(d, w // 2, 52, 34)
    centred(d, w // 2, 108, "REPUBLIC OF VELMARA", (SERIF_B, 17), fill=TEAL_DEEP)
    centred(d, w // 2, 128, "L Ý Ð V E L D I Ð   V E L M A R A", (SANS, 8), fill=INK_SOFT)
    d.line([52, 152, w - 52, 152], fill=RULE, width=1)
    centred(d, w // 2, 158, "P A S S P O R T", (SERIF_B, 14), fill=INK)
    centred(d, w // 2, 176, "VEGABRÉF", (SANS, 8), fill=INK_SOFT)

    # portrait, left, with a thin frame
    photo = Image.open(HERE / "portrait.jpg").convert("RGB")
    pw, ph = 148, 196
    # centre-crop to 3:4
    tw, th = photo.size
    target = 3 / 4
    if tw / th > target:
        nw = int(th * target)
        photo = photo.crop(((tw - nw) // 2, 0, (tw + nw) // 2, th))
    else:
        nh = int(tw / target)
        photo = photo.crop((0, (th - nh) // 2, tw, (th + nh) // 2))
    photo = photo.resize((pw, ph), Image.LANCZOS)
    page.paste(photo, (44, 202))
    d.rectangle([44, 202, 44 + pw, 202 + ph], outline=INK, width=1)
    # signature under the portrait
    d.line([44, 428, 44 + pw, 428], fill=RULE, width=1)
    centred(d, 44 + pw // 2, 432, "Ingrid Halvorsdóttir", (SERIF_I, 12), fill=INK_SOFT)
    centred(d, 44 + pw // 2, 448, "HOLDER'S SIGNATURE", (SANS, 7), fill=FAINT)

    # data fields, right of the portrait
    fx = 214
    y = 200
    y = label_value(d, fx, y, "TYPE / GERÐ", "P")
    y = label_value(d, fx + 62, 200, "CODE / LAND", "VLM")
    y = label_value(d, fx + 132, 200, "PASSPORT No.", "VM 0417826", vsize=14)
    y = 252
    y = label_value(d, fx, y, "SURNAME / EFTIRNAFN", "HALVORSDÓTTIR")
    y = label_value(d, fx, y, "GIVEN NAMES / FORNÖFN", "Ingrid Sólveig")
    y = label_value(d, fx, y, "NATIONALITY / ÞJÓÐERNI", "VELMARAN")
    y = label_value(d, fx, y, "DATE OF BIRTH / FÆÐINGARDAGUR", "14 JUN 1982")
    y = label_value(d, fx, y, "PLACE OF BIRTH / FÆÐINGARSTAÐUR", "Ternvik, Velmara")
    y = label_value(d, fx, y, "SEX / KYN", "F")
    y = label_value(d, fx, y, "DATE OF ISSUE / ÚTGÁFUDAGUR", "12 MAR 2024")
    y = label_value(d, fx, y, "DATE OF EXPIRY / GILDISTÍMI", "12 MAR 2034")
    y = label_value(d, fx, y, "AUTHORITY / ÚTGEFANDI", "Harbour Office, Ternvik")

    # MRZ
    line1, line2 = build_mrz()
    d.rectangle([30, h - 74, w - 30, h - 24], fill=(238, 234, 220))
    text(d, (40, h - 68), line1, (MONO_B, 13), fill=INK)
    text(d, (40, h - 50), line2, (MONO_B, 13), fill=INK)
    centred(d, w // 2, h - 18, "12", (SANS, 8), fill=FAINT)

    base.alpha_composite(page, (x0, y0))


# ---------------------------------------------------------------- right page
def rect_stamp(d, x, y, w, h, color, city, country, date, kind, code):
    d.rectangle([x, y, x + w, y + h], outline=color, width=2)
    d.rectangle([x + 4, y + 4, x + w - 4, y + h - 4], outline=color, width=1)
    centred(d, x + w // 2, y + 10, city, (SANS_B, 11), fill=color)
    centred(d, x + w // 2, y + 26, country, (SANS, 8), fill=color)
    d.line([x + 14, y + 40, x + w - 14, y + 40], fill=color, width=1)
    centred(d, x + w // 2, y + 46, date, (SANS_B, 11), fill=color)
    centred(d, x + w // 2, y + 62, kind, (SANS, 8), fill=color)
    centred(d, x + w // 2, y + 74, code, (SANS, 7), fill=color)


def oval_stamp(d, x, y, w, h, color, city, country, date, kind, code):
    d.ellipse([x, y, x + w, y + h], outline=color, width=2)
    d.ellipse([x + 5, y + 5, x + w - 5, y + h - 5], outline=color, width=1)
    centred(d, x + w // 2, y + 12, city, (SANS_B, 10), fill=color)
    centred(d, x + w // 2, y + 27, country, (SANS, 8), fill=color)
    d.line([x + 22, y + 41, x + w - 22, y + 41], fill=color, width=1)
    centred(d, x + w // 2, y + 46, date, (SANS_B, 11), fill=color)
    centred(d, x + w // 2, y + 62, kind, (SANS, 8), fill=color)
    centred(d, x + w // 2, y + 73, code, (SANS, 7), fill=color)


def circle_stamp(d, cx, cy, r, color, top, mid, bottom):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], outline=color, width=1)
    centred(d, cx, cy - 26, top, (SANS_B, 10), fill=color)
    centred(d, cx, cy - 8, mid, (SANS_B, 9), fill=color)
    centred(d, cx, cy + 10, bottom, (SANS, 8), fill=color)
    d.ellipse([cx - 3, cy + 26, cx + 3, cy + 32], fill=color)


def draw_right(base, x0, y0, x1, y1):
    page = Image.new("RGBA", (x1 - x0, y1 - y0), PAGE_R + (255,))
    d = ImageDraw.Draw(page)
    w, h = x1 - x0, y1 - y0

    centred(d, w // 2, 26, "V I S A S", (SERIF_B, 14), fill=INK)
    centred(d, w // 2, 44, "VISA  ·  ÁRITANIR", (SANS, 8), fill=INK_SOFT)
    d.line([52, 62, w - 52, 62], fill=RULE, width=1)

    # six stamps, 2 columns x 3 rows, chronological, all after issue
    stamps = [
        ("rect", BLUE, "BERGEN", "NORWAY", "28 MAY 2024", "ENTRY", "NO-0147"),
        ("oval", GREEN, "REYKJAVIK", "ICELAND", "09 JUN 2024", "ENTRY", "IS-0221"),
        ("oval", BLUE, "LERWICK", "SHETLAND", "17 SEP 2025", "ENTRY", "UK-0918"),
        ("rect", RED, "TÓRSHAVN", "FAROE ISLANDS", "30 OCT 2025", "EXIT", "FO-0330"),
        ("rect", GREEN, "COPENHAGEN", "DENMARK", "03 FEB 2026", "ENTRY", "DK-0104"),
        ("rect", TEAL, "TERNVIK", "VELMARA", "21 FEB 2026", "RETURN · MV SÆTERN", "VM-HOME"),
    ]
    sw, sh = 196, 92
    gx0, gy0 = 34, 82
    dx, dy = 216, 108
    for i, (shape, color, city, country, date, kind, code) in enumerate(stamps):
        col, row = i % 2, i // 2
        bx = gx0 + col * dx
        by = gy0 + row * dy
        angle = rng.uniform(-2.2, 2.2)

        def _draw(dd, ox, oy, ww, hh, _s=(shape, color, city, country, date, kind, code)):
            sh_, col_, ci_, co_, da_, ki_, cd_ = _s
            if sh_ == "rect":
                rect_stamp(dd, ox, oy, ww, hh, col_, ci_, co_, da_, ki_, cd_)
            else:
                oval_stamp(dd, ox, oy, ww, hh, col_, ci_, co_, da_, ki_, cd_)

        rotated_stamp(page, (bx, by, bx + sw, by + sh), angle, _draw)

    # the telling detail: the purple condition stamp
    cy0 = gy0 + 3 * dy + 8
    box = (34, cy0, w - 34, cy0 + 118)

    def _purple(dd, ox, oy, ww, hh):
        dd.rectangle([ox, oy, ox + ww, oy + hh], outline=PURPLE, width=3)
        dd.rectangle([ox + 5, oy + 5, ox + ww - 5, oy + hh - 5], outline=PURPLE, width=1)
        centred(dd, ox + ww // 2, oy + 10, "VELMARA BORDER CONTROL — CONDITION OF ENTRY",
                (SANS_B, 9), fill=PURPLE)
        centred(dd, ox + ww // 2, oy + 30, "TIDAL ROAD ONLY", (SANS_B, 15), fill=PURPLE)
        centred(dd, ox + ww // 2, oy + 50, "NO OVERLAND CROSSING AT LOW TIDE",
                (SANS_B, 11), fill=PURPLE)
        centred(dd, ox + ww // 2, oy + 68, "GEOTHERMAL BATH TAX 450 KR PAID",
                (SANS_B, 11), fill=PURPLE)
        centred(dd, ox + ww // 2, oy + 88, "FERRY MV SÆTERN · TERNVIK HARBOUR",
                (SANS, 8), fill=PURPLE)

    rotated_stamp(page, box, -2.0, _purple)

    # circular harbour stamp, bottom right, overlapping the corner
    circle_stamp(d, w - 78, h - 78, 46, TEAL, "TERNVIK", "21 FEB 2026", "HARBOUR")
    centred(d, w // 2, h - 18, "13", (SANS, 8), fill=FAINT)

    base.alpha_composite(page, (x0, y0))


# ---------------------------------------------------------------- spread
def main():
    img = Image.new("RGBA", (W, H), DESK + (255,))
    d = ImageDraw.Draw(img)

    # soft vignette on the desk
    for i in range(40):
        a = 10 - i // 4
        d.rectangle([i, i, W - 1 - i, H - 1 - i], outline=(0, 0, 0, max(0, a)))

    margin = 26
    gutter = 10
    page_w = (W - 2 * margin - gutter) // 2
    page_h = H - 2 * margin
    lx0, ly0 = margin, margin
    lx1, ly1 = lx0 + page_w, ly0 + page_h
    rx0, ry0 = lx1 + gutter, margin
    rx1, ry1 = rx0 + page_w, ly0 + page_h

    # page drop shadows
    for (x0, y0, x1, y1) in ((lx0, ly0, lx1, ly1), (rx0, ry0, rx1, ry1)):
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rectangle([x0 + 4, y0 + 5, x1 + 4, y1 + 5], fill=(0, 0, 0, 90))
        img.alpha_composite(sh)

    # centre gutter shadow
    gutter_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gutter_layer)
    for i in range(gutter):
        alpha = 46 - abs(i - gutter // 2) * 8
        gd.line([lx1 + i, ly0, lx1 + i, ly1], fill=(0, 0, 0, max(0, alpha)), width=1)
    img.alpha_composite(gutter_layer)

    draw_left(img, lx0, ly0, lx1, ly1)
    draw_right(img, rx0, ry0, rx1, ry1)

    rgb = img.convert("RGB")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(OUT, format="PNG", optimize=True)
    data = OUT.read_bytes()
    print(f"wrote {OUT} {rgb.size[0]}x{rgb.size[1]} {len(data)} bytes "
          f"sha256={hashlib.sha256(data).hexdigest()[:16]}")


if __name__ == "__main__":
    sys.exit(main())
