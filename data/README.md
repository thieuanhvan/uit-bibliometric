# Data

CSV files are **not included** in this repository due to Scopus licensing  
(see `.gitignore`). To reproduce the analysis, download from Scopus.

## Naming convention (REQUIRED)

```
scopus-[AffiliationID]-[shortname]-[yyyyMMdd].csv
```

| File | Affiliation ID | Institution |
|------|---------------|-------------|
| `scopus-60283218-hcmuit-20260408.csv` | 60283218 | UIT (primary) |
| `scopus-60071419-hcmuns-20260408.csv` | 60071419 | HCMUS-CS |
| `scopus-60272237-hcmut-20260408.csv`  | 60272237 | HCMUT-CS |

The date `20260408` = export date (8 April 2026). Use your actual download date.

---

## Scopus queries

Go to [scopus.com](https://www.scopus.com) → **Search → Advanced Search**,  
export **all results as CSV (all fields)**.

**UIT — save as `scopus-60283218-hcmuit-[yyyyMMdd].csv`**
```
AF-ID(60283218) AND LIMIT-TO(SUBJAREA,"COMP") AND PUBYEAR AFT 2009 AND PUBYEAR BEF 2026
```
Expected: ~1,703 records (as of 8 April 2026)

**HCMUS — save as `scopus-60071419-hcmuns-[yyyyMMdd].csv`**
```
AF-ID(60071419) AND LIMIT-TO(SUBJAREA,"COMP") AND PUBYEAR AFT 2009 AND PUBYEAR BEF 2026
```
Expected: ~1,944 records (as of 8 April 2026)

**HCMUT — save as `scopus-60272237-hcmut-[yyyyMMdd].csv`**
```
AF-ID(60272237) AND LIMIT-TO(SUBJAREA,"COMP") AND PUBYEAR AFT 2009 AND PUBYEAR BEF 2026
```
Expected: ~2,114 records (as of 8 April 2026)

> **Note:** Record counts may differ slightly due to ongoing Scopus indexing.
> The archived snapshot preserves the exact corpus used in the paper.
