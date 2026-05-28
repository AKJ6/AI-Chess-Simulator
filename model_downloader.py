# download_gemma_gguf.py

from huggingface_hub import hf_hub_download
from pathlib import Path

# ============================================
# CONFIG
# ============================================

REPO_ID = "Qwen/Qwen3-8B-GGUF"

FILENAME = "Qwen3-8B-Q8_0.gguf"

SAVE_DIR = Path("models") / "Gemma-GGUF"

# ============================================
# DOWNLOAD
# ============================================

def main():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Downloading GGUF model...")
    print(f"Repo      : {REPO_ID}")
    print(f"File      : {FILENAME}")
    print(f"Save Path : {SAVE_DIR}")
    print("=" * 60)

    downloaded_file = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILENAME,
        local_dir=SAVE_DIR,
        local_dir_use_symlinks=False
    )

    print("\nDownload complete.")
    print(f"Saved at:\n{downloaded_file}")


if __name__ == "__main__":
    main()