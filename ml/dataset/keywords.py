# ml/dataset/keywords.py
"""
Mots-clés organisés par catégorie pour constituer un dataset équilibré.
70% data — 30% non-data
"""

#KEYWORDS_DATA = ["data engineer"]
#KEYWORDS_NON_DATA = ["développeur fullstack"]

# ── Métiers DATA (70% des requêtes) ──────────────────────────
KEYWORDS_DATA = [

    # Data Engineering
    "data engineer",
    "ingénieur données",
    "ingénieur data",
    "pipeline données",
    "ETL développeur",
    "architecte données",
    "architecte data",

    # Data Science / ML
    "data scientist",
    "machine learning engineer",
    "ingénieur machine learning",
    "MLOps",
    "NLP engineer",
    "computer vision",
    "deep learning",

    # Data Analysis
    "data analyst",
    "analyste données",
    "business analyst",
    "business intelligence",
    "analyste BI",

    # Data Management
    "data manager",
    "data steward",
    "data quality",
    "data governance",
    "chief data officer",

    # Cloud / Infrastructure Data
    "databricks",
    "spark developer",
    "kafka engineer",
    "airflow",
    "dbt developer",
]

# ── Métiers NON-DATA (30% des requêtes) ──────────────────────
KEYWORDS_NON_DATA = [

    # Développement
    "développeur backend",
    "développeur frontend",
    "développeur fullstack",
    "développeur mobile",

    # Infrastructure
    "devops engineer",
    "administrateur système",
    "ingénieur cloud",
    "architecte solution",

    # Métiers transverses
    "chef de projet",
    "product manager",
    "scrum master",
    "UX designer",

    # Métiers non-tech
    "comptable",
    "responsable marketing",
    "commercial",
    "chargé de communication",
    "directeur financier",
    "infirmier",
    "juriste",
]
