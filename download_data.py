import os
import yaml
import zipfile
import logging
import shutil
from pathlib import Path
from typing import List
from kaggle.api.kaggle_api_extended import KaggleApi

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KaggleDownloader:
    """Gestore professionale per il recupero selettivo di asset da Kaggle Datasets."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        self.dataset_id: str = self.config["kaggle"]["dataset_name"]
        self.target_path = Path(self.config["kaggle"].get("download_path", "data"))
        self.temp_dir = Path("temp_cache")
        
        os.environ['KAGGLE_CONFIG_DIR'] = '.'
        self.api = KaggleApi()
        
        self._prepare_environment()

    def _load_config(self) -> dict:
        """Carica e valida il file di configurazione YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configurazione non trovata: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _prepare_environment(self) -> None:
        """Inizializza le directory di destinazione e pulisce cache pregresse."""
        self.target_path.mkdir(parents=True, exist_ok=True)
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True)

    def _authenticate(self) -> None:
        """Esegue l'autenticazione API."""
        try:
            self.api.authenticate()
        except Exception as e:
            logger.error(f"Errore durante l'autenticazione Kaggle: {e}")
            raise

    def get_remote_file_list(self) -> List:
        """Recupera i metadati dei file disponibili sul server remoto."""
        self._authenticate()
        logger.info(f"Interrogazione dataset remoto: {self.dataset_id}")
        return self.api.dataset_list_files(self.dataset_id).files

    def select_and_download(self) -> None:
        """Workflow interattivo per la selezione e il download granulare."""
        try:
            remote_files = self.get_remote_file_list()
            if not remote_files:
                logger.warning("Il dataset remoto è vuoto.")
                return

            print(f"\n{'ID':<5} | {'NOME FILE':<40} | {'DIMENSIONE':<10}")
            print("-" * 60)
            for i, file in enumerate(remote_files):
                size_mb = file.sizeBytes / (1024**2)
                print(f"{i:<5} | {file.name:<40} | {size_mb:>7.2f} MB")

            choice = input("\nInserisci l'ID della lezione, una lista (es. 1,3,5) o 'all': ").strip().lower()
            
            self._execute_download(remote_files, choice)

        except Exception as e:
            logger.error(f"Errore durante il workflow di download: {e}")
        finally:
            self._cleanup()

    def _execute_download(self, file_list: List, choice: str) -> None:
        """Scarica l'archivio ed estrae solo i file selezionati (Memory efficient)."""
        logger.info("Avvio download pacchetto compresso...")
        self.api.dataset_download_files(self.dataset_id, path=str(self.temp_dir), unzip=False)
        
        zip_name = f"{self.dataset_id.split('/')[-1]}.zip"
        zip_path = self.temp_dir / zip_name

        if not zip_path.exists():
            raise FileNotFoundError("Archivio scaricato non trovato.")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            filenames_to_extract = []

            if choice == 'all':
                filenames_to_extract = [f.name for f in file_list]
            else:
                indices = [int(i.strip()) for i in choice.split(',') if i.strip().isdigit()]
                filenames_to_extract = [file_list[i].name for i in indices if i < len(file_list)]

            for filename in filenames_to_extract:
                logger.info(f"Estrazione: {filename} -> {self.target_path}")
                zip_ref.extract(filename, path=str(self.target_path))
            
            logger.info(f"Operazione completata. {len(filenames_to_extract)} file estratti.")

    def _cleanup(self) -> None:
        """Rimozione sicura dei file temporanei."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            logger.debug("Cache temporanea rimossa.")

if __name__ == "__main__":
    downloader = KaggleDownloader()
    downloader.select_and_download()