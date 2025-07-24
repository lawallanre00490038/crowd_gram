import argparse
import logging
from pathlib import Path
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
def load_iso_mapping(filepath):
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

# Detect language with optional name/script metadata
def detect_language(text, mapping):
    if not text or not isinstance(text, str) or not text.strip():
        return {"code": "unknown", "language": "unknown", "script": "unknown", "confidence": 0.0}

    try:
        result = afrolid_model(text.strip())[0]
        code = result["label"]
        confidence = round(result["score"], 3)
        meta = mapping.get(code, {"name": code, "script": "unknown"})

        return {
            "code": code,
            "language": meta["name"],
            "script": meta["script"],
            "confidence": confidence
        }

    except Exception as e:
        logger.warning(f"Detection failed: {e}")
        return {"code": "unknown", "language": "unknown", "script": "unknown", "confidence": 0.0}

mapping = load_iso_mapping("supported-languages.csv")
# Single text detection
def detect_single(args):
    result = detect_language(args.text, mapping)
    print(f"Detected Language Code: {result['code']}")
    print(f"Language Name: {result['language']}")
    print(f"Script: {result['script']}")
    print(f"Confidence: {result['confidence']}")

# Batch detection from file
def detect_batch(args):
    input_path = Path(args.input)
    ext = input_path.suffix.lower()

    if ext == ".txt":
        with open(input_path, encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
        df = pd.DataFrame({"text": lines})
    elif ext == ".csv":
        df = pd.read_csv(input_path)
    elif ext == ".xlsx":
        df = pd.read_excel(input_path)
    elif ext == ".json":
        df = pd.read_json(input_path)
    else:
        raise ValueError("Unsupported input format. Use .txt, .csv, .xlsx, or .json.")

    if "text" not in df.columns:
        raise ValueError("Input file must contain a 'text' column.")

    results = []
    for i, text in enumerate(df["text"]):
        result = detect_language(text, mapping)
        logger.info(f"[{i+1}] {result['code']} ({result['confidence']:.2%}) — {result['language']}")
        results.append({
            "text": text,
            "language_code": result["code"],
            "language_name": result["language"],
            "unicode_script": result["script"],
            "confidence": result["confidence"]
        })

    out_df = pd.DataFrame(results)
    if args.output:
        out_path = Path(args.output)
        out_ext = out_path.suffix.lower()
        if out_ext == ".csv":
            out_df.to_csv(out_path, index=False)
        elif out_ext == ".xlsx":
            out_df.to_excel(out_path, index=False)
        elif out_ext == ".json":
            out_df.to_json(out_path, orient="records", indent=2, force_ascii=False)
        else:
            raise ValueError("Unsupported output format. Use .csv, .xlsx, or .json.")
        print(f"Saved output to {args.output}")
    else:
        print(out_df.to_string(index=False))

# CLI entry
def main():
    parser = argparse.ArgumentParser(description="AfroLID Language Detection CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single
    single_parser = subparsers.add_parser("single", help="Detect language for a single string")
    single_parser.add_argument("--text", type=str, required=True, help="Text to detect")
    single_parser.set_defaults(func=detect_single)

    # Batch
    batch_parser = subparsers.add_parser("batch", help="Detect language in a file")
    batch_parser.add_argument("--input", required=True, help="Input file (.txt, .csv, .xlsx, .json)")
    batch_parser.add_argument("--output", help="Optional output file (.csv, .xlsx, .json)")
    batch_parser.set_defaults(func=detect_batch)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
