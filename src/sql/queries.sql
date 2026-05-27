-- CarteBlanche — Requêtes analytiques SQL

-- 1. Top 10 départements avec le plus de patients par médecin (surcharge)
SELECT
    d.libelle_dep,
    d.libelle_region,
    f.annee,
    f.nombre_patients
FROM fact_patientele f
JOIN dim_departement d ON f.code_dep = d.code_dep
WHERE f.annee = 2024
ORDER BY f.nombre_patients DESC
LIMIT 10;

-- 2. Évolution nationale moyenne patients/médecin par année
SELECT
    annee,
    ROUND(AVG(nombre_patients)::numeric, 0) AS patients_moyens,
    MIN(nombre_patients)                     AS min_patients,
    MAX(nombre_patients)                     AS max_patients
FROM fact_patientele
WHERE code_dep != '999'
GROUP BY annee
ORDER BY annee;

-- 3. Départements avec la plus forte croissance de patientèle
SELECT
    d.libelle_dep,
    d.libelle_region,
    p2016.nombre_patients AS patients_2016,
    p2024.nombre_patients AS patients_2024,
    ROUND(
        ((p2024.nombre_patients - p2016.nombre_patients)::float
        / p2016.nombre_patients * 100)::numeric, 1
    ) AS evolution_pct
FROM fact_patientele p2016
JOIN fact_patientele p2024
    ON p2016.code_dep = p2024.code_dep
JOIN dim_departement d ON p2016.code_dep = d.code_dep
WHERE p2016.annee = 2016
  AND p2024.annee = 2024
  AND p2016.nombre_patients > 0
ORDER BY evolution_pct DESC
LIMIT 15;

-- 4. Comparaison régions — patients moyens 2024
SELECT
    d.libelle_region,
    ROUND(AVG(f.nombre_patients)::numeric, 0) AS patients_moyens,
    COUNT(DISTINCT f.code_dep)                 AS nb_departements
FROM fact_patientele f
JOIN dim_departement d ON f.code_dep = d.code_dep
WHERE f.annee = 2024
  AND f.code_dep != '999'
GROUP BY d.libelle_region
ORDER BY patients_moyens DESC;

-- 5. Départements sous le seuil critique (< 600 patients/médecin = sous-doté)
SELECT
    d.libelle_dep,
    d.libelle_region,
    f.nombre_patients,
    CASE
        WHEN f.nombre_patients < 600  THEN 'Sous-doté'
        WHEN f.nombre_patients < 800  THEN 'Fragile'
        WHEN f.nombre_patients < 1000 THEN 'Correct'
        ELSE 'Surchargé'
    END AS statut
FROM fact_patientele f
JOIN dim_departement d ON f.code_dep = d.code_dep
WHERE f.annee = 2024
  AND f.code_dep != '999'
ORDER BY f.nombre_patients ASC;