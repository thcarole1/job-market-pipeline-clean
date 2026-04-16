from pathlib import Path
from dotenv import load_dotenv
import os

ENV_PATH = Path(__file__).parent / ".env"

# Vérifier que le fichier existe
print(f".env trouvé : {ENV_PATH.exists()}")
print(f".env chemin : {ENV_PATH}")

load_dotenv(dotenv_path=ENV_PATH)

# Vérifier que les variables sont chargées
print(f"ELASTIC_HOST : {os.getenv('ELASTIC_HOST')}")
print(f"ELASTIC_PORT : {os.getenv('ELASTIC_PORT')}")


# Dans ton script, ajoute ce débogage
from pathlib import Path

# Voir le chemin de ce fichier
print(f"__file__              : {Path(__file__).resolve()}")
print(f"parent                : {Path(__file__).parent.resolve()}")
print(f"parent.parent         : {Path(__file__).parent.parent.resolve()}")
print(f"parent.parent.parent  : {Path(__file__).parent.parent.parent.resolve()}")

# Voir où est le .env
env_path = Path(__file__).parent/".env"
print(f"Chemin .env cherché   : {env_path.resolve()}")
print(f".env existe           : {env_path.exists()}")
