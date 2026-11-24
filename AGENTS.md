# Chevra Ahavas Chesed Cemetery

Agent guide for this repository. Read this before changing data, the map, or the printable index.

## Current state

The first schematic is built. `data/`, `web/`, and the PDF script are in the repo. The assumptions behind them are at the top of `open-questions.md`. None of those assumptions is confirmed on the ground. When one of them is wrong, change it in that file, change the matching rule in `scripts/build_dataset.py`, and rebuild. Do not silently treat the schematic as surveyed.

`scripts/build_dataset.py` reads the two source PDFs and writes `data/burials.csv`, `data/plots.csv`, `data/qa-issues.csv`, and `web/cemetery.json`. `scripts/build_pdf.py` reads the CSVs and writes `print/chevra-ahavas-chesed.pdf`. That PDF is gitignored. The CSVs and `web/cemetery.json` are committed. Do not hand-edit the generated files.

Rebuild from the repository root:

```
python scripts/build_dataset.py
python scripts/build_pdf.py
```

The dataset script needs `pdfplumber`. The PDF script needs `reportlab`, plus Arial on Windows or Liberation Sans on Linux. There is no requirements file.

`.github/workflows/build.yml` runs those two scripts on every push and pull request. The job fails when a rebuild changes the committed CSVs or `web/cemetery.json`. It uploads `data/burials.csv`, `data/plots.csv`, `data/qa-issues.csv`, `web/cemetery.json`, and `print/chevra-ahavas-chesed.pdf` as artifacts, kept for 90 days. When the repository is public, that workflow also publishes `web/` to GitHub Pages at `https://hroskes.github.io/chevra-map/`. On the free plan, Pages runs from a public repository, so the deploy job stays off while this repository is private.

The summary row in `data/qa-issues.csv` is the count to trust after a rebuild. The current file says: 1,547 Chevra rows from the master list, against the printed total of 1,545 as of 12/22/2022; 130 Rosedale rows; 74 rows from the 2020–2026 list that did not match a master row; 64 rows matched to both lists; 1,598 drawn on the working grid; 1,397 dates with an assumed century; 1,859 plot squares. The burial file has 1,751 rows: 1,614 Chevra, 130 Rosedale, 5 elsewhere, and 2 with no location. Sixteen Chevra rows are off the working grid. Twenty-four Chevra rows have a letter suffix; those people are listed under "Not on a square" rather than inside the numbered square. The plot file has 1,573 occupied squares and 286 empty squares, across 42 fields. The QA file has 59 rows, all `review`: 24 shared lots, 16 off-grid, 6 location conflicts, 6 spelling matches, 5 buried elsewhere, 1 near-name match (Harry / Harvey Honick), and the summary. No source line failed to parse.

The interactive map is `web/index.html`. It loads `web/cemetery.json`. From the repository root, run `python -m http.server` and open `web/index.html`. The main page draws every lot in the same arrangement as the printable overview: entrance at the top, A–J beside Shaari Zion, K–S continuing down, AA–JJ and AAA–KKK to the right, and the plot listing board between HH and II, beside S. KK and LLL stay off that page. A field name opens that field. Search by name, or click a lot, for the name, date, and field/row/lot. Occupied and empty lots look different. Nothing is marked reserved, because no named list has identified a held lot. KK and LLL are in the field list, with a dashed border, after JJ and after KKK. A narrow screen puts the map above the field list, and the map scrolls sideways. The satellite photo is not on the page. It shows field bands, not graves.

The printable map is a landscape letter PDF: a cover, an overview with the entrance at the top, a list of Chevra records that are not on a square, one or more fields per page, and an alphabetical index. The overview follows `cemetery map.png`, with the plot listing board one field tall between HH and II, beside S. KK and LLL are omitted there and each has its own field page, marked as an assumed place. The index has Chevra burials, then a separate list for Rosedale, elsewhere, and unknown locations. Empty lots stay on the field pages. Each field page names the fields toward the entrance, toward the far end, and to either side.

## Goal

The three deliverables are the burial CSV, the interactive map, and the printable index. The CSV is the source for both maps. A change to a name, a date, or a lot starts in the parser or the source lists, then both maps are rebuilt.

## Source files

These three files are the original sources. Leave their bytes unchanged. A later commit may move them with `git mv` only.

| File | Role |
| --- | --- |
| `cemetery map.png` | Satellite photo of Chevra Ahavas Chesed Cemetery on Liberty Road, with colored field bands. |
| `master list of departed poorly formatted.pdf` | Alphabetical burials, about the 1950s through 2022. Printed total: "1,545 as of 12/22/2022". |
| `list of departed since 2020 (11-10-26).pdf` | Chronological burials from Paula Junker on 3/26/20 through Morris Lasson on 7/17/2026. |

