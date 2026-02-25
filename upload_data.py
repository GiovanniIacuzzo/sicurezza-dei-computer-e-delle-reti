import os
os.environ['KAGGLE_CONFIG_DIR'] = '.'
import json
import yaml
from kaggle.api.kaggle_api_extended import KaggleApi

def load_config(config_path="config.yaml"):
    """Carica le impostazioni dal file YAML."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def create_metadata(data_path: str, dataset_id: str):
    """Genera automaticamente il file dataset-metadata.json richiesto da Kaggle."""
    try:
        username, slug = dataset_id.split('/')
    except ValueError:
        raise ValueError("Il 'dataset_name' nel config.yaml deve essere nel formato 'tuo-username/nome-dataset'.")

    # Creiamo un titolo leggibile partendo dallo slug (es. "nome-dataset-lezioni" -> "Nome Dataset Lezioni")
    title = slug.replace('-', ' ').title()
    
    metadata = {
        "title": title,
        "id": dataset_id,
        "licenses": [{"name": "CC0-1.0"}] # Licenza di default (Pubblico Dominio)
    }
    
    metadata_path = os.path.join(data_path, "dataset-metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        
    print(f"[*] Creato file di metadati in: {metadata_path}")

def main():
    config = load_config()
    dataset_id = config["kaggle"]["dataset_name"]
    data_path = "data" # La cartella dove hai messo i tuoi file .mp4
    
    print("="*50)
    print(f"Inizio procedura di upload verso Kaggle ({dataset_id})")
    print("="*50)

    # 1. Controllo base: la cartella esiste e contiene file?
    if not os.path.exists(data_path):
        print(f"[ERRORE] La cartella '{data_path}' non esiste nel tuo computer.")
        return
        
    files_in_dir = [f for f in os.listdir(data_path) if f.endswith(('.mp4', '.m4a'))]
    if not files_in_dir:
        print(f"[ERRORE] Nessun file .mp4 trovato nella cartella '{data_path}'. Aggiungi gli audio prima di caricare.")
        return
        
    print(f"[*] Trovati {len(files_in_dir)} file audio da caricare.")

    # 2. Inizializzazione API Kaggle
    try:
        api = KaggleApi()
        api.authenticate()
    except Exception as e:
        print(f"[ERRORE] Autenticazione fallita. Assicurati di avere il file kaggle.json in ~/.kaggle/ nel tuo computer locale.\nDettagli: {e}")
        return

    # 3. Creazione del file metadata
    create_metadata(data_path, dataset_id)

    # 4. Upload su Kaggle
    print("\n[*] Connessione ai server Kaggle in corso... (potrebbe volerci un po' a seconda della tua connessione)")
    
    try:
        # Tenta prima di creare una nuova versione (se il dataset esiste già su Kaggle)
        api.dataset_create_version(
            folder=data_path,
            version_notes="Nuovi audio aggiunti o aggiornati",
            dir_mode="zip"
        )
        print("\n[SUCCESSO] Nuova versione del dataset caricata correttamente!")
        
    except Exception as e:
        # Se fallisce, probabilmente il dataset non è mai stato creato, quindi lo crea da zero
        print("[*] Il dataset non esiste ancora. Creazione di un nuovo dataset in corso...")
        try:
            api.dataset_create_new(
                folder=data_path,
                dir_mode="zip"
            )
            print("\n[SUCCESSO] Nuovo dataset creato e caricato correttamente!")
        except Exception as ex:
            print(f"\n[ERRORE CRITICO] Impossibile caricare il dataset. Dettagli: {ex}")

if __name__ == "__main__":
    main()