# Open questions

Running list of things the burial lists do not settle. Most of these need someone at the cemetery, reading stones and counting graves. A few can be answered by Stanley from the cemetery's own records.

Add new items at the bottom. When an item is answered, write the answer underneath it and set the status to answered. Leave the question in place.

Working assumptions stay assumptions until a visit or Stanley confirms them.

## Assumptions for the first CSV and maps

These are in force for `data/`, `web/`, and `print/`. None of them is confirmed on the ground. The maps are a first schematic.

1. **Row 1 faces the entrance.** "Each block" is read as each field. Row 1 is the row closest to the Liberty Road entrance. Row 2 is the next row away from the entrance, then row 3. Every field, including KK and LLL, is drawn with three rows. On the maps, row 1 is the top of the field and the top of the page is the entrance side.

2. **Lot 1 is on the left.** Lots increase left to right when row 1 is at the top. On the overview, that left is the A–J and K–S side, with Shaari Zion to the right of A–J. Left and right on the page are the reverse of left and right as you walk in from Liberty Road, so the left end of a row is on your right as you enter. The lists do not say which end is lot 1. Question 5.

3. **The printable overview follows the source photo, with the entrance at the top.** In the upper part, blue A–J is on the left and Shaari Zion Cemetery parallels it on the right. Green K–S continues straight down from J. Orange AA–JJ and pink AAA–KKK are to the right of K–S, starting where Shaari Zion ends. Each field is drawn the same height, so K lines up with AA and AAA. The plot listing board is one field tall between HH and II, which puts it beside S, and II, JJ, JJJ, and KKK continue past S. The photo itself shows the bands ending together; this equal-height reading is unconfirmed. Fields T–Z are not drawn. The source legend extends those bands through Z, ZZ, and ZZZ; the burial lists stop at S, JJ, and KKK.

4. **KK and LLL are not on the printable overview.** They were added after the photo, so page 2 leaves them off and each has its own field page. You asked for KK between JJ and AAA, and LLL after KKK. That is still unconfirmed. The interactive map still lists KK after JJ and LLL after KKK. Question 6.

5. **Row lengths, used as the grid even where a visit may find more empty lots.** Numbering restarts at 1 each row, except J–O.

   | Fields | Lots per row | Numbering |
   | --- | --- | --- |
   | A | 14 | restarts |
   | B, C | 12 | restarts |
   | D | 13 | restarts |
   | E, F | 14 | restarts |
   | G, H | 16 | restarts |
   | I | 15 | restarts |
   | J, K | 14 | continuous: 1–14, 15–28, 29–42 |
   | L, M, N, O | 16 | continuous: 1–16, 17–32, 33–48 |
   | P, Q, R, S | 18 | restarts |
   | AA–JJ and KK | 14 | restarts |
   | AAA–KKK and LLL | 14 | restarts |

   Stanley's 18 and 14 are what P–S and the double- and triple-letter fields follow. A–O follow the lengths the master list actually uses. Questions 2 and 4.

6. **A burial is drawn only when its lot sits in that row's block.** In J–O the printed row is kept, and it is drawn when the lot number falls in that row's range above. Esther Birnbaum (`J 2 3`) and Hans Morgenroth (`J 3 24A`) fall outside those blocks. They stay in the CSV and appear as "not on the working grid," not as extra squares. The same treatment is used for Max Bodenheimer at HH row 2 lot 19, and for anyone else whose lot is outside the width. Questions 3 and 10.

7. **Natalie Greenfield is drawn at JJ row 1 lot 11. Susan Roedel is drawn at S row 1 lot 15.** The master-list coordinates (J row 1 lot 11 and J row 1 lot 15) are kept on the row and are not drawn. Where the two lists give different years, the later list's full date is the one stored as `date_iso`, and the master date stays in the notes. Greenfield is 2021-10-13 on the map; the master list says 10/13/20. Question 1.

8. **When the two lists name one person and disagree, the 2020–2026 list supplies the map location.** Both original lines stay on the CSV row. A match requires the same first and last name. A parenthetical nickname does not block it. Names that differ by a letter are left as two rows.

9. **A letter suffix is not drawn on the numbered square.** The lot stays as printed (`15A`), and that person is listed under “Not on a square” on the field page. Empty "A" lots are not invented. Two unsuffixed names on one lot share the cell. What the letter means on the ground is still open. Question 8 and question 9.

10. **An empty square means the lists have no burial there.** Some of those lots may be reserved. The map does not mark a lot reserved until Stanley or the cemetery names it. Question 7.

11. **Rosedale, King David, "buried elsewhere," and rows with no field are in the CSV and off the grave map.**

