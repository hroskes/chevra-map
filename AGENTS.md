# Chevra Ahavas Chesed Cemetery

Agent guide for this repository. Read this before changing data, the map, or the printable index.

## Goal

Build three deliverables from the committed source files:

1. A well-formatted CSV of burials, including empty lots once the grid is confirmed.
2. An interactive map web app for finding a grave.
3. A readable PDF map with symbols, numbers, and an alphabetical index, in the spirit of an amusement-park map.

Do the CSV first. The map and the PDF both depend on it. Pause before drawing any field whose lot numbering disagrees with Stanley's counts.

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

Infant and fetus lines exist (`Levi Baby D`, `Weis Foetus C`, `Stein Fetus E`, `Zippert Foetus 1 C`). Keep them.

## Cemetery layout

Chevra Ahavas Chesed sits on Liberty Road, between Beth El Cemetery and Shaari Zion Cemetery. The entrance and field A are at the Liberty Road end. The plot-listing display board is toward the far end.

Fields used in the master list:

- Single letters A through S
- Double letters AA through JJ
- Triple letters AAA through KKK

The map legend draws wider ranges (K through Z, AA through ZZ, AAA through ZZZ). Those extra letters do not appear in the burial lists. Draw the letters that exist.

Color bands on the source image:

- Blue: single letters A through J
- Green: single letters continuing through S (the legend text says K through Z)
- Orange: double letters (the legend text says AA through ZZ; the lists use AA through JJ)
- Pink: triple letters (the legend text says AAA through ZZZ; the lists use AAA through KKK)
- Red: outline of the whole cemetery

LLL was added after this image was made. The recent list also contains field KK (2025–2026), which is absent from the master list and is not labeled on the image. Ask before drawing KK or LLL.

### Lots per row (Stanley)

- Single-letter fields: 18 lots per row
- Double-letter and triple-letter fields: 14 lots per row

The lists show three rows (1, 2, and 3) in every field that has enough burials to tell. Stanley did not state the row count. Use three rows as the working grid, and ask before adding a fourth.

Stanley's cap fits the double-letter fields, the triple-letter fields, and single-letter fields P, Q, R, and S (max lot 18, numbering restarts each row). One recorded exception: HH row 2 lot 19.

Fields A through I restart each row at 1. The highest lot number is the row length, and it is shorter than 18. Several rows are filled from 1 through that number, so the unused tail is not a hidden run of lots out to 18.

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

That is 378 numbered plots. A letter suffix (`10A`, `1A`) is an extra grave beside that number. Those extras are concentrated in B (7), with a few in C, D, E, and F. The map does not draw the suffix name inside the numbered square. It lists that person under “Not on a square” on the field page. A handful of numbers also carry two unsuffixed names.

Fields J through O do not restart. Each row continues the previous row's numbers.

- K is 14 per row and continuous: row 1 is 1–14, row 2 is 15–28, row 3 is 29–42. No number is shared across rows. Lots 2 and 33 are empty. Suffix graves: 14A, 15A, 28A, 29A.
- L, M, N, and O are 16 per row and continuous: 1–16, 17–32, 33–48. L fills all 48. M is missing 22 and has 12A. N is missing 46. O fills 1–47, so only 48 is absent.
- J is the same 14-wide continuous shape, and it is the messy one. The working assumption, pending a visit, is that two master-list lines are mis-filed: Natalie Greenfield (the other name on J row 1 lot 11 is Julius Eick, and Olga Eick is lot 12; the 2020–2026 list puts Natalie at JJ row 1 lot 11) and Susan Roedel (she is the only name on J row 1 lot 15; the later list puts her at S row 1 lot 15). Nathan Prager is J row 2 lot 15, with Bertha Neuhof at 15A. Under that assumption row 1 is 1–14 plus 14A. Row 2 occupies 15–22 and 24–27, plus 15A, so 23 and 28 are empty, and it also contains Esther Birnbaum at lot 3, which is already Eugen Baer's lot on row 1. Row 3 is 29–42 plus 42A, and Hans Morgenroth at 24A, while lot 24 itself is on row 2. See `open-questions.md`.

Keep the printed lot. The continuous fields are the map's numbering, not a sequence to fold back into 1–18.

### Empty and reserved lots

Many lots have no burial. Some empty lots are reserved for a surviving spouse. The source files do not say which empties are reserved.

Represent every lot in the confirmed grid:

- `occupied` when a burial is recorded
- `empty` when no burial is recorded
- `reserved` only when Stanley or the cemetery has identified that lot as held

Adjacent same-surname burials are common. That pattern can suggest a reserved neighbor. Record the suggestion as a QA note. Mark a lot `reserved` only from a named source, not from the name pattern alone.

## Find a Grave

Skip a Find a Grave reconciliation.

Find a Grave does not publish a public read API. The site has an internal GraphQL endpoint, and third-party tools call it, but that is not a documented API. Ancestry's terms (Find a Grave is an Ancestry service) prohibit automated or programmatic access beyond ordinary human use. FamilySearch offers a limited "Find a Grave Index" through its developer platform (collection 2221801). That index is thinner than the memorial pages, requires FamilySearch credentials, and is a poor fit for plot-by-plot checking.

Do not scrape Find a Grave, and do not call its undocumented endpoint. A person may later look up individual public memorials by hand and add discrepancies to `data/qa-issues.csv`. That step waits until the CSV exists.

## Target layout

