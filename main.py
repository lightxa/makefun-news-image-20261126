#!/usr/bin/env python3
"""news-image-20261126: draws one front page summing up the world news of
Thursday 26 November 2026 and writes it to /output/entry.png.

Pure standard library. Deterministic: both runs write byte-identical PNGs.
No network at runtime. The image is drawn pixel by pixel with a small
built-in 5x7 bitmap font; nothing is copied in from any other file.

Every story on the page happened, or was first reported, on 26 November
2026: the Kim nuclear report (KCNA, Thursday), Thanksgiving Day in the
United States, the EU special summit and ECB minutes in Brussels, the
Bank of Korea rate decision, the Zootopia 2 cinema opening, India
marking Constitution Day and 18 years since the 26/11 Mumbai attacks,
and the Europa League night. Seven stories, three regions.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- PNG output

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(pixels):
    """pixels: list of H rows, each a bytearray of W*3 RGB bytes."""
    raw = b"".join(b"\x00" + bytes(row) for row in pixels)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw, 6))
        + _chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits, most significant bit on the left.

FONT = {
    "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    "C": [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    "D": [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    "G": [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "I": [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    "M": [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "P": [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    "Q": [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
    "X": [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "2": [0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F],
    "3": [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    "6": [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    "7": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    " ": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    ".": [0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C],
    ",": [0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08],
    ":": [0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00],
    "'": [0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00],
    "-": [0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00],
    "!": [0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04],
    "?": [0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04],
    "%": [0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13],
    "/": [0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10],
    "(": [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ")": [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    "&": [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    "+": [0x00, 0x04, 0x04, 0x0E, 0x04, 0x04, 0x00],
    "$": [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
    "*": [0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00],
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


class Canvas:
    def __init__(self):
        self.px = [bytearray(W * 3) for _ in range(H)]

    def fill(self, color):
        r, g, b = color
        row = bytes((r, g, b)) * W
        for y in range(H):
            self.px[y][:] = row

    def rect(self, x0, y0, x1, y1, color):
        r, g, b = color
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(W, x1)
        y1 = min(H, y1)
        row = bytes((r, g, b)) * (x1 - x0)
        for y in range(y0, y1):
            self.px[y][x0 * 3:x1 * 3] = row

    def set_px(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = x * 3
            self.px[y][i:i + 3] = bytes(color)

    def disc(self, cx, cy, rad, color):
        for y in range(cy - rad, cy + rad + 1):
            for x in range(cx - rad, cx + rad + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= rad * rad:
                    self.set_px(x, y, color)

    def ring(self, cx, cy, rad, thick, color):
        for y in range(cy - rad - thick, cy + rad + thick + 1):
            for x in range(cx - rad - thick, cx + rad + thick + 1):
                d2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if (rad - thick) * (rad - thick) <= d2 <= (rad + thick) * (rad + thick):
                    self.set_px(x, y, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            x = x0 + dx * i // steps
            y = y0 + dy * i // steps
            for a in range(thick):
                for b in range(thick):
                    self.set_px(x + a, y + b, color)

    def grain(self, x0, y0, x1, y1, amount):
        """Deterministic paper grain: tiny hash-based brightness jitter."""
        for y in range(y0, y1):
            row = self.px[y]
            for x in range(x0, x1):
                h = (x * 2654435761 + y * 40503) & 0xFFFFFFFF
                h ^= h >> 13
                d = (h % (2 * amount + 1)) - amount
                if d:
                    i = x * 3
                    for c in range(3):
                        v = row[i + c] + d
                        row[i + c] = 0 if v < 0 else (255 if v > 255 else v)

    def text(self, x, y, s, scale, color):
        """Draw uppercase text; y is the top row. Returns width used."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT["?"])
            for gy in range(7):
                bits = glyph[gy]
                for gx in range(5):
                    if bits & (1 << (4 - gx)):
                        for dy in range(scale):
                            for dx in range(scale):
                                self.set_px(cx + gx * scale + dx,
                                            y + gy * scale + dy, color)
            cx += 6 * scale
        return cx - x - scale

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)

    def para(self, x, y, s, scale, color, max_w, leading):
        """Word-wrapped paragraph; returns the y after the last line."""
        words = s.split(" ")
        lines = []
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        for ln in lines:
            self.text(x, y, ln, scale, color)
            y += 7 * scale + leading
        return y

