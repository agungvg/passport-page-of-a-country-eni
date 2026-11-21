#!/usr/bin/env python3
"""
The Passport Page of a Country That Isn't There
================================================
A program that draws one invented passport spread and writes it to
/output/entry.png (or ./output/entry.png when run locally).

The country: the Republic of Velmara (Lydveldid Velmara), a small
North Atlantic island republic. Capital and only deep-water port:
Ternvik. The island is reached by ferry and by a tidal causeway,
the Tidal Road, which floods at high tide; its hot springs are
taxed. The holder, Ingrid Solveig Halvorsdottir, was born in
Ternvik in 1982 and works the cod boats.

Everything on the spread agrees with everything else:
  * Passport issued 12 MAR 2024 in Ternvik, expires 12 MAR 2034.
  * Every stamp is dated after the issue date and in chronological
    order: Bergen (Norway) 28 MAY 2024, Reykjavik (Iceland)
    09 JUN 2024, Lerwick (United Kingdom) 17 SEP 2025,
    Copenhagen (Denmark) 03 FEB 2026, home to Ternvik 21 FEB 2026.
  * The machine-readable zone is built with real ICAO 9303 check
    digits, computed in code, not typed by hand.
  * The telling paperwork detail is the border-control condition
    stamp: TIDAL ROAD ONLY, no overland crossing at low tide,
    geothermal bath tax 450 kr paid.

The portrait is a photographic portrait made in-session
(portrait.jpg, shipped beside this file) and pasted in at
passport-photo size. No face is drawn in code. No network is used.
All randomness is seeded, so the output is deterministic.
"""

import math
import os
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SEED = 20261121
W, H = 1024, 724

# ---------------------------------------------------------------- palette
INK = (28, 34, 48)            # near-black document ink
INK_SOFT = (58, 64, 78)
RULE = (96, 104, 122)         # hairline rules
PAGE_L = (247, 243, 230)      # left page: warm cream
PAGE_R = (242, 238, 224)      # right page: a shade cooler/darker
DESK = (52, 56, 64)           # table the passport lies on
TEAL = (18, 74, 84)           # Velmara state teal
TEAL_DEEP = (11, 48, 58)
GOLD = (176, 138, 62)
STAMP_BLUE = (32, 66, 138)
STAMP_GREEN = (28, 96, 70)
STAMP_RED = (146, 44, 44)
STAMP_PURPLE = (104, 52, 128)
FAINT = (120, 128, 140)

HERE = Path(__file__).resolve().parent
OUT = Path("/output/entry.png")


# ---------------------------------------------------------------- fonts
def _font(names, size):
    """First available font from the candidate list, else PIL default."""
    for name in names:
        for base in ("/usr/share/fonts/truetype", "/usr/share/fonts"):
            p = Path(base) / name
            if p.exists():
                try:
                    return ImageFont.truetype(str(p), size)
                except OSError:
                    pass
    return ImageFont.load_default()


SERIF = "liberation/LiberationSerif-Regular.ttf"
SERIF_B = "liberation/LiberationSerif-Bold.ttf"
SERIF_I = "liberation/LiberationSerif-Italic.ttf"
SANS = "liberation/LiberationSans-Regular.ttf"
SANS_B = "liberation/LiberationSans-Bold.ttf"
MONO = "liberation/LiberationMono-Regular.ttf"
MONO_B = "liberation/LiberationMono-Bold.ttf"
DEJ_SERIF = "dejavu/DejaVuSerif.ttf"
DEJ_SERIF_B = "dejavu/DejaVuSerif-Bold.ttf"
DEJ_SANS = "dejavu/DejaVuSans.ttf"
DEJ_SANS_B = "dejavu/DejaVuSans-Bold.ttf"
DEJ_MONO = "dejavu/DejaVuSansMono.ttf"


def f_serif(size):
    return _font([SERIF, DEJ_SERIF], size)


def f_serif_b(size):
    return _font([SERIF_B, DEJ_SERIF_B], size)


def f_serif_i(size):
    return _font([SERIF_I, DEJ_SERIF], size)


def f_sans(size):
    return _font([SANS, DEJ_SANS], size)


def f_sans_b(size):
    return _font([SANS_B, DEJ_SANS_B], size)


def f_mono(size):
    return _font([MONO, DEJ_MONO], size)


def f_mono_b(size):
    return _font([MONO_B, DEJ_MONO], size)


def text(draw, xy, s, font, fill=INK, anchor="la"):
    draw.text(xy, s, font=font, fill=fill, anchor=anchor)


