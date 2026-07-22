#!/usr/bin/env bash
# config.sh

# --- DYNAMIC PATH DETECTION ---
export PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export DIFFDOCK_ROOT="$PROJECT_ROOT/DiffDock"

# --- Inference Engine Paths ---
export DIFFDOCK_PATH="$DIFFDOCK_ROOT/inference.py"

# --- Input/Output Directories ---
export PROTEIN_DIR="$PROJECT_ROOT/data_analysis/proteins"
export LIGAND_DIR="$PROJECT_ROOT/data_analysis/ligands"
export OUT_DIR="$PROJECT_ROOT/results"
export CSV_NAME="$PROJECT_ROOT/data_analysis/inference_map.csv"

# --- Inference Parameters ---
# Aquí sí dejamos el :- por si quieres cambiarlos rápido desde la terminal luego
export INFERENCE_STEPS="${INFERENCE_STEPS:-20}"
export SAMPLES_PER_COMPLEX="${SAMPLES_PER_COMPLEX:-5}"

echo "[config.sh] Dynamically loaded variables:"
echo "  PROJECT_ROOT        = ${PROJECT_ROOT}"
echo "  PROTEIN_DIR         = ${PROTEIN_DIR}"
echo "  LIGAND_DIR          = ${LIGAND_DIR}"