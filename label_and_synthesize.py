"""
label_and_synthesize.py

Workflow:
1) Read transcripts.csv (auto-detect text column).
2) For each transcript, call local Ollama REST API at http://localhost:11434/api/generate
   to obtain one of the labels: Declarative, Interrogative, Exclamatory, Imperative.
   - Ollama response IS the ground-truth label (as you requested).
   - The prompt forces the model to output only the label (no extra text).
3) Save labels incrementally to transcripts_with_labels.csv (checkpointing).
4) Use SpeechT5 to synthesize each transcript while preserving sentence_type:
   - Use fixed random-but-deterministic embeddings per sentence type (consistent across runs).
   - Optionally tweak text slightly for prosody cues.
5) Save outputs to generated_audio_sentence_types/ with filenames like: {idx}_{sentence_type}.wav
6) Extensive logging, retry/backoff for Ollama calls, failed list saved to failed_calls.json.

Configurable parameters are at the top of the file.
"""

import os
import time
import json
import hashlib
import requests
import logging
import argparse
from typing import Optional
from tqdm import tqdm
import pandas as pd
import torch
import soundfile as sf
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan

# ---------------- CONFIG ----------------
OLLTAMA_HOST = "http://localhost:11434"   # Ollama server
OLLA_MODEL = "gemma3"                     # Model you've pulled in Ollama. Change as needed.
TRANSCRIPTS_CSV = "transcripts.csv"      # Input CSV you already generated
OUT_CSV = "transcripts_with_labels.csv"   # Checkpoint CSV with labels appended
FAILED_JSON = "ollama_failed.json"        # Log of failed label calls
OUTPUT_DIR = "generated_audio_sentence_types"  # Where synthesized audios go
BATCH_SIZE = 1    # number of parallel calls to Ollama per iteration (1 = sequential). Increase carefully.
RATE_LIMIT_SLEEP = 0.05  # seconds between requests (tweak depending on Ollama capacity)
MAX_RETRIES = 5
RETRY_BACKOFF = 2.0  # multiplier for exponential backoff
CHECKPOINT_INTERVAL = 500   # save CSV/checkpoint every N labelled samples
SYNTHESIZE_AFTER_LABELING = True  # set False to only label and skip synthesis
SAMPLE_LIMIT = None  # set to int for quick testing (e.g., 20). None -> full CSV
# ----------------------------------------

# Setup logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("label_and_synthesize.log"),
        logging.StreamHandler()
    ],
)

# Ollama prompt to enforce single-label reply
OLLAMA_PROMPT = """
You are an assistant that MUST label a single English sentence into exactly one of the following four classes:
- Declarative
- Interrogative
- Exclamatory
- Imperative

Rules:
1) Respond with exactly ONE word: Declarative, Interrogative, Exclamatory, or Imperative (case-sensitive).
2) Do NOT add any explanations, punctuation, or extra text — only the single label.
3) If the sentence is ambiguous, choose the label that best matches the primary communicative intent.

Examples:
"Please pass the salt." -> Imperative
"Is the train on time?" -> Interrogative
"What a wonderful day!" -> Exclamatory
"I will go to the store." -> Declarative

Now label this sentence:

SENTENCE:
\"\"\"{sentence}\"\"\"

Return only the label.
"""

# ---------------- Helper utilities ----------------

def deterministic_embedding_for_label(label: str) -> torch.Tensor:
    """
    Produce a deterministic (but pseudo-random) 512-d embedding per label using hashing.
    This ensures the embedding is the same across runs for the same label.
    """
    # 512 dims
    seed_bytes = hashlib.sha256(label.encode("utf-8")).digest()
    # turn into int seed
    seed_int = int.from_bytes(seed_bytes[:8], "big") % (2**31)
    rng = torch.Generator()
    rng.manual_seed(seed_int)
    emb = torch.randn((1, 512), generator=rng) * 0.2
    return emb

def detect_text_column(df: pd.DataFrame) -> str:
    cand = [c for c in df.columns if c.lower() in ("text", "transcript", "sentence", "utterance")]
    if cand:
        logging.info(f"Auto-detected text column: {cand[0]}")
        return cand[0]
    # fallback: if only two columns, choose the one that's not speaker/wav; else raise
    if len(df.columns) == 1:
        return df.columns[0]
    # Prefer 'transcript' if present despite case
    for c in df.columns:
        if "transcript" in c.lower():
            return c
    raise ValueError(f"Couldn't auto-detect text column. CSV columns: {list(df.columns)}")