def centre(draw, cx, y, s, font, fill=INK):
    draw.text((cx, y), s, font=font, fill=fill, anchor="ma")


def rule(draw, x0, x1, y, fill=RULE, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- MRZ (ICAO 9303)
def mrz_check(s):
    vals = {c: i for i, c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
    total = 0
    for i, ch in enumerate(s):
        v = 0 if ch == "<" else vals[ch]
        total += v * (7, 3, 1)[i % 3]
    return str(total % 10)


def build_mrz():
    surname, given = "HALVORSDOTTIR", "INGRID<SOLVEIG"
    name_field = (surname + "<<" + given).ljust(39, "<")[:39]
    line1 = "P<VMR" + name_field
    assert len(line1) == 44

    doc = "VM0417826"                      # passport number
    dob, sex, exp = "820614", "F", "340312"  # 14 JUN 1982 / 12 MAR 2034
    personal = "<" * 14
    l2 = (
        doc + mrz_check(doc)
        + "VMR"
        + dob + mrz_check(dob)
        + sex
        + exp + mrz_check(exp)
        + personal + mrz_check(personal)
    )
    assert len(l2) == 43
    composite = l2[0:10] + l2[13:20] + l2[21:43]
    line2 = l2 + mrz_check(composite)
    assert len(line2) == 44
    return line1, line2


# ---------------------------------------------------------------- emblem
def draw_emblem(draw, cx, cy, r, outline=TEAL_DEEP, fill=TEAL):
    """Velmara state emblem: a ring, three sea waves, and a puffin
    head in profile. Small and flat by design: it is a printed seal,
    not a picture."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=outline, width=3)
    draw.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
                 outline=outline, width=1)
    # waves
    for k, yy in enumerate((cy + r * 0.28, cy + r * 0.48, cy + r * 0.68)):
        pts = []
        for a in range(-70, 71, 5):
            x = cx + r * 0.78 * math.sin(math.radians(a))
            y = yy + 3.5 * math.sin(math.radians(a * 3 + k * 40))
            pts.append((x, y))
        draw.line(pts, fill=fill, width=2)
    # puffin head: black cap, white cheek, orange beak
    hx, hy = cx - r * 0.18, cy - r * 0.42
    draw.ellipse([hx - 13, hy - 12, hx + 13, hy + 12], fill=(24, 26, 30))
    draw.ellipse([hx - 2, hy + 1, hx + 12, hy + 11], fill=(248, 246, 240))
    draw.polygon([(hx + 8, hy - 4), (hx + 24, hy + 1), (hx + 8, hy + 6)],
                 fill=(214, 110, 44))
    draw.ellipse([hx - 1, hy - 6, hx + 3, hy - 2], fill=(248, 246, 240))
    # tiny star above
    sx, sy = cx, cy - r - 9
    draw.polygon([(sx, sy - 5), (sx + 1.6, sy - 1.6), (sx + 5, sy),
                  (sx + 1.6, sy + 1.6), (sx, sy + 5), (sx - 1.6, sy + 1.6),
                  (sx - 5, sy), (sx - 1.6, sy - 1.6)], fill=GOLD)


# ---------------------------------------------------------------- stamps
def stamp_rect(base, box, lines, ink, angle, font_s=11, font_b=None):
    """A rectangular border-control stamp, rotated, inked translucent."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fb = font_b or f_sans_b(font_s)
    fs = f_sans(font_s)
    d.rectangle([20, 20, 20 + w, 20 + h], outline=ink + (235,), width=2)
    d.rectangle([23, 23, 20 + w - 3, 20 + h - 3], outline=ink + (200,), width=1)
    cy = 20 + 14
    for i, ln in enumerate(lines):
        f = fb if i == 0 else fs
        d.text((20 + w / 2, cy), ln, font=f, fill=ink + (235,),
               anchor="ma")
        cy += font_s + 5
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (x0 - 20, y0 - 20))


def stamp_oval(base, cx, cy, rx, ry, lines, ink, angle):
    """An oval arrival/departure stamp."""
    layer = Image.new("RGBA", (rx * 2 + 60, ry * 2 + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = 30, 30
    d.ellipse([ox, oy, ox + 2 * rx, oy + 2 * ry], outline=ink + (235,),
              width=2)
    d.ellipse([ox + 5, oy + 5, ox + 2 * rx - 5, oy + 2 * ry - 5],
              outline=ink + (190,), width=1)
    fb, fs = f_sans_b(11), f_sans(10)
    y = oy + 16
    for i, ln in enumerate(lines):
        f = fb if i in (0, 1) else fs
        d.text((ox + rx, y), ln, font=f, fill=ink + (235,), anchor="ma")
        y += 14
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (cx - rx - 30, cy - ry - 30))


# ---------------------------------------------------------------- guilloche
def guilloche(base, box, rng, colour, step=24, alpha=12):
    """Faint security wave lines across a page, seeded so the
    render is identical on every run. Drawn on a separate layer
    and alpha-composited: ImageDraw on an RGBA canvas *replaces*
    pixels instead of blending, so drawing the lines directly
    would print them at full strength. Kept barely visible: a
    real passport's guilloche is a whisper, not lined paper."""
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(y0 + 6, y1 - 4, step):
        pts = []
        ph = rng.uniform(0, 6.28)
        for x in range(x0, x1 + 1, 8):
            yy = y + 1.0 * math.sin(x / 52.0 + ph)
            pts.append((x, yy))
        d.line(pts, fill=colour + (alpha,), width=1)
    base.alpha_composite(layer)


# ---------------------------------------------------------------- build
def build():
    rng = random.Random(SEED)
    img = Image.new("RGB", (W, H), DESK)
    draw = ImageDraw.Draw(img)

    # desk vignette: soft dark corners so the spread sits on a table
    for i in range(60):
        a = 200 - i * 3
        draw.rectangle([i, i, W - 1 - i, H - 1 - i],
                       outline=(52 - i // 6, 56 - i // 6, 64 - i // 6))

    # ---- page geometry: an open spread, left = data page, right = visas
    # NOTE: from here on, EVERYTHING is drawn on one RGBA canvas
    # (`base`). Re-converting to RGB mid-build would silently discard
    # everything drawn since the last conversion.
    lx0, ly0, lx1, ly1 = 24, 20, 502, 704
    rx0, ry0, rx1, ry1 = 522, 20, 1000, 704
    base = img.convert("RGBA")
    draw = ImageDraw.Draw(base)
    draw.rectangle([lx0 - 3, ly0 - 3, lx1 + 3, ly1 + 3], fill=(30, 32, 38, 255))
    draw.rectangle([rx0 - 3, ry0 - 3, rx1 + 3, ry1 + 3], fill=(30, 32, 38, 255))
    draw.rectangle([lx0, ly0, lx1, ly1], fill=PAGE_L + (255,))
    draw.rectangle([rx0, ry0, rx1, ry1], fill=PAGE_R + (255,))
    # centre gutter shadow
    for i in range(10):
        draw.line([(lx1 + i, ly0), (lx1 + i, ly1)],
                  fill=(214 - i * 4, 210 - i * 4, 196 - i * 4, 255))
        draw.line([(rx0 - i, ry0), (rx0 - i, ry1)],
                  fill=(214 - i * 4, 210 - i * 4, 196 - i * 4, 255))

    guilloche(base, (lx0 + 8, ly0 + 8, lx1 - 8, ly1 - 8), rng, (70, 96, 110))
    guilloche(base, (rx0 + 8, ry0 + 8, rx1 - 8, ry1 - 8), rng, (70, 96, 110))

    # ================= LEFT PAGE: data page =================
    # header: emblem + country name, bilingual
    draw_emblem(draw, lx0 + 52, ly0 + 52, 30)
    centre(draw, lx0 + 268, ly0 + 22, "REPUBLIC OF VELMARA",
           f_serif_b(25), TEAL_DEEP)
    centre(draw, lx0 + 268, ly0 + 52, "Lýðveldið Velmara  ·  PASSPORT — VEGABRÉF",
           f_serif(12), INK_SOFT)
    rule(draw, lx0 + 22, lx1 - 22, ly0 + 86, fill=TEAL, width=2)
    rule(draw, lx0 + 22, lx1 - 22, ly0 + 90, fill=GOLD, width=1)

    # ---- portrait (photographic, shipped with the program)
    px0, py0, px1, py1 = lx0 + 30, ly0 + 108, lx0 + 178, ly0 + 302
    photo = Image.open(HERE / "portrait.jpg").convert("RGB")
    photo = photo.resize((px1 - px0, py1 - py0), Image.LANCZOS)
    base.paste(photo, (px0, py0))
    draw.rectangle([px0, py0, px1, py1], outline=INK + (255,), width=2)
    # photo caption + holder signature under the photo
    centre(draw, (px0 + px1) // 2, py1 + 8, "PHOTOGRAPH — MYND",
           f_sans(9), FAINT)
    centre(draw, (px0 + px1) // 2, py1 + 26, "Ingrid Sólveig",
           f_serif_i(17), INK)
    rule(draw, px0 + 8, px1 - 8, py1 + 48, fill=RULE)
    centre(draw, (px0 + px1) // 2, py1 + 54, "HOLDER'S SIGNATURE",
           f_sans(8), FAINT)

    # ---- personal data, two columns right of the photo
    fx = lx0 + 198
    fw = lx1 - 22 - fx
    rows = [
        ("TYPE / TEGUND", "P", "CODE / KÓÐI", "VMR"),
        ("PASSPORT No. / VEGABRÉFSNÚMER", "VM 0417826", None, None),
        ("SURNAME / EFTIRNAFN", "HALVORSDÓTTIR", None, None),
        ("GIVEN NAMES / FORNÖFN", "INGRID SÓLVEIG", None, None),
        ("NATIONALITY / ÞJÓÐERNI", "VELMARAN", "SEX / KYN", "F"),
        ("DATE OF BIRTH / FÆÐINGARDAGUR", "14 JUN 1982", None, None),
        ("PLACE OF BIRTH / FÆÐINGARSTAÐUR", "TERNVIK, VELMARA", None, None),
        ("DATE OF ISSUE / ÚTGÁFUDAGUR", "12 MAR 2024", None, None),
        ("DATE OF EXPIRY / GILDISTÍMI", "12 MAR 2034", None, None),
        ("AUTHORITY / ÚTGÁFUSTOFNUN", "TERNVIK PASSPORT OFFICE", None, None),
    ]
    y = ly0 + 104
    for lab, val, lab2, val2 in rows:
        text(draw, (fx, y), lab, f_sans(8), FAINT)
        if lab2:
            text(draw, (fx + 168, y), lab2, f_sans(8), FAINT)
        y += 12
        text(draw, (fx, y), val, f_serif_b(15), INK)
        if val2:
            text(draw, (fx + 168, y), val2, f_serif_b(15), INK)
        y += 21
        rule(draw, fx, fx + fw, y - 4, fill=(196, 190, 172))
    # personal number line under the data block
    text(draw, (fx, y + 2), "PERSONAL No. / KENNITALA", f_sans(8), FAINT)
    text(draw, (fx, y + 13), "140682 — 0417", f_serif_b(14), INK)
    text(draw, (fx + 168, y + 2), "HEIGHT / HÆÐ", f_sans(8), FAINT)
    text(draw, (fx + 168, y + 13), "171 cm", f_serif_b(14), INK)
    y += 40
    text(draw, (fx, y), "OCCUPATION / STARF", f_sans(8), FAINT)
    text(draw, (fx, y + 11), "COD BOAT SKIPPER — FV SKARVEN",
         f_serif_b(14), INK)

    # ---- machine-readable zone
    mz_y = ly1 - 78
    draw.rectangle([lx0 + 14, mz_y - 10, lx1 - 14, ly1 - 12], fill=(238, 234, 220))
    rule(draw, lx0 + 14, lx1 - 14, mz_y - 10, fill=RULE)
    l1, l2 = build_mrz()
    text(draw, (lx0 + 24, mz_y + 2), l1, f_mono(13), INK)
    text(draw, (lx0 + 24, mz_y + 24), l2, f_mono(13), INK)
    text(draw, (lx0 + 24, mz_y + 46), "MACHINE-READABLE ZONE — DO NOT FOLD",
         f_sans(7), FAINT)
    text(draw, (lx1 - 24, mz_y + 46), "PAGE 2 — SÍÐA 2",
         f_sans(7), FAINT, anchor="ra")

    # ================= RIGHT PAGE: visas & stamps =================
    centre(draw, (rx0 + rx1) // 2, ry0 + 20, "VISAS",
           f_serif_b(20), TEAL_DEEP)
    centre(draw, (rx0 + rx1) // 2, ry0 + 46,
           "VEGABRÉF — ENTRIES, EXITS AND CONDITIONS OF STAY",
           f_sans(9), INK_SOFT)
    rule(draw, rx0 + 22, rx1 - 22, ry0 + 68, fill=TEAL, width=2)
    text(draw, (rx1 - 22, ry0 + 76), "PAGE 12 — SÍÐA 12",
         f_sans(8), FAINT, anchor="ra")

    # travel history, every stamp after the 12 MAR 2024 issue date,
    # in chronological order, each a real neighbouring port.
    stamp_oval(base, rx0 + 118, ry0 + 168, 92, 46,
               ["BERGEN", "NORWAY — NORGE", "ARRIVAL  28 MAY 2024",
                "PORT OF BERGEN"],
               STAMP_BLUE, -7)
    stamp_rect(base, (rx0 + 268, ry0 + 108, rx0 + 428, ry0 + 168),
               ["VELMARA — TERNVIK", "DEPARTURE  28 MAY 2024",
                "FERRY MV SÆTERN"],
               STAMP_BLUE, 6)
    stamp_oval(base, rx0 + 118, ry0 + 292, 92, 46,
               ["REYKJAVIK", "ICELAND — ÍSLAND", "ARRIVAL  09 JUN 2024",
                "KEFLAVÍK AIRPORT"],
               STAMP_GREEN, 8)
    stamp_rect(base, (rx0 + 268, ry0 + 238, rx0 + 428, ry0 + 298),
               ["UNITED KINGDOM", "LERWICK — SHETLAND",
                "ARRIVAL  17 SEP 2025"],
               STAMP_RED, -6)
    stamp_oval(base, rx0 + 118, ry0 + 420, 92, 46,
               ["COPENHAGEN", "DENMARK — DANMARK", "ARRIVAL  03 FEB 2026",
                "KASTRUP AIRPORT"],
               STAMP_BLUE, -9)
    stamp_rect(base, (rx0 + 268, ry0 + 366, rx0 + 428, ry0 + 426),
               ["VELMARA — TERNVIK", "ARRIVAL  21 FEB 2026",
                "FERRY MV SÆTERN"],
               STAMP_GREEN, 5)

    # handwritten-style border note, in ink, beside the stamps
    note = Image.new("RGBA", (430, 60), (0, 0, 0, 0))
    nd = ImageDraw.Draw(note)
    nd.text((6, 6), "Seen at Ternvik — home again, 21 Feb 2026.",
            font=f_serif_i(15), fill=(28, 58, 128, 235))
    nd.text((6, 30), "Cod season opens 1 April. — H.",
            font=f_serif_i(15), fill=(28, 58, 128, 235))
    note = note.rotate(-2, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(note, (rx0 + 30, ry0 + 470))

    # ---- the telling detail: the condition stamp (purple, boxed)
    cx0, cy0, cx1, cy1 = rx0 + 30, ry0 + 540, rx1 - 30, ry1 - 66
    cond = Image.new("RGBA", (cx1 - cx0 + 40, cy1 - cy0 + 40), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cond)
    cd.rectangle([20, 20, cx1 - cx0 + 20, cy1 - cy0 + 20],
                 outline=STAMP_PURPLE + (240,), width=3)
    cd.rectangle([25, 25, cx1 - cx0 + 15, cy1 - cy0 + 15],
                 outline=STAMP_PURPLE + (200,), width=1)
    cd.text((20 + (cx1 - cx0) // 2, 34),
            "CONDITION OF ENTRY — VELMARA", font=f_sans_b(13),
            fill=STAMP_PURPLE + (245,), anchor="ma")
    cd.text((20 + (cx1 - cx0) // 2, 56),
            "TIDAL ROAD ONLY — NO OVERLAND CROSSING AT LOW TIDE",
            font=f_sans_b(11), fill=STAMP_PURPLE + (245,), anchor="ma")
    cd.text((20 + (cx1 - cx0) // 2, 76),
            "GEOTHERMAL BATH TAX 450 KR PAID  ·  TERNVIK BORDER OFFICE",
            font=f_sans(11), fill=STAMP_PURPLE + (245,), anchor="ma")
    cond = cond.rotate(-1.5, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(cond, (cx0 - 20, cy0 - 20))

    # footer line under the condition box, small and factual
    centre(draw, (rx0 + rx1) // 2, ry1 - 52,
           "This passport remains the property of the Republic of Velmara.",
           f_serif_i(11), INK_SOFT)
    centre(draw, (rx0 + rx1) // 2, ry1 - 34,
           "Lost or found, return to any Velmaran consulate or to Ternvik Harbour Office.",
           f_sans(9), FAINT)

    return base.convert("RGB")


def main():
    img = build()
    out = OUT if Path("/output").is_dir() else Path("output/entry.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    size = out.stat().st_size
    print(f"wrote {out}  {img.size[0]}x{img.size[1]}  {size} bytes")
    assert img.size[0] <= 1024 and img.size[1] <= 1024, "too large"
    assert size <= 1_048_576, "over 1 MiB"


if __name__ == "__main__":
    main()
