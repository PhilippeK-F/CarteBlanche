import pandas as pd


def clean_patientele(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]
    df = df.drop_duplicates()
    df['annee'] = pd.to_numeric(df['annee'], errors='coerce').astype('Int64')
    df['nombre_patients'] = pd.to_numeric(df['nombre_patients'], errors='coerce')
    df['taux_evolution'] = pd.to_numeric(df['taux_evolution'], errors='coerce')
    df['code_dep'] = df['code_dep'].astype(str).str.zfill(3)
    df = df[df['code_dep'] != '999']

    # Statut surcharge
    def statut(n):
        if pd.isna(n):
            return None
        if n >= 1200:
            return 'Critique'
        elif n >= 1000:
            return 'Surchargé'
        elif n >= 800:
            return 'Fragile'
        else:
            return 'Correct'

    df['statut'] = df['nombre_patients'].apply(statut)
    return df.sort_values(['annee', 'code_dep']).reset_index(drop=True)