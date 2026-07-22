#!/bin/bash

# Check if a Conda environment is active for safety
if [ -z "$CONDA_PREFIX" ]; then
    echo "Error: No Conda environment detected. Please run 'conda activate diffdock' first."
    exit 1
fi

# 1. Load environment variables
echo "[1/2] Loading configuration..."
source config.sh

# 2. Run the orchestrator using the environment's dynamic Python
echo "[2/2] Starting Orchestrator..."
"$CONDA_PREFIX/bin/python" core_pipeline/run_pipeline.py

echo "Process finished."