```
AGENTS.md
.cursor/rules/chevra-cemetery.mdc
cemetery map.png
list of departed since 2020 (11-10-26).pdf
master list of departed poorly formatted.pdf
scripts/build_dataset.py  # rebuilds the CSVs from the two PDFs
data/burials.csv          # one row per person
data/plots.csv            # one row per lot on the working grid
data/qa-issues.csv        # parse failures, conflicts, numbering flags
web/index.html            # interactive map; open it from a local web server
web/cemetery.json         # map data, rewritten by scripts/build_dataset.py
scripts/build_pdf.py       # rebuilds the printable map from the CSVs
print/chevra-ahavas-chesed.pdf  # generated; not committed
```

Create `data/`, `web/`, and `print/` when that phase starts. Generated files should be reproducible from the CSV and the source image.

## Canonical CSV

`data/burials.csv` columns:

- `burial_id` — stable id assigned by the parser
- `name_raw` — the name text as printed
- `name_last`, `name_first`, `name_other` — split when the split is clear; leave blank when it is not
- `name_order` — `last_first` (master list) or `first_last` (recent list)
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

Matching rule for `source=both`: same first and last name after swapping order. If several master rows share that name, the field, row, lot, or date decides which one. A nickname in parentheses (`Eddie`) does not block a match. The same field, row, lot, and date are one person even when the spelling differs by a letter (`Kaufman` / `Kaufmann`, `Guttman` / `Guttmann`). When the later list gives the field and row and no lot, and the first names are close, the master-list lot is kept (`Harry` / `Harvey Honick`). Other names that differ by a letter stay as two rows. When the lines disagree, the 2020–2026 list supplies the map location, both original lines are kept, and a QA issue is written. When both dates are a full day, `date_iso` uses the recent list's date.

`data/plots.csv` columns:

- `field`, `row`, `lot_number`, `lot_suffix`
- `lots_per_row` — the working width for that field
- `numbering` — `restart` or `continuous`
- `status` — `occupied` or `empty` in the first version (`reserved` waits for a named list)
- `burial_id` — blank when empty; more than one id, separated by semicolons, when several people share the lot

Letter-suffix plots are extra rows, created only when a burial uses that suffix. The base lot is still in the grid.

`data/qa-issues.csv` columns:

- `issue_id`, `severity` (`block` or `review`), `kind`, `source_line`, `detail`

Treat these as blocks: location text that does not parse, two different people on one lot, a lot above the Stanley cap outside fields J–O, and any drawing of KK or LLL before those fields are placed. Treat these as reviews: J–O high lot numbers, missing dates, ambiguous centuries, possible reserved neighbors, and people buried elsewhere.

The master list's printed total is 1,545 Chevra names as of 12/22/2022. The QA report should show the parsed Chevra count, the Rosedale count, and the elsewhere count beside that figure.

## Plan

### Phase 1 — CSV

1. Parse the master PDF line by line. Separate the Rosedale block from the Chevra block.
2. Parse the recent PDF. Normalize the location phrases above. Keep elsewhere and missing-location rows.
3. Match overlapping people from 2020 onward.
4. Write `data/burials.csv` and `data/qa-issues.csv`.
5. Review `data/qa-issues.csv`. Off-grid lots and list conflicts stay visible. They do not block the first schematic.

### Phase 2 — Plot grid

1. The first `data/plots.csv` uses the assumptions in `open-questions.md`, including three rows, the widths in that file, KK after JJ, and LLL after KKK.
2. Replace a width or a placement when a visit answers the matching question. Rebuild the CSV and both maps from the script.
3. One burial per lot is the normal case. Shared lots and letter suffixes stay on the plot and in the QA file.
4. Join burials onto plots. One burial per lot. Conflicts go to QA and stay visible in the app.

### Phase 3 — Interactive map

A static site in `web/` that loads the CSVs in the browser. No account and no server.

- Schematic grid, field by field, using the source image's colors for single, double, and triple bands.
- Search by name. Filter by field.
- Click a lot for the name, date, and field/row/lot.
- Occupied, empty, and reserved lots look different.
- Usable on a phone at the cemetery.
- The satellite photo can sit beside the schematic as a field-level overview. The photo does not show individual graves, so the grave map is the schematic.

### Phase 4 — PDF map

A multi-page PDF in `print/`:

- An overview page of the field bands, in the same spatial order as `cemetery map.png`, with KK and LLL omitted until placed.
- One page per field, or per small group of fields, with a symbol and a number on each lot.
- An alphabetical index: name, field, row, lot, and the map key.
- Empty lots stay on the map and stay visually quiet. Reserved lots use their own symbol.
- The index includes Chevra burials. Elsewhere and Rosedale names can have a short separate list so they are omitted from the grave drawing.

## First version

`data/`, `web/`, and `print/` are a first schematic. The assumptions behind them are listed at the top of `open-questions.md`. They are not confirmed. When one of them is wrong, change the assumption in that file and rebuild. Do not silently treat the schematic as surveyed.

## Open questions

The running list is `open-questions.md`. Add a new item there when the lists do not settle something. A cemetery visit is the way to answer most of them.

## Working rules

- Commit after each step. A step is one coherent change to the data, the web map, or the printable map. Do not leave finished work uncommitted.
- `print/chevra-ahavas-chesed.pdf` is rebuilt by `scripts/build_pdf.py` and is not committed. The two source PDFs stay in the repository.
- Preserve every source string in a `*_raw` column.
- Keep a person when the date or the location is incomplete.
- Do not scrape Find a Grave.
- Do not edit the three source files.
- Mark a lot reserved only from a named source.
- Use the satellite photo for field bands. It does not locate a grave inside a field.