def call_ollama_label(sentence: str, model: str = OLLA_MODEL, timeout=60.0) -> Optional[str]:
    """
    Call the local Ollama REST endpoint to get a single label.
    Returns the label (string) if successful, else None.
    Uses the /api/generate endpoint with stream false.
    """
    url = f"{OLLTAMA_HOST}/api/generate"
    prompt = OLLAMA_PROMPT.format(sentence=sentence)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
    except Exception as e:
        logging.debug(f"Ollama request exception: {e}")
        return None

    if resp.status_code != 200:
        logging.debug(f"Ollama returned status {resp.status_code}: {resp.text[:400]}")
        return None

    # The API will return JSON. Common shape: { "response": "...", ... } or streaming chunks.
    try:
        data = resp.json()
    except Exception as e:
        logging.debug(f"Failed to parse Ollama JSON: {e}, raw: {resp.text[:400]}")
        return None

    # Search common fields for text
    # In many Ollama responses final text is in data["output"] or data["response"] or data["choices"]
    # We'll try a few places:
    text = None
    # Try 'response'
    if isinstance(data.get("response"), str):
        text = data.get("response")
    # Try 'output'
    if not text and isinstance(data.get("output"), list):
        # output is a list of items (usually streaming), join textual parts
        parts = []
        for item in data["output"]:
            if isinstance(item, dict) and "content" in item:
                parts.append(item["content"])
            elif isinstance(item, str):
                parts.append(item)
        text = " ".join(parts).strip() if parts else None
    # Try 'choices'
    if not text and isinstance(data.get("choices"), list) and len(data["choices"]) > 0:
        ch = data["choices"][0]
        if isinstance(ch, dict) and "message" in ch and isinstance(ch["message"], dict) and "content" in ch["message"]:
            text = ch["message"]["content"]
        elif isinstance(ch, str):
            text = ch

    # Last fallback: try top-level fields that are strings
    if not text:
        for k, v in data.items():
            if isinstance(v, str) and len(v) < 1000:
                text = v
                break

    if not text:
        logging.debug(f"Ollama response JSON had no textual field. Full JSON: {json.dumps(data)[:1000]}")
        return None

    # Clean label: sometimes the model returns newline/punctuation — keep only the first token
    label = text.strip().splitlines()[0].strip()
    # If it returns extra words, extract the first token that matches one of the labels
    for token in label.replace(",", " ").split():
        if token in ("Declarative", "Interrogative", "Exclamatory", "Imperative"):
            return token
    # Sometimes the whole string matches ignoring case
    low = label.lower()
    if "declar" in low:
        return "Declarative"
    if "interrog" in low or low.startswith("q") or low.endswith("?"):
        return "Interrogative"
    if "exclam" in low or "!" in label:
        return "Exclamatory"
    if "imper" in low or low.startswith("please"):
        return "Imperative"
    # If nothing matched, return the raw first token (but caller should treat as uncertain)
    return label.split()[0] if label else None

# ---------------- Main pipeline ----------------

def label_transcripts_with_ollama(df: pd.DataFrame, text_col: str):
    n = len(df) if SAMPLE_LIMIT is None else min(SAMPLE_LIMIT, len(df))
    logging.info(f"Starting labeling for {n} rows (SAMPLE_LIMIT={SAMPLE_LIMIT})")
    labels = []
    failed = {}
    start_idx = 0

    # If OUT_CSV exists, resume from it
    if os.path.exists(OUT_CSV):
        resume_df = pd.read_csv(OUT_CSV)
        if text_col in resume_df.columns and "sentence_type" in resume_df.columns:
            logging.info(f"Resuming from existing {OUT_CSV}. Already labeled: {len(resume_df)}")
            # Merge existing labels back into df
            merged = df.merge(resume_df[["speaker","wav_file","sentence_type"]], how="left", on=["speaker","wav_file"]) if {"speaker","wav_file"}.issubset(df.columns) else None
            if merged is not None and "sentence_type" in merged.columns:
                df["sentence_type"] = merged["sentence_type"]
                # Continue from first unlabeled
                for i in range(n):
                    if pd.isna(df.at[i, "sentence_type"]):
                        start_idx = i
                        break
                else:
                    start_idx = n
            else:
                # fallback: just continue
                pass

    for i in tqdm(range(start_idx, n), desc="Labeling"):
        row = df.iloc[i]
        sentence = str(row[text_col]).strip()
        if not sentence:
            df.at[i, "sentence_type"] = ""
            continue
        # Skip if already labeled
        if "sentence_type" in df.columns and pd.notna(df.at[i, "sentence_type"]) and df.at[i, "sentence_type"] != "":
            continue

        success = False
        attempt = 0
        label = None
        while attempt < MAX_RETRIES and not success:
            attempt += 1
            label = call_ollama_label(sentence)
            if label is None:
                wait = (RETRY_BACKOFF ** attempt)
                logging.warning(f"Ollama call failed for row {i} (attempt {attempt}), sleeping {wait:.1f}s then retrying.")
                time.sleep(wait)
            else:
                # accept only the four allowed labels or treat as unknown
                if label not in ("Declarative", "Interrogative", "Exclamatory", "Imperative"):
                    logging.warning(f"Ollama returned unexpected label '{label}' for row {i}; accepting but marking as 'UNKNOWN_{label}'")
                    label = f"UNKNOWN_{label}"
                df.at[i, "sentence_type"] = label
                success = True
            time.sleep(RATE_LIMIT_SLEEP)

        if not success:
            logging.error(f"Failed to label row {i} after {MAX_RETRIES} attempts. Marking as __FAILED__.")
            df.at[i, "sentence_type"] = "__FAILED__"
            failed[int(i)] = { "sentence": sentence }
        # checkpoint periodically
        if (i+1) % CHECKPOINT_INTERVAL == 0:
            logging.info(f"Checkpoint at {i+1} — saving {OUT_CSV} and failed list.")
            df.to_csv(OUT_CSV, index=False)
            with open(FAILED_JSON, "w", encoding="utf-8") as f:
                json.dump(failed, f, indent=2)

    # final save
    df.to_csv(OUT_CSV, index=False)
    with open(FAILED_JSON, "w", encoding="utf-8") as f:
        json.dump(failed, f, indent=2)
    logging.info(f"Labeling finished. Saved {OUT_CSV}, failed calls saved to {FAILED_JSON}")
    return df

