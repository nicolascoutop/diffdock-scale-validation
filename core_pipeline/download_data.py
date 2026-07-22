import os
import argparse
import pandas as pd
from Bio.PDB import PDBList

def parse_arguments():
    """Configura los argumentos de la línea de comandos (CLI) con enfoque híbrido."""
    parser = argparse.ArgumentParser(
        description="Pipeline genérico para automatizar la preparación de inputs (Proteína + Ligando) para DiffDock-L."
    )
    
    # Opción 1: Procesamiento en lote (CSV)
    parser.add_argument("--csv", type=str, help="Ruta al archivo .csv con el listado de complejos.")
    
    # Opción 2: Procesamiento individual (CLI de prueba rápida)
    parser.add_argument("--pdb", type=str, help="ID de 4 caracteres de la proteína en el PDB (ej. 6o0k).")
    parser.add_argument("--smiles", type=str, help="Cadena SMILES del ligando.")
    parser.add_argument("--name", type=str, help="Nombre para la carpeta del complejo (obligatorio para modo individual).")
    
    return parser.parse_args()

def download_pdb(pdb_id, output_dir):
    """Conecta con la RCSB PDB, descarga la estructura y la renombra de forma limpia."""
    print(f"   -> Descargando proteína PDB [{pdb_id}]...")
    try:
        pdbl = PDBList()
        # BioPython descarga por defecto un formato 'pdbXXXX.ent'
        fetched_file = pdbl.retrieve_pdb_file(pdb_id, pdir=output_dir, file_format="pdb")
        
        if os.path.exists(fetched_file):
            # Renombrar a un formato estándar más amigable: 'XXXX.pdb'
            clean_path = os.path.join(output_dir, f"{pdb_id.lower()}.pdb")
            os.rename(fetched_file, clean_path)
            print(f"   [OK] Archivo PDB guardado en: {clean_path}")
            return clean_path
    except Exception as e:
        print(f"   [ERROR] Falló la descarga del PDB {pdb_id}: {e}")
    return None

def save_smiles(smiles, output_dir, complex_name):
    """Guarda la estructura del ligando en un archivo de texto .smi estándar."""
    smi_path = os.path.join(output_dir, f"{complex_name}.smi")
    try:
        with open(smi_path, "w") as f:
            f.write(f"{smiles}\n")
        print(f"   [OK] Ligando SMILES guardado en: {smi_path}")
        return smi_path
    except Exception as e:
        print(f"   [ERROR] No se pudo guardar el SMILES: {e}")
    return None

def process_complex(name, pdb_id, smiles, base_data_dir):
    """Orquesta la creación de directorios y almacenamiento de archivos por complejo."""
    print(f"\n[Procesando] Complejo: {name} (PDB: {pdb_id})")
    
    # Crear carpeta específica para el complejo dentro de core_pipeline/data/
    complex_dir = os.path.join(base_data_dir, name)
    os.makedirs(complex_dir, exist_ok=True)
    
    # Lanzar la descarga y almacenamiento
    download_pdb(pdb_id, complex_dir)
    save_smiles(smiles, complex_dir, name)

def main():
    args = parse_arguments()
    
    # Definir la ruta de la carpeta 'data' relativa a donde está este script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_data_dir = os.path.join(script_dir, "data")
    
    # CASO A: Procesamiento por archivo de lotes (.csv)
    if args.csv:
        if not os.path.exists(args.csv):
            print(f"[ERROR] El archivo CSV especificado no existe: {args.csv}")
            return
        
        print(f"== Leyendo lote de complejos desde: {args.csv} ==")
        df = pd.read_csv(args.csv)
        
        # Validar que el CSV contenga las columnas requeridas
        required_cols = {"complex_name", "pdb_id", "smiles"}
        if not required_cols.issubset(df.columns):
            print(f"[ERROR] El CSV debe tener exactamente las columnas: {required_cols}")
            return
        
        for _, row in df.iterrows():
            process_complex(
                name=str(row["complex_name"]).strip(),
                pdb_id=str(row["pdb_id"]).strip().lower(),
                smiles=str(row["smiles"]).strip(),
                base_data_dir=base_data_dir
            )
            
    # CASO B: Procesamiento de un único complejo por comandos
    elif args.pdb and args.smiles:
        if not args.name:
            print("[ERROR] Para procesar un complejo individual debes añadir un nombre con `--name`.")
            return
        process_complex(args.name, args.pdb.strip().lower(), args.smiles.strip(), base_data_dir)
        
    else:
        print("[ERROR] Uso incorrecto. Elige una opción:\n"
              "  1. En lote:   python download_data.py --csv mis_complejos.csv\n"
              "  2. Individual: python download_data.py --pdb 6o0k --smiles \"C...\" --name mi_prueba")

if __name__ == "__main__":
    main()