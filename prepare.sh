#!/bin/bash

echo "Aggiornamento e installazione delle librerie di sistema per FFmpeg..."
sudo apt-get update && sudo apt-get install -y \
    libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libswresample-dev libavfilter-dev pkg-config

echo "Installazione delle dipendenze Python da requirements.txt..."

pip install -r requirements.txt

echo "Setup completato!"