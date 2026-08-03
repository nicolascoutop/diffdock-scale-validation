#!/usr/bin/env python3
import os
import csv
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

def validate_inputs(protein_dir, ligand_dir):
    """Checks directory existence and extracts file paths"""
    p_dir = Path(protein_dir)
    l_dir = Path(ligand_dir)
    
    if not p_dir.exists() or not p_dir.is_dir():
        print(f"Error: Protein directory '{protein_dir}' does not exist.")
        return None, None
        
    if not l_dir.exists() or not l_dir.is_dir():
        print(f"Error: Ligand directory '{ligand_dir}' does not exist.")
        return None, None

    proteins = list(p_dir.glob("*.pdb"))
    ligands = list(l_dir.glob("*.sdf")) + list(l_dir.glob("*.smi"))

    if not proteins:
        print(f"Warning: No valid .pdb files found in '{protein_dir}'.")
    if not ligands:
        print(f"Warning: No valid ligand files (.sdf/.smi) found in '{ligand_dir}'.")
        
    return proteins, ligands

def create_inference_csv(proteins, ligands, output_csv_path):
    """Creates a cross-docking mapping CSV"""
    csv_path = Path(output_csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["complex_name","protein_path", "ligand_description", "protein_sequence"])
        
        pair_count = 0
        for protein in proteins:
            for ligand in ligands:
                c_name = f"{protein.stem}_{ligand.stem}"
                writer.writerow([c_name, str(protein.resolve()), str(ligand.resolve()), ""])
                pair_count += 1
                
    print(f"Mapping completed. {pair_count} combinations structured in '{output_csv_path}'.")
    return pair_count

def detect_gpu():
    """
    Detects if the node has a visible NVIDIA GPU
    """
    if shutil.which("nvidia-smi") is None:
        return False
    try:
        result = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and "GPU" in result.stdout
    except Exception:
        return False


def run_diffdock(csv_path, out_dir, diffdock_script, inference_steps, samples,
                 batch_size=1, threads=4, device=None, dry_run=False):
    """Invokes the external DiffDock inference script via system call."""
    if not Path(diffdock_script).exists():
        print(f"Error: Executor script '{diffdock_script}' not found.")
        return False
        
    cmd = [
        sys.executable, diffdock_script,
        "--protein_ligand_csv", str(Path(csv_path).resolve()),
        "--out_dir", str(Path(out_dir).resolve()),
        "--inference_steps", str(inference_steps),
        "--samples_per_complex", str(samples),
        "--batch_size", str(batch_size),
    ]

    # Copy variables from the enviroment to execute inference.py with the same packages
    child_env = os.environ.copy()
    child_env["OMP_NUM_THREADS"] = str(threads)
    child_env["MKL_NUM_THREADS"] = str(threads)


    if device == "cpu":
        # Not showing the GPU
        child_env["CUDA_VISIBLE_DEVICES"] = ""
        compute_device = "CPU (forced)"
    elif device == "gpu":
        if not detect_gpu():
            print("[WARN] GPU requested but nvidia-smi does not detect any. "
                  "inference.py will internally fallback to CPU if CUDA is not found.")
        compute_device = "GPU (forced, respecting scheduler's CUDA_VISIBLE_DEVICES)"
    else:
        compute_device = "GPU (autodetected)" if detect_gpu() else "CPU (autodetected)"

    print(f"[CONFIG] Hardware: {compute_device} | CPU threads: {threads} | Batch size: {batch_size}")
    print("\nSUBPROCESS INTERFACE ACTIVATED")
    print(f"System command:\n{' '.join(cmd)}\n")

    if dry_run:
        print("[DRY RUN] Command constructed but not executed.")
        print("The CSV and paths are validated. Ready for production.")
        return True

    print("Executing molecular simulation in background...")
    
    try:
        result = subprocess.run(cmd, check=True, text=True, cwd=Path(diffdock_script).parent, env=child_env)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Critical Error: DiffDock process failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"Unexpected error during command invocation: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Automated Orchestrator for DiffDock")
    
    parser.add_argument("--protein_dir", type=str, default=os.environ.get("PROTEIN_DIR"),
                        help="Path to proteins directory (.pdb)")
    parser.add_argument("--ligand_dir", type=str, default=os.environ.get("LIGAND_DIR"),
                        help="Path to ligands directory (.sdf/.smi)")
    parser.add_argument("--out_dir", type=str, default=os.environ.get("OUT_DIR", "results"),
                        help="Directory to save output poses")
    parser.add_argument("--csv_name", type=str, default=os.environ.get("CSV_NAME", "data/inference_map.csv"),
                        help="Temporary mapping CSV file")
    parser.add_argument("--diffdock_path", type=str, default=os.environ.get("DIFFDOCK_PATH", "inference.py"),
                        help="Path to DiffDock inference.py")
    parser.add_argument("--steps", type=int, default=int(os.environ.get("INFERENCE_STEPS", 20)),
                        help="Number of inference steps")
    parser.add_argument("--samples", type=int, default=int(os.environ.get("SAMPLES_PER_COMPLEX", 5)),
                        help="Number of samples per complex")
    parser.add_argument("--device", type=str, choices=["cpu", "gpu"],
                        default=os.environ.get("DEVICE"),
                        help="Force 'cpu' or 'gpu'. If omitted, autodetected via nvidia-smi.")
    parser.add_argument("--batch_size", type=int,
                        default=int(os.environ.get("BATCH_SIZE", 1)),
                        help="Complexes processed in parallel (real --batch_size of inference.py)")
    parser.add_argument("--threads", type=int,
                        default=int(os.environ.get("THREADS", 4)),
                        help="CPU threads (OMP_NUM_THREADS/MKL_NUM_THREADS) for the child process")
    parser.add_argument("--dry_run", action="store_true",
                        help="Build CSV and command, but do not execute DiffDock")

    args = parser.parse_args()

    if not args.protein_dir or not args.ligand_dir:
        parser.error("Missing directories. Make sure to run 'source config.sh' or pass them as arguments.")

    print("STARTING ORCHESTRATOR PIPELINE")
    
    proteins, ligands = validate_inputs(args.protein_dir, args.ligand_dir)
    if not proteins or not ligands:
        print("Pipeline aborted: Missing input files.")
        return

    total_pairs = create_inference_csv(proteins, ligands, args.csv_name)
    if total_pairs == 0:
        print("Pipeline aborted: No valid combinations found.")
        return

    success = run_diffdock(args.csv_name, args.out_dir, args.diffdock_path,
                            args.steps, args.samples,
                            batch_size=args.batch_size, threads=args.threads,
                            device=args.device, dry_run=args.dry_run)
    
    if success:
        print("\nPIPELINE COMPLETED SUCCESSFULLY")
    else:
        print("\nPIPELINE FAILED")

if __name__ == "__main__":
    main()