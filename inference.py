import logging
import sys
import time
from pathlib import Path
from typing import List

from config import AppConfig
from dataset.dataset import AudioPreprocessor, AudioProcessingError
from model.model import WhisperTranscriber, TranscriptionResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline.log")
    ]
)
logger = logging.getLogger("TranscriptionPipeline")

class Transcription:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = AppConfig.from_yaml(config_path)
        
        self.preprocessor = AudioPreprocessor(self.config)
        self.transcriber = WhisperTranscriber(self.config)
        
        self.input_dir = Path("data/")
        self.output_dir = Path("data/transcriptions/")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_files_to_process(self, extension: str = "*.m4a") -> List[Path]:
        """Recupera la lista dei file ignorando quelli già processati."""
        all_files = list(self.input_dir.glob(extension))
        to_process = []
        
        for file_path in all_files:
            output_file = self.output_dir / f"{file_path.stem}.txt"
            if output_file.exists():
                logger.info(f"Skipping {file_path.name}: Transcription already exists.")
                continue
            to_process.append(file_path)
            
        return to_process

    def run(self):
        """Esegue il loop di elaborazione batch."""
        files = self._get_files_to_process()
        
        if not files:
            logger.warning("No new files found to process.")
            return

        logger.info(f"Starting batch processing for {len(files)} files.")

        for video_path in files:
            start_time = time.perf_counter()
            temp_audio: Path = None
            
            try:
                logger.info(f"--- Processing: {video_path.name} ---")

                temp_audio = self.preprocessor.process(str(video_path))

                result: TranscriptionResult = self.transcriber.transcribe(temp_audio)

                self._save_result(video_path.stem, result)

                elapsed = (time.perf_counter() - start_time) / 60
                logger.info(f"Successfully processed {video_path.name} in {elapsed:.2f} minutes.")

            except (AudioProcessingError, Exception) as e:
                logger.error(f"Failed to process {video_path.name}: {str(e)}", exc_info=True)
            
            finally:
                if temp_audio and temp_audio.exists():
                    temp_audio.unlink()
                    logger.debug(f"Temporary file {temp_audio} deleted.")

    def _save_result(self, filename_stem: str, result: TranscriptionResult):
        """Salva il testo e potenzialmente i metadati (JSON/SRT)."""
        txt_path = self.output_dir / f"{filename_stem}.txt"
        
        txt_path.write_text(result.text, encoding="utf-8")
        

def main():
    try:
        orchestrator = Transcription("config.yaml")
        orchestrator.run()
    except KeyboardInterrupt:
        logger.warning("\nProcess interrupted by user. Exiting gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error in application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()