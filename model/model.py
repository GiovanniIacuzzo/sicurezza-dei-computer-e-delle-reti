import logging
from pathlib import Path
from typing import List, Optional, Dict

from faster_whisper import WhisperModel
from config import AppConfig

logger = logging.getLogger(__name__)

class TranscriptionResult:
    """Data class per strutturare l'output della trascrizione."""
    def __init__(self, text: str, language: str, probability: float, segments: List[Dict]):
        self.text = text
        self.language = language
        self.probability = probability
        self.segments = segments

class WhisperTranscriber:
    def __init__(self, config: AppConfig):
        self.cfg = config
        self._model: Optional[WhisperModel] = None
        self._load_model()

    def _load_model(self) -> None:
        """Inizializza il modello con gestione delle risorse."""
        try:
            logger.info(
                f"Loading Whisper {self.cfg.model.name} on {self.cfg.model.device.upper()} "
                f"({self.cfg.model.compute_type})"
            )
            self._model = WhisperModel(
                model_size_or_path=self.cfg.model.name,
                device=self.cfg.model.device,
                compute_type=self.cfg.model.compute_type
            )
        except Exception as e:
            logger.critical(f"Failed to initialize Whisper model: {e}")
            raise RuntimeError("Model initialization failed.") from e

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        """
        Esegue la trascrizione con logging granulare e ritorno strutturato.
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        t_cfg = self.cfg.transcription
        logger.info(f"Starting transcription: {audio_path.name}")

        segments_gen, info = self._model.transcribe(
            str(audio_path),
            language=t_cfg.language,
            beam_size=t_cfg.beam_size,
            vad_filter=t_cfg.vad_filter,
            vad_parameters=t_cfg.vad_parameters.model_dump(),
            initial_prompt=t_cfg.initial_prompt,
            condition_on_previous_text=False
        )

        logger.info(f"Detected language: {info.language} ({info.language_probability:.2%})")

        processed_segments = []
        full_text_parts = []

        for segment in segments_gen:
            logger.debug(f"[{segment.start:.2f}s -> {segment.end:.2f}s] Processing segment...")
            
            segment_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
            processed_segments.append(segment_data)
            full_text_parts.append(segment_data["text"])

        return TranscriptionResult(
            text=" ".join(full_text_parts),
            language=info.language,
            probability=info.language_probability,
            segments=processed_segments
        )