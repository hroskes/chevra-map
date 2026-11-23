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

pdfmetrics.registerFont(TTFont("Body", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold", r"C:\Windows\Fonts\arialbd.ttf"))

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


def display_name(burial: dict) -> str:
    if burial["name_last"] and burial["name_first"]:
        return f"{burial['name_last']}, {burial['name_first']}"
    return burial["name_raw"]


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
        "First schematic, not a survey. Row 1 is toward the entrance. Lot 1 is on the left. Empty is not reserved.",
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
        "A first map of the graves. The lot number on each square is the key used in the index. A filled square has a burial in the lists. An open square has no name in the lists and is not marked reserved.",
        "Row 1 of each field is drawn at the top of the page, as the row closest to the Liberty Road entrance. Lot 1 is the left end of the row. Single letters run from A at the entrance to S at the far end. Double letters run from AA through JJ, with KK drawn after JJ. Triple letters run from AAA through KKK, with LLL drawn after KKK.",
        "These placements are assumptions. KK is not drawn between JJ and AAA as a neighbor of both: AAA stays at the start of the triple-letter band, where the source photo labels it. The photo also shows AA beside AAA and JJ beside KKK. A visit still has to confirm row direction, which end is lot 1, the row lengths in A through O, and the real places of KK and LLL.",
        "Fields J through O are numbered straight through the three rows. The other fields start again at 1 on each row. People whose lot does not fall in that working grid are listed as not drawn, and they remain in the index.",
    ]
    for paragraph in paragraphs:
        y = wrapped(pdf, paragraph, MARGIN, y, WIDTH - 2 * MARGIN, "Body", 11, 15)
        y -= 8
    footer(pdf, page)
    pdf.showPage()


def draw_overview(pdf: canvas.Canvas, fields: list[str], page: int) -> None:
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(INK)
    pdf.setFont("Body-Bold", 18)
    pdf.drawString(MARGIN, HEIGHT - 48, "Fields, from the entrance toward the far end")
    pdf.setFont("Body", 10)
    pdf.setFillColor(MUTED)
    pdf.drawString(MARGIN, HEIGHT - 66, "Dashed codes are KK and LLL. Their places are assumed.")
    groups = [
        ("A–J  single letters", [field for field in fields if band_for(field) == "single-early"]),
        ("K–S  single letters", [field for field in fields if band_for(field) == "single-late"]),
        ("AA–KK  double letters", [field for field in fields if band_for(field) == "double"]),
        ("AAA–LLL  triple letters", [field for field in fields if band_for(field) == "triple"]),
    ]
    column_w = (WIDTH - 2 * MARGIN - 30) / 4
    for index, (title, codes) in enumerate(groups):
        x = MARGIN + index * (column_w + 10)
        y = HEIGHT - 100
        pdf.setFillColor(BANDS[band_for(codes[0])])
        pdf.rect(x, y - 4, column_w, 18, fill=1, stroke=0)
        pdf.setFillColor(white)
        pdf.setFont("Body-Bold", 9)
        pdf.drawString(x + 6, y, title)
        y -= 28
        for code in codes:
            pdf.setStrokeColor(BANDS[band_for(code)])
            pdf.setFillColor(white)
            pdf.setDash(3, 2) if code in {"KK", "LLL"} else pdf.setDash()
            pdf.roundRect(x, y - 16, 42, 20, 3, fill=1, stroke=1)
            pdf.setFillColor(INK)
            pdf.setFont("Body-Bold", 9)
            pdf.drawString(x + 8, y - 10, code)
            y -= 24
        pdf.setDash()
    footer(pdf, page)
    pdf.showPage()


def draw_missing(pdf: canvas.Canvas, burials: list[dict], page: int) -> None:
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(INK)
    pdf.setFont("Body-Bold", 18)
    pdf.drawString(MARGIN, HEIGHT - 48, "Recorded, but not drawn on a square")
    pdf.setFont("Body", 10)
    pdf.setFillColor(MUTED)
    y = HEIGHT - 72
    y = wrapped(
        pdf,
        "These Chevra records do not fall on the working grid. The index still lists them.",
        MARGIN,
        y,
        WIDTH - 2 * MARGIN,
        "Body",
        10,
        13,
    )
    y -= 8
    pdf.setFillColor(INK)
    missing = [row for row in burials if row["cemetery"] == "chevra" and row["on_map"] != "yes"]
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
        pdf.setFont("Body", 10)
        pdf.drawString(MARGIN, y, f"{display_name(burial)}  —  {where}")
        y -= 14
        if burial["notes"]:
            pdf.setFillColor(MUTED)
            pdf.setFont("Body", 8)
            pdf.drawString(MARGIN + 12, y, fit(pdf, burial["notes"], "Body", 8, WIDTH - 2 * MARGIN - 12))
            pdf.setFillColor(INK)
            y -= 12
    footer(pdf, page)
    pdf.showPage()


def draw_field(pdf: canvas.Canvas, field: str, plots: list[dict], by_id: dict, page: int) -> None:
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    band = band_for(field)
    pdf.setFillColor(BANDS[band])
    pdf.rect(0, HEIGHT - 28, WIDTH, 28, fill=1, stroke=0)
    pdf.setFillColor(white)
    pdf.setFont("Body-Bold", 14)
    title = f"Field {field}"
    if field in {"KK", "LLL"}:
        title += "   (place assumed)"
    pdf.drawString(MARGIN, HEIGHT - 19, title)
    sample = next(plot for plot in plots if plot["field"] == field and not plot["lot_suffix"])
    pdf.setFillColor(MUTED)
    pdf.setFont("Body", 9)
    numbering = (
        f"Numbers continue across the rows, {sample['lots_per_row']} lots each."
        if sample["numbering"] == "continuous"
        else f"Each row restarts at 1. {sample['lots_per_row']} lots in a row."
    )
    pdf.drawString(MARGIN, HEIGHT - 46, numbering + "  Row 1 is the entrance side. Lot 1 is on the left.")

    rows = defaultdict(list)
    suffixes = defaultdict(list)
    for plot in plots:
        if plot["field"] != field:
            continue
        key = (int(plot["row"]), int(plot["lot_number"]))
        if plot["lot_suffix"]:
            suffixes[key].append(plot)
        else:
            rows[int(plot["row"])].append(plot)

    max_lots = max(len(rows[row]) for row in rows)
    label_w = 62
    gap = 3
    usable = WIDTH - 2 * MARGIN - label_w
    cell_w = (usable - gap * (max_lots - 1)) / max_lots
    cell_h = 118
    top = HEIGHT - 64
    for row_number in (1, 2, 3):
        y = top - row_number * (cell_h + 8)
        pdf.setFillColor(MUTED)
        pdf.setFont("Body-Bold", 8)
        pdf.drawString(MARGIN, y + cell_h - 16, f"Row {row_number}")
        if row_number == 1:
            pdf.setFont("Body", 7)
            pdf.drawString(MARGIN, y + cell_h - 28, "entrance")
        for index, plot in enumerate(sorted(rows[row_number], key=lambda item: int(item["lot_number"]))):
            x = MARGIN + label_w + index * (cell_w + gap)
            occupants = people(plot, by_id)
            extra = []
            for suffix_plot in suffixes[(row_number, int(plot["lot_number"]))]:
                extra.extend(people(suffix_plot, by_id))
            pdf.setStrokeColor(LINE)
            pdf.setFillColor(OCCUPIED if occupants or extra else white)
            pdf.roundRect(x, y, cell_w, cell_h, 3, fill=1, stroke=1)
            pdf.setFillColor(INK)
            pdf.setFont("Body-Bold", 9)
            pdf.drawString(x + 3, y + cell_h - 12, plot["lot_number"])
            text_y = y + cell_h - 26
            pdf.setFont("Body", 7)
            for burial in occupants:
                pdf.drawString(x + 3, text_y, fit(pdf, burial["name_last"] or burial["name_raw"], "Body", 7, cell_w - 6))
                text_y -= 9
            for burial in extra:
                label = f"{plot['lot_number']}{burial['lot_suffix']} {burial['name_last']}"
                pdf.drawString(x + 3, text_y, fit(pdf, label, "Body", 7, cell_w - 6))
                text_y -= 9
    footer(pdf, page)
    pdf.showPage()


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
            label = fit(pdf, display_name(burial), "Body", 8, col_w - 78)
            x = MARGIN + column * (col_w + 8)
            pdf.setFillColor(INK)
            pdf.setFont("Body", 8)
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
    draw_missing(pdf, burials, page)
    page += 1
    for field in fields:
        draw_field(pdf, field, plots, by_id, page)
        page += 1
    last = draw_index(pdf, burials, page)
    pdf.save()
    print(f"Wrote {OUTPUT} ({last} pages)")


if __name__ == "__main__":
    main()
