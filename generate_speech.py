from datasets import load_dataset
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import soundfile as sf

import torch
import pandas as pd
import os

# === Load the model and processor ===
print("Loading SpeechT5 model...")
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# === Create output folder ===
output_dir = "generated_audio"
os.makedirs(output_dir, exist_ok=True)

# === Load transcripts CSV ===
df = pd.read_csv("transcripts.csv")

# === Use a dummy speaker embedding ===
# (Same for all samples — we skip the xvector dataset)
speaker_embeddings = torch.zeros((1, 512))

# === Generate speech for each text line ===
for idx, row in df.iterrows():
    text = row["transcript"]
    file_name = f"sample_{idx}.wav"
    print(f"Generating: {file_name}")

    inputs = processor(text=text, return_tensors="pt")
    speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)

    sf.write(os.path.join(output_dir, file_name), speech.numpy(), 16000)


print(f"\n✅ All samples generated in folder: {output_dir}")
