#!/bin/bash
#------------------------------------------------------------------
# run_hpc.sbatch — Submission of diffdock-scale-validation to CESGA FT3
#------------------------------------------------------------------
#SBATCH --job-name=diffdock_stage2
#SBATCH -o logs/diffdock_%j.out
#SBATCH -e logs/diffdock_%j.err
# #SBATCH --account=your_cesga_account # Uncomment and adjust ONLY if `sacctmgr show
                                       # associations user=$USER` shows more than one
                                       # possible association for your user.
#SBATCH --gres=gpu:a100:1             # 1 GPU out of the 2 available on a standard A100 node
#SBATCH -c 32                         # MANDATORY on FT3: 32 cores per GPU on standard A100 nodes
#SBATCH --mem-per-cpu=3G              # ~96GB total (3G x 32 cores), following CESGA convention
#SBATCH -t 02:00:00
# --partition is not set: FT3 has no "gpu" partition; SLURM automatically assigns
# short/medium/long/ondemand/requeue according to requested --time.

set -euo pipefail
mkdir -p logs

# --- 1. Environment ---
module purge
module load cesga/system   # CESGA recommends this module tree (not cesga/2020) to avoid
                            # Gentoo prefix incompatibilities with miniconda3
module load miniconda3     # Verify the exact name available with: module spider miniconda3

# $HOME has a small quota on FT3; the DiffDock environment (torch+pyg+deps) weighs
# several GBs, so conda must live in $STORE, not $HOME.
export CONDA_ENVS_PATH=$STORE/conda/envs
export CONDA_PKGS_DIRS=$STORE/conda/pkgs
mkdir -p "$CONDA_ENVS_PATH" "$CONDA_PKGS_DIRS"

conda activate diffdock

# --- Quick guard: if CUDA is unavailable, abort before spending
# compute time on the actual pipeline. Leverages the GPU already requested
# above -- no separate job needed just for this check.
echo "CUDA environment check:"
nvidia-smi | grep "CUDA Version"
python -c "import torch; assert torch.cuda.is_available(), 'CUDA unavailable: check pytorch-cuda vs FT3 driver'; print(f'torch={torch.__version__} cuda={torch.version.cuda} OK')"

# --- 2. Project variables (paths, not compute resources) ---
if [ -f "config.sh" ]; then
    source config.sh
fi

# --- 3. Orchestrator launch ---
# We do not pass --device: when SLURM assigns the GPU via --gres=gpu:a100:1, it sets
# CUDA_VISIBLE_DEVICES for this job. run_pipeline.py autodetects via nvidia-smi
# and does not touch that variable in GPU mode, respecting SLURM's binding.
# --threads is passed explicitly: it comes from the actual --cpus-per-task reserved
# for this job, not a hardcoded value.
python core_pipeline/run_pipeline.py \
    --threads "$SLURM_CPUS_PER_TASK" \
    --batch_size 16