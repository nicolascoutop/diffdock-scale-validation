#!/bin/bash
#SBATCH --job-name=install_diffdock_env
#SBATCH --output=install_log_%j.out
#SBATCH --error=install_log_%j.err
#SBATCH --time=00:45:00
#SBATCH -c 4
#SBATCH --mem=8G
# Without --gres=gpu: creating the environment compiles nothing locally (torch-scatter/
# sparse/cluster arrive precompiled from the pyg channel), so there is no need to
# reserve a GPU -- FT3's most contested resource -- just to resolve and install
# packages. This should enter the queue much faster.

set -euo pipefail

module purge
module load cesga/system miniconda3

export CONDA_ENVS_PATH=$STORE/conda/envs
export CONDA_PKGS_DIRS=$STORE/conda/pkgs
mkdir -p "$CONDA_ENVS_PATH" "$CONDA_PKGS_DIRS"

DIFFDOCK_DIR="${DIFFDOCK_DIR:-../DiffDock}"

if [ -d "$DIFFDOCK_DIR" ]; then
    cd "$DIFFDOCK_DIR"
else
    echo "Error: DiffDock directory not found at '$DIFFDOCK_DIR'"
    exit 1
fi

echo "Starting environment installation..."
conda env create -f environment.yml
echo "Installation completed. Check above for any conda errors."