import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import time

load_dotenv()

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5433")
DB_USER     = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_NAME     = os.getenv("DB_NAME", "carteblanche")


def get_engine():
    url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


def drop_all(engine):
    with engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS vue_deserts_medicaux CASCADE"))
        conn.execute(text("DROP VIEW IF EXISTS vue_apl_departement CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS fact_apl CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS fact_patientele CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS dim_departement CASCADE"))
        conn.commit()
    print("Tables supprimées")


def create_tables(engine):
    with open('src/sql/create_tables.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    with engine.connect() as conn:
        for statement in sql.split(';'):
            stmt = statement.strip()
            if stmt:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    print(f"  Warning: {e}")
        conn.commit()
    print("Tables créées")


def load_dim_departement(engine):
    df = pd.read_csv('data/processed/dim_departement.csv',
                     encoding='utf-8-sig', dtype={'code_dep': str})
    df['code_region'] = pd.to_numeric(df['code_region'], errors='coerce').astype('Int64')
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM dim_departement"))
        conn.commit()
    df.to_sql('dim_departement', engine, if_exists='append', index=False)
    print(f"dim_departement : {len(df)} lignes chargées")


def load_fact_patientele(engine):
    df = pd.read_csv('data/processed/patientele_clean.csv',
                     encoding='utf-8-sig', dtype={'code_dep': str})
    cols = ['annee', 'code_dep', 'nombre_patients', 'taux_evolution']
    df = df[cols].dropna(subset=['annee', 'code_dep'])
    df = df[df['code_dep'] != '999']
    df['taux_evolution'] = pd.to_numeric(df['taux_evolution'], errors='coerce')
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM fact_patientele"))
        conn.commit()
    df.to_sql('fact_patientele', engine, if_exists='append', index=False)
    print(f"fact_patientele : {len(df)} lignes chargées")


def create_views(engine):
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE OR REPLACE VIEW vue_patientele_dep AS
            SELECT
                d.code_dep,
                d.libelle_dep,
                d.libelle_region,
                f.annee,
                f.nombre_patients,
                f.taux_evolution
            FROM fact_patientele f
            JOIN dim_departement d ON f.code_dep = d.code_dep
        """))
        conn.execute(text("""
            CREATE OR REPLACE VIEW vue_evolution_nationale AS
            SELECT
                annee,
                ROUND(AVG(nombre_patients)::numeric, 0) AS patients_moyens,
                MIN(nombre_patients) AS min_patients,
                MAX(nombre_patients) AS max_patients
            FROM fact_patientele
            GROUP BY annee
            ORDER BY annee
        """))
        conn.commit()
    print("Vues créées")


def run_etl():
    print("Connexion à PostgreSQL...")
    time.sleep(3)
    engine = get_engine()
    print("Connexion établie")

    print("\nSuppression des anciennes tables...")
    drop_all(engine)

    print("\nCréation des tables...")
    create_tables(engine)

    print("\nChargement dim_departement...")
    load_dim_departement(engine)

    print("\nChargement fact_patientele...")
    load_fact_patientele(engine)

    print("\nCréation des vues...")
    create_views(engine)

    print("\n✅ ETL terminé — données disponibles dans PostgreSQL")


if __name__ == "__main__":
    run_etl()