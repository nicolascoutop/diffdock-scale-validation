# diffdock-scale-validation
Automating and scaling DiffDock-L molecular docking with SLURM/HPC and statistical benchmarks against classical methods.

# DiffDock HPC Benchmarking & Validation Pipeline

This project implements, scales, and validates **DiffDock-L**, a state-of-the-art molecular docking diffusion model (ICLR 2024). The repository showcases a complete bioinformatic workflow, shifting from local automation to High-Performance Computing (HPC) infrastructure, and concluding with a rigorous statistical benchmark against classical physics-based docking methods.

The project is structured into three progressive phases:

## Project Architecture

### Phase 1: Automation & Core Pipeline (`/core_pipeline`)
- Development of a modular Python pipeline to automate structural data retrieval (PDB/SMILES).
- Programmatic setup and execution of the pretrained DiffDock-L generative and confidence models.
- Automated extraction and parsing of molecular confidence scores.

### Phase 2: HPC Infrastructure & Scalability (`/hpc_deployment`)
- Adaptation of the core pipeline for batch processing and high-throughput screening.
- Implementation of Bash and **SLURM** orchestration scripts for deployment on distributed clusters.
- Computational profiling focusing on CPU/GPU acceleration, parallel efficiency, and memory optimization (mitigating Out-Of-Memory/OOM-kill errors).

### Phase 3: Data Analysis & Statistical Benchmarking (`/data_analysis`)
- Comparative evaluation using a subset of the **DOCKGEN** benchmark.
- Parallel screening using classical physics-based docking methods (e.g., **AutoDock Vina** or **Smina**).
- Statistical analysis (Python/R) analyzing computation time, affinity energy correlations, and success rate transitions in unseen protein domains.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
