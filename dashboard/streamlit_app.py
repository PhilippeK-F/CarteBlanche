import sys
sys.path.insert(0, '..')

import streamlit as st
import pandas as pd

from src.analysis.analyze import (
    compute_kpis,
    evolution_nationale,
    top_charges,
    evolution_par_region,
    statut_2024,
)
from src.analysis.visualize import (
    plot_evolution_nationale,
    plot_top_charges,
    plot_evolution_region,
    plot_statut_2024,
)
from src.analysis.clean import clean_patientele

st.set_page_config(
    page_title="CarteBlanche",
    page_icon="🗺️",
    layout="wide",
)

st.title("CarteBlanche")
st.markdown("Analyse des déserts médicaux en France — Patients par médecin traitant (2016–2024)")

# ---------------------------------------------------------------------------
# Chargement depuis PostgreSQL
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_all():
    df_evo    = evolution_nationale()
    df_top    = top_charges(2024, 15)
    df_region = evolution_par_region()
    df_statut = statut_2024()
    return df_evo, df_top, df_region, df_statut

try:
    df_evo, df_top, df_region, df_statut = load_all()
    db_ok = True
except Exception as e:
    st.error(f"Connexion PostgreSQL impossible : {e}")
    db_ok = False

if not db_ok:
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.header("Filtres")

annees = sorted(df_statut['nombre_patients'].unique().tolist())
selected_n = st.sidebar.slider(
    "Top N départements",
    min_value=5, max_value=20, value=15
)

statuts = df_statut['statut'].unique().tolist()
selected_statuts = st.sidebar.multiselect(
    "Statut", options=statuts, default=statuts
)
df_statut_f = df_statut[df_statut['statut'].isin(selected_statuts)]

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
st.subheader("Indicateurs clés — 2024")
df_statut_kpi = statut_2024()
patients_moyens = int(df_statut_kpi['nombre_patients'].mean())
dep_max = df_statut_kpi.loc[df_statut_kpi['nombre_patients'].idxmax(), 'libelle_dep']
dep_min = df_statut_kpi.loc[df_statut_kpi['nombre_patients'].idxmin(), 'libelle_dep']
pct_surcharge = round((df_statut_kpi['statut'].isin(['Surchargé', 'Critique'])).mean() * 100, 1)

kpis = {
    "Patients moyens / médecin": f"{patients_moyens}",
    "Dép. le plus chargé": dep_max,
    "Dép. le moins chargé": dep_min,
    "% dép. surchargés": f"{pct_surcharge}%",
}
cols = st.columns(len(kpis))
for col, (label, value) in zip(cols, kpis.items()):
    col.metric(label=label, value=value)

st.divider()

# ---------------------------------------------------------------------------
# Onglets
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Évolution", "Départements", "Données brutes"])

with tab1:
    st.subheader("Évolution nationale")
    st.pyplot(plot_evolution_nationale(df_evo))

    st.divider()

    st.subheader("Évolution par région")
    st.pyplot(plot_evolution_region(df_region))

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Top {selected_n} départements les plus chargés")
        df_top_n = top_charges(2024, selected_n)
        st.pyplot(plot_top_charges(df_top_n))
    with col2:
        st.subheader("Répartition par statut (2024)")
        st.pyplot(plot_statut_2024(df_statut_f))

with tab3:
    st.subheader("Détail par département — 2024")
    st.dataframe(df_statut_f.sort_values('nombre_patients', ascending=False),
                 use_container_width=True)
    csv = df_statut_f.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger CSV", csv, "carteblanche_export.csv", "text/csv")