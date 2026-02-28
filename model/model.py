import logging
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm

from faster_whisper import WhisperModel
from config import AppConfig

logger = logging.getLogger(__name__)

class TranscriptionResult:
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
        try:
            logger.info(f"Loading Whisper {self.cfg.model.name} on {self.cfg.model.device.upper()}...")
            self._model = WhisperModel(
                model_size_or_path=self.cfg.model.name,
                device=self.cfg.model.device,
                compute_type=self.cfg.model.compute_type
            )
        except Exception as e:
            logger.critical(f"Failed to initialize Whisper model: {e}")
            raise

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        t_cfg = self.cfg.transcription
        logger.info(f"Starting transcription: {audio_path.name}")

        segments_gen, info = self._model.transcribe(
            str(audio_path),
            language=t_cfg.language,
            beam_size=t_cfg.beam_size,
            vad_filter=t_cfg.vad_filter,
            vad_parameters=t_cfg.vad_parameters.dict(),
            initial_prompt=t_cfg.initial_prompt,
            condition_on_previous_text=False
        )

        logger.info(f"Language: {info.language} | Total Audio Duration: {info.duration:.2f}s")

        processed_segments = []
        full_text_parts = []
        
        with tqdm(
            total=round(info.duration, 2), 
            unit="s", 
            desc=f"Transcriving {audio_path.stem}", 
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n:.2f}/{total:.2f}s [{elapsed}<{remaining}, {rate_fmt}]",
            colour="green"
        ) as pbar:
            
            previous_end = 0.0
            for segment in segments_gen:
                segment_data = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                }
                processed_segments.append(segment_data)
                full_text_parts.append(segment_data["text"])

                advance = segment.end - previous_end
                pbar.update(advance)
                previous_end = segment.end

        return TranscriptionResult(
            text=" ".join(full_text_parts),
            language=info.language,
            probability=info.language_probability,
            segments=processed_segments
        )