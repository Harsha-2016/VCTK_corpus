import os
import pandas as pd
import torch
import torchaudio
from transformers import (
    SpeechT5Processor,
    SpeechT5ForTextToSpeech,
    SpeechT5HifiGan
)
from datasets import load_dataset
import soundfile as sf

# ============ CONFIG ============
CSV_PATH = "transcripts_with_labels_backup.csv"
OUTPUT_BASE = "outputs_by_type"
MAX_SAMPLES = 1500  # process first 1500 only
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ============ MODEL LOADING ============
print("🔊 Loading SpeechT5 model and vocoder...")
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(DEVICE)
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(DEVICE)

# ============ LOAD SPEAKER EMBEDDINGS ============
print("🎙️ Loading speaker embeddings...")
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
# Pick one default embedding (you can change speaker ID for variety)
speaker_embeddings = torch.tensor(embeddings_dataset[0]["xvector"]).unsqueeze(0).to(DEVICE)

# ============ STYLE PROMPTS ============
def style_prompt(text, label):
    label_prompts = {
        "Declarative": f"Speak calmly and clearly: {text}",
        "Interrogative": f"Ask this question naturally: {text}",
        "Exclamatory": f"Say this with excitement: {text}",
        "Imperative": f"Say this as a firm command: {text}",
    }
    return label_prompts.get(label, text)

# ============ LOAD LABELLED TRANSCRIPTS ============
print(f"📖 Reading {CSV_PATH}...")
df = pd.read_csv(CSV_PATH)
df = df.head(MAX_SAMPLES)
print(f"✅ Loaded {len(df)} labelled transcripts.")

# ============ GENERATE SPEECH ============
os.makedirs(OUTPUT_BASE, exist_ok=True)

for idx, row in df.iterrows():
    text = row.get("transcript") or row.get("text") or ""
    if not isinstance(text, str) or not text.strip():
        print(f"⚠️ Skipping empty text at index {idx}")
        continue

    label = str(row.get("sentence_type", "Declarative")).strip()
    styled_text = style_prompt(text, label)

    label_dir = os.path.join(OUTPUT_BASE, label)
    os.makedirs(label_dir, exist_ok=True)
    file_path = os.path.join(label_dir, f"sample_{idx}.wav")

    print(f"[{idx}] Generating {label} → {file_path}")
    try:
        inputs = processor(text=styled_text, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            speech = model.generate_speech(
                inputs["input_ids"],
                speaker_embeddings=speaker_embeddings,
                vocoder=vocoder
            )
        sf.write(file_path, speech.cpu().numpy(), 16000)
    except Exception as e:
        print(f"⚠️ Error at index {idx}: {e}")
        continue

print("✅ Batch synthesis complete!")

