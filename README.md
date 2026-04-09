# Bibliometric Analysis of CS Research at UIT VNU-HCM (2010–2025)

**Paper:** *A Bibliometric Analysis of Computer Science Research at the University of Information Technology, VNU-HCM: Trends, AI Alignment, and Institutional Benchmarking (2010–2025)*

**Author:** Thiều Anh Vân  
**Affiliation:** University of Information Technology (UIT), VNU-HCM, Vietnam  
**Submitted to:** Scientometrics (Springer), April 2026  
**ORCID:** 0009-0003-9637-0195

---

## Repository structure

```
uit-bibliometric/
├── src/
│   ├── bibliometric_analysis.py   # Main analysis pipeline (5 dimensions + A(T))
│   └── run_analysis.py            # Entry point — auto-detects CSV files
├── data/
│   └── (CSV files not included — see below)
├── results/
│   └── (output figures and tables)
├── requirements.txt
└── README.md
```

> **⚠️ CSV files are not included** (Scopus license does not permit redistribution).  
> Follow the instructions below to reproduce the dataset.

---

## Quickstart

### 1. Clone and install

```bash
git clone https://github.com/thieuanhvan/uit-bibliometric.git
cd uit-bibliometric
pip install -r requirements.txt
```

### 2. Download data from Scopus

Go to [https://www.scopus.com](https://www.scopus.com) → **Search → Advanced Search**.

Use these queries and export **all results as CSV (all fields)**:

| File to save as | Scopus query |
|----------------|-------------|
| `data/scopus_60283218_20260408.csv` | `AF-ID(60283218) AND LIMIT-TO(SUBJAREA,"COMP") AND PUBYEAR AFT 2009 AND PUBYEAR BEF 2026` |
| `data/scopus_60071419_20260408.csv` | `AF-ID(60071419) AND LIMIT-TO(SUBJAREA,"COMP") AND PUBYEAR AFT 2009 AND PUBYEAR BEF 2026` |
| `data/scopus_60272237_20260408.csv` | `AF-ID(60272237) AND LIMIT-TO(SUBJAREA,"COMP") AND PUBYEAR AFT 2009 AND PUBYEAR BEF 2026` |

> **Note:** Record counts may differ slightly from the paper (1,703 / 1,944 / 2,114)  
> due to ongoing Scopus indexing. The archived snapshot date was **8 April 2026**.

### 3. Run

```bash
cd src
python run_analysis.py
```

Output figures will be saved to `results/`.

---

## File naming convention

The pipeline detects CSV files by **Affiliation ID** in the filename:

```
scopus_[AffiliationID]_[yyyyMMdd].csv
```

| Filename example | Affiliation ID | Institution |
|-----------------|---------------|-------------|
| `scopus_60283218_20260408.csv` | 60283218 | UIT (primary) |
| `scopus_60071419_20260408.csv` | 60071419 | HCMUS-CS |
| `scopus_60272237_20260408.csv` | 60272237 | HCMUT-CS |

If a file is not found or has the wrong name format, the script prints  
the correct Scopus query and exits with a clear error message.

---

## Dependencies

```
pandas >= 1.5.0
matplotlib >= 3.5.0
numpy >= 1.21.0
networkx >= 2.8
scikit-learn >= 1.0   # for NMF topic modeling
```

---

## Citation

If you use this code or data, please cite:

```
Van, T.A. (2026). A Bibliometric Analysis of Computer Science Research at the 
University of Information Technology, VNU-HCM: Trends, AI Alignment, and 
Institutional Benchmarking (2010–2025). Scientometrics (under review).
```

---

## License

MIT License — free to use and adapt with attribution.
