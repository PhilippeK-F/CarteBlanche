import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="darkgrid")

ROUGE  = "#e74c3c"
BLEU   = "#3498db"
VERT   = "#2ecc71"
ORANGE = "#f39c12"

PALETTE_STATUT = {
    'Critique':  ROUGE,
    'Surchargé': ORANGE,
    'Fragile':   "#f1c40f",
    'Correct':   VERT,
}


def _style(fig, ax, title):
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#16213e")
    ax.set_title(title, color="white", fontsize=13)
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    for spine in ax.spines.values():
        spine.set_color("#444")


def plot_evolution_nationale(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df['annee'], df['patients_moyens'],
            marker='o', linewidth=2.5, color=ROUGE, label='Moyenne nationale')
    ax.fill_between(df['annee'], df['min_patients'], df['max_patients'],
                    alpha=0.15, color=BLEU, label='Min–Max')
    ax.set_xlabel("Année")
    ax.set_ylabel("Patients / médecin")
    ax.legend(facecolor="#222", labelcolor="white")
    _style(fig, ax, "Évolution nationale — Patients par médecin traitant")
    plt.tight_layout()
    return fig


def plot_top_charges(df: pd.DataFrame) -> plt.Figure:
    df = df.sort_values('nombre_patients', ascending=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = [ROUGE if v >= 1200 else ORANGE if v >= 1000 else "#f1c40f"
              for v in df['nombre_patients']]
    ax.barh(df['libelle_dep'], df['nombre_patients'],
            color=colors, edgecolor="#222")
    ax.set_xlabel("Patients / médecin")
    _style(fig, ax, "Top départements les plus chargés (2024)")
    plt.tight_layout()
    return fig


def plot_evolution_region(df: pd.DataFrame) -> plt.Figure:
    # Filtrer Mayotte avant 2019
    df = df[~((df['libelle_region'] == 'Mayotte') & (df['annee'] < 2019))]
    fig, ax = plt.subplots(figsize=(14, 6))
    for region in df['libelle_region'].unique():
        subset = df[df['libelle_region'] == region]
        ax.plot(subset['annee'], subset['patients_moyens'],
                linewidth=1.5, alpha=0.8, label=region)
    ax.set_xlabel("Année")
    ax.set_ylabel("Patients moyens / médecin")
    ax.legend(facecolor="#222", labelcolor="white", fontsize=7,
              loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0)
    _style(fig, ax, "Évolution par région (2016–2024)")
    plt.tight_layout()
    return fig


def plot_statut_2024(df: pd.DataFrame) -> plt.Figure:
    agg = df['statut'].value_counts().reset_index()
    agg.columns = ['statut', 'count']
    colors = [PALETTE_STATUT.get(s, BLEU) for s in agg['statut']]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(agg['statut'], agg['count'], color=colors, edgecolor="#222")
    ax.set_xlabel("Statut")
    ax.set_ylabel("Nombre de départements")
    _style(fig, ax, "Répartition des départements par statut (2024)")
    plt.tight_layout()
    return fig