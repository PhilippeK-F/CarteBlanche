import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()


def get_engine():
    url = (
        f"postgresql://{os.getenv('DB_USER', 'admin')}:"
        f"{os.getenv('DB_PASSWORD', 'admin123')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5433')}/"
        f"{os.getenv('DB_NAME', 'carteblanche')}"
    )
    return create_engine(url)


def query_db(sql: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


def compute_kpis(df: pd.DataFrame) -> dict:
    last = df[df['annee'] == df['annee'].max()]
    dep_max = last.loc[last['nombre_patients'].idxmax(), 'code_dep']
    dep_min = last.loc[last['nombre_patients'].idxmin(), 'code_dep']
    pct_surcharge = round((last['statut'].isin(['Surchargé', 'Critique'])).mean() * 100, 1)
    return {
        "Patients moyens / médecin": f"{int(last['nombre_patients'].mean())}",
        "Dép. le plus chargé": dep_max,
        "Dép. le moins chargé": dep_min,
        "% dép. surchargés": f"{pct_surcharge}%",
    }


def evolution_nationale() -> pd.DataFrame:
    return query_db("SELECT * FROM vue_evolution_nationale ORDER BY annee")


def top_charges(annee: int = 2024, n: int = 15) -> pd.DataFrame:
    return query_db(f"""
        SELECT d.libelle_dep, d.libelle_region, f.nombre_patients
        FROM fact_patientele f
        JOIN dim_departement d ON f.code_dep = d.code_dep
        WHERE f.annee = {annee}
        ORDER BY f.nombre_patients DESC
        LIMIT {n}
    """)


def evolution_par_region() -> pd.DataFrame:
    return query_db("""
        SELECT
            d.libelle_region,
            f.annee,
            ROUND(AVG(f.nombre_patients)::numeric, 0) AS patients_moyens
        FROM fact_patientele f
        JOIN dim_departement d ON f.code_dep = d.code_dep
        GROUP BY d.libelle_region, f.annee
        ORDER BY f.annee, d.libelle_region
    """)


def statut_2024() -> pd.DataFrame:
    return query_db("""
        SELECT
            d.libelle_dep, d.libelle_region, f.nombre_patients,
            CASE
                WHEN f.nombre_patients >= 1200 THEN 'Critique'
                WHEN f.nombre_patients >= 1000 THEN 'Surchargé'
                WHEN f.nombre_patients >= 800  THEN 'Fragile'
                ELSE 'Correct'
            END AS statut
        FROM fact_patientele f
        JOIN dim_departement d ON f.code_dep = d.code_dep
        WHERE f.annee = 2024
        ORDER BY f.nombre_patients DESC
    """)