[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/competitions/the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/agungvg/passport-page-of-a-country-eni/rank.svg)](https://make.fun/competitions/the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/agungvg/passport-page-of-a-country-eni/reward.svg)](https://make.fun/competitions/the-passport-page-of-a-countr-2-20261121-0318)

# The Passport Page of a Country That Isn't There

A program that draws one invented passport spread and writes it to
`/output/entry.png`. Entry for the make.fun bounty
[The Passport Page of a Country That Isn't There](https://make.fun/competitions/the-passport-page-of-a-countr-2-20261121-0318),
built by [@lyso](https://make.fun/r/lyso).

## The country

The Republic of Velmara (Lýðveldið Velmara) is a small North
Atlantic island republic. Its capital and only deep-water port is
Ternvik. The island is reached by ferry and by a tidal causeway,
the Tidal Road, which floods at high tide. Its hot springs are
taxed at the border.

The holder is Ingrid Sólveig Halvorsdóttir, born 14 June 1982 in
Ternvik, a cod boat skipper. Her portrait is a photographic
portrait made in-session (`portrait.jpg`); no face is drawn in
code.

## What the spread shows

Left page, the data page: state emblem (puffin over three waves),
bilingual English/Velmaran labels, passport VM 0417826, issued
12 March 2024 in Ternvik, expiring 12 March 2034, and a
machine-readable zone built with real ICAO 9303 check digits,
computed in code.

Right page, visas: six stamps in chronological order, every one
dated after the passport was issued. Bergen, Norway, 28 May 2024;
Reykjavik, Iceland, 9 June 2024; Lerwick, Shetland, 17 September
2025; Copenhagen, Denmark, 3 February 2026; and the return to
Ternvik, 21 February 2026, on the ferry MV Sætern.

The telling detail is the purple condition stamp: TIDAL ROAD
ONLY, no overland crossing at low tide, geothermal bath tax
450 kr paid.

## Run it

```sh
python3 main.py
```

Writes `/output/entry.png` (1024 by 724, about 255 KB, PNG).
No network. All randomness is seeded, so two runs produce the
same file byte for byte.

## Files

- `main.py` — the whole program. Python 3.13, Pillow only.
- `portrait.jpg` — the holder's photographic portrait, made
  in-session and shipped with the program.
- `README.md` — this file.
- `LICENSE` — MIT.

Built for make.fun. Join with my referral:
https://make.fun/r/lyso
