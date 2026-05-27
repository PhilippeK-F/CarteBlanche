# CarteBlanche — Déserts médicaux en France (2016–2024)

## Description

Projet data analyst personnel analysant l'évolution des déserts médicaux en France sur la période 2016–2024, à partir des données officielles de l'Assurance Maladie.

L'objectif est de construire un **pipeline ETL complet** (Python → PostgreSQL → Streamlit + Power BI) pour identifier les départements en situation critique et suivre l'évolution de la charge des médecins traitants.

> *"En 2024, 65% des départements français sont en situation de surcharge médicale. Ce n'est pas une crise à venir — c'est une crise déjà là."*

---

## Stack technique

| Outil | Usage |
|---|---|
| Python | Pipeline ETL |
| Pandas / OpenPyXL | Extraction et nettoyage |
| PostgreSQL | Stockage et requêtes analytiques |
| SQLAlchemy | Connexion Python → PostgreSQL |
| SQL | Vues analytiques, agrégations |
| Streamlit | Dashboard interactif |
| Power BI | Dashboard analytics |
| Docker | Conteneurisation |
| GitHub | Versioning |

---

## Structure du projet

```
CarteBlanche/
│
├── data/
│   ├── raw/
│   │   ├── Indicateur_APL.xlsx
│   │   └── patientele-medecintraitant-generalistes-annuelle.csv
│   └── processed/
│       ├── patientele_clean.csv
│       └── dim_departement.csv
│
├── src/
│   ├── loaders/
│   │   ├── extract.py              # Extraction depuis Excel/CSV
│   │   └── load_to_db.py           # ETL → PostgreSQL
│   ├── sql/
│   │   ├── create_tables.sql       # Création des tables
│   │   └── queries.sql             # Requêtes analytiques
│   └── analysis/
│       ├── clean.py
│       ├── analyze.py              # Requêtes SQL via SQLAlchemy
│       └── visualize.py
│
├── dashboard/
│   ├── streamlit_app.py
│   └── CarteBlanche.pbix
│
├── .env
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Base de données PostgreSQL

### Schéma en étoile

```
DIM_Departement ──────► fact_patientele ◄────── DIM_Temps
(code_dep, libelle,       (annee, code_dep,        (annee)
 libelle_region)           nombre_patients,
                           taux_evolution)
```

### Vues SQL

```sql
-- Vue agrégée nationale
vue_evolution_nationale : annee, patients_moyens, min_patients, max_patients

-- Vue enrichie par département
vue_patientele_dep : annee, code_dep, libelle_dep, libelle_region, nombre_patients
```

---

## Sources officielles

| Source | Description | Lien |
|---|---|---|
| **Assurance Maladie** | Patientèle médecins traitants par département | data.ameli.fr |
| **DREES** | Accessibilité Potentielle Localisée (APL) | data.gouv.fr |

---

## Dashboards

### Streamlit — http://localhost:8505

- **Onglet Évolution** : ligne nationale + évolution par région
- **Onglet Départements** : top N + répartition par statut
- **Onglet Données brutes** : table + export CSV

### Power BI

- 4 KPI Cards : Patients moyens, Maximum, Départements surchargés, % surchargés
- 2 Slicers : Année, Région
- Line chart : Évolution nationale 2016–2024
- Bar chart : Top départements les plus chargés
- Donut : Répartition par statut
- Table : Détail par département filtré 2024

---

## Lancement

### Avec Docker

```bash
# Démarrer PostgreSQL
docker-compose up postgres -d

# Lancer l'ETL
python src/loaders/extract.py
python src/loaders/load_to_db.py

# Démarrer Streamlit
docker-compose up --build
```

Accès : **http://localhost:8505**

### Sans Docker

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python src/loaders/extract.py
python src/loaders/load_to_db.py
streamlit run dashboard/streamlit_app.py
```

---

## Principaux enseignements

1. **999 patients/médecin en moyenne nationale** en 2024 — contre 865 en 2016 (+25%)
2. **Eure-et-Loir** est le département le plus chargé avec 1582 patients/médecin
3. **65% des départements** sont en situation de surcharge (≥1000 patients)
4. **Hautes-Alpes** est le département le moins chargé — effet montagne/tourisme
5. **La tendance est continue** — aucune année ne montre de baisse depuis 2016
6. **Les DOM-TOM** présentent des situations très disparates — Mayotte sous-dotée, Martinique surchargée

---

## Conclusion

CarteBlanche met en données une crise sanitaire structurelle : la désertification médicale française n'est pas un phénomène ponctuel mais une tendance lourde et continue depuis 2016.

Avec 999 patients en moyenne par médecin traitant en 2024 — et des pointes à 1582 dans certains départements — le système de soins primaires français est sous pression croissante. Sans action structurelle sur la formation et la répartition des médecins, la situation continuera de se dégrader.

Ce projet pourrait être enrichi avec les données d'APL par commune pour une analyse géographique plus fine, et des projections basées sur les départs en retraite des médecins actuels.

---

## Auteur

**Philippe Kirstetter-Fender**
Projet personnel — Data Analyst / Data Engineer
En recherche active d'un poste de Data Engineer en France et à l'étranger.
