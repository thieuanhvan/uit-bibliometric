# -*- coding: utf-8 -*-
"""
Bibliometric Analysis: Mapping Research Trends at UIT VNU-HCM
=============================================================
Paper: "Mapping Research Trends at UIT VNU-HCM: A Bibliometric Analysis
        of Computer Science Output, Global AI Alignment, and Institutional
        Comparison (2010-2025)"

Authors: Thieu Anh Van, Cao Thi Nhan
School : University of Information Technology, VNU-HCM
Date   : April 2026
GitHub : github.com/thieuanhvan/uit-bibliometric

Usage:
    # Single institution profiling
    python bibliometric_analysis.py --input scopus_uit.csv --output results/ --inst UIT

    # Pilot comparison
    python bibliometric_analysis.py \
        --input scopus_uit.csv \
        --compare scopus_hcmus.csv \
        --output results/ \
        --inst UIT --inst2 HCMUS

Requirements:
    pip install pandas matplotlib numpy networkx
"""

import argparse
import os
import sys
import warnings
from collections import Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# ── Cluster definitions ───────────────────────────────────────────────────────
CLUSTERS = {
    'AI / Machine Learning': [
        'machine learning', 'deep learning', 'neural network', 'cnn', 'rnn', 'lstm',
        'transformer', 'attention', 'bert', 'gpt', 'llm', 'reinforcement learning',
        'federated learning', 'transfer learning', 'generative adversarial', 'gan',
        'diffusion', 'xgboost', 'random forest', 'xai', 'explainab', 'interpretab',
        'shap', 'lime', 'neural architecture', 'artificial intelligence',
        'multi-objective optimization',
    ],
    'Computer Vision': [
        'object detection', 'image classification', 'image segmentation',
        'face recognition', 'video', 'optical flow', 'pattern recognition',
        'computer vision', '3d', 'point cloud', 'image processing',
        'multimodal', 'visual',
    ],
    'NLP / Vietnamese': [
        'natural language processing', 'nlp', 'sentiment analysis',
        'text classification', 'named entity', 'machine translation',
        'question answering', 'information retrieval', 'vietnamese',
        'text mining', 'word embedding', 'language model',
    ],
    'Security & Privacy': [
        'intrusion detection', 'malware', 'network security', 'cryptograph',
        'blockchain', 'adversarial', 'privacy', 'authentication',
        'anomaly detection', 'cyber', 'vulnerability', 'access control', 'lora',
    ],
    'Systems & Networks': [
        'cloud computing', 'iot', 'internet of things', 'edge computing',
        'fog computing', 'wireless', 'network optimization', 'distributed',
        'embedded', 'real-time', 'fpga', 'hardware', '5g',
        'resource allocation', 'scheduling',
    ],
    'Knowledge & Data': [
        'knowledge graph', 'ontology', 'knowledge representation',
        'knowledge engineering', 'intelligent problem solver',
        'data mining', 'big data', 'database', 'recommendation',
        'semantic', 'information extraction',
    ],
}

# Global AI/CS trends for alignment analysis
GLOBAL_TRENDS = {
    'large language model / LLM':  ['large language model', 'llm', 'gpt', 'chatgpt', 'llama'],
    'multimodal learning':          ['multimodal', 'vision-language', 'clip', 'vqa'],
    'diffusion model':              ['diffusion model', 'stable diffusion', 'ddpm'],
    'federated learning':           ['federated learning', 'federated'],
    'graph neural network':         ['graph neural', 'gnn', 'graph convolutional'],
    'self-supervised learning':     ['self-supervised', 'contrastive learning', 'masked autoencoder'],
    'transformer / attention':      ['transformer', 'attention mechanism', 'vision transformer', 'vit'],
    'object detection':             ['object detection', 'yolo', 'detr'],
    'reinforcement learning':       ['reinforcement learning', 'rl', 'ppo', 'dqn'],
    'knowledge graph':              ['knowledge graph', 'knowledge-based'],
    'adversarial / robustness':     ['adversarial', 'robustness', 'backdoor'],
    'explainability / XAI':         ['explainab', 'xai', 'interpretab', 'shap', 'lime'],
    'medical image / AI health':    ['medical image', 'clinical', 'healthcare ai', 'diagnosis'],
    'NLP Vietnamese / low-resource':['vietnamese', 'low-resource', 'multilingual'],
    'IoT / edge AI':                ['iot', 'edge computing', 'edge ai', 'tinyml', 'embedded'],
}