### How the lists are written

Master list, one person per line, last name first:

`Abosch Joseph AA 2 6 10/21/76`

Meaning: name, field, row, lot, date of death. The date is often missing or partial (`3/??/94`, `60`, `8/8/`). Lot values sometimes have a letter suffix (`11A`, `1A`, `15A`).

The same file ends with a separate Rosedale block. Those lines use a different plot style (`Rosedale B3`) and sometimes a Hebrew name. One line spells it `Rosdale`. Keep Rosedale rows in the CSV and keep them off the Chevra map.

Recent list, first name first, with a header `NAME Date of Death Location of Grave`:

`Paula Junker 3/26/20 Field R, Row 3, Lot 10`

The same person can appear in both files under opposite name order, sometimes with a nickname:

- Master: `Baer Adolph R 3 17 9/6/20`
- Recent: `Adolph (Eddie) Baer 9/6/20 Field R, Row 3, Lot 17`

Location text in the recent list is inconsistent: `Field JJJ-Row 3-#6`, `Number 6`, `Grave 11`, `Field AAA* Row1 lot 14`, `Field KK, Row 2. Lot 6`, `JJ,,`, and the typo `Fiels`. Some people have no location. Some say `Buried Elsewhere`, `Buried in Denver, CO`, or `King David Cemetery`.

Infant and fetus lines exist (`Levi Baby D`, `Weis Foetus C`, `Stein Fetus E`, `Zippert Foetus 1 C`). Keep them. A few master lines omit the row or the lot. The parser keeps those rows and leaves them off the grid. See `special_master` in `scripts/build_dataset.py`.

## Cemetery layout

Chevra Ahavas Chesed sits on Liberty Road, between Beth El Cemetery and Shaari Zion Cemetery. The entrance and field A are at the Liberty Road end. The plot-listing display board is toward the far end.

Fields used in the master list:

- Single letters A through S
- Double letters AA through JJ
- Triple letters AAA through KKK

The map legend draws wider ranges (K through Z, AA through ZZ, AAA through ZZZ). Those extra letters do not appear in the burial lists. The schematic draws A–S, AA–KK, and AAA–LLL. KK and LLL come from the 2020–2026 list and from the working assumptions, not from the master list.

Color bands on the source image, and the same colors on both maps:

- Blue: single letters A through J
- Green: single letters continuing through S (the legend text says K through Z)
- Orange: double letters (the legend text says AA through ZZ; the lists use AA through JJ). The interactive map and the field pages also draw KK.
- Pink: triple letters (the legend text says AAA through ZZZ; the lists use AAA through KKK). The interactive map and the field pages also draw LLL.
- Red: outline of the whole cemetery

KK and LLL were added after the source photo. The printable overview leaves them off. The interactive map lists KK after JJ and LLL after KKK, and each has a field page. That placement is assumption 4 in `open-questions.md`. Do not move either field unless that assumption is answered.

### Lots per row (Stanley)

- Single-letter fields: 18 lots per row
- Double-letter and triple-letter fields: 14 lots per row

The lists show three rows (1, 2, and 3) in every field that has enough burials to tell. Stanley did not state the row count. The working grid is three rows. Ask before adding a fourth.

Stanley's cap fits the double-letter fields, the triple-letter fields, and single-letter fields P, Q, R, and S (max lot 18, numbering restarts each row). One recorded exception: HH row 2 lot 19, which is off the grid.

Fields A through I restart each row at 1. The highest lot number is the row length, and it is shorter than 18. Several rows are filled from 1 through that number, so the unused tail is not a hidden run of lots out to 18. The schematic uses these lengths. Do not widen A–I to 18 unless a visit says the empty tail is real.

| Field | Lots per row | Numbered plots (3 rows) |
| --- | --- | --- |
| A | 14 | 42 |
| B | 12 | 36 |
| C | 12 | 36 |
| D | 13 | 39 |
| E | 14 | 42 |
| F | 14 | 42 |
| G | 16 | 48 |
| H | 16 | 48 |
| I | 15 | 45 |

That is 378 numbered plots. A letter suffix (`10A`, `1A`) is an extra grave beside that number. Those extras are concentrated in B (7), with a few in C, D, E, and F. The map does not draw the suffix name inside the numbered square. It lists that person under "Not on a square" on the field page. A handful of numbers also carry two unsuffixed names. Those share the square and are listed in `data/qa-issues.csv` as `shared_lot`.

