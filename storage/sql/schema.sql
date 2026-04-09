-- ─────────────────────────────────────────────
-- Schéma PostgreSQL — Job Market Explorer
-- Etape 2 : Architecture des données
-- ─────────────────────────────────────────────

-- Table principale des offres
CREATE TABLE IF NOT EXISTS offres (
    id                  VARCHAR     PRIMARY KEY,
    source              VARCHAR     NOT NULL,
    titre               VARCHAR     NOT NULL,
    description         TEXT,
    entreprise          VARCHAR,
    localisation_ville  VARCHAR,
    localisation_dept   VARCHAR,
    type_contrat        VARCHAR,
    teletravail         VARCHAR,
    salaire_min         INTEGER,
    salaire_max         INTEGER,
    experience_min      INTEGER,
    secteur             VARCHAR,
    nb_employes         VARCHAR,
    date_publication    DATE,
    date_extraction     TIMESTAMP,
    url                 VARCHAR
);

-- Table des compétences (relation 1..N avec offres)
CREATE TABLE IF NOT EXISTS competences (
    id          SERIAL      PRIMARY KEY,
    offre_id    VARCHAR     NOT NULL REFERENCES offres(id) ON DELETE CASCADE,
    competence  VARCHAR(500) NOT NULL
);

-- Table des missions (relation 1..N avec offres)
CREATE TABLE IF NOT EXISTS missions (
    id          SERIAL  PRIMARY KEY,
    offre_id    VARCHAR NOT NULL REFERENCES offres(id) ON DELETE CASCADE,
    mission     TEXT    NOT NULL
);

-- Table des avantages (relation 1..N avec offres)
CREATE TABLE IF NOT EXISTS avantages (
    id          SERIAL      PRIMARY KEY,
    offre_id    VARCHAR     NOT NULL REFERENCES offres(id) ON DELETE CASCADE,
    avantage    VARCHAR(500) NOT NULL
);

-- ─────────────────────────────────────────────
-- Index pour accélérer les requêtes fréquentes
-- ─────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_offres_source
    ON offres(source);

CREATE INDEX IF NOT EXISTS idx_offres_ville
    ON offres(localisation_ville);

CREATE INDEX IF NOT EXISTS idx_offres_contrat
    ON offres(type_contrat);

CREATE INDEX IF NOT EXISTS idx_offres_date
    ON offres(date_publication);

CREATE INDEX IF NOT EXISTS idx_competences_offre_id
    ON competences(offre_id);

CREATE INDEX IF NOT EXISTS idx_competences_competence
    ON competences(competence);

CREATE INDEX IF NOT EXISTS idx_missions_offre_id
    ON missions(offre_id);

CREATE INDEX IF NOT EXISTS idx_avantages_offre_id
    ON avantages(offre_id);
