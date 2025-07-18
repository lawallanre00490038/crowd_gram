from transformers import XLMTokenizer, XLMWithLMHeadModel, MarianMTModel, MarianTokenizer
import logging
import math
import torch
from functools import lru_cache
from sentence_transformers import SentenceTransformer, util


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model with error handling
try:
    embedder = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
except Exception as e:
    logger.error(f"Failed to load SentenceTransformer: {e}")
    raise



try:
    xlm_tokenizer = XLMTokenizer.from_pretrained("xlm-roberta-base")
    xlm_model = XLMWithLMHeadModel.from_pretrained("xlm-roberta-base")
    xlm_model.eval()
except Exception as e:
    logger.error(f"Failed to load XLM-RoBERTa model: {e}")
    raise

# --- SEMANTIC & COHERENCE CHECKS ---
def calculate_perplexity(text):
    """Calculate perplexity for coherence using XLM-RoBERTa (multilingual)."""
    if not text or not isinstance(text, str):
        return float('inf')
    try:
        inputs = xlm_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = xlm_model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
        return round(math.exp(loss.item()), 2)
    except Exception as e:
        logger.warning(f"Perplexity calculation failed: {e}")
        return float('inf')

@lru_cache(maxsize=100)
def back_translate(text, target_lang_code):
    """Perform back-translation to English with caching, handling unsupported languages."""
    if not text or not isinstance(text, str):
        return "[Invalid Input]"
    try:
        model_name = f"Helsinki-NLP/opus-mt-{target_lang_code}-en"
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        translated = model.generate(**inputs, max_length=512)
        return tokenizer.decode(translated[0], skip_special_tokens=True)
    except Exception as e:
        logger.warning(f"Back-translation failed for {target_lang_code}: {e}. Language may be unsupported.")
        return "[Unsupported Language or Error]"

def is_relevant_to_prompt(prompt, back_translation, similarity_threshold=0.6):
    """Check semantic similarity between prompt and back-translation."""
    if not prompt or not back_translation or not isinstance(prompt, str) or not isinstance(back_translation, str):
        return False, 0.0
    try:
        embeddings = embedder.encode([prompt, back_translation], convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
        return similarity >= similarity_threshold, round(similarity, 3)
    except Exception as e:
        logger.warning(f"Similarity check failed: {e}")
        return False, 0.0
    


def main(prompt, translation, target_lang_code="yo", similarity_threshold=0.6):
    """Run semantic QA checks on a prompt and its translation."""
    results = {}

    # Perplexity
    results["perplexity"] = calculate_perplexity(translation)

    # Back-translation and semantic similarity
    back_translation = back_translate(translation, target_lang_code)
    results["back_translation"] = back_translation
    relevant, similarity = is_relevant_to_prompt(prompt, back_translation, similarity_threshold)
    results["relevance_ok"] = relevant
    results["semantic_similarity"] = similarity

    return results

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run semantic and coherence QA checks.")
    parser.add_argument("--prompt", type=str, required=True, help="Source prompt")
    parser.add_argument("--translation", type=str, required=True, help="Translated text")
    parser.add_argument("--target_lang", type=str, default="yo", help="Target language code for back-translation")
    parser.add_argument("--similarity_threshold", type=float, default=0.6, help="Minimum semantic similarity for relevance")

    args = parser.parse_args()

    output = main(
        prompt=args.prompt,
        translation=args.translation,
        target_lang_code=args.target_lang,
        similarity_threshold=args.similarity_threshold
    )

    for key, value in output.items():
        print(f"{key}: {value}")
