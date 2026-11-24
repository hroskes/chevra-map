"""Build the first printable cemetery map.

    python scripts/build_pdf.py

Reads data/burials.csv and data/plots.csv. Writes
print/chevra-ahavas-chesed.pdf. The drawing uses the same working
assumptions as the interactive map.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import Color, HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "print" / "chevra-ahavas-chesed.pdf"

# Arial on Windows. Liberation Sans on the Ubuntu Actions runner; its metrics match Arial.
FONT_CANDIDATES = (
    (Path(r"C:\Windows\Fonts\arial.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")),
    (
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ),
    (
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
    ),
)


def register_fonts() -> None:
    for regular, bold in FONT_CANDIDATES:
        if regular.is_file() and bold.is_file():
            pdfmetrics.registerFont(TTFont("Body", str(regular)))
            pdfmetrics.registerFont(TTFont("Body-Bold", str(bold)))
            return
    raise SystemExit("No usable font pair found. Expected Arial or Liberation Sans.")


register_fonts()

PAGE = landscape(letter)
WIDTH, HEIGHT = PAGE
MARGIN = 36
INK = HexColor("#241f1a")
MUTED = HexColor("#5e564c")
LINE = HexColor("#cfc6b8")
PAPER = HexColor("#f4efe6")
OCCUPIED = HexColor("#e4f0e4")
BANDS = {
    "single-early": HexColor("#1d5c86"),
    "single-late": HexColor("#2c6a3c"),
    "double": HexColor("#c05612"),
    "triple": HexColor("#a33b62"),
}


def load():
    with (DATA / "burials.csv").open(encoding="utf-8-sig", newline="") as handle:
        burials = list(csv.DictReader(handle))
    with (DATA / "plots.csv").open(encoding="utf-8-sig", newline="") as handle:
        plots = list(csv.DictReader(handle))
    by_id = {row["burial_id"]: row for row in burials}
    fields = []
    for plot in plots:
        if plot["field"] not in fields:
            fields.append(plot["field"])
    return burials, plots, by_id, fields


def band_for(field: str) -> str:
    if len(field) == 1 and field <= "J":
        return "single-early"
    if len(field) == 1:
        return "single-late"
    if len(field) == 2:
        return "double"
    return "triple"


def people(plot: dict, by_id: dict) -> list[dict]:
    return [by_id[item] for item in plot["burial_id"].split(";") if item and item in by_id]


def not_on_square(burial: dict) -> bool:
    """A numbered square, not a letter-suffix grave beside it and not an off-grid lot."""
    return burial["cemetery"] == "chevra" and (burial["on_map"] != "yes" or bool(burial["lot_suffix"]))


def display_name(burial: dict) -> str:
    if burial["name_last"] and burial["name_first"]:
        return f"{burial['name_last']}, {burial['name_first']}"
    return burial["name_raw"]


def listed_name(burial: dict) -> str:
    name = display_name(burial)
    other = burial.get("name_other", "").strip()
    if other and other not in name:
        return f"{name} {other}"
    return name


def fit(pdf: canvas.Canvas, text: str, font: str, size: float, width: float) -> str:
    if pdf.stringWidth(text, font, size) <= width:
        return text
    trimmed = text
    while trimmed and pdf.stringWidth(trimmed + "…", font, size) > width:
        trimmed = trimmed[:-1]
    return (trimmed + "…") if trimmed else ""


def footer(pdf: canvas.Canvas, number: int) -> None:
    pdf.setFillColor(MUTED)
    pdf.setFont("Body", 8)
    pdf.drawString(
        MARGIN,
        20,
        "First schematic, not a survey. Row 1 is toward the entrance. Lot 1 is on the left. Empty lots may still be reserved.",
    )
    pdf.drawRightString(WIDTH - MARGIN, 20, str(number))


def wrapped(pdf: canvas.Canvas, text: str, x: float, y: float, width: float, font: str, size: float, leading: float) -> float:
    words = text.split()
    line = ""
    pdf.setFont(font, size)
    for word in words:
        trial = word if not line else f"{line} {word}"
        if pdf.stringWidth(trial, font, size) <= width:
            line = trial
            continue
        pdf.drawString(x, y, line)
        y -= leading
        line = word
    if line:
        pdf.drawString(x, y, line)
        y -= leading
    return y


def draw_cover(pdf: canvas.Canvas, page: int) -> None:
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(INK)
    pdf.setFont("Body", 11)
    pdf.drawString(MARGIN, HEIGHT - 48, "Liberty Road")
    pdf.setFont("Body-Bold", 26)
    pdf.drawString(MARGIN, HEIGHT - 80, "Chevra Ahavas Chesed Cemetery")
    pdf.setFont("Body", 12)
    y = HEIGHT - 112
    paragraphs = [
        "A first map of the graves. The lot number on each square is the key used in the index. A filled square has a burial in the lists. An open square has no name in the lists. The lists do not say which of those empty lots are reserved.",
        "The next page has the entrance at the top. In the upper part, A through J are on the left and Shaari Zion Cemetery runs beside them on the right. Left and right on that page are the reverse of left and right as you walk in. Lower down, K through S continue from A through J. AA through JJ and AAA through KKK are to the right, past the end of Shaari Zion. Each field is drawn the same height, so K lines up with AA and AAA. The plot listing board is one field tall, between HH and II, and so it sits beside S. II, JJ, JJJ, and KKK continue past S.",
        "KK and LLL were added after that photo, so they are not on the overview. On each field page, row 1 is at the top, as the row closest to the entrance, and lot 1 is at the left. Those directions, and the row lengths, still need a visit.",
        "Fields J through O are numbered straight through the three rows. The other fields start again at 1 on each row. A person whose lot does not fall on that grid is named on the field page and in the list that follows the overview.",
    ]
    for paragraph in paragraphs:
        y = wrapped(pdf, paragraph, MARGIN, y, WIDTH - 2 * MARGIN, "Body", 11, 15)
        y -= 8
    footer(pdf, page)
    pdf.showPage()


def draw_stack(pdf: canvas.Canvas, x: float, top: float, step: float, w: float, color, labels: list[str]) -> None:
    for index, label in enumerate(labels):
        y = top - (index + 1) * step
        if label == "plot listing board":
            pdf.setFillColor(HexColor("#fff8ea"))
            pdf.setStrokeColor(INK)
            pdf.setLineWidth(0.9)
            pdf.rect(x, y, w, step, fill=1, stroke=1)
            pdf.setFillColor(INK)
            pdf.setFont("Body-Bold", 6)
            pdf.drawCentredString(x + w / 2, y + step / 2 + 1.5, "Plot listing")
            pdf.drawCentredString(x + w / 2, y + step / 2 - 6.5, "board")
            continue
        pdf.setFillColor(color)
        pdf.setStrokeColor(white)
        pdf.setLineWidth(0.8)
        pdf.rect(x, y, w, step, fill=1, stroke=1)
        pdf.setFillColor(white)
        pdf.setFont("Body-Bold", 7)
        pdf.drawCentredString(x + w / 2, y + step / 2 - 2.5, label)


def draw_overview(pdf: canvas.Canvas, fields: list[str], page: int) -> None:
    del fields
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(INK)
    pdf.setFont("Body-Bold", 16)
    pdf.drawString(MARGIN, HEIGHT - 40, "Fields, as on the source map")
    pdf.setFillColor(MUTED)
    wrapped(
        pdf,
        "Entrance at the top. A–J is on the left, and Shaari Zion Cemetery parallels it on the right. Left and right on this page are reversed as you walk in.",
        MARGIN,
        HEIGHT - 58,
        WIDTH - 2 * MARGIN,
        "Body",
        9,
        12,
    )

    blue = list("ABCDEFGHIJ")
    green = list("KLMNOPQRS")
    orange = [letter * 2 for letter in "ABCDEFGH"] + ["plot listing board"] + [letter * 2 for letter in "IJ"]
    pink = [letter * 3 for letter in "ABCDEFGHIJK"]

    step = 18
    col_w = 64
    gap = 5
    top = 492
    split = top - len(blue) * step
    s_bottom = split - len(green) * step
    lower_bottom = split - len(orange) * step
    sx = 430
    ox = sx + col_w + gap
    px = ox + col_w + gap
    right = px + col_w

    pdf.setFillColor(HexColor("#e3ebe2"))
    pdf.setStrokeColor(HexColor("#8b9786"))
    pdf.setLineWidth(1)
    pdf.roundRect(ox, split, right - ox, top - split, 4, fill=1, stroke=1)
    pdf.setFillColor(MUTED)
    pdf.setFont("Body-Bold", 9)
    neighbor_x = (ox + right) / 2
    neighbor_y = (split + top) / 2
    pdf.drawCentredString(neighbor_x, neighbor_y + 6, "Shaari Zion")
    pdf.setFont("Body", 8)
    pdf.drawCentredString(neighbor_x, neighbor_y - 8, "Cemetery")

    draw_stack(pdf, sx, top, step, col_w, BANDS["single-early"], blue)
    draw_stack(pdf, sx, split, step, col_w, BANDS["single-late"], green)
    draw_stack(pdf, ox, split, step, col_w, BANDS["double"], orange)
    draw_stack(pdf, px, split, step, col_w, BANDS["triple"], pink)

    pad = 4
    pdf.setStrokeColor(HexColor("#9a1c1c"))
    pdf.setLineWidth(2)
    path = pdf.beginPath()
    path.moveTo(sx - pad, s_bottom)
    path.lineTo(sx - pad, top + pad)
    path.lineTo(sx + col_w + pad, top + pad)
    path.lineTo(sx + col_w + pad, split)
    path.lineTo(right + pad, split)
    path.lineTo(right + pad, lower_bottom - pad)
    path.lineTo(ox - pad, lower_bottom - pad)
    path.lineTo(ox - pad, s_bottom)
    path.close()
    pdf.drawPath(path, fill=0, stroke=1)

    pdf.setFillColor(INK)
    pdf.setFont("Body-Bold", 10)
    pdf.drawCentredString(sx + col_w / 2, top + 22, "Liberty Rd")
    pdf.setFont("Body", 8)
    pdf.drawCentredString(sx + col_w / 2, top + 11, "Entrance")
    pdf.setFont("Body", 9)
    pdf.drawCentredString(sx - 40, (top + s_bottom) / 2, "Beth El")
    pdf.setFillColor(MUTED)
    pdf.setFont("Body", 8)
    pdf.drawCentredString((ox + right) / 2, lower_bottom - 16, "Far end")

    pdf.setFillColor(INK)
    pdf.setFont("Body-Bold", 10)
    pdf.drawString(MARGIN, HEIGHT - 108, "Same colors as the source map")
    swatches = [
        (BANDS["single-early"], "Blue: A–J, from the entrance"),
        (BANDS["single-late"], "Green: K–S, continuing from J"),
        (BANDS["double"], "Orange: AA–JJ, to the right of K–S"),
        (BANDS["triple"], "Pink: AAA–KKK, farther right"),
    ]
    y = HEIGHT - 130
    for color, label in swatches:
        pdf.setFillColor(color)
        pdf.roundRect(MARGIN, y - 3, 14, 10, 2, fill=1, stroke=0)
        pdf.setFillColor(INK)
        pdf.setFont("Body", 9)
        pdf.drawString(MARGIN + 22, y, label)
        y -= 20
    wrapped(
        pdf,
        "Each field is the same height. K lines up with AA and AAA. The plot listing board is one field tall, between HH and II, so it sits beside S. II, JJ, JJJ, and KKK continue past S. The source legend extends the bands through Z, ZZ, and ZZZ. The burial lists stop at S, JJ, and KKK. KK and LLL were added later, so this page leaves them off.",
        MARGIN,
        y - 6,
        sx - 90 - MARGIN,
        "Body",
        9,
        12,
    )
    footer(pdf, page)
    pdf.showPage()


def draw_missing(pdf: canvas.Canvas, burials: list[dict], page: int) -> int:
    bottom = 40

    def begin(continued: bool) -> float:
        nonlocal page
        if continued:
            footer(pdf, page)
            pdf.showPage()
            page += 1
        pdf.setFillColor(PAPER)
        pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
        pdf.setFillColor(INK)
        pdf.setFont("Body-Bold", 18)
        title = "Recorded, but not drawn on a square"
        if continued:
            title += ", continued"
        pdf.drawString(MARGIN, HEIGHT - 48, title)
        return HEIGHT - 72

    y = begin(False)
    pdf.setFont("Body", 10)
    pdf.setFillColor(MUTED)
    y = wrapped(
        pdf,
        "These Chevra records do not fall on a square. A lot with a letter, such as 15A, is one of them. Anyone with a field is also named on that field's page. The index still lists them.",
        MARGIN,
        y,
        WIDTH - 2 * MARGIN,
        "Body",
        10,
        13,
    )
    y -= 8
    pdf.setFillColor(INK)
    missing = [row for row in burials if not_on_square(row)]
    for burial in sorted(missing, key=lambda row: (row["name_last"], row["name_first"])):
        where = " ".join(
            part
            for part in (
                burial["field"] and f"field {burial['field']}",
                burial["row"] and f"row {burial['row']}",
                burial["lot_raw"] and f"lot {burial['lot_raw']}",
            )
            if part
        ) or "no field, row, or lot"
        note_h = 12 if burial["notes"] else 0
        if y - 14 - note_h < bottom:
            y = begin(True)
            pdf.setFillColor(INK)
        pdf.setFont("Body", 10)
        pdf.drawString(MARGIN, y, f"{listed_name(burial)}  —  {where}")
        y -= 14
        if burial["notes"]:
            pdf.setFillColor(MUTED)
            pdf.setFont("Body", 8)
            pdf.drawString(MARGIN + 12, y, fit(pdf, burial["notes"], "Body", 8, WIDTH - 2 * MARGIN - 12))
            pdf.setFillColor(INK)
            y -= 12
    footer(pdf, page)
    pdf.showPage()
    return page + 1


UPPER = list("ABCDEFGHIJ")
LOWER = list("KLMNOPQRS")
SINGLES = UPPER + LOWER
DOUBLE_FIELDS = [letter * 2 for letter in "ABCDEFGHIJ"]
TRIPLES = [letter * 3 for letter in "ABCDEFGHIJK"]
BOARD = "plot listing board"
# Equal field height, lower section starting together at K, AA, and AAA.
# The board is one field between HH and II, which puts it beside S.
DOUBLE_SLOTS = DOUBLE_FIELDS[:8] + [BOARD] + DOUBLE_FIELDS[8:]


def span(codes: list[str]) -> str:
    if not codes:
        return ""
    if len(codes) == 1:
        return codes[0]
    return f"{codes[0]}–{codes[-1]}"


def is_code(item: str) -> bool:
    return item.isalpha() and item.isupper()


def continues(prev: str, nxt: str) -> bool:
    if not is_code(prev) or not is_code(nxt) or len(prev) != len(nxt):
        return False
    column = SINGLES if len(prev) == 1 else DOUBLE_FIELDS if len(prev) == 2 else TRIPLES
    return abs(column.index(prev) - column.index(nxt)) == 1


def phrase(items: list[str]) -> str:
    groups: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        if buf:
            groups.append(span(buf))
            buf.clear()

    for item in items:
        if buf and not continues(buf[-1], item):
            flush()
        if is_code(item):
            buf.append(item)
        else:
            flush()
            groups.append(item)
    flush()
    if not groups:
        return ""
    if len(groups) == 1:
        return groups[0]
    tail = groups[-1]
    if len(groups) == 2:
        joiner = " and " if tail in {"Liberty Rd", "Shaari Zion", "Beth El"} else ", "
        return f"{groups[0]}{joiner}{tail}"
    return ", ".join(groups[:-1]) + f", and {tail}"


def directions(field: str) -> tuple[str, str, str, str]:
    """What lies straight up, down, left, and right. Side bands stay off a vertical arrow."""
    if len(field) == 1:
        index = SINGLES.index(field)
        up = phrase(list(reversed(SINGLES[:index])) + ["Liberty Rd"])
        down = phrase(SINGLES[index + 1:])
        if field in UPPER:
            right = "Shaari Zion"
        else:
            slot = LOWER.index(field)
            right = phrase([DOUBLE_SLOTS[slot], TRIPLES[slot]])
        return up, down, "Beth El", right
    if field == "KK":
        up = phrase(list(reversed(DOUBLE_SLOTS)) + ["Shaari Zion"])
        return up, "far end", "Beth El", ""
    if len(field) == 2:
        slot = DOUBLE_SLOTS.index(field)
        up = phrase(list(reversed(DOUBLE_SLOTS[:slot])) + ["Shaari Zion"])
        down = "far end" if field == "JJ" else phrase(DOUBLE_SLOTS[slot + 1:])
        if slot < len(LOWER):
            left = phrase([LOWER[slot], "Beth El"])
        else:
            left = "Beth El"
        right = TRIPLES[slot]
        return up, down, left, right
    if field == "LLL":
        return phrase(list(reversed(TRIPLES)) + ["Shaari Zion"]), "far end", "", ""
    slot = TRIPLES.index(field)
    up = phrase(list(reversed(TRIPLES[:slot])) + ["Shaari Zion"])
    down = "far end" if field == "KKK" else phrase(TRIPLES[slot + 1:])
    left_items = [DOUBLE_SLOTS[slot]]
    if slot < len(LOWER):
        left_items.append(LOWER[slot])
    left_items.append("Beth El")
    return up, down, phrase(left_items), ""


def wrap_text(pdf: canvas.Canvas, text: str, font: str, size: float, width: float) -> list[str]:
    if not text:
        return []
    lines: list[str] = []
    line = ""
    for word in text.split():
        trial = word if not line else f"{line} {word}"
        if pdf.stringWidth(trial, font, size) <= width:
            line = trial
            continue
        if line:
            lines.append(line)
        line = word
    if line:
        lines.append(line)
    return lines


def fit_name(pdf: canvas.Canvas, text: str, width: float) -> list[tuple[str, float]]:
    size = 7.0
    while size > 5 and pdf.stringWidth(text, "Body", size) > width:
        size -= 0.25
    if pdf.stringWidth(text, "Body", size) <= width:
        return [(text, size)]
    if "-" in text:
        bits = [bit for bit in text.split("-") if bit]
        parts = [bit + ("-" if index < len(bits) - 1 else "") for index, bit in enumerate(bits)]
        lines: list[tuple[str, float]] = []
        for part in parts:
            lines.extend(fit_name(pdf, part, width))
        return lines
    return [(text, 5.0)]


def field_spec(pdf: canvas.Canvas, field: str, plots: list[dict], by_id: dict, width: float) -> dict:
    rows: dict[int, list] = defaultdict(list)
    for plot in plots:
        if plot["field"] != field or plot["lot_suffix"]:
            continue
        rows[int(plot["row"])].append(plot)
    sample = next(plot for plot in plots if plot["field"] == field and not plot["lot_suffix"])
    lot_count = max(len(rows[row]) for row in rows)
    label_w = 12
    gap = 1
    cell_w = (width - label_w - gap * (lot_count - 1)) / lot_count
    inner = cell_w - 2

    def person_lines(text: str) -> list[tuple[str, float]]:
        return fit_name(pdf, text, inner)

    row_cells: dict[int, list] = {}
    row_heights: list[float] = []
    for row_number in (1, 2, 3):
        cells = []
        tallest = 0.0
        for plot in sorted(rows[row_number], key=lambda item: int(item["lot_number"])):
            lines: list[tuple[str, float]] = []
            for burial in people(plot, by_id):
                lines.extend(person_lines(burial["name_last"] or burial["name_raw"]))
            text_h = sum(size + 1.5 for _, size in lines)
            tallest = max(tallest, text_h)
            cells.append({"lot": plot["lot_number"], "lines": lines, "occupied": bool(lines)})
        row_cells[row_number] = cells
        row_heights.append(max(14, 10 + tallest))

    up, down, left, right = directions(field)
    dir_size = 7
    up_lines = wrap_text(pdf, f"↑  {up}", "Body", dir_size, width) if up else []
    down_lines = wrap_text(pdf, f"↓  {down}", "Body", dir_size, width) if down else []
    left_label = f"←  {left}" if left else ""
    right_label = f"{right}  →" if right else ""
    if not left_label and not right_label:
        side_lines = 0
    elif (
        left_label
        and right_label
        and pdf.stringWidth(left_label, "Body", dir_size) + pdf.stringWidth(right_label, "Body", dir_size) + 12 > width
    ):
        side_lines = 2
    else:
        side_lines = 1
    missing = sorted(
        (
            burial
            for burial in by_id.values()
            if not_on_square(burial) and burial["field"] == field
        ),
        key=lambda burial: (burial["name_last"], burial["name_first"], burial["name_raw"]),
    )
    missing_lines: list[str] = []
    if missing:
        bits = []
        for burial in missing:
            where = " ".join(
                part
                for part in (
                    burial["row"] and f"row {burial['row']}",
                    burial["lot_raw"] and f"lot {burial['lot_raw']}",
                )
                if part
            ) or "no row or lot"
            bit = f"{listed_name(burial)} — {where}"
            if burial["notes"]:
                bit += f". {burial['notes']}"
            bits.append(bit)
        missing_lines = wrap_text(pdf, "Not on a square: " + "; ".join(bits), "Body", 6.5, width)
    title = f"Field {field}"
    if field in {"KK", "LLL"}:
        title += "  ·  place assumed"
    subtitle = (
        f"{sample['lots_per_row']} lots · numbers continue"
        if sample["numbering"] == "continuous"
        else f"{sample['lots_per_row']} lots · each row restarts"
    )
    height = 13 + 3 + 8 * len(up_lines) + 9 * side_lines + sum(row_heights) + 1.5 * 3 + 4 + 8 * len(down_lines) + 8 * len(missing_lines)
    return {
        "field": field,
        "band": band_for(field),
        "title": title,
        "subtitle": subtitle,
        "rows": row_cells,
        "row_heights": row_heights,
        "cell_w": cell_w,
        "label_w": label_w,
        "gap": gap,
        "up_lines": up_lines,
        "down_lines": down_lines,
        "left_label": left_label,
        "right_label": right_label,
        "side_lines": side_lines,
        "missing_lines": missing_lines,
        "height": height,
    }


def draw_zone(pdf: canvas.Canvas, spec: dict, top: float, x: float, width: float) -> float:
    y = top
    pdf.setFillColor(BANDS[spec["band"]])
    pdf.rect(x, y - 12, width, 12, fill=1, stroke=0)
    pdf.setFillColor(white)
    pdf.setFont("Body-Bold", 8)
    pdf.drawString(x + 4, y - 9, spec["title"])
    pdf.setFont("Body", 6.5)
    pdf.drawRightString(x + width - 4, y - 9, spec["subtitle"])
    y -= 16
    pdf.setFillColor(INK)
    pdf.setFont("Body", 7)
    for line in spec["up_lines"]:
        pdf.drawString(x, y - 7, line)
        y -= 8
    if spec["side_lines"] == 2:
        pdf.drawString(x, y - 7, spec["left_label"])
        y -= 9
        if spec["right_label"]:
            pdf.drawRightString(x + width, y - 7, spec["right_label"])
            y -= 9
    elif spec["side_lines"] == 1:
        if spec["left_label"]:
            pdf.drawString(x, y - 7, spec["left_label"])
        if spec["right_label"]:
            pdf.drawRightString(x + width, y - 7, spec["right_label"])
        y -= 9
    pdf.setLineWidth(0.4)
    for row_number, row_h in zip((1, 2, 3), spec["row_heights"]):
        pdf.setFillColor(MUTED)
        pdf.setFont("Body", 7)
        pdf.drawString(x, y - 9, str(row_number))
        cell_x = x + spec["label_w"]
        for cell in spec["rows"][row_number]:
            pdf.setStrokeColor(LINE)
            pdf.setFillColor(OCCUPIED if cell["occupied"] else white)
            pdf.roundRect(cell_x, y - row_h, spec["cell_w"], row_h, 1.2, fill=1, stroke=1)
            pdf.setFillColor(INK)
            pdf.setFont("Body-Bold", 6.5)
            pdf.drawString(cell_x + 1.5, y - 8, cell["lot"])
            text_y = y - 9
            for line, size in cell["lines"]:
                text_y -= size
                pdf.setFont("Body", size)
                pdf.drawString(cell_x + 1.5, text_y, line)
                text_y -= 1.5
            cell_x += spec["cell_w"] + spec["gap"]
        y -= row_h + 1.5
    pdf.setLineWidth(1)
    y -= 2
    pdf.setFillColor(INK)
    pdf.setFont("Body", 7)
    for line in spec["down_lines"]:
        pdf.drawString(x, y - 7, line)
        y -= 8
    if spec["missing_lines"]:
        pdf.setFillColor(MUTED)
        pdf.setFont("Body", 6.5)
        for line in spec["missing_lines"]:
            pdf.drawString(x, y - 7, line)
            y -= 8
    return y


def draw_field_pages(pdf: canvas.Canvas, fields: list[str], plots: list[dict], by_id: dict, start_page: int) -> int:
    margin_x = 10
    width = WIDTH - 2 * margin_x
    bottom = 32
    gap = 8
    page = start_page
    specs = [field_spec(pdf, field, plots, by_id, width) for field in fields]
    batches: list[list[dict]] = []
    batch: list[dict] = []
    used = 0
    limit = HEIGHT - 28 - bottom
    for spec in specs:
        extra = gap if batch else 0
        if batch and used + extra + spec["height"] > limit:
            batches.append(batch)
            batch = []
            used = 0
            extra = 0
        batch.append(spec)
        used += extra + spec["height"]
    if batch:
        batches.append(batch)

    for batch in batches:
        pdf.setFillColor(PAPER)
        pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
        pdf.setFillColor(MUTED)
        pdf.setFont("Body", 7.5)
        pdf.drawString(margin_x, HEIGHT - 16, "Row 1 is toward the entrance. Lot 1 is on the left.")
        footer(pdf, page)
        y = HEIGHT - 26
        for index, spec in enumerate(batch):
            y = draw_zone(pdf, spec, y, margin_x, width)
            if index < len(batch) - 1:
                y -= gap
        pdf.showPage()
        page += 1
    groups = ", ".join("+".join(spec["field"] for spec in batch) for batch in batches)
    smallest = min(
        (size for spec in specs for row in spec["rows"].values() for cell in row for _, size in cell["lines"]),
        default=7,
    )
    print(f"Field pages: {len(batches)} ({groups})")
    print(f"Smallest name size: {smallest}")
    return page


def draw_index(pdf: canvas.Canvas, burials: list[dict], start_page: int) -> int:
    chevra = [row for row in burials if row["cemetery"] == "chevra"]
    others = [row for row in burials if row["cemetery"] != "chevra"]
    sections = [
        ("Index of Chevra burials", chevra),
        ("Rosedale, elsewhere, and unknown locations", others),
    ]
    page = start_page
    columns = 3
    col_w = (WIDTH - 2 * MARGIN - 16) / columns
    line_h = 11
    top = HEIGHT - 56
    bottom = 36

    def new_page(heading: str) -> float:
        nonlocal page
        pdf.setFillColor(PAPER)
        pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
        pdf.setFillColor(INK)
        pdf.setFont("Body-Bold", 16)
        pdf.drawString(MARGIN, HEIGHT - 40, heading)
        footer(pdf, page)
        page += 1
        return top

    for heading, rows in sections:
        rows = sorted(rows, key=lambda row: (row["name_last"].upper(), row["name_first"].upper(), row["name_raw"].upper()))
        y = new_page(heading)
        column = 0
        for burial in rows:
            if burial["on_map"] == "yes":
                place = f"{burial['field']}  r{burial['row']}  {burial['lot_raw']}"
            elif burial["cemetery"] == "chevra":
                place = "not drawn"
            elif burial["cemetery"] == "rosedale":
                place = burial["location_raw"] or "Rosedale"
            else:
                place = "elsewhere" if burial["cemetery"] == "elsewhere" else "no location"
            label = display_name(burial)
            name_size = 8
            name_width = col_w - 78
            while name_size > 6 and pdf.stringWidth(label, "Body", name_size) > name_width:
                name_size -= 0.25
            x = MARGIN + column * (col_w + 8)
            pdf.setFillColor(INK)
            pdf.setFont("Body", name_size)
            pdf.drawString(x, y, label)
            pdf.setFillColor(MUTED)
            pdf.drawRightString(x + col_w, y, place)
            y -= line_h
            if y < bottom:
                column += 1
                y = top
                if column == columns:
                    pdf.showPage()
                    y = new_page(heading)
                    column = 0
        pdf.showPage()
    return page - 1


def main() -> None:
    burials, plots, by_id, fields = load()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=PAGE)
    pdf.setTitle("Chevra Ahavas Chesed Cemetery")
    pdf.setAuthor("First schematic from the cemetery lists")
    page = 1
    draw_cover(pdf, page)
    page += 1
    draw_overview(pdf, fields, page)
    page += 1
    page = draw_missing(pdf, burials, page)
    page = draw_field_pages(pdf, fields, plots, by_id, page)
    last = draw_index(pdf, burials, page)
    pdf.save()
    print(f"Wrote {OUTPUT} ({last} pages)")


if __name__ == "__main__":
    main()
