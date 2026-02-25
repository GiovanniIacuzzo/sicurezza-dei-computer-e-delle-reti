import yaml
from faster_whisper import WhisperModel

class WhisperTranscriber:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
            
        model_config = self.config["model"]
        
        print(f"Caricamento modello Whisper '{model_config['name']}' su {model_config['device'].upper()} "
              f"({model_config['compute_type']})...")
        
        # Inizializza il modello SOTA. compute_type="float16" dimezza la VRAM necessaria.
        self.model = WhisperModel(
            model_size_or_path=model_config["name"],
            device=model_config["device"],
            compute_type=model_config["compute_type"]
        )

    def transcribe(self, audio_path: str) -> str:
        """Trascrive l'audio gestendo allucinazioni (VAD) ed esitazioni (Prompt)."""
        transcription_config = self.config["transcription"]
        
        print(f"Inizio trascrizione di {audio_path}...")
        
        # Esecuzione dell'inferenza con tutti i parametri di sicurezza
        segments, info = self.model.transcribe(
            audio_path,
            language=transcription_config["language"],
            beam_size=transcription_config["beam_size"],
            vad_filter=transcription_config["vad_filter"],
            vad_parameters=transcription_config["vad_parameters"],
            initial_prompt=transcription_config["initial_prompt"],
            condition_on_previous_text=False # Fondamentale: impedisce che ripeta la stessa frase all'infinito se si "incastra"
        )
        
        print(f"Lingua rilevata: {info.language} (probabilità: {info.language_probability:.2f})")
        
        full_text = []
        # 'segments' è un generatore. Il calcolo vero e proprio avviene man mano che iteriamo.
        for segment in segments:
            # Opzionale: puoi stampare il progresso in tempo reale
            print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
            full_text.append(segment.text.strip())
            
        # Uniamo tutti i segmenti in un unico grande testo, separandoli con uno spazio
        return " ".join(full_text)