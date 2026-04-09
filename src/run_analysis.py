# -*- coding: utf-8 -*-
"""
run_analysis.py
===============
Entry point for the UIT Bibliometric Analysis pipeline.

Run:
    python run_analysis.py

File naming convention (REQUIRED):
    data/scopus-[AffiliationID]-[shortname]-[yyyyMMdd].csv

    Examples:
        data/scopus-60283218-hcmuit-20260408.csv   ← UIT   (primary)
        data/scopus-60071419-hcmuns-20260408.csv   ← HCMUS (comparison)
        data/scopus-60272237-hcmut-20260408.csv    ← HCMUT (comparison)

Affiliation IDs (Scopus):
    UIT   : 60283218
    HCMUS : 60071419
    HCMUT : 60272237

If no CSV is found, Scopus query instructions are printed automatically.
"""

import os
import sys
import glob
import re

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR    = os.path.join(os.path.dirname(__file__), '..', 'data')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')

# ── Affiliation registry ──────────────────────────────────────────────────────
INSTITUTIONS = {
    '60283218': 'UIT',
    '60071419': 'HCMUS-CS',
    '60272237': 'HCMUT-CS',
    '60026468': 'HUST',
    '60002490': 'PTIT',
}

PRIMARY_AF_ID = '60283218'  # UIT

# ── File pattern: scopus-[AfID]-[shortname]-[yyyyMMdd].csv ───────────────────
FNAME_RE = re.compile(r'^scopus-(\d+)-([a-z]+)-(\d{8})\.csv$', re.IGNORECASE)


def parse_filename(path: str):
    """
    Parse scopus-[AfID]-[shortname]-[yyyyMMdd].csv
    Returns (af_id, shortname, date) or None if pattern does not match.
    """
    m = FNAME_RE.match(os.path.basename(path))
    return (m.group(1), m.group(2), m.group(3)) if m else None


def find_csvs() -> dict:
    """
    Scan data/ for all files matching the naming convention.
    Returns dict: {af_id: filepath}  (newest date wins if duplicates)
    """
    all_csv = sorted(glob.glob(os.path.join(DATA_DIR, 'scopus-*.csv')))
    found = {}
    for path in all_csv:
        parsed = parse_filename(path)
        if parsed:
            af_id, _, date = parsed
            if af_id not in found or date > parse_filename(found[af_id])[2]:
                found[af_id] = path
        else:
            print(f'[WARN] Skipped — name does not match convention:')
            print(f'       {os.path.basename(path)}')
            print(f'       Expected: scopus-[AffiliationID]-[shortname]-[yyyyMMdd].csv')
    return found


def inst_name(af_id: str) -> str:
    return INSTITUTIONS.get(af_id, f'INST-{af_id}')


def scopus_query(af_id: str) -> str:
    return (
        f'AF-ID({af_id}) AND LIMIT-TO(SUBJAREA,"COMP")\n'
        f'    AND PUBYEAR AFT 2009 AND PUBYEAR BEF 2026'
    )


def print_missing_instructions(missing_ids: list):
    sep = '=' * 68
    print(f'\n{sep}')
    print('  DATA FILE(S) NOT FOUND')
    print(sep)
    print(f'\n  Expected location : {os.path.abspath(DATA_DIR)}/')
    print(f'  Naming convention : scopus-[AffiliationID]-[shortname]-[yyyyMMdd].csv')
    print()
    print('  Examples:')
    print('    data/scopus-60283218-hcmuit-20260408.csv   ← UIT   (primary)')
    print('    data/scopus-60071419-hcmuns-20260408.csv   ← HCMUS (comparison)')
    print('    data/scopus-60272237-hcmut-20260408.csv    ← HCMUT (comparison)')
    print()
    print('  CSV files are NOT included in this repository.')
    print('  To reproduce the dataset:')
    print()
    print('  1. Go to https://www.scopus.com (institutional access required)')
    print('  2. Click Search > Advanced Search')
    print('  3. Use the queries below, export ALL results as CSV (all fields)')
    print('  4. Save to data/ with the exact naming convention above')
    print()
    for af_id in missing_ids:
        label = inst_name(af_id)
        print(f'  ── {label} (AF-ID {af_id}) ──')
        print(f'  {scopus_query(af_id)}')
        print(f'  Save as: data/scopus-{af_id}-[shortname]-<yyyyMMdd>.csv')
        print()
    print('  Full instructions: data/README.md')
    print(f'{sep}\n')
    sys.exit(1)


def main():
    found = find_csvs()

    # ── 1. Primary: UIT ───────────────────────────────────────────────────────
    if PRIMARY_AF_ID not in found:
        print_missing_instructions([PRIMARY_AF_ID])

    primary_csv  = found[PRIMARY_AF_ID]
    primary_name = inst_name(PRIMARY_AF_ID)
    print(f'\n[Config] Primary institution : {primary_name}')
    print(f'         CSV file            : {primary_csv}')

    # ── 2. Comparison institutions (all non-UIT found) ────────────────────────
    others = [(af_id, path) for af_id, path in found.items()
              if af_id != PRIMARY_AF_ID]
    compare_csv  = others[0][1] if others else None
    compare_name = inst_name(others[0][0]) if others else None

    if compare_csv:
        print(f'         Comparison inst.    : {compare_name}')
        print(f'         CSV file            : {compare_csv}')
    else:
        print('         Comparison inst.    : (none — single-institution mode)')

    os.makedirs(RESULTS_DIR, exist_ok=True)
    print(f'         Output directory    : {RESULTS_DIR}\n')

    # ── 3. Run pipeline ───────────────────────────────────────────────────────
    sys.path.insert(0, os.path.dirname(__file__))

    argv = [
        'bibliometric_analysis.py',
        '--input',  primary_csv,
        '--inst',   primary_name,
        '--output', RESULTS_DIR,
    ]
    if compare_csv:
        argv += ['--compare', compare_csv, '--inst2', compare_name]

    sys.argv = argv

    import bibliometric_analysis
    bibliometric_analysis.main()


if __name__ == '__main__':
    main()
