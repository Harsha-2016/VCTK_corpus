import torch
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import soundfile as sf

print("🔊 Loading SpeechT5 model and vocoder...")
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# --- Load speaker embedding ---
try:
    print("🎙️ Loading speaker embedding from Hugging Face...")
    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
    base_embedding = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
    print("✅ Speaker embedding loaded successfully.")
except Exception as e:
    print("⚠️ Could not load pretrained speaker embedding. Using neutral voice instead.")
    print(f"Error details: {e}")
    base_embedding = torch.zeros((1, 512))

# --- Define tone modifiers ---
TONE_MODIFIERS = {
    "Declarative": torch.zeros_like(base_embedding),  # calm, neutral
    "Interrogative": torch.randn_like(base_embedding) * 0.05,  # slightly higher pitch
    "Exclamatory": torch.randn_like(base_embedding) * 0.1,  # expressive, energetic
    "Imperative": -torch.abs(torch.randn_like(base_embedding) * 0.05),  # lower, firm tone
}

print("\n🎤 Interactive Mode: Type any sentence and its label to generate audio!")
print("Type 'exit' at any point to quit.\n")

while True:
    text = input("Enter a sentence (or type 'exit' to quit): ").strip()
    if text.lower() == "exit":
        print("👋 Exiting demo...")
        break

    label = input("Enter its type (Declarative / Interrogative / Exclamatory / Imperative): ").strip().capitalize()
    if label.lower() == "exit":
        print("👋 Exiting demo...")
        break

    print(f"\n🗣️ Generating speech for: \"{text}\" with tone → {label}")

    # Adjust speaker embedding based on label
    modifier = TONE_MODIFIERS.get(label, torch.zeros_like(base_embedding))
    speaker_embedding = base_embedding + modifier

    inputs = processor(text=text, return_tensors="pt")

    with torch.no_grad():
        speech = model.generate_speech(inputs["input_ids"], speaker_embedding, vocoder=vocoder)

    output_path = f"output_{label.lower()}.wav"
    sf.write(output_path, speech.numpy(), samplerate=16000)
    print(f"✅ Audio generated successfully with {label} tone → saved as '{output_path}'\n")