COLORS = {
    'primary':   '#185FA5',
    'secondary': '#0F6E56',
    'accent':    '#BA7517',
    'highlight': '#534AB7',
    'orange':    '#E06C1A',
    'neutral':   '#5F5E5A',
    'light':     '#E6F1FB',
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_data(filepath: str, cs_filter: bool = False) -> pd.DataFrame:
    """Load Scopus CSV. Optionally apply CS keyword filter for multidisciplinary institutions."""
    if not os.path.exists(filepath):
        sys.exit(f'[ERROR] File not found: {filepath}')
    df = pd.read_csv(filepath, low_memory=False)
    df['Year']     = pd.to_numeric(df['Year'],     errors='coerce')
    df['Cited by'] = pd.to_numeric(df['Cited by'], errors='coerce').fillna(0)
    df = df[~df['Document Type'].isin(['Erratum', 'Editorial', 'Retracted']) &
            (df['Year'] >= 2010)].copy()
    if cs_filter:
        CS_TERMS = [
            'machine learning', 'deep learning', 'neural', 'computer vision', 'nlp',
            'natural language', 'blockchain', 'network security', 'intrusion', 'iot',
            'cloud', 'algorithm', 'data mining', 'image', 'classification', 'detection',
            'software', 'database', 'information system', 'artificial intelligence',
            'programming', 'web', 'mobile', 'embedded', 'fpga', 'knowledge', 'ontology',
            'semantic', 'graph neural', 'optimization', 'scheduling', 'computer science',
            'pattern recognition', 'object detection', 'sentiment', 'text', 'speech',
        ]
        def is_cs(row):
            t = (str(row.get('Author Keywords', '')) + ' ' +
                 str(row.get('Source title', ''))).lower()
            return any(term in t for term in CS_TERMS)
        df = df[df.apply(is_cs, axis=1)].copy()
        print(f'[CS filter] {len(df):,} CS/IT documents retained')
    print(f'[OK] Loaded {len(df):,} records from {os.path.basename(filepath)}')
    return df


def classify_cluster(kw_str: str) -> str:
    if pd.isna(kw_str):
        return 'Other'
    kw = str(kw_str).lower()
    for cluster, terms in CLUSTERS.items():
        if any(t in kw for t in terms):
            return cluster
    return 'Other'


def add_period(df: pd.DataFrame) -> pd.DataFrame:
    def period(y):
        if y <= 2014: return '2010-2014'
        elif y <= 2019: return '2015-2019'
        else: return '2020-2025'
    df['Cluster'] = df['Author Keywords'].apply(classify_cluster)
    df['Period']  = df['Year'].apply(period)
    return df


def hindex(df: pd.DataFrame) -> int:
    s = df['Cited by'].sort_values(ascending=False).reset_index(drop=True)
    return int(sum(s[i] >= i + 1 for i in range(len(s))))


# ── Phase 1: Deep profiling ───────────────────────────────────────────────────

def plot_trend(df: pd.DataFrame, inst: str, output_dir: str) -> str:
    trend = df['Year'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(11, 5))
    colors = [COLORS['light'] if y == 2026 else COLORS['primary'] for y in trend.index]
    bars = ax.bar(trend.index, trend.values, color=colors, edgecolor='white', linewidth=0.5)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 2, str(int(h)),
                ha='center', va='bottom', fontsize=7.5, fontweight='bold')
    z = np.polyfit(trend.index[-8:], trend.values[-8:], 1)
    ax.plot(trend.index[-8:], np.poly1d(z)(trend.index[-8:]),
            color=COLORS['accent'], linestyle='--', linewidth=1.5, label='Growth trend (2018-2025)')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Publications', fontsize=11)
    ax.set_title(f'Annual publication trend — {inst} (2010-2025)', fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    path = os.path.join(output_dir, 'fig1_trend.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def plot_cluster_evolution(df: pd.DataFrame, inst: str, output_dir: str) -> str:
    periods = ['2010-2014', '2015-2019', '2020-2025']
    pc = df.groupby(['Period', 'Cluster']).size().unstack(fill_value=0)
    pc = pc.reindex(periods).fillna(0)
    if 'Other' in pc.columns:
        pc = pc.drop(columns='Other')
    pc_pct = pc.div(pc.sum(axis=1), axis=0) * 100
    clr_map = {
        'AI / Machine Learning': COLORS['primary'],
        'Computer Vision':       COLORS['secondary'],
        'NLP / Vietnamese':      COLORS['accent'],
        'Security & Privacy':    COLORS['highlight'],
        'Systems & Networks':    COLORS['orange'],
        'Knowledge & Data':      COLORS['neutral'],
    }
    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = np.zeros(3)
    for col in [c for c in CLUSTERS.keys() if c in pc_pct.columns]:
        vals = pc_pct[col].values
        ax.bar(periods, vals, bottom=bottom, color=clr_map.get(col, '#999'),
               label=col, edgecolor='white', linewidth=0.4)
        for i, (v, b) in enumerate(zip(vals, bottom)):
            if v > 6:
                ax.text(i, b + v / 2, f'{v:.0f}%', ha='center', va='center',
                        fontsize=8, color='white', fontweight='bold')
        bottom += vals
    ax.set_ylabel('Share (%)', fontsize=11)
    ax.set_title(f'Thematic cluster evolution — {inst}', fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=8)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    path = os.path.join(output_dir, 'fig2_cluster_evolution.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def plot_citation_quadrant(df: pd.DataFrame, inst: str, output_dir: str) -> str:
    stats = []
    for cl in CLUSTERS.keys():
        sub = df[df['Cluster'] == cl]
        if len(sub) == 0:
            continue
        stats.append({'Cluster': cl, 'Papers': len(sub),
                      'Mean_citations': round(sub['Cited by'].mean(), 1)})
    stats_df = pd.DataFrame(stats)
    x_mean = df['Cited by'].mean()
    y_mean = len(df) / len(CLUSTERS)
    fig, ax = plt.subplots(figsize=(9, 7))
    colors_list = list(COLORS.values())
    for i, row in stats_df.iterrows():
        ax.scatter(row['Papers'], row['Mean_citations'], s=200,
                   color=colors_list[i % len(colors_list)], zorder=5,
                   edgecolors='white', linewidth=1.5)
        ax.annotate(row['Cluster'], (row['Papers'], row['Mean_citations']),
                    textcoords='offset points', xytext=(6, 4), fontsize=8.5, fontweight='bold')
    ax.axvline(x=y_mean, color='gray', linestyle='--', linewidth=1, alpha=0.6)
    ax.axhline(y=x_mean, color='gray', linestyle='--', linewidth=1, alpha=0.6)
    ax.set_xlabel('Number of papers (volume)', fontsize=11)
    ax.set_ylabel('Mean citations per paper (impact)', fontsize=11)
    ax.set_title(f'Volume vs Impact quadrant — {inst}\nDashed lines = corpus mean',
                 fontsize=11, fontweight='bold')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    path = os.path.join(output_dir, 'fig3_quadrant.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def plot_global_alignment(df: pd.DataFrame, inst: str, output_dir: str) -> str:
    kws_all = df['Author Keywords'].fillna('').str.lower()
    uit_global = {}
    for trend, keywords in GLOBAL_TRENDS.items():
        count = sum(kws_all.str.contains(k, na=False).sum() for k in keywords)
        uit_global[trend] = count
    uit_s = pd.Series(uit_global).sort_values(ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    # Panel A
    ax = axes[0]
    bar_colors = [COLORS['secondary'] if v >= 20 else
                  COLORS['accent'] if v >= 5 else '#CC3333'
                  for v in uit_s.values]
    ax.barh(range(len(uit_s)), uit_s.values, color=bar_colors, edgecolor='white')
    ax.set_yticks(range(len(uit_s)))
    ax.set_yticklabels(uit_s.index, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel('Keyword occurrences', fontsize=10)
    ax.set_title(f'Panel A: {inst} alignment\nwith global AI/CS trends', fontsize=10, fontweight='bold')
    ax.spines[['top', 'right']].set_visible(False)
    for i, v in enumerate(uit_s.values):
        ax.text(v + 0.3, i, str(v), va='center', fontsize=8)

    # Panel B: classified
    ax2 = axes[1]
    strong   = [(k, v) for k, v in uit_s.items() if v >= 20]
    moderate = [(k, v) for k, v in uit_s.items() if 5 <= v < 20]
    gap      = [(k, v) for k, v in uit_s.items() if v < 5]
    all_items = strong + moderate + gap
    cat_colors = ([COLORS['secondary']] * len(strong) +
                  [COLORS['accent']] * len(moderate) +
                  ['#CC3333'] * len(gap))
    ax2.barh(range(len(all_items)), [v for _, v in all_items],
             color=cat_colors, edgecolor='white')
    ax2.set_yticks(range(len(all_items)))
    ax2.set_yticklabels([k for k, _ in all_items], fontsize=8)
    ax2.invert_yaxis()
    ax2.set_xlabel('Keyword occurrences', fontsize=10)
    ax2.set_title('Panel B: Alignment classification\n(Strong / Moderate / Gap)',
                  fontsize=10, fontweight='bold')
    ax2.spines[['top', 'right']].set_visible(False)
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['secondary'], label='Strong (>=20)'),
        mpatches.Patch(facecolor=COLORS['accent'],    label='Moderate (5-19)'),
        mpatches.Patch(facecolor='#CC3333',           label='Gap (<5)'),
    ]
    ax2.legend(handles=legend_elements, loc='lower right', fontsize=8)
    for i, (_, v) in enumerate(all_items):
        ax2.text(v + 0.3, i, str(v), va='center', fontsize=8)

    plt.suptitle(f'Global AI/CS trend alignment — {inst} (2010-2025)\n'
                 'Based on 15 representative trends from NeurIPS/CVPR/ACL/ICLR 2022-2025',
                 fontsize=11, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(output_dir, 'fig4_global_alignment.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def plot_coauthorship(df: pd.DataFrame, inst: str, output_dir: str) -> str:
    try:
        import networkx as nx
    except ImportError:
        print('[WARN] networkx not installed; skipping co-authorship graph')
        return ''
    G = nx.Graph()
    author_paper_count = Counter()
    id_to_name = {}
    for _, row in df.iterrows():
        ids   = [x.strip() for x in str(row.get('Author(s) ID', '')).split(';')
                 if x.strip() and x.strip() != 'nan']
        names = [x.strip() for x in str(row.get('Authors', '')).split(';')
                 if x.strip()]
        for i, aid in enumerate(ids):
            nm = names[i] if i < len(names) else aid
            id_to_name[aid] = nm
            author_paper_count[aid] += 1
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = ids[i], ids[j]
                if G.has_edge(a, b):
                    G[a][b]['weight'] += 1
                else:
                    G.add_edge(a, b, weight=1)
    for n in G.nodes():
        G.nodes[n]['name']   = id_to_name.get(n, n)
        G.nodes[n]['papers'] = author_paper_count[n]
    sub_nodes = [n for n in G.nodes() if author_paper_count[n] >= 5]
    G_sub = G.subgraph(sub_nodes).copy()
    comps = sorted(nx.connected_components(G_sub), key=len, reverse=True)
    G_main = G_sub.subgraph(comps[0]).copy()
    degree_cent  = nx.degree_centrality(G_main)
    between_cent = nx.betweenness_centrality(G_main, weight='weight', normalized=True)
    pos = nx.spring_layout(G_main, seed=42, k=0.8)
    node_sizes  = [300 + author_paper_count[n] * 40 for n in G_main.nodes()]
    node_colors = [between_cent.get(n, 0) for n in G_main.nodes()]
    edge_widths = [0.3 + G_main[u][v]['weight'] * 0.4 for u, v in G_main.edges()]
    fig, ax = plt.subplots(figsize=(14, 10))
    nx.draw_networkx_edges(G_main, pos, ax=ax, width=edge_widths, alpha=0.3, edge_color='#AAAAAA')
    sc = nx.draw_networkx_nodes(G_main, pos, ax=ax, node_size=node_sizes,
                                 node_color=node_colors, cmap=plt.cm.YlOrRd, alpha=0.85)
    top_nodes = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:20]
    labels = {n: G_main.nodes[n].get('name', '?') for n, _ in top_nodes}
    nx.draw_networkx_labels(G_main, pos, labels=labels, ax=ax, font_size=7, font_weight='bold')
    plt.colorbar(sc, ax=ax, label='Betweenness centrality', shrink=0.6)
    ax.set_title(f'Co-authorship network — {inst} (>=5 publications)\n'
                 f'Node size = publication count | Color = betweenness centrality | '
                 f'n={G_main.number_of_nodes()} researchers',
                 fontsize=11, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    path = os.path.join(output_dir, 'fig5_coauthorship.png')
    plt.savefig(path, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


# ── Phase 2: Comparison ───────────────────────────────────────────────────────

def plot_comparison_trend(df1, df2, inst1, inst2, output_dir):
    years = range(2010, 2026)
    u_yr = df1['Year'].value_counts().reindex(years, fill_value=0).sort_index()
    h_yr = df2['Year'].value_counts().reindex(years, fill_value=0).sort_index()
    fig, ax = plt.subplots(figsize=(11, 5))
    x, w = np.arange(len(years)), 0.38
    ax.bar(x - w/2, u_yr.values, w, label=inst1, color=COLORS['primary'], alpha=0.85, edgecolor='white')
    ax.bar(x + w/2, h_yr.values, w, label=inst2, color=COLORS['secondary'], alpha=0.85, edgecolor='white')
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Publications', fontsize=11)
    ax.set_title(f'Annual publication trend — {inst1} vs {inst2} (2010-2025)',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=10)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    path = os.path.join(output_dir, 'figC1_trend_compare.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def plot_comparison_clusters(df1, df2, inst1, inst2, output_dir):
    cl_order = list(CLUSTERS.keys())
    def cluster_pct(df):
        counts = df['Cluster'].value_counts()
        total = sum(counts.get(c, 0) for c in cl_order)
        return [100 * counts.get(c, 0) / total for c in cl_order]
    u_pct = cluster_pct(df1)
    h_pct = cluster_pct(df2)
    short = ['AI/ML', 'Computer\nVision', 'NLP/\nVietnamese',
             'Security\n& Privacy', 'Systems\n& Networks', 'Knowledge\n& Data']
    fig, ax = plt.subplots(figsize=(12, 5))
    x, w = np.arange(len(cl_order)), 0.38
    b1 = ax.bar(x - w/2, u_pct, w, label=inst1, color=COLORS['primary'], alpha=0.85, edgecolor='white')
    b2 = ax.bar(x + w/2, h_pct, w, label=inst2, color=COLORS['secondary'], alpha=0.85, edgecolor='white')
    for bar, v in list(zip(b1, u_pct)) + list(zip(b2, h_pct)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f'{v:.0f}%', ha='center', va='bottom', fontsize=7.5, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(short, fontsize=9)
    ax.set_ylabel('Share of classified papers (%)', fontsize=11)
    ax.set_title(f'Research cluster portfolio — {inst1} vs {inst2}',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=10)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    path = os.path.join(output_dir, 'figC2_cluster_compare.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def plot_comparison_impact(df1, df2, inst1, inst2, output_dir):
    cl_order = list(CLUSTERS.keys())
    short = ['AI/ML', 'Computer\nVision', 'NLP/\nVietnamese',
             'Security\n& Privacy', 'Systems\n& Networks', 'Knowledge\n& Data']
    u_means = [df1[df1['Cluster'] == cl]['Cited by'].mean() for cl in cl_order]
    h_means = [df2[df2['Cluster'] == cl]['Cited by'].mean() for cl in cl_order]
    fig, ax = plt.subplots(figsize=(11, 5))
    x, w = np.arange(len(cl_order)), 0.38
    b1 = ax.bar(x - w/2, u_means, w, label=inst1, color=COLORS['primary'], alpha=0.85, edgecolor='white')
    b2 = ax.bar(x + w/2, h_means, w, label=inst2, color=COLORS['secondary'], alpha=0.85, edgecolor='white')
    for bar, v in list(zip(b1, u_means)) + list(zip(b2, h_means)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f'{v:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(short, fontsize=9)
    ax.set_ylabel('Mean citations per paper', fontsize=11)
    ax.set_title(f'Mean citation impact by cluster — {inst1} vs {inst2}',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=10)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    path = os.path.join(output_dir, 'figC3_impact_compare.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def print_summary(df, inst):
    print(f'\n{"="*55}')
    print(f'  {inst} — KEY FINDINGS')
    print(f'{"="*55}')
    print(f'  Total documents (2010-2025) : {len(df):,}')
    print(f'  Total citations             : {int(df["Cited by"].sum()):,}')
    print(f'  Mean citations/paper        : {df["Cited by"].mean():.1f}')
    print(f'  h-index corpus              : {hindex(df)}')
    print(f'  Papers in 2025              : {len(df[df["Year"]==2025])}')
    print(f'\n  Cluster breakdown:')
    for cl in CLUSTERS.keys():
        n = len(df[df['Cluster'] == cl])
        m = df[df['Cluster'] == cl]['Cited by'].mean()
        pct = 100 * n / len(df[df['Cluster'] != 'Other']) if len(df[df['Cluster'] != 'Other']) > 0 else 0
        print(f'    {cl:<30} {n:4d} papers  {pct:5.1f}%  mean={m:.1f} cite/paper')


# ── Main ──────────────────────────────────────────────────────────────────────



# ── Data availability check ──────────────────────────────────────────────────
def check_data_files(args):
    """Warn user if CSV files are missing; print Scopus query instructions."""
    missing = []
    if args.input and not os.path.isfile(args.input):
        missing.append(args.input)
    compare = getattr(args, 'compare', None)
    if compare and not os.path.isfile(compare):
        missing.append(compare)

    if not missing:
        return

    sep = "=" * 68
    print(f"\n{sep}")
    print("  DATA FILE(S) NOT FOUND")
    print(sep)
    for p in missing:
        print(f"  Missing: {p}")
    print()
    print("  Scopus CSV files are NOT included in this repository.")
    print("  To reproduce the dataset:")
    print()
    print("  1. Go to https://www.scopus.com (institutional access required)")
    print("  2. Click Search > Advanced Search and use the queries below.")
    print("  3. Export all results as CSV (select ALL fields).")
    print("  4. Save files to the data/ folder as shown.")
    print()
    print("  -- UIT primary corpus (save as: data/scopus_uit.csv) --")
    print("  AF-ID(60283218) AND SUBJAREA(COMP)")
    print("  AND PUBYEAR AFT 2009 AND PUBYEAR BEF 2026")
    print("  Expected: ~2,046 records")
    print()
    print("  -- HCMUS comparison corpus (save as: data/scopus_hcmus.csv) --")
    print("  AF-ID(60071419)")
    print("  AND PUBYEAR AFT 2009 AND PUBYEAR BEF 2026")
    print("  Expected: ~7,217 records")
    print()
    print("  Full instructions: data/README.md")
    print(f"{sep}\n")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Bibliometric analysis pipeline for IT university research profiling'
    )
    parser.add_argument('--input',   required=True, help='Scopus CSV for primary institution')
    parser.add_argument('--inst',    default='UIT', help='Name of primary institution')
    parser.add_argument('--compare', default=None,  help='Scopus CSV for comparison (optional)')
    parser.add_argument('--inst2',   default='HCMUS', help='Name of comparison institution')
    parser.add_argument('--cs-filter', action='store_true',
                        help='Apply CS keyword filter (for multidisciplinary institutions)')
    parser.add_argument('--output',  default='results', help='Output directory')
    args = parser.parse_args()
    check_data_files(args)

    os.makedirs(args.output, exist_ok=True)

    # Load primary
    df = load_data(args.input)
    df = add_period(df)

    print(f'\n[Phase 1] Deep profiling: {args.inst}')
    plot_trend(df, args.inst, args.output)
    plot_cluster_evolution(df, args.inst, args.output)
    plot_citation_quadrant(df, args.inst, args.output)
    plot_global_alignment(df, args.inst, args.output)
    plot_coauthorship(df, args.inst, args.output)
    print_summary(df, args.inst)

    if args.compare:
        df2 = load_data(args.compare, cs_filter=args.cs_filter)
        df2 = add_period(df2)
        print(f'\n[Phase 2] Pilot comparison: {args.inst} vs {args.inst2}')
        plot_comparison_trend(df, df2, args.inst, args.inst2, args.output)
        plot_comparison_clusters(df, df2, args.inst, args.inst2, args.output)
        plot_comparison_impact(df, df2, args.inst, args.inst2, args.output)
        print_summary(df2, args.inst2)

    print(f'\n[DONE] All outputs saved to: {args.output}/')


if __name__ == '__main__':
    main()
