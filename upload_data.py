import os
import shutil
import logging
import yaml
from typing import List, Optional
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KaggleUploader:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        self.dataset_id: str = self.config["kaggle"]["dataset_name"]

        self.archive_path = Path("data")
        self.queue_path = Path("new_data")
        
        os.environ['KAGGLE_CONFIG_DIR'] = os.path.abspath('.')
        self.api = KaggleApi()
        
        self._prepare_directories()
        self._fix_token_permissions()

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configurazione non trovata: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _prepare_directories(self) -> None:
        self.archive_path.mkdir(parents=True, exist_ok=True)
        self.queue_path.mkdir(parents=True, exist_ok=True)

    def _fix_token_permissions(self) -> None:
        """Risolve il warning sulla leggibilità del file kaggle.json su sistemi Unix."""
        token_path = Path("kaggle.json")
        if token_path.exists() and os.name != 'nt':
            os.chmod(token_path, 0o600)
            logger.debug("Permessi kaggle.json impostati a 600.")

    def _authenticate(self) -> None:
        """Autenticazione con verifica di autorizzazione."""
        try:
            self.api.authenticate()
            user = self.api.config_values.get('username')
            logger.info(f"Autenticato come utente: {user}")
        except Exception as e:
            logger.error(f"Errore autenticazione: {e}")
            raise

    def get_pending_files(self) -> List[Path]:
        extensions = ('.mp4', '.m4a', '.wav', '.mp3')
        return [p for p in self.queue_path.iterdir() if p.suffix.lower() in extensions]

    def process_upload(self, version_notes: Optional[str] = None) -> bool:
        pending_files = self.get_pending_files()
        
        if not pending_files:
            logger.warning(f"Nessun file trovato in {self.queue_path}. Operazione annullata.")
            return False

        self._authenticate()
        
        file_names = [f.name for f in pending_files]
        logger.info(f"File identificati per lo staging: {file_names}")

        try:
            for file_path in pending_files:
                dest_file = self.archive_path / file_path.name
                shutil.copy2(file_path, dest_file)
            
            notes = version_notes or f"Update: {', '.join(file_names)}"

            logger.info(f"Avvio caricamento su Kaggle per il dataset: {self.dataset_id}")
            
            self.api.dataset_create_version(
                folder=str(self.archive_path),
                version_notes=notes,
                dir_mode="zip"
            )
            
            logger.info("Upload completato. Procedo alla pulizia della coda.")
            self._cleanup_queue(pending_files)
            return True

        except Exception as e:
            logger.error(f"Errore critico durante l'upload: {e}")
            return False

    def _cleanup_queue(self, files: List[Path]) -> None:
        for file_path in files:
            try:
                file_path.unlink()
            except Exception as e:
                logger.error(f"Impossibile rimuovere {file_path.name}: {e}")

if __name__ == "__main__":
    uploader = KaggleUploader()
    uploader.process_upload()