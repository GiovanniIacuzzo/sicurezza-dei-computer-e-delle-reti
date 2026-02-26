import subprocess
import logging
from pathlib import Path
import librosa
import soundfile as sf
import noisereduce as nr
from config import AppConfig

logger = logging.getLogger(__name__)

class AudioProcessingError(Exception):
    """Exception custom per errori legati al processamento audio."""
    pass

class AudioPreprocessor:
    def __init__(self, config: AppConfig):
        self.config = config.audio
        self.temp_dir = Path("data/temp_audio")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def _execute_ffmpeg(self, input_path: Path, output_path: Path) -> None:
        """Esegue l'estrazione audio delegando a FFmpeg."""
        command = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-vn", "-acodec", "pcm_s16le",
            "-ar", str(self.config.sample_rate), "-ac", "1",
            str(output_path)
        ]
        
        try:
            logger.info(f"Extracting audio from {input_path.name}")
            subprocess.run(
                command, 
                check=True, 
                capture_output=True, 
                text=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise AudioProcessingError(f"Failed to extract audio: {e.stderr}")

    def _apply_noise_reduction(self, input_path: Path, output_path: Path) -> None:
        """Applica algoritmi di DSP per la pulizia del segnale."""
        logger.info(f"Applying noise reduction to {input_path.name}")
        try:
            audio_data, sr = librosa.load(str(input_path), sr=self.config.sample_rate)
            
            reduced_audio = nr.reduce_noise(
                y=audio_data, 
                sr=sr, 
                stationary=True, 
                prop_decrease=0.8
            )
            
            sf.write(str(output_path), reduced_audio, sr)
        except Exception as e:
            logger.error(f"Denoise failed: {e}")
            raise AudioProcessingError(f"Noise reduction failed: {e}")

    def process(self, video_path_str: str) -> Path:
        """Pipeline orchestrator con gestione del ciclo di vita dei file."""
        video_path = Path(video_path_str)
        if not video_path.exists():
            raise FileNotFoundError(f"Video non trovato: {video_path}")

        raw_wav = self.temp_dir / f"{video_path.stem}_raw.wav"
        final_wav = self.temp_dir / f"{video_path.stem}_ready.wav"

        try:
            self._execute_ffmpeg(video_path, raw_wav)

            if self.config.apply_noise_reduction:
                self._apply_noise_reduction(raw_wav, final_wav)
                raw_wav.unlink()
            else:
                raw_wav.replace(final_wav)

            logger.info(f"Processing completed: {final_wav}")
            return final_wav

        except Exception as e:
            if raw_wav.exists(): raw_wav.unlink()
            logger.critical(f"Pipeline failed for {video_path.name}: {e}")
            raise