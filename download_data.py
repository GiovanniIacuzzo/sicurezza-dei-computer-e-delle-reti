import os
os.environ['KAGGLE_CONFIG_DIR'] = '.'
import yaml
from kaggle.api.kaggle_api_extended import KaggleApi

def load_config(config_path="config.yaml"):
    """Carica le impostazioni dal file YAML."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def download_dataset():
    """Connette l'API di Kaggle e scarica gli audio .m4a."""
    config = load_config()
    dataset_name = config["kaggle"]["dataset_name"]
    download_path = config["kaggle"]["download_path"]

    print(f"Inizializzazione API Kaggle per il dataset: {dataset_name}...")
    
    try:
        api = KaggleApi()
        api.authenticate()
    except Exception as e:
        print(f"Errore di autenticazione Kaggle. Hai messo il file kaggle.json in ~/.kaggle/?\nDettagli: {e}")
        return

    print(f"Download e decompressione in corso in '{download_path}'...")
    os.makedirs(download_path, exist_ok=True)
    
    api.dataset_download_files(dataset_name, path=download_path, unzip=True)
    print("Download completato con successo!")

if __name__ == "__main__":
    download_dataset()