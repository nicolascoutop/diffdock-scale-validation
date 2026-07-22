# DiffDock Scale Validation Pipeline

An automated orchestration pipeline designed to streamline, manage, and scale molecular docking simulations using [DiffDock](https://github.com/gcorso/DiffDock). 

This project was built to test computational scalability before moving to High-Performance Computing (HPC) environments (such as CESGA). It structures the biological input data (proteins and ligands), dynamically handles system paths, automatically generates inference mapping CSVs, and executes background docking processes cleanly.

The current test case validates the pipeline using Streptavidin (PDB ID: [1STP](https://www.rcsb.org/structure/1STP)) and its natural ligand Biotin (BTN).

## Prerequisites

* Linux environment (or WSL)
* [Miniforge](https://github.com/conda-forge/miniforge) or Anaconda
* A dedicated Conda environment containing DiffDock dependencies (Python 3.9, PyTorch, ProDy, Pandas, etc.)

## Installation

1. **Clone this orchestrator repository:**
   ```bash
   git clone [https://github.com/nicolascoutop/diffdock-scale-validation.git](https://github.com/nicolascoutop/diffdock-scale-validation.git)
   cd diffdock-scale-validation
   ```

2. **Clone the DiffDock inference engine:**
   The orchestration script uses the original DiffDock code as its engine. You must clone it directly into the root of this project:
   ```bash
   git clone [https://github.com/gcorso/DiffDock.git](https://github.com/gcorso/DiffDock.git)
   ```

3. **Set up the virtual environment:**
   Create and activate the environment using the provided YAML configuration:
   ```bash
   conda env create -f environment.yml
   conda activate diffdock
   ```

## Usage

The pipeline separates code from data. Place your clean protein files (`.pdb`) in `data_analysis/proteins/` and your ligands (`.sdf` or `.smi`) in `data_analysis/ligands/`. 

To launch the automated pipeline, activate the environment and execute the run script:

```bash
conda activate diffdock
./run.sh
```

### How it works
The `run.sh` script automatically:
1. Detects your active Conda environment.
2. Loads dynamic paths relative to the project root via `config.sh` (preventing absolute path errors on new machines).
3. Executes `core_pipeline/run_pipeline.py`.
4. The Python orchestrator matches all proteins and ligands, validates them, and builds a temporary `inference_map.csv`.
5. It triggers DiffDock in a subprocess and logs the exit codes.

Outputs (the predicted 3D poses) will be saved in the `results/` directory, organized by complex.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.