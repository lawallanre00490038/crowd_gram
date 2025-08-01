

from functools import lru_cache
import logging
import pandas as pd
from transformers import pipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("afrolid")

# Load AfroLID model globally
try:
    afrolid_model = pipeline("text-classification", model="UBC-NLP/afrolid_1.5")
except Exception as e:
    logger.error(f"Failed to load AfroLID model: {e}")
    raise



# Load supported languages CSV file 
def load_iso_mapping(filepath="services/supported-languages.csv"):
    try:
        df = pd.read_csv(filepath)
        mapping = {
            row["isocode"]: {"name": row["language"], "script": row["script"]}
            for _, row in df.iterrows()
        }
        return mapping
    except Exception as e:
        logger.error(f"Failed to load mapping file: {e}")
        return {}

# Mapping loaded once
mapping = load_iso_mapping()


def detect_message_language(text: str) -> dict:
    if not text or not isinstance(text, str) or not text.strip():
        return {"code": "unknown", "language": "unknown", "script": "unknown", "confidence": 0.0}

    try:
        result = afrolid_model(text.strip())[0]
        code = result["label"]
        print(f"Detected code: {code}")
        confidence = round(result["score"], 3)
        meta = mapping.get(code, {"name": code, "script": "unknown"})
        print("meta:", meta )

        return {
            "code": code,
            "language": meta["name"],
            "script": meta["script"],
            "confidence": confidence
        }

    except Exception as e:
        logger.warning(f"Detection failed: {e}")
        return {"code": "unknown", "language": "unknown", "script": "unknown", "confidence": 0.0}
