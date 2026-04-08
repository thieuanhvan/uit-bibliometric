# Data Directory

The raw Scopus CSV files are **not included** in this repository
(excluded by `.gitignore` per Scopus Terms of Service).

---

## How to reproduce the dataset

### Dataset 1 — UIT VNU-HCM (primary corpus)

1. Go to [Scopus](https://www.scopus.com) (institutional access required)
2. Click **Search** → **Advanced Search**
3. Paste the following query:

```
AF-ID ( 60283218 ) AND SUBJAREA ( COMP ) AND PUBYEAR AFT 2009 AND PUBYEAR BEF 2026
```

4. **Select all** results → **Export** → **CSV** → select all fields
5. Save as: `data/scopus_uit.csv`

Expected result: ~2,046 records (before filtering errata/editorials)

---

### Dataset 2 — HCMUS (comparison corpus)

1. Go to [Scopus](https://www.scopus.com) → **Advanced Search**
2. Paste:

```
AF-ID ( 60071419 ) AND PUBYEAR AFT 2009 AND PUBYEAR BEF 2026
```

3. Export all fields → Save as: `data/scopus_hcmus.csv`

Expected result: ~7,217 records (all subject areas; CS/IT filter applied in pipeline)

---

## Field reference

The analysis uses these Scopus CSV columns:

| Column | Used for |
|--------|---------|
| `Title` | Keyword matching, NMF |
| `Year` | Trend analysis |
| `Author Keywords` | Cluster classification, NMF |
| `Cited by` | Citation impact |
| `Document Type` | Filtering (remove Erratum, Editorial) |
| `Source title` | Venue analysis |
| `Authors` | Co-authorship network |
| `Author(s) ID` | Co-authorship network (unique IDs) |
| `Affiliations` | International collaboration |

---

## Notes

- Data collected: **April 8, 2026**
- Scopus coverage note: only Scopus-indexed publications are included;
  non-indexed venues are excluded
- Raw CSV files cannot be shared per Scopus Terms of Service;
  results are fully reproducible by re-running the query above