# ---------------- Synthesis section ----------------

def synthesize_with_sentence_type(df: pd.DataFrame, text_col: str):
    # prepare SpeechT5
    logging.info("Loading SpeechT5 components for synthesis...")
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # deterministic embeddings per sentence type
    emb_map = {
        "Declarative": deterministic_embedding_for_label("Declarative"),
        "Interrogative": deterministic_embedding_for_label("Interrogative"),
        "Exclamatory": deterministic_embedding_for_label("Exclamatory"),
        "Imperative": deterministic_embedding_for_label("Imperative"),
    }

    # function to tweak text for prosody cues
    def tweak_text(text, stype):
        t = str(text).strip()
        if stype == "Exclamatory":
            if not t.endswith("!"):
                t = t + "!"
        elif stype == "Interrogative":
            if not t.endswith("?"):
                t = t + "?"
        elif stype == "Imperative":
            if not t.lower().startswith("please"):
                t = "Please " + t.lstrip().capitalize()
        return t

    n = len(df) if SAMPLE_LIMIT is None else min(SAMPLE_LIMIT, len(df))
    logging.info(f"Starting synthesis for {n} rows")
    for i in tqdm(range(n), desc="Synthesis"):
        row = df.iloc[i]
        text = str(row[text_col]).strip()
        stype = row.get("sentence_type", "")
        if not text:
            continue
        if not stype or stype.startswith("__FAILED__") or stype.startswith("UNKNOWN_"):
            # fallback: detect using punctuation as cheap fallback
            if text.endswith("?"):
                stype = "Interrogative"
            elif text.endswith("!"):
                stype = "Exclamatory"
            elif text.lower().startswith(("please","do ","make ","go ","let ")):
                stype = "Imperative"
            else:
                stype = "Declarative"

        emb = emb_map.get(stype, emb_map["Declarative"])
        mod_text = tweak_text(text, stype)

        # generate audio
        try:
            inputs = processor(text=mod_text, return_tensors="pt")
            speech = model.generate_speech(inputs["input_ids"], emb, vocoder=vocoder)  # tensor (T,)
            out_name = f"{i}_{stype}.wav"
            out_path = os.path.join(OUTPUT_DIR, out_name)
            sf.write(out_path, speech.numpy(), 16000)
        except Exception as e:
            logging.exception(f"Synthesis failed for idx {i}, stype {stype}, text={text[:80]}...: {e}")
            # continue with next

    logging.info(f"Synthesis complete. Outputs in: {OUTPUT_DIR}")

# ---------------- Main CLI ----------------

def main():
    parser = argparse.ArgumentParser(description="Label transcripts with Ollama and synthesize preserving sentence type.")
    parser.add_argument("--label-only", action="store_true", help="Only run labeling (don't synthesize).")
    parser.add_argument("--synthesize-only", action="store_true", help="Only run synthesis using existing transcripts_with_labels.csv.")
    parser.add_argument("--sample-limit", type=int, default=None, help="Process only first N samples (useful for quick testing).")
    args = parser.parse_args()

    global SAMPLE_LIMIT
    if args.sample_limit:
        SAMPLE_LIMIT = args.sample_limit

    # read original transcripts
    if args.synthesize_only:
        if not os.path.exists(OUT_CSV):
            raise FileNotFoundError(f"{OUT_CSV} not found — run labeling first.")
        df = pd.read_csv(OUT_CSV)
        text_col = detect_text_column(df)
        synthesize_with_sentence_type(df, text_col)
        return

    # normal flow: label then synthesize (unless label-only)
    if not os.path.exists(TRANSCRIPTS_CSV):
        raise FileNotFoundError(f"{TRANSCRIPTS_CSV} not found in working dir.")
    df = pd.read_csv(TRANSCRIPTS_CSV)
    text_col = detect_text_column(df)
    logging.info(f"Using text column: {text_col}")

    df = label_transcripts_with_ollama(df, text_col)

    if not args.label_only and SYNTHESIZE_AFTER_LABELING:
        synthesize_with_sentence_type(df, text_col)

if __name__ == "__main__":
    main()
