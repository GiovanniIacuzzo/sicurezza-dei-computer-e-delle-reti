from pydantic import BaseModel
import yaml
from pathlib import Path

class KaggleConfig(BaseModel):
    dataset_name: str
    download_path: Path

class AudioConfig(BaseModel):
    sample_rate: int = 16000
    apply_noise_reduction: bool = True

class VadParameters(BaseModel):
    min_silence_duration_ms: int = 500

class ModelConfig(BaseModel):
    name: str
    device: str = "cuda"
    compute_type: str = "float16"

class TranscriptionConfig(BaseModel):
    language: str = "it"
    beam_size: int = 5
    vad_filter: bool = True
    vad_parameters: VadParameters
    initial_prompt: str

class AppConfig(BaseModel):
    kaggle: KaggleConfig
    audio: AudioConfig
    model: ModelConfig
    transcription: TranscriptionConfig

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)