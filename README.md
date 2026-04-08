# Bibliometric Analysis of CS Research Trends at UIT VNU-HCM

**Paper:** *A Bibliometric Analysis of Computer Science Research Trends at UIT VNU-HCM:
A Multi-Dimensional Study with Institutional Comparison (2010–2025)*

**Authors:** Thieu Anh Van · Cao Thi Nhan
**Affiliation:** University of Information Technology (UIT), VNU-HCM
**Venue:** MAPR 2026

---

## Repository structure

```
uit-bibliometric/
├── src/
│   └── bibliometric_analysis.py   # Main analysis pipeline (5 dimensions)
├── data/
│   └── README.md                  # ← HOW TO DOWNLOAD THE DATASET
├── requirements.txt
├── .gitignore
└── README.md
```

> **⚠️ CSV files are not included.**
> See [`data/README.md`](data/README.md) for Scopus query instructions.

---

## Quickstart

### 1. Clone and install

```bash
git clone https://github.com/thieuanhvan/uit-bibliometric.git
cd uit-bibliometric
pip install -r requirements.txt
```

### 2. Download data

Follow the instructions in [`data/README.md`](data/README.md) to export
the Scopus CSV files and place them in the `data/` folder:

```
data/
├── scopus_uit.csv      # AF-ID(60283218), SUBJAREA=COMP, 2010-2025
└── scopus_hcmus.csv    # AF-ID(60071419), all fields, 2010-2025
```

### 3. Run

```bash
# UIT profiling only
python src/bibliometric_analysis.py \
    --input data/scopus_uit.csv \
    --output results/ \
    --inst UIT

# UIT + HCMUS comparison
python src/bibliometric_analysis.py \
    --input data/scopus_uit.csv \
    --compare data/scopus_hcmus.csv \
    --output results/ \
    --inst UIT --inst2 HCMUS
```

Output figures are saved to `results/`.

---

## Five analytical dimensions

| Dimension | Description |
|-----------|-------------|
| (i) Publication trend | Annual output, CAGR |
| (ii) Thematic evolution | 6 rule-based clusters + NMF validation (k=6) |
| (iii) Citation impact | Volume × mean-citation quadrant |
| (iv) Global AI alignment | A(T) score vs 15 representative trends |
| (v) Co-authorship network | Betweenness centrality, hub detection |

---

## Key results

- Annual output tripled post-2020 (95 → 296 papers/year)
- AI/ML share: 8.2% → 40.6% (CAGR = 44.8%/year)
- Global AI alignment: A(T) = 12/15 = 0.80 (approximate indicator)
- NMF recovers 5/6 clusters independently (agreement 34.1% vs random 16.7%)
- UIT vs HCMUS-CS: 1.7× citation gap largely associated with journal ratio

---

## Requirements

```
pandas>=1.5
matplotlib>=3.6
numpy>=1.23
networkx>=2.8
scikit-learn>=1.1
scipy>=1.9
```

Install: `pip install -r requirements.txt`

---

## Citation

```bibtex
@inproceedings{van2026bibliometric,
  title     = {A Bibliometric Analysis of Computer Science Research Trends
               at UIT VNU-HCM: A Multi-Dimensional Study with
               Institutional Comparison (2010--2025)},
  author    = {Thieu, Anh Van and Cao, Thi Nhan},
  booktitle = {Proceedings of the International Conference on
               Machine Learning and Pattern Recognition (MAPR)},
  year      = {2026}
}
```

---

## License

Code: MIT License.
Data: Not included (see [`data/README.md`](data/README.md)).
