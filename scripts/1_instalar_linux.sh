#!/bin/bash
# =====================================================
# VIGILANTE EPP — Instalacion en Linux / Mac
# =====================================================
# Este script instala PyTorch CPU (~750 MB) antes de
# instalar ultralytics, evitando la descarga de CUDA
# (~5-6 GB) que pip seleccionaria por defecto.
# =====================================================

echo "[1/3] Instalando PyTorch CPU (version ligera, sin CUDA)..."
pip install torch==2.2.2+cpu torchvision==0.17.2+cpu --index-url https://download.pytorch.org/whl/cpu

echo "[2/3] Instalando dependencias de la aplicacion..."
pip install -r requirements.txt

echo "[3/3] Instalacion completada."
echo "Para iniciar: streamlit run app.py"