Fields J through O do not restart. Each row continues the previous row's numbers.

- K is 14 per row and continuous: row 1 is 1–14, row 2 is 15–28, row 3 is 29–42. No number is shared across rows. Lots 2 and 33 are empty. Suffix graves: 14A, 15A, 28A, 29A.
- L, M, N, and O are 16 per row and continuous: 1–16, 17–32, 33–48. L fills all 48. M is missing 22 and has 12A. N is missing 46. O fills 1–47, so only 48 is absent.
- J is the same 14-wide continuous shape, and it is the messy one. The working assumption, pending a visit, is that two master-list lines are mis-filed: Natalie Greenfield (the other name on J row 1 lot 11 is Julius Eick, and Olga Eick is lot 12; the 2020–2026 list puts Natalie at JJ row 1 lot 11) and Susan Roedel (she is the only name on J row 1 lot 15; the later list puts her at S row 1 lot 15). Nathan Prager is J row 2 lot 15, with Bertha Neuhof at 15A. Under that assumption row 1 is 1–14 plus 14A. Row 2 occupies 15–22 and 24–27, plus 15A, so 23 and 28 are empty, and it also contains Esther Birnbaum at lot 3, which is already Eugen Baer's lot on row 1. Row 3 is 29–42 plus 42A, and Hans Morgenroth at 24A, while lot 24 itself is on row 2. Esther and Hans are off the grid. See `open-questions.md`.

Keep the printed lot. The continuous fields are the map's numbering, not a sequence to fold back into 1–18.

