"""Build the first-version burial CSV, plot grid, and QA notes.

Run from anywhere:

    python scripts/build_dataset.py

Reads the two source PDFs in the repo root. Writes data/burials.csv,
data/plots.csv, and data/qa-issues.csv. The grid rules are the working
assumptions at the top of open-questions.md.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
MASTER_PDF = ROOT / "master list of departed poorly formatted.pdf"
RECENT_PDF = ROOT / "list of departed since 2020 (11-10-26).pdf"
DATA = ROOT / "data"

RESTART_WIDTH = {
    "A": 14,
    "B": 12,
    "C": 12,
    "D": 13,
    "E": 14,
    "F": 14,
    "G": 16,
    "H": 16,
    "I": 15,
    "P": 18,
    "Q": 18,
    "R": 18,
    "S": 18,
}
CONTINUOUS_WIDTH = {"J": 14, "K": 14, "L": 16, "M": 16, "N": 16, "O": 16}
DOUBLE_WIDTH = {chr(code) * 2: 14 for code in range(ord("A"), ord("K") + 1)}
TRIPLE_WIDTH = {chr(code) * 3: 14 for code in range(ord("A"), ord("L") + 1)}

BURIAL_FIELDS = [
    "burial_id",
    "name_raw",
    "name_last",
    "name_first",
    "name_other",
    "name_order",
    "date_raw",
    "date_iso",
    "date_certainty",
    "date_year",
    "on_map",
    "cemetery",
    "field",
    "row",
    "lot_raw",
    "lot_number",
    "lot_suffix",
    "location_raw",
    "hebrew_name",
    "source",
    "master_line",
    "since_2020_line",
    "notes",
]
PLOT_FIELDS = [
    "field",
    "row",
    "lot_number",
    "lot_suffix",
    "lots_per_row",
    "numbering",
    "status",
    "burial_id",
]
QA_FIELDS = ["issue_id", "severity", "kind", "source_line", "detail"]

MASTER_LINE = re.compile(
    r"^(?P<name>.+?)\s+(?P<field>([A-Za-z])\3{0,2})\s+(?P<row>\d+)\s+"
    r"(?P<lot>\d+)(?P<suf>[A-Za-z])?(?:\s+(?P<date>.*))?$"
)
RECENT_LINE = re.compile(
    r"^(?P<name>.+?)\s+(?P<date>\d{1,2}/\d{1,2}/\d{2,4})\s*(?P<location>.*)$"
)
ROSEDALE_LINE = re.compile(
    r"^(?P<name>.+?)\s+Ros+e?dale\s+(?P<plot>\S+)(?:\s+(?P<rest>.*))?$",
    re.IGNORECASE,
)


def lines_of(path: Path) -> list[str]:
    found = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                line = line.strip()
                if line:
                    found.append(line)
    return found


def norm_name(value: str) -> str:
    value = value.upper().replace("-", " ")
    value = re.sub(r"[^A-Z ]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def squash_name(value: str) -> str:
    return re.sub(r"(.)\1+", r"\1", norm_name(value).replace(" ", ""))


def expand_year(year: int, source: str) -> tuple[int | None, str]:
    if year >= 1000:
        return year, "exact"
    if source == "since_2020":
        if year <= 26:
            return 2000 + year, "exact"
        return 1900 + year, "assumed_century"
    if 50 <= year <= 99:
        return 1900 + year, "assumed_century"
    if 27 <= year <= 49:
        return 1900 + year, "assumed_century"
    if 0 <= year <= 26:
        return 2000 + year, "assumed_century"
    return None, "unknown"


def parse_date(raw: str, source: str) -> tuple[str, str, str]:
    """Return date_iso, date_certainty, date_year."""
    raw = (raw or "").strip()
    if not raw:
        return "", "unknown", ""
    if "?" in raw or raw.endswith("/"):
        year_text = re.search(r"(\d{2,4})\s*$", raw.replace("?", ""))
        if year_text and set(raw.replace("?", "")) <= set("0123456789/ "):
            year, _ = expand_year(int(year_text.group(1)), source)
            return "", "partial", "" if year is None else str(year)
        return "", "partial", ""

    full = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", raw)
    if full:
        month, day, year = (int(part) for part in full.groups())
        expanded, certainty = expand_year(year, source)
        if expanded is None or not (1 <= month <= 12 and 1 <= day <= 31):
            return "", "partial", ""
        iso = f"{expanded:04d}-{month:02d}-{day:02d}"
        if year < 100 and certainty == "assumed_century":
            return iso, "assumed_century", str(expanded)
        return iso, "exact", str(expanded)

    month_year = re.fullmatch(r"(\d{1,2})/(\d{2,4})", raw)
    if month_year:
        year, _ = expand_year(int(month_year.group(2)), source)
        return "", "partial", "" if year is None else str(year)

    year_only = re.fullmatch(r"(\d{2,4})", raw)
    if year_only:
        year, _ = expand_year(int(year_only.group(1)), source)
        return "", "year", "" if year is None else str(year)

    return "", "unknown", ""


def month_day(raw: str) -> tuple[int, int] | None:
    match = re.search(r"(\d{1,2})/(\d{1,2})/", raw or "")
    if not match:
        return None
    month, day = int(match.group(1)), int(match.group(2))
    if 1 <= month <= 12 and 1 <= day <= 31:
        return month, day
    return None


def split_master_name(name: str) -> tuple[str, str, str]:
    parenthetical = re.findall(r"\(([^)]*)\)", name)
    cleaned = re.sub(r"\([^)]*\)", " ", name)
    tokens = [token for token in cleaned.split() if token]
    last = tokens[0] if tokens else ""
    first = tokens[1] if len(tokens) > 1 else ""
    other = " ".join([*tokens[2:], *parenthetical])
    return last, first, other


def split_recent_name(name: str) -> tuple[str, str, str]:
    notes = re.findall(r"\(([^)]*)\)", name)
    cleaned = re.sub(r"\([^)]*\)", " ", name)
    cleaned = cleaned.strip(" ,")
    tokens = [token for token in cleaned.replace(",", " ").split() if token]
    if tokens and tokens[0].lower().rstrip(".") in {"mrs", "mr", "ms", "dr"}:
        tokens = tokens[1:]
    extra = " ".join(part for part in [*tokens[1:-1], *notes] if part)
    if not tokens:
        return "", "", extra
    if len(tokens) == 1:
        return tokens[0], "", extra
    return tokens[-1], tokens[0], extra


def blank_record() -> dict:
    return {key: "" for key in BURIAL_FIELDS}


def width_and_kind(field: str) -> tuple[int, str] | None:
    if field in CONTINUOUS_WIDTH:
        return CONTINUOUS_WIDTH[field], "continuous"
    if field in RESTART_WIDTH:
        return RESTART_WIDTH[field], "restart"
    if field in DOUBLE_WIDTH:
        return DOUBLE_WIDTH[field], "restart"
    if field in TRIPLE_WIDTH:
        return TRIPLE_WIDTH[field], "restart"
    return None


def lot_on_grid(field: str, row: str, lot: str) -> bool:
    spec = width_and_kind(field)
    if spec is None or not row.isdigit() or not lot.isdigit():
        return False
    row_number = int(row)
    lot_number = int(lot)
    if row_number not in (1, 2, 3):
        return False
    width, kind = spec
    if kind == "continuous":
        start = (row_number - 1) * width + 1
        return start <= lot_number <= start + width - 1
    return 1 <= lot_number <= width


def field_order() -> list[str]:
    singles = [chr(code) for code in range(ord("A"), ord("S") + 1)]
    doubles = [chr(code) * 2 for code in range(ord("A"), ord("K") + 1)]
    triples = [chr(code) * 3 for code in range(ord("A"), ord("L") + 1)]
    return singles + doubles + triples


def apply_date(record: dict, raw: str, source: str) -> None:
    iso, certainty, year = parse_date(raw, source)
    record["date_raw"] = raw
    record["date_iso"] = iso
    record["date_certainty"] = certainty
    record["date_year"] = year


def add_note(record: dict, text: str) -> None:
    if not text:
        return
    record["notes"] = f"{record['notes']}; {text}" if record["notes"] else text


def master_record(line: str, name: str, field: str, row: str, lot: str, suffix: str, date: str, extra: str = "") -> dict:
    record = blank_record()
    last, first, other = split_master_name(name)
    record.update(
        {
            "name_raw": name,
            "name_last": last,
            "name_first": first,
            "name_other": other,
            "name_order": "last_first",
            "cemetery": "chevra",
            "field": field.upper(),
            "row": row,
            "lot_number": lot,
            "lot_suffix": suffix.upper(),
            "lot_raw": f"{lot}{suffix.upper()}" if lot else "",
            "source": "master",
            "master_line": line,
        }
    )
    apply_date(record, date, "master")
    if extra:
        add_note(record, extra)
    record["on_map"] = "yes" if lot_on_grid(record["field"], row, lot) else "no"
    return record


def special_master(line: str) -> dict | None:
    specials = {
        "Freedman Sherry HeleneB 11/26/55": ("Freedman Sherry Helene", "B", "", "", "11/26/55", "The field letter B is printed against the first name. No row or lot."),
        "Hellman Judith D 1/16/85": ("Hellman Judith", "D", "", "", "1/16/85", "No row or lot."),
        "Levi Baby D": ("Levi Baby", "D", "", "", "", "No row, lot, or date."),
        "Lowenstein Shifra E 5/27/87": ("Lowenstein Shifra", "E", "", "", "5/27/87", "No row or lot."),
        "Maytin Jane R 2 8/4/19": ("Maytin Jane", "R", "2", "", "8/4/19", "No lot number."),
        "Pretsfelder Garry B 10/5/54": ("Pretsfelder Garry", "B", "", "", "10/5/54", "No row or lot."),
        "Stein Fetus E 8/13/97": ("Stein Fetus", "E", "", "", "8/13/97", "No row or lot."),
        "Weis Foetus C": ("Weis Foetus", "C", "", "", "", "No row, lot, or date."),
        "Zippert Foetus 1 C": ("Zippert Foetus 1", "C", "", "", "", "No row, lot, or date."),
        "Zippert Foetus 2 C": ("Zippert Foetus 2", "C", "", "", "", "No row, lot, or date."),
    }
    if line in specials:
        name, field, row, lot, date, note = specials[line]
        return master_record(line, name, field, row, lot, "", date, note)
    if line == "Lewin Hilda H I 10":
        record = master_record(line, "Lewin Hilda", "", "", "", "", "", "Field could be H or I, and 10 may be a lot. Not placed.")
        record["on_map"] = "no"
        return record
    return None


def parse_master(lines: list[str]) -> tuple[list[dict], list[dict], list[str]]:
    cut = next(
        index
        for index, line in enumerate(lines)
        if "Rosedale" in line or line.startswith("Rosenthal Gustav Rosdale")
    )
    chevra_lines = [
        line
        for line in lines[:cut]
        if not line.startswith("1,545")
    ]
    chevra = []
    missed = []
    for line in chevra_lines:
        special = special_master(line)
        if special:
            chevra.append(special)
            continue
        match = MASTER_LINE.match(line)
        if not match:
            missed.append(line)
            continue
        chevra.append(
            master_record(
                line,
                match.group("name"),
                match.group("field"),
                match.group("row"),
                match.group("lot"),
                match.group("suf") or "",
                (match.group("date") or "").strip(),
            )
        )

    rosedale = []
    for line in lines[cut:]:
        if line.startswith("1,545"):
            continue
        match = ROSEDALE_LINE.match(line)
        if not match:
            missed.append(line)
            continue
        rest = (match.group("rest") or "").strip()
        date = ""
        hebrew = ""
        dated = re.match(r"(\d{1,2}/\d{1,2}/\d{2,4}|\d{4})\s*(.*)$", rest)
        if dated:
            date, hebrew = dated.group(1), dated.group(2).strip()
        elif rest:
            hebrew = rest
        last, first, other = split_master_name(match.group("name"))
        record = blank_record()
        record.update(
            {
                "name_raw": match.group("name"),
                "name_last": last,
                "name_first": first,
                "name_other": other,
                "name_order": "last_first",
                "cemetery": "rosedale",
                "location_raw": f"Rosedale {match.group('plot')}",
                "hebrew_name": hebrew,
                "source": "master",
                "master_line": line,
                "on_map": "no",
            }
        )
        apply_date(record, date, "master")
        rosedale.append(record)
    return chevra, rosedale, missed


def parse_location(location: str) -> dict:
    original = location.strip(" .,;")
    lowered = original.lower()
    if not original:
        return {"kind": "missing"}
    if "elsewhere" in lowered or "denver" in lowered:
        return {"kind": "elsewhere", "text": original}
    if "king david" in lowered:
        return {"kind": "elsewhere", "text": original}
    text = re.sub(r"^fiels\b", "field", original, flags=re.IGNORECASE)
    text = re.sub(r"^field\b", "", text, flags=re.IGNORECASE)
    text = text.replace("*", " ").replace(".", " ").replace(",", " ")
    text = re.sub(r"\s+", " ", text).strip(" -")
    placed = re.match(
        r"^([A-Za-z]{1,3})\s*-?\s*row\s*(\d+)\s*-?\s*(?:lot|number|grave|#)\s*(\d+)\s*([A-Za-z])?\b",
        text,
        re.IGNORECASE,
    )
    if placed:
        return {
            "kind": "plot",
            "field": placed.group(1).upper(),
            "row": placed.group(2),
            "lot": placed.group(3),
            "suffix": (placed.group(4) or "").upper(),
        }
    row_only = re.match(r"^([A-Za-z]{1,3})\s*-?\s*row\s*(\d+)\b", text, re.IGNORECASE)
    if row_only:
        return {
            "kind": "row_only",
            "field": row_only.group(1).upper(),
            "row": row_only.group(2),
            "text": original,
        }
    return {"kind": "unparsed", "text": original}


def parse_recent(lines: list[str]) -> tuple[list[dict], list[str]]:
    records = []
    missed = []
    for line in lines:
        if line.upper().startswith("NAME "):
            continue
        match = RECENT_LINE.match(line)
        if not match:
            missed.append(line)
            continue
        last, first, other = split_recent_name(match.group("name"))
        location = parse_location(match.group("location"))
        record = blank_record()
        record.update(
            {
                "name_raw": match.group("name").strip(" ,"),
                "name_last": last,
                "name_first": first,
                "name_other": other,
                "name_order": "first_last",
                "source": "since_2020",
                "since_2020_line": line,
                "location_raw": match.group("location").strip(),
            }
        )
        apply_date(record, match.group("date"), "since_2020")
        kind = location["kind"]
        if kind == "plot":
            record.update(
                {
                    "cemetery": "chevra",
                    "field": location["field"],
                    "row": location["row"],
                    "lot_number": location["lot"],
                    "lot_suffix": location["suffix"],
                    "lot_raw": f"{location['lot']}{location['suffix']}",
                }
            )
        elif kind == "row_only":
            record.update({"cemetery": "chevra", "field": location["field"], "row": location["row"]})
            add_note(record, "Location has a field and row and no lot.")
        elif kind == "elsewhere":
            record["cemetery"] = "elsewhere"
            add_note(record, location["text"])
        elif kind == "missing":
            record["cemetery"] = "unknown"
            add_note(record, "No location in the 2020-2026 list.")
        else:
            record["cemetery"] = "unknown"
            add_note(record, f"Location was not parsed: {location['text']}")
        record["on_map"] = "yes" if lot_on_grid(record["field"], record["row"], record["lot_number"]) else "no"
        records.append(record)
    return records, missed


def same_plot(left: dict, right: dict) -> bool:
    return (
        left["field"]
        and left["field"] == right["field"]
        and left["row"] == right["row"]
        and left["lot_number"] == right["lot_number"]
        and left["lot_suffix"] == right["lot_suffix"]
    )


def merge(master: dict, recent: dict, issues: list[dict]) -> None:
    master["source"] = "both"
    master["since_2020_line"] = recent["since_2020_line"]
    master["location_raw"] = recent["location_raw"]
    if recent["name_other"] and recent["name_other"] not in master["name_other"]:
        master["name_other"] = " ".join(
            part for part in (master["name_other"], recent["name_other"]) if part
        )
    if recent["name_raw"] and recent["name_raw"] != master["name_raw"]:
        master["name_raw"] = recent["name_raw"]
        master["name_order"] = "first_last"
    if recent["date_iso"] and recent["date_iso"] != master["date_iso"]:
        if master["date_raw"]:
            add_note(master, f"Master list date: {master['date_raw']}.")
        master["date_raw"] = recent["date_raw"]
        master["date_iso"] = recent["date_iso"]
        master["date_certainty"] = recent["date_certainty"]
        master["date_year"] = recent["date_year"]
    elif not master["date_iso"] and recent["date_iso"]:
        master["date_raw"] = recent["date_raw"]
        master["date_iso"] = recent["date_iso"]
        master["date_certainty"] = recent["date_certainty"]
        master["date_year"] = recent["date_year"]
    if (
        recent["field"]
        and not recent["lot_number"]
        and recent["field"] == master["field"]
        and recent["row"] == master["row"]
    ):
        add_note(master, "2020-2026 list gives this field and row and no lot.")
    elif recent["field"] and not same_plot(master, recent):
        issues.append(
            {
                "severity": "review",
                "kind": "location_conflict",
                "source_line": f"{master['master_line']} || {recent['since_2020_line']}",
                "detail": (
                    f"{master['name_last']}, {master['name_first']}: master list "
                    f"{master['field']} row {master['row']} lot {master['lot_raw']}; "
                    f"2020-2026 list {recent['field']} row {recent['row']} lot {recent['lot_raw']}. "
                    "The map uses the 2020-2026 list."
                ),
            }
        )
        add_note(
            master,
            f"Master list location: {master['field']} row {master['row']} lot {master['lot_raw']}.",
        )
        master["field"] = recent["field"]
        master["row"] = recent["row"]
        master["lot_number"] = recent["lot_number"]
        master["lot_suffix"] = recent["lot_suffix"]
        master["lot_raw"] = recent["lot_raw"]
        master["cemetery"] = recent["cemetery"] or master["cemetery"]
    elif recent["cemetery"] == "elsewhere":
        issues.append(
            {
                "severity": "review",
                "kind": "location_conflict",
                "source_line": f"{master['master_line']} || {recent['since_2020_line']}",
                "detail": (
                    f"{master['name_last']}, {master['name_first']} has a Chevra grave in the "
                    f"master list and is marked {recent['location_raw']} in the later list. "
                    "The map keeps the master-list grave."
                ),
            }
        )
        add_note(master, f"2020-2026 list says: {recent['location_raw']}.")
    master["on_map"] = "yes" if lot_on_grid(master["field"], master["row"], master["lot_number"]) else "no"


def match_lists(chevra: list[dict], recent: list[dict], issues: list[dict]) -> list[dict]:
    by_name = defaultdict(list)
    for record in chevra:
        by_name[(norm_name(record["name_last"]), norm_name(record["name_first"]))].append(record)
    recent_only = []
    for record in recent:
        key = (norm_name(record["name_last"]), norm_name(record["name_first"]))
        candidates = [item for item in by_name.get(key, []) if item["source"] != "both"]
        if not candidates:
            recent_only.append(record)
            continue

        def score(candidate: dict) -> int:
            value = 0
            if same_plot(candidate, record):
                value += 10
            if candidate["date_iso"] and candidate["date_iso"] == record["date_iso"]:
                value += 5
            else:
                left = month_day(candidate["date_raw"])
                right = month_day(record["date_raw"])
                if left and right and left == right:
                    value += 2
            return value

        ranked = sorted(candidates, key=score, reverse=True)
        best = ranked[0]
        best_score = score(best)
        tied = [item for item in ranked if score(item) == best_score]
        if len(tied) > 1:
            issues.append(
                {
                    "severity": "review",
                    "kind": "ambiguous_match",
                    "source_line": record["since_2020_line"],
                    "detail": (
                        f"{record['name_raw']} matches {len(tied)} master-list rows "
                        "equally. Left as its own row."
                    ),
                }
            )
            recent_only.append(record)
            continue
        merge(best, record, issues)
    return match_by_plot_and_date(chevra, recent_only, issues)


def first_names_close(left: str, right: str) -> bool:
    left, right = norm_name(left), norm_name(right)
    if not left or not right:
        return False
    if left == right or left.startswith(right) or right.startswith(left):
        return True
    return len(left) >= 3 and len(right) >= 3 and left[:3] == right[:3]


def match_by_plot_and_date(chevra: list[dict], recent_only: list[dict], issues: list[dict]) -> list[dict]:
    """Catch the same grave when the spelling differs, or the later list omits the lot."""
    by_plot = defaultdict(list)
    for record in chevra:
        if record["source"] == "both":
            continue
        if record["field"] and record["row"] and record["lot_number"] and record["date_iso"]:
            key = (record["field"], record["row"], record["lot_number"], record["lot_suffix"], record["date_iso"])
            by_plot[key].append(record)

    still = []
    for record in recent_only:
        if not (record["field"] and record["row"] and record["lot_number"] and record["date_iso"]):
            still.append(record)
            continue
        key = (record["field"], record["row"], record["lot_number"], record["lot_suffix"], record["date_iso"])
        candidates = [item for item in by_plot.get(key, []) if item["source"] != "both"]
        if len(candidates) != 1:
            still.append(record)
            continue
        master = candidates[0]
        recent_name = record["name_raw"]
        names_differ = norm_name(master["name_last"]) != norm_name(record["name_last"]) or norm_name(
            master["name_first"]
        ) != norm_name(record["name_first"])
        merge(master, record, issues)
        if names_differ:
            add_note(master, f"2020-2026 list spells the name {recent_name}.")
            issues.append(
                {
                    "severity": "review",
                    "kind": "spelling",
                    "source_line": f"{master['master_line']} || {record['since_2020_line']}",
                    "detail": (
                        f"Same grave and date, different spelling. Master list {master['master_line']}. "
                        f"Later list {recent_name}."
                    ),
                }
            )

    leftover = []
    for record in still:
        if not (record["field"] and record["row"] and record["date_iso"]) or record["lot_number"]:
            leftover.append(record)
            continue
        candidates = [
            item
            for item in chevra
            if item["source"] != "both"
            and item["field"] == record["field"]
            and item["row"] == record["row"]
            and item["date_iso"] == record["date_iso"]
            and item["lot_number"]
            and squash_name(item["name_last"]) == squash_name(record["name_last"])
            and first_names_close(item["name_first"], record["name_first"])
        ]
        if len(candidates) != 1:
            leftover.append(record)
            continue
        master = candidates[0]
        add_note(
            master,
            f"2020-2026 list says {record['name_raw']} and does not give a lot. "
            f"The map uses master-list lot {master['lot_raw']}. First names: "
            f"{master['name_first']} / {record['name_first']}.",
        )
        issues.append(
            {
                "severity": "review",
                "kind": "near_name",
                "source_line": f"{master['master_line']} || {record['since_2020_line']}",
                "detail": (
                    f"{master['name_last']}: master list {master['name_first']}, later list "
                    f"{record['name_first']}. Same field, row, and date. The later list has no lot, "
                    f"so the map uses lot {master['lot_raw']}."
                ),
            }
        )
        merge(master, record, issues)
    return leftover


def assign_ids(records: list[dict]) -> None:
    for number, record in enumerate(records, start=1):
        record["burial_id"] = f"b{number:04d}"


def build_plots(burials: list[dict]) -> list[dict]:
    plots = []
    index = {}
    for field in field_order():
        spec = width_and_kind(field)
        if spec is None:
            continue
        width, kind = spec
        for row in (1, 2, 3):
            start = (row - 1) * width + 1 if kind == "continuous" else 1
            for lot in range(start, start + width):
                plot = {
                    "field": field,
                    "row": str(row),
                    "lot_number": str(lot),
                    "lot_suffix": "",
                    "lots_per_row": str(width),
                    "numbering": kind,
                    "status": "empty",
                    "burial_id": "",
                    "_ids": [],
                }
                plots.append(plot)
                index[(field, str(row), str(lot), "")] = plot

    for burial in burials:
        if burial["on_map"] != "yes":
            continue
        key = (burial["field"], burial["row"], burial["lot_number"], burial["lot_suffix"])
        plot = index.get(key)
        if plot is None and burial["lot_suffix"]:
            spec = width_and_kind(burial["field"])
            width, kind = spec
            plot = {
                "field": burial["field"],
                "row": burial["row"],
                "lot_number": burial["lot_number"],
                "lot_suffix": burial["lot_suffix"],
                "lots_per_row": str(width),
                "numbering": kind,
                "status": "empty",
                "burial_id": "",
                "_ids": [],
            }
            plots.append(plot)
            index[key] = plot
        if plot is None:
            continue
        plot["_ids"].append(burial["burial_id"])
        plot["status"] = "occupied"

    for plot in plots:
        plot["burial_id"] = ";".join(plot.pop("_ids"))
    return plots


def plot_issues(plots: list[dict], burials: list[dict]) -> list[dict]:
    by_id = {burial["burial_id"]: burial for burial in burials}
    issues = []
    for plot in plots:
        ids = [item for item in plot["burial_id"].split(";") if item]
        if len(ids) < 2 or plot["lot_suffix"]:
            continue
        names = [
            f"{by_id[item]['name_last']}, {by_id[item]['name_first']}".strip(", ")
            for item in ids
        ]
        issues.append(
            {
                "severity": "review",
                "kind": "shared_lot",
                "source_line": " | ".join(by_id[item]["master_line"] or by_id[item]["since_2020_line"] for item in ids),
                "detail": (
                    f"{plot['field']} row {plot['row']} lot {plot['lot_number']} has "
                    f"{len(ids)} names and no letter suffix: {'; '.join(names)}."
                ),
            }
        )
    return issues


def off_grid_issues(burials: list[dict]) -> list[dict]:
    issues = []
    for burial in burials:
        if burial["cemetery"] != "chevra" or burial["on_map"] == "yes":
            continue
        issues.append(
            {
                "severity": "review",
                "kind": "off_grid",
                "source_line": burial["master_line"] or burial["since_2020_line"],
                "detail": (
                    f"{burial['name_last']}, {burial['name_first']} is not on the working grid "
                    f"({burial['field'] or 'no field'} row {burial['row'] or '-'} "
                    f"lot {burial['lot_raw'] or '-'})."
                ),
            }
        )
    return issues


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def person_name(burial: dict) -> str:
    if burial["name_last"] and burial["name_first"]:
        return f"{burial['name_last']}, {burial['name_first']}"
    return burial["name_raw"]


def band_for(field: str) -> str:
    if len(field) == 1 and field <= "J":
        return "single-early"
    if len(field) == 1:
        return "single-late"
    if len(field) == 2:
        return "double"
    return "triple"


def write_web(burials: list[dict], plots: list[dict]) -> None:
    people = []
    for burial in burials:
        people.append(
            {
                "id": burial["burial_id"],
                "name": person_name(burial),
                "last": burial["name_last"],
                "first": burial["name_first"],
                "other": burial["name_other"],
                "date": burial["date_iso"] or burial["date_raw"],
                "rawDate": burial["date_raw"],
                "certainty": burial["date_certainty"],
                "field": burial["field"],
                "row": burial["row"],
                "lot": burial["lot_raw"] or burial["lot_number"],
                "suffix": burial["lot_suffix"],
                "onMap": burial["on_map"] == "yes",
                "cemetery": burial["cemetery"],
                "notes": burial["notes"],
                "hebrew": burial["hebrew_name"],
                "where": burial["location_raw"],
                "master": burial["master_line"],
                "recent": burial["since_2020_line"],
            }
        )
    web_plots = []
    for plot in plots:
        web_plots.append(
            {
                "field": plot["field"],
                "row": int(plot["row"]),
                "lot": int(plot["lot_number"]),
                "suffix": plot["lot_suffix"],
                "status": plot["status"],
                "ids": [item for item in plot["burial_id"].split(";") if item],
            }
        )
    fields = []
    for code in field_order():
        spec = width_and_kind(code)
        if spec is None:
            continue
        width, kind = spec
        fields.append(
            {
                "code": code,
                "width": width,
                "numbering": kind,
                "band": band_for(code),
                "assumed": code in {"KK", "LLL"},
            }
        )
    payload = {"people": people, "plots": web_plots, "fields": fields}
    destination = ROOT / "web" / "cemetery.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def numbering_issues(issues: list[dict]) -> None:
    for index, issue in enumerate(issues, start=1):
        issue["issue_id"] = f"q{index:04d}"


def main() -> None:
    issues: list[dict] = []
    chevra, rosedale, master_missed = parse_master(lines_of(MASTER_PDF))
    recent, recent_missed = parse_recent(lines_of(RECENT_PDF))
    for line in master_missed:
        issues.append(
            {
                "severity": "block",
                "kind": "unparsed",
                "source_line": line,
                "detail": "Master-list line was not parsed.",
            }
        )
    for line in recent_missed:
        issues.append(
            {
                "severity": "block",
                "kind": "unparsed",
                "source_line": line,
                "detail": "2020-2026 line was not parsed.",
            }
        )
    recent_only = match_lists(chevra, recent, issues)
    burials = chevra + recent_only + rosedale
    assign_ids(burials)
    assumed = sum(1 for burial in burials if burial["date_certainty"] == "assumed_century")
    for burial in burials:
        if burial["cemetery"] == "elsewhere":
            issues.append(
                {
                    "severity": "review",
                    "kind": "buried_elsewhere",
                    "source_line": burial["since_2020_line"] or burial["master_line"],
                    "detail": f"{burial['name_raw']} is not drawn on the Chevra map.",
                }
            )
    plots = build_plots(burials)
    issues.extend(plot_issues(plots, burials))
    issues.extend(off_grid_issues(burials))

    on_map = sum(1 for burial in burials if burial["on_map"] == "yes")
    summary = (
        f"Chevra rows from the master list: {len(chevra)}. "
        f"Printed total: 1,545 as of 12/22/2022. "
        f"Rosedale rows: {len(rosedale)}. "
        f"2020-2026 rows not matched to the master list: {len(recent_only)}. "
        f"Rows matched to both lists: {sum(1 for burial in burials if burial['source'] == 'both')}. "
        f"Drawn on the working grid: {on_map}. "
        f"Dates with an assumed century: {assumed}. "
        f"Plot squares: {len(plots)}."
    )
    issues.insert(
        0,
        {
            "severity": "review",
            "kind": "summary",
            "source_line": "",
            "detail": summary,
        },
    )
    numbering_issues(issues)
    write_csv(DATA / "burials.csv", BURIAL_FIELDS, burials)
    write_csv(DATA / "plots.csv", PLOT_FIELDS, plots)
    write_csv(DATA / "qa-issues.csv", QA_FIELDS, issues)
    write_web(burials, plots)
    print(summary)
    print(f"QA issues: {len(issues)}")
    for kind in ("unparsed", "location_conflict", "ambiguous_match", "off_grid", "shared_lot"):
        rows = [issue for issue in issues if issue["kind"] == kind]
        print(f"  {kind}: {len(rows)}")
        for issue in rows[:12]:
            print(f"    {issue['detail']}")


if __name__ == "__main__":
    main()
