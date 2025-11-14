import os
import pandas as pd

# ==================================================
# STEP 1: Update this path to your txt folder
# ==================================================
TXT_ROOT = r"C:\Users\manda\OneDrive\Desktop\VCTK_corpus\VCTK-Corpus\txt"  # 👈 Example: r"C:\Users\manda\OneDrive\Desktop\VCTK_corpus\VCTK-Corpus\txt"

# ==================================================
# STEP 2: Output CSV path
# ==================================================
OUTPUT_CSV = "transcripts.csv"

# ==================================================
# STEP 3: Read transcripts and generate CSV
# ==================================================
def create_transcript_csv(txt_root, output_csv):
    if not os.path.exists(txt_root):
        raise FileNotFoundError(f"The folder '{txt_root}' does not exist. Please check the path.")

    rows = []
    speakers = sorted(os.listdir(txt_root))

    for speaker in speakers:
        speaker_dir = os.path.join(txt_root, speaker)
        if not os.path.isdir(speaker_dir):
            continue

        for txt_file in os.listdir(speaker_dir):
            if txt_file.endswith(".txt"):
                txt_path = os.path.join(speaker_dir, txt_file)
                try:
                    with open(txt_path, "r", encoding="utf-8") as f:
                        transcript = f.read().strip()
                        if transcript:
                            wav_name = txt_file.replace(".txt", ".wav")
                            rows.append([speaker, wav_name, transcript])
                except Exception as e:
                    print(f"Error reading {txt_path}: {e}")

    df = pd.DataFrame(rows, columns=["speaker", "wav_file", "transcript"])
    df.to_csv(output_csv, index=False)
    print(f"\n✅ Transcripts CSV created successfully: {output_csv}")
    print(f"📄 Total entries: {len(df)}")

# ==================================================
# STEP 4: Run
# ==================================================
if __name__ == "__main__":
    create_transcript_csv(TXT_ROOT, OUTPUT_CSV)
