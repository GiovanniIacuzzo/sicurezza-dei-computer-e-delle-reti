import os
import glob
import time
from dataset.dataset import AudioPreprocessor
from model.model import WhisperTranscriber

def main():
    # Definiamo le cartelle di input e output
    input_dir = "data/"
    output_dir = "data/transcriptions/"
    os.makedirs(output_dir, exist_ok=True)

    # Troviamo tutti i file .m4a scaricati
    video_files = glob.glob(os.path.join(input_dir, "*.m4a"))
    
    if not video_files:
        print(f"Nessun file .m4a trovato in '{input_dir}'. Hai eseguito download_data.py?")
        return

    print(f"Trovati {len(video_files)} file da processare. Inizializzazione pipeline...")

    # Inizializziamo i nostri moduli
    preprocessor = AudioPreprocessor(config_path="config.yaml")
    transcriber = WhisperTranscriber(config_path="config.yaml")

    for video_path in video_files:
        filename = os.path.basename(video_path)
        base_name = os.path.splitext(filename)[0]
        output_txt_path = os.path.join(output_dir, f"{base_name}.txt")

        # Se il file è già stato trascritto, lo saltiamo (utile se il processo si interrompe a metà)
        if os.path.exists(output_txt_path):
            print(f"\n[SKIP] Il file {filename} è già stato trascritto.")
            continue

        print(f"\n{'='*50}")
        print(f"Inizio elaborazione: {filename}")
        print(f"{'='*50}")
        
        start_time = time.time()
        temp_audio_path = None

        try:
            # 1. Pre-processing: Estrazione e Denoise
            print("-> Fase 1: Estrazione e pulizia audio...")
            preprocessor_start = time.time()
            temp_audio_path = preprocessor.process(video_path)
            print(f"   Audio pronto in {time.time() - preprocessor_start:.2f} secondi.")

            # 2. Inferenza: Trascrizione con VAD e Prompting
            print("-> Fase 2: Trascrizione in corso...")
            transcription_start = time.time()
            testo_finale = transcriber.transcribe(temp_audio_path)
            print(f"   Trascrizione completata in {time.time() - transcription_start:.2f} secondi.")

            # 3. Salvataggio dell'output
            with open(output_txt_path, "w", encoding="utf-8") as f:
                f.write(testo_finale)
            print(f"-> File salvato con successo in: {output_txt_path}")

        except Exception as e:
            print(f"\n[ERRORE] Elaborazione fallita per {filename}. Dettagli: {e}")
        
        finally:
            # 4. Cleanup: Pulizia aggressiva della cache temporanea
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                print(f"   Pulizia file temporaneo ({temp_audio_path}) eseguita.")
        
        total_time = time.time() - start_time
        print(f"Tempo totale per {filename}: {total_time/60:.2f} minuti.")

    print("\nElaborazione batch completata! Tutte le lezioni sono state trascritte.")

if __name__ == "__main__":
    main()