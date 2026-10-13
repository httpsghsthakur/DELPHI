import os
import sys
import subprocess
from datetime import datetime

def run_step(name, command):
    print(f"\n[{datetime.utcnow().isoformat()}] --- Starting {name} ---")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"\n[ERROR] {name} failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    print(f"[{datetime.utcnow().isoformat()}] --- Completed {name} ---")

def main():
    print("========================================")
    print("  DELPHI UNIFIED TRAINING PIPELINE")
    print("========================================")
    
    # 1. Dataset Generation / Fetching
    run_step("Fetch Real Datasets", "python scripts/fetch_real_gdelt_data.py")
    
    # 2. Tokenizer
    run_step("Train Tokenizer", "python -m delphi.tokenizer.train")
    
    # 3. EventEmbed
    run_step("Train EventEmbed", "python src/delphi/models/eventembed/train.py")
    
    # 4. EventNet
    run_step("Train EventNet", "python src/delphi/models/eventnet/train.py")
    
    # 5. CredNet
    run_step("Train CredNet", "python src/delphi/models/crednet/train.py")
    
    # 6. CausalSeq
    run_step("Train CausalSeq", "python src/delphi/models/causalseq/train.py")
    
    # 7. Historical FAISS
    run_step("Generate FAISS Index", "python src/delphi/historical/build_index.py")
    
    # 8. Calibration
    run_step("Fit Calibration", "python src/delphi/forecast/fit_calibration.py")
    
    print("\n========================================")
    print("  PIPELINE COMPLETED SUCCESSFULLY")
    print("========================================")

if __name__ == "__main__":
    main()
