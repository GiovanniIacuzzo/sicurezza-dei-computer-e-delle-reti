#!/bin/bash

echo "Creazione della struttura delle directory..."
mkdir -p data
mkdir -p model
mkdir -p dataset

echo "Creazione ambiente Conda (potrebbe richiedere qualche minuto)..."
conda env create -f environment.yaml

echo "Struttura pronta."
echo "Per attivare l'ambiente esegui: conda activate asr_env"
echo "ATTENZIONE: Ricordati di caricare il tuo file kaggle.json in ~/.kaggle/ per l'autenticazione!"