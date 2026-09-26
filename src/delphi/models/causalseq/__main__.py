import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="DELPHI CausalSeq CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    train_parser = subparsers.add_parser("train")
    
    eval_parser = subparsers.add_parser("evaluate")
    
    predict_parser = subparsers.add_parser("predict")
    
    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("--checkpoint", required=True)
    
    smoke_parser = subparsers.add_parser("smoke-test")
    
    args = parser.parse_args()
    
    if args.command == "train":
        print("CAUSALSEQ ADAPTER READY — REAL HISTORICAL TRAINING PENDING")
    elif args.command == "evaluate":
        print("CAUSALSEQ BACKTESTING PENDING")
    elif args.command == "predict":
        print("PREDICT requires trained weights.")
    elif args.command == "inspect":
        import os, json
        if os.path.exists(os.path.join(args.checkpoint, "metadata.json")):
            with open(os.path.join(args.checkpoint, "metadata.json")) as f:
                print(json.dumps(json.load(f), indent=2))
        else:
            print("Checkpoint metadata not found.")
    elif args.command == "smoke-test":
        from .smoke_test import run_smoke_test
        run_smoke_test()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
