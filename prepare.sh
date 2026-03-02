#!/bin/bash

# 1. Installazione FFmpeg e librerie di sviluppo (SISTEMA)
echo "Installazione FFmpeg e dipendenze di sistema..."
sudo apt-get update && sudo apt-get install -y \
    ffmpeg \
    libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libswresample-dev libavfilter-dev pkg-config

# 2. Pulizia versioni Torch in conflitto
echo "Pulizia versioni Torch..."
pip uninstall -y torch torchvision torchaudio

# 3. Installazione pulita con CUDA 12.1 (PYTHON)
echo "Installazione librerie Python..."
pip install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu121

# 4. Installazione del resto delle dipendenze
pip install faster-whisper==1.0.1 librosa==0.10.1 noisereduce==3.0.2 av kaggle==1.6.6 pyyaml==6.0.1 tqdm==4.66.2 setuptools