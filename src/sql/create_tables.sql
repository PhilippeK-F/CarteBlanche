-- CarteBlanche — Création des tables PostgreSQL

-- Dimension départements
CREATE TABLE IF NOT EXISTS dim_departement (
    code_dep        VARCHAR(3)  PRIMARY KEY,
    libelle_dep     VARCHAR(100),
    code_region     INTEGER,
    libelle_region  VARCHAR(100)
);

-- Faits patientèle médecins traitants
CREATE TABLE IF NOT EXISTS fact_patientele (
    id              SERIAL PRIMARY KEY,
    annee           INTEGER     NOT NULL,
    code_dep        VARCHAR(3)  REFERENCES dim_departement(code_dep),
    nombre_patients INTEGER,
    taux_evolution  FLOAT,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Faits APL par commune
CREATE TABLE IF NOT EXISTS fact_apl (
    id              SERIAL PRIMARY KEY,
    code_commune    VARCHAR(10),
    libelle_commune VARCHAR(200),
    code_dep        VARCHAR(3)  REFERENCES dim_departement(code_dep),
    apl_2022        FLOAT,
    apl_2023        FLOAT,
    est_desert_2022 BOOLEAN GENERATED ALWAYS AS (apl_2022 < 2.5) STORED,
    est_desert_2023 BOOLEAN GENERATED ALWAYS AS (apl_2023 < 2.5) STORED,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Vue agrégée par département
CREATE OR REPLACE VIEW vue_apl_departement AS
SELECT
    d.code_dep,
    d.libelle_dep,
    d.libelle_region,
    ROUND(AVG(a.apl_2022)::numeric, 2)          AS apl_moyen_2022,
    ROUND(AVG(a.apl_2023)::numeric, 2)          AS apl_moyen_2023,
    COUNT(*)                                     AS nb_communes,
    SUM(CASE WHEN a.est_desert_2023 THEN 1 ELSE 0 END) AS nb_communes_desert,
    ROUND(
        (SUM(CASE WHEN a.est_desert_2023 THEN 1 ELSE 0 END)::float / COUNT(*) * 100)::numeric, 1
    )                                            AS pct_communes_desert
FROM fact_apl a
JOIN dim_departement d ON a.code_dep = d.code_dep
GROUP BY d.code_dep, d.libelle_dep, d.libelle_region;

-- Vue déserts médicaux critiques
CREATE OR REPLACE VIEW vue_deserts_medicaux AS
SELECT
    code_dep,
    libelle_dep,
    libelle_region,
    apl_moyen_2023,
    pct_communes_desert,
    CASE
        WHEN apl_moyen_2023 < 1.5 THEN 'Critique'
        WHEN apl_moyen_2023 < 2.5 THEN 'Sous-doté'
        WHEN apl_moyen_2023 < 4.0 THEN 'Fragile'
        ELSE 'Correct'
    END AS niveau_acces
FROM vue_apl_departement
ORDER BY apl_moyen_2023 ASC;