12. **Two-digit death years are expanded, and marked `assumed_century` when the day is otherwise complete.** Master list: 50–99 are 1950–1999, 27–49 are 1927–1949, and 00–26 are 2000–2026. The 2020–2026 list's own two-digit years 20–26 are 2020–2026 and are marked `exact`, because that file is the 2020s. A four-digit year in either file is `exact`. Partial dates and year-only dates stay out of `date_iso`. A visit or a stone is still the check on any single year.

13. **The same grave and the same date are one person, even when the spelling differs.** Susan Kaufman and Kaufmann Susan are one row. Egon Guttman and Guttmann are one row. Dora Weiss (Blum) is one row. When the later list gives the field and row and no lot, and the first names are close, the master-list lot is used. That is how Harry Honick is drawn at III row 2 lot 14, the Harvey Honick grave. Question 12.

14. **The plot listing board is one field tall, between HH and II, beside S.** You first placed it between HH and II. Giving every field the same height then puts that one-field board directly to the right of S. The words are written in the board, not beside the figure. The source photo only says the board is toward the far end. Question 11.

## 1. Natalie Greenfield and Susan Roedel in field J

- Status: open
- How to answer: visit. Read the stones at J row 1 lot 11, J row 1 lot 15, JJ row 1 lot 11, and S row 1 lot 15.

The master list puts both women in field J. The 2020–2026 list puts them somewhere else. The working assumption is that the master list is wrong.

Lot 11, row 1, has two master-list lines:

- `Eick Julius J 1 11` (no date)
- `Greenfield Natalie J 1 11 10/13/20`

Olga Eick is the next grave: `Eick Olga J 1 12 9/14/93`. Julius and Olga are the pair on 11 and 12. Natalie is the extra name on Julius's lot. The later list says `Natalie Greenfield 10/13/2021 Field JJ, Row 1, Lot 11`. The day matches. The year does not: the master list says 2020, the later list says 2021. The stone should have the date.

Lot 15, row 1, has only Susan:

- `Roedel Susan J 1 15 1/13/22`

Nobody else is on J row 1 lot 15. The later list says `Susan Roedel 1/13/2022 Field S, Row 1, Lot 15`. The number 15 is also used on row 2, which is a different grave if J is numbered straight through: `Prager Nathan J 2 15`, with `Neuhof Bertha J 2 15A 6/??/81` beside him. Irma Prager is lot 16 on that row.

If the assumption holds, field J row 1 ends at lot 14 plus Chaim Birnbaum at 14A, and Susan's row-1 lot 15 was never a J grave.

## 2. Do fields J through O number straight through the three rows?

- Status: open
- How to answer: visit. Walk each row and read the lot numbers on the stones.

The lists do not restart at 1 in these fields. K reads as 14 per row: 1–14, 15–28, 29–42. L, M, N, and O read as 16 per row: 1–16, 17–32, 33–48. J matches K's 14-wide blocks once Greenfield and Roedel are set aside (question 1), except the two lines in question 3.

What to check: a stone in K row 2 should bear a number in the teens or twenties, not a restarted 1. The same test in L through O should show the thirties and forties on row 3. O's list has every number from 1 through 47 and no 48, so look for whether lot 48 exists and is empty.

## 3. Two J lines that fall outside those blocks

- Status: open
- How to answer: visit.

- `Birnbaum Esther J 2 3 9/25/09`. Row 1 lot 3 is already Eugen Baer, with Hedwig Baer in lot 4. Frieda Birnbaum is J row 1 lot 14, and Chaim Birnbaum is 14A.
- `Morgenroth Hans J 3 24A 5/8/85`. Lot 24 on row 2 is Manny Rosenbusch, with Betty Rosenbusch in lot 25.

Find Esther's stone and Hans's stone, and note the field, row, and lot actually cut there.

## 4. How many graves are in each row of fields A through I?

- Status: open
- How to answer: visit. Count the graves in each row, including empties.

These fields restart at 1 every row. The highest lot number in the master list, which is the working row length:

| Field | Lots per row |
| --- | --- |
| A | 14 |
| B | 12 |
| C | 12 |
| D | 13 |
| E | 14 |
| F | 14 |
| G | 16 |
| H | 16 |
| I | 15 |

Stanley said every single-letter field has 18 lots per row. P, Q, R, and S do match 18 and do restart. A through I never go past the lengths above, and several rows are filled from 1 through that last number. D at 13 and I at 15 are the odd ones to count twice.

Also confirm there are three rows and no fourth.

## 5. Which end of a row is lot 1, and which side of a field is row 1?

- Status: open. The first map assumes an answer for row 1 only. See the assumptions at the top.
- How to answer: visit. The source photo shows field bands only. It does not show the direction of the numbers.