# ---------------------------------------------------------------- palette

PAPER = (246, 241, 231)
NAVY = (22, 35, 63)
NAVY2 = (27, 42, 74)
GOLD = (217, 164, 65)
RED = (179, 32, 44)
INK = (24, 24, 28)
WHITE = (255, 255, 255)
BLUE = (36, 80, 164)
TEAL = (14, 122, 110)
PURPLE = (104, 62, 150)
GREEN = (46, 125, 60)
ORANGE = (196, 98, 16)
GREY = (120, 118, 110)
LIGHT = (255, 255, 255)


def card(c, x0, y0, x1, y1, fill):
    c.rect(x0, y0, x1, y1, fill)
    c.rect(x0, y0, x1, y0 + 3, INK)
    c.rect(x0, y1 - 3, x1, y1, INK)
    c.rect(x0, y0, x0 + 3, y1, INK)
    c.rect(x1 - 3, y0, x1, y1, INK)


def header_band(c, x0, y0, x1, color, label):
    c.rect(x0, y0, x1, y0 + 40, color)
    c.text(x0 + 16, y0 + 9, label, 3, WHITE)


def star(c, cx, cy, r, color):
    # Five-pointed star from 10 vertices.
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + int(rr * math.cos(ang)), cy + int(rr * math.sin(ang))))
    for i in range(10):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % 10]
        c.line(x0, y0, x1, y1, color, 2)
    # Fill by horizontal scan of the outline is overkill; paint a disc core.
    c.disc(cx, cy, max(2, r // 3), color)


def draw_missile_panel(c, x0, y0, x1, y1):
    """Dark panel with a rising rocket, red star and stippled sky."""
    c.rect(x0, y0, x1, y1, NAVY2)
    # Stippled sky: deterministic dot grid.
    for gy in range(y0 + 12, y1 - 12, 26):
        for gx in range(x0 + 14, x1 - 14, 26):
            if ((gx * 7 + gy * 13) % 5) < 2:
                c.disc(gx, gy, 2, (70, 88, 130))
    # Ground.
    c.rect(x0, y1 - 26, x1, y1 - 22, GOLD)
    cx = (x0 + x1) // 2
    # Flame.
    c.line(cx, y1 - 30, cx - 26, y1 - 26, (240, 140, 40), 3)
    c.line(cx, y1 - 30, cx + 26, y1 - 26, (240, 140, 40), 3)
    c.line(cx, y1 - 30, cx, y1 - 26, (250, 200, 60), 4)
    # Rocket body.
    c.rect(cx - 22, y0 + 78, cx + 22, y1 - 30, WHITE)
    c.rect(cx - 22, y0 + 78, cx + 22, y0 + 96, RED)
    # Nose cone.
    for i in range(20):
        wdt = 3 + i
        c.rect(cx - wdt, y0 + 58 + i, cx + wdt, y0 + 59 + i, RED)
    # Fins.
    c.line(cx - 22, y1 - 90, cx - 52, y1 - 30, RED, 5)
    c.line(cx + 22, y1 - 90, cx + 52, y1 - 30, RED, 5)
    # Window.
    c.disc(cx, y0 + 130, 10, NAVY)
    c.ring(cx, y0 + 130, 10, 2, GOLD)
    # Red star above the rocket.
    star(c, cx, y0 + 34, 16, (230, 60, 60))
    c.text_center(cx, y1 - 20, "PYONGYANG", 2, GOLD)


def draw_eu_stars(c, cx, cy, r):
    import math
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        sx = cx + int(r * math.cos(ang))
        sy = cy + int(r * math.sin(ang))
        c.disc(sx, sy, 4, GOLD)


def draw_bank(c, x0, y0, w, color):
    c.rect(x0, y0, x0 + w, y0 + 8, color)
    for i in range(4):
        cx = x0 + 12 + i * (w - 24) // 3
        c.rect(cx - 4, y0 + 12, cx + 4, y0 + 44, color)
    c.rect(x0, y0 + 48, x0 + w, y0 + 56, color)


def draw_balloon(c, cx, cy, r, color):
    """Parade balloon: round body, knot and a wavy string."""
    c.disc(cx, cy, r, color)
    c.disc(cx - r // 3, cy - r // 3, r // 4, WHITE)
    c.line(cx - 5, cy + r - 2, cx + 5, cy + r - 2, color, 3)
    c.line(cx, cy + r + 2, cx - 8, cy + r + 10, color, 2)
    c.line(cx - 8, cy + r + 10, cx + 6, cy + r + 16, color, 2)


def draw_clapper(c, x0, y0, w, h, color):
    """Film clapperboard: striped top bar over a plain board."""
    c.rect(x0, y0, x0 + w, y0 + h, WHITE)
    c.rect(x0, y0, x0 + w, y0 + 3, INK)
    c.rect(x0, y0 + h - 3, x0 + w, y0 + h, INK)
    c.rect(x0, y0, x0 + 3, y0 + h, INK)
    c.rect(x0 + w - 3, y0, x0 + w, y0 + h, INK)
    # Hinged top bar, tilted stripes.
    c.rect(x0, y0, x0 + w, y0 + 16, color)
    for i in range(6):
        sx = x0 + 4 + i * 16
        c.line(sx, y0 + 16, sx + 10, y0, WHITE, 4)
    # Board lines.
    c.line(x0 + 8, y0 + 30, x0 + w - 8, y0 + 30, color, 2)
    c.line(x0 + 8, y0 + 42, x0 + w - 8, y0 + 42, color, 2)


def draw_globe(c, cx, cy, r, color):
    c.ring(cx, cy, r, 3, color)
    c.line(cx - r, cy, cx + r, cy, color, 2)
    c.line(cx, cy - r, cx, cy + r, color, 2)
    c.disc(cx - r // 3, cy - r // 3, r // 4, color)
    c.disc(cx + r // 4, cy + r // 4, r // 5, color)


def draw_ball(c, cx, cy, r):
    c.disc(cx, cy, r, RED)
    c.ring(cx, cy, r, 2, WHITE)
    c.line(cx - r + 4, cy - 6, cx + r - 4, cy + 6, WHITE, 2)
    c.line(cx - r + 4, cy + 6, cx + r - 4, cy - 6, WHITE, 2)


# ---------------------------------------------------------------- front page

def build():
    c = Canvas()
    c.fill(PAPER)
    c.grain(0, 0, W, H, 5)

    # Masthead.
    c.rect(0, 0, W, 148, NAVY)
    c.text_center(W // 2, 20, "THE WORLD IN ONE DAY", 6, WHITE)
    c.rect(40, 76, W - 40, 80, GOLD)
    c.text(40, 98, "THURSDAY 26 NOVEMBER 2026", 3, GOLD)
    c.text(W - 40 - text_width("7 STORIES * 3 REGIONS", 3), 98,
           "7 STORIES * 3 REGIONS", 3, WHITE)

    # Lead story.
    card(c, 24, 160, 1000, 480, LIGHT)
    c.rect(24, 160, 1000, 172, RED)
    c.text(48, 186, "NORTH KOREA * SECURITY", 3, RED)
    c.text(48, 216, "KIM ORDERS", 7, NAVY)
    c.text(48, 273, "WIDER NUCLEAR", 7, NAVY)
    c.text(48, 330, "DEPLOYMENT", 7, NAVY)
    c.para(48, 396, "KCNA: TACTICAL ARMS TO SPREAD ACROSS DOMAINS. "
           "NUCLEAR STATUS 'ABSOLUTELY INVIOLABLE'.", 3, INK, 560, 5)
    draw_missile_panel(c, 640, 184, 976, 464)

    # Middle row: USA, Europe, Asia.
    mid = [
        (24, 336, RED, "USA", "THANKSGIVING DAY", "US MARKETS SHUT",
         "AMERICA PAUSES FOR THANKSGIVING. WALL STREET SHUT.", "balloon"),
        (356, 668, BLUE, "EUROPE", "EU SUMMIT OPENS", "IN BRUSSELS",
         "UKRAINE FUNDS AND NEXT ECB CHIEF ON AGENDA. "
         "ECB PUBLISHES OCTOBER MINUTES.", "stars"),
        (688, 1000, TEAL, "ASIA", "BANK OF KOREA", "DECIDES ON RATES",
         "HIKE TO 3.25% EXPECTED. 32 OF 34 ECONOMISTS BACK A RISE.",
         "bank"),
    ]
    for x0, x1, color, label, h1, h2, sub, icon in mid:
        card(c, x0, 492, x1, 748, LIGHT)
        header_band(c, x0, 492, x1, color, label)
        if icon == "balloon":
            draw_balloon(c, x0 + 66, 572, 22, RED)
        elif icon == "stars":
            draw_eu_stars(c, x0 + 66, 576, 26)
            c.disc(x0 + 66, 576, 5, GOLD)
        else:
            draw_bank(c, x0 + 20, 548, 92, TEAL)
        c.text(x0 + 16, 616, h1, 3, NAVY)
        c.text(x0 + 16, 641, h2, 3, NAVY)
        c.para(x0 + 16, 676, sub, 2, INK, x1 - x0 - 32, 3)

    # Bottom row: culture, world, sport.
    bot = [
        (24, 336, PURPLE, "CULTURE", "ZOOTOPIA 2 OPENS", "IN CINEMAS TODAY",
         "JUDY AND NICK ARE BACK. $125M DEBUT EYED.",
         "clapper"),
        (356, 668, GREEN, "WORLD", "INDIA MARKS", "CONSTITUTION DAY",
         "MUMBAI MARKS 18 YEARS SINCE 26/11 ATTACKS.", "globe"),
        (688, 1000, ORANGE, "SPORT", "EUROPA LEAGUE", "17 TIES TONIGHT",
         "MILAN AT OLYMPIACOS. CELTA HOST BOURNEMOUTH.", "ball"),
    ]
    for x0, x1, color, label, h1, h2, sub, icon in bot:
        card(c, x0, 760, x1, 940, LIGHT)
        header_band(c, x0, 760, x1, color, label)
        if icon == "clapper":
            draw_clapper(c, x0 + 20, 802, 92, 48, PURPLE)
        elif icon == "globe":
            draw_globe(c, x0 + 52, 830, 20, GREEN)
        else:
            draw_ball(c, x0 + 52, 830, 20)
        c.text(x0 + 16, 856, h1, 3, NAVY)
        c.text(x0 + 16, 881, h2, 3, NAVY)
        c.para(x0 + 16, 906, sub, 2, INK, x1 - x0 - 32, 3)

    # Footer.
    c.rect(0, 952, W, 1012, NAVY)
    c.text_center(W // 2, 962,
                  "7 STORIES * 3 REGIONS * THURSDAY 26 NOVEMBER 2026", 3, WHITE)
    c.text_center(W // 2, 990, "SOURCES: REUTERS * CNN * KCNA * AP * WSJ", 2, GOLD)

    # Light print grain over the whole sheet for a dense file.
    c.grain(0, 0, W, H, 2)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build().px)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