The other disagreements, where the 2020–2026 list supplies the square, are Joseph Cotton (JJ row 1 lot 7), Michael Eisenberg (JJ row 1 lot 18, which is off the 14-lot grid), Doris Fox (P row 3 lot 6, already David Berzon's lot), and Sara Kovacs (JJ row 3 lot 4).

### Empty and reserved lots

Many lots have no burial. Some empty lots are reserved for a surviving spouse. The source files do not say which empties are reserved.

Represent every lot in the confirmed grid:

- `occupied` when a burial is recorded
- `empty` when no burial is recorded
- `reserved` only when Stanley or the cemetery has identified that lot as held

The current plot file uses only `occupied` and `empty`. Adjacent same-surname burials are common. That pattern can suggest a reserved neighbor. The current QA file does not list those suggestions. If they are added, they are review notes. Mark a lot `reserved` only from a named source, not from the name pattern alone.

## Find a Grave

Skip a Find a Grave reconciliation.

Find a Grave does not publish a public read API. The site has an internal GraphQL endpoint, and third-party tools call it, but that is not a documented API. Ancestry's terms (Find a Grave is an Ancestry service) prohibit automated or programmatic access beyond ordinary human use. FamilySearch offers a limited "Find a Grave Index" through its developer platform (collection 2221801). That index is thinner than the memorial pages, requires FamilySearch credentials, and is a poor fit for plot-by-plot checking.

Do not scrape Find a Grave, and do not call its undocumented endpoint. A person may look up individual public memorials by hand and add discrepancies to `data/qa-issues.csv`.

## Repository

```
AGENTS.md
.cursor/rules/chevra-cemetery.mdc
open-questions.md
.gitignore
.github/workflows/build.yml   # rebuild, artifacts, and GitHub Pages when public
cemetery map.png
list of departed since 2020 (11-10-26).pdf
master list of departed poorly formatted.pdf
scripts/build_dataset.py       # PDFs -> CSVs and web/cemetery.json
scripts/build_pdf.py            # CSVs -> print/chevra-ahavas-chesed.pdf
data/burials.csv                # one row per person
data/plots.csv                  # one row per lot on the working grid
data/qa-issues.csv              # summary, conflicts, shared lots, off-grid rows
web/index.html                  # interactive map; open it from a local web server
web/cemetery.json               # generated by scripts/build_dataset.py
print/chevra-ahavas-chesed.pdf  # generated; not committed
```

## Canonical CSV

`data/burials.csv` columns:

- `burial_id` — stable id assigned by the parser (`b0001` onward, in file order)
- `name_raw` — the name text as printed
- `name_last`, `name_first`, `name_other` — split when the split is clear; leave blank when it is not
- `name_order` — `last_first` (master list) or `first_last` (recent list). A merged row takes `first_last` when the recent name differs
- `date_raw`
- `date_iso` — `YYYY-MM-DD` when the day is known, otherwise blank
- `date_certainty` — `exact`, `assumed_century`, `year`, `partial`, or `unknown`
- `date_year` — expanded year when one can be read, otherwise blank
- `on_map` — `yes` when the canonical field, row, and lot fall on the working grid
- `cemetery` — `chevra`, `rosedale`, `elsewhere`, or `unknown`
- `field` — uppercase letters, blank when the person is not in a Chevra field
- `row` — integer text, or blank
- `lot_raw` — printed lot, including a suffix
- `lot_number` — integer part, or blank
- `lot_suffix` — blank, or the trailing letters (`A`)
- `location_raw` — the recent-list location phrase, or the Rosedale plot phrase
- `hebrew_name` — Rosedale lines that include one
- `source` — `master`, `since_2020`, or `both`
- `master_line` — original master line when present
- `since_2020_line` — original recent line when present
- `notes`

Date rules:

- Always keep `date_raw`.
- In the recent list, two-digit years 20–26 are 2020–2026 and `date_certainty` is `exact`.
- In the master list, two-digit years are expanded and `date_certainty` is `assumed_century` when the day is complete: 50–99 are 1950–1999, 27–49 are 1927–1949, and 00–26 are 2000–2026.
- A four-digit year is `exact`.
- Partial dates and year-only dates stay out of `date_iso`.
- `date_year` holds the expanded year when one can be read, including year-only dates.

Matching rule for `source=both`: same first and last name after swapping order. If several master rows share that name, the field, row, lot, or date decides which one. A nickname in parentheses (`Eddie`) does not block a match. The same field, row, lot, and date are one person even when the spelling differs by a letter (`Kaufman` / `Kaufmann`, `Guttman` / `Guttmann`). When the later list gives the field and row and no lot, and the first names are close, the master-list lot is kept (`Harry` / `Harvey Honick`). Other names that differ by a letter stay as two rows. When the lines disagree, the 2020–2026 list supplies the map location, both original lines are kept, and a QA issue is written. When both dates are a full day, `date_iso` uses the recent list's date. An ambiguous name match is left as its own row.

`data/plots.csv` columns:

- `field`, `row`, `lot_number`, `lot_suffix`
- `lots_per_row` — the working width for that field
- `numbering` — `restart` or `continuous`
- `status` — `occupied` or `empty` (`reserved` waits for a named list)
- `burial_id` — blank when empty; more than one id, separated by semicolons, when several people share the lot

Letter-suffix plots are extra rows, created only when a burial uses that suffix and the lot number sits in that row's block. The base lot is still in the grid. A suffix whose number falls outside the block stays in the burial file and does not get a plot row.

`data/qa-issues.csv` columns:

- `issue_id`, `severity` (`block` or `review`), `kind`, `source_line`, `detail`

The first row is a `summary`. A source line that does not parse is a `block`. The current file has none. These are `review`: `location_conflict`, `spelling`, `near_name`, `ambiguous_match`, `buried_elsewhere`, `shared_lot`, and `off_grid`. Shared lots and off-grid lots stay visible. They do not stop the schematic.

The master list's printed total is 1,545 Chevra names as of 12/22/2022. The summary row reports the parsed Chevra count, the Rosedale count, and the elsewhere count beside that figure. The parser currently counts 1,547 Chevra rows in the master list, two more than the printed total. Leave that difference visible. Do not drop two rows to force the printed number.

## Later changes

The first pass is done. Further work replaces an assumption with an answer.

1. Write the answer under the question in `open-questions.md` and set that item to answered. Leave the question in place.
2. If the answer changes a width, a row count, a placement, or who is drawn, change `scripts/build_dataset.py` to match. The widths live in `RESTART_WIDTH`, `CONTINUOUS_WIDTH`, `DOUBLE_WIDTH`, and `TRIPLE_WIDTH`.
3. Rebuild the CSVs, `web/cemetery.json`, and the PDF.
4. Commit that step. A step is one coherent change to the data, the web map, or the printable map.

Ask before adding a fourth row. Do not move KK or LLL, and do not widen A–I to 18, unless the matching item in `open-questions.md` is answered. A visit is how most of those items get answered.

## Open questions

The running list is `open-questions.md`. Add a new item there when the lists do not settle something.

## Working rules

- Commit after each step. A step is one coherent change to the data, the web map, or the printable map. Do not leave finished work uncommitted.
- `print/chevra-ahavas-chesed.pdf` is rebuilt by `scripts/build_pdf.py` and is not committed. The two source PDFs stay in the repository.
- Preserve every source string in a `*_raw` column.
- Keep a person when the date or the location is incomplete.
- Do not scrape Find a Grave.
- Do not edit the three source files.
- Mark a lot reserved only from a named source.
- Use the satellite photo for field bands. It does not locate a grave inside a field.