Stand in one field whose occupants we trust, such as field A or field L, and record which physical end is lot 1 and which side is row 1. One confident example is enough if the cemetery uses the same direction everywhere. If a field breaks the pattern, note that field.

## 6. Where are fields KK and LLL?

- Status: open. The printable overview leaves KK and LLL off, because they are not on the source photo. The interactive map still lists KK after JJ and LLL after KKK. See assumption 4.
- How to answer: visit, or Stanley if he has a current field diagram.

Neither field is labeled on `cemetery map.png`. LLL was added after that image. KK appears only in the 2025–2026 burials (the master list stops at JJ and KKK). The later list uses both, so the graves exist. We need the walk order: KK relative to JJ, LLL relative to KKK, and whether each row has 14 lots.

## 7. Which empty lots are reserved?

- Status: open
- How to answer: Stanley, or the cemetery's plot book. A visit can see an empty space. It cannot tell a reserved lot from an unused one unless the marker says so.

Some empties are held for a surviving spouse. The burial lists never mark those. Until there is a named list, an empty square only means no burial is recorded. It may still be reserved.

## 8. What is a letter-suffix lot on the ground?

- Status: open
- How to answer: visit. Look at one or two, then say whether the rest look the same.

The master list has graves such as `Birnbaum Chaim J 1 14A` beside Frieda at 14, and several in field B (`Deutsch Elsa B 2 1A` beside Johanna Lieberman at lot 1). We need to know whether the "A" is a separate grave cut beside that number, a second burial in the same grave, or a list-keeping habit. Until then the map does not put the suffix name inside the numbered square. It lists the person under “Not on a square” on that field’s page.

Field B has seven of these. C, D, E, and F have a few. K has 14A, 15A, 28A, and 29A.

## 9. Two names on one lot number, with no letter

- Status: open
- How to answer: visit the examples below. The CSV pass should list every other case.

Some of these are a couple sharing a number. Some look like a duplicate line. The stones will tell them apart.

- K row 1 lot 1: Herbert Nussbaum and Ernest Rothschild
- K row 3 lot 32: Erna May and Frieda Mayer, with Mathilde Mayer on lot 34
- C row 3 lot 8: Henry Kartman and Frieda Weil
- D row 1 lot 11: Emil Burger, Fred Kaufmann, and Lina Zellermayer at 11A
- D row 1 lot 13: Agnes Blank and Frieda Mendel
- I row 1 lot 8: Sara Bugatch, plus Ilie Riszel (9/12/83) and Ilie Rizel (9/11/83), which may be one person entered twice

## 10. HH row 2 lot 19

- Status: open
- How to answer: visit, or check the plot book.

Double-letter fields otherwise stop at 14. The master list has `Bodenheimer Max HH 2 19 11/24/13`. Every other HH lot fits 1–14. Confirm whether lot 19 is real.

## 11. Field order and the edges of each field

- Status: open
- How to answer: visit, with the source photo in hand.

The photo labels A at the Liberty Road entrance and S, JJ, and KKK at the far end. The color bands group A–J, then the later single letters, then the double letters, then the triple letters. The lists use A–S, AA–JJ, and AAA–KKK only. Walk the bands and confirm the order of the unlabeled fields, and where one field stops and the next starts. The printable map gives every field the same height, so K lines up with AA and AAA. It draws the plot listing board as one field between HH and II, which puts the board beside S, and lets II, JJ, JJJ, and KKK continue past S. Confirm the equal heights and that spot.

## 12. Places where the two lists disagree, other than Greenfield and Roedel

- Status: open
- How to answer: visit, or the plot book.

The first map uses the 2020–2026 list when both lines name a grave. These four are the other disagreements. Michael Eisenberg's later lot is 18, and the working grid for JJ only runs to 14, so he is left off the drawing.

- Joseph Cotton: master list JJ row 1 lot 8, later list JJ row 1 lot 7
- Michael Eisenberg: master list JJ row 1 lot 14, later list JJ row 1 lot 18
- Doris Fox: master list P row 3 lot 8, later list P row 3 lot 6. Lot 6 already has David Berzon in the master list.
- Sara Kovacs: master list JJ row 3 lot 3, later list JJ row 3 lot 4

Same grave and same date are drawn once when the spelling differs: Susie Schwarz / Schwartz at R row 3 lot 15, Susan and Naomi Propper / Proper, Susan Kaufman / Kaufmann at CCC row 2 lot 6, Egon Guttman / Guttmann at GG row 3 lot 7, and Dora Weiss (Blum) at BB row 1 lot 4. Harry Honick in the later list has no lot number; the master list's Harvey Honick, III row 2 lot 14, same date, is used for the square. Question the stone if Harry and Harvey might be different people.
