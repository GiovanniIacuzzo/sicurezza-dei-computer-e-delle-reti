import os
import yaml
import subprocess
import librosa
import soundfile as sf
import noisereduce as nr

class AudioPreprocessor:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        
        self.sample_rate = self.config["audio"]["sample_rate"]
        self.apply_nr = self.config["audio"]["apply_noise_reduction"]

    def _extract_audio(self, video_path: str, temp_wav_path: str):
        """Estrae l'audio dal video mp4 usando ffmpeg, forzando mono e 16kHz."""
        print(f"Estrazione audio da {video_path}...")
        # Il comando ffmpeg: -vn (no video), -acodec pcm_s16le (formato wav), -ar 16000 (sample rate), -ac 1 (mono)
        command = [
            "ffmpeg", "-y", "-i", video_path, 
            "-vn", "-acodec", "pcm_s16le", 
            "-ar", str(self.sample_rate), "-ac", "1", 
            temp_wav_path
        ]
        
        # Eseguiamo silenziosamente
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if not os.path.exists(temp_wav_path):
            raise FileNotFoundError(f"Errore: FFmpeg non ha generato il file {temp_wav_path}")
        return temp_wav_path

    def process(self, video_path: str) -> str:
        """Pipeline completa: estrazione ed eventuale denoise. Ritorna il percorso dell'audio pronto."""
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        temp_dir = "data/temp_audio"
        os.makedirs(temp_dir, exist_ok=True)
        
        raw_wav_path = os.path.join(temp_dir, f"{base_name}_raw.wav")
        final_wav_path = os.path.join(temp_dir, f"{base_name}_ready.wav")

        # 1. Estrazione audio dal video
        self._extract_audio(video_path, raw_wav_path)

        # 2. Riduzione del rumore (opzionale ma consigliata per le aule)
        if self.apply_nr:
            print(f"Applicazione riduzione del rumore per {base_name}...")
            # Carichiamo l'audio
            audio_data, sr = librosa.load(raw_wav_path, sr=self.sample_rate)
            
            # Applichiamo noisereduce (usa un algoritmo spettrale per eliminare rumori stazionari)
            reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sr, prop_decrease=0.8)
            
            # Salviamo il file pulito
            sf.write(final_wav_path, reduced_noise_audio, sr)
            
            # Pulizia file temporaneo
            os.remove(raw_wav_path)
            return final_wav_path
        else:
            # Se non facciamo il denoise, il file raw è già il nostro file finale
            os.rename(raw_wav_path, final_wav_path)
            return final_wav_path