# EXPERIMENT PROTOCOL

Every experiment in DELPHI must adhere to strict reproducibility standards.

## Requirements

1. **Seed**: A deterministic seed must be used and logged. Do not scatter random seeds across source files; use the common seed utility.
2. **Dataset Version**: The exact version and checksum of the dataset must be logged.
3. **Code Commit**: The git commit hash must be logged.
4. **Configuration Version**: The config file (or dict) used must be saved.
5. **Model Version**: Model architectures must be versioned.
6. **Hyperparameters**: All hyperparameters must be stored in the experiment metadata.
7. **Metrics**: Training and evaluation metrics must be logged via MLflow or similar tool.
8. **Checkpoints**: Model checkpoints must include metadata tracking back to the exact experiment run.

## Workflow

1. Define a YAML configuration for the experiment.
2. Run the experiment using the CLI/Makefile.
3. Validate that the checkpoint directory contains `metadata.json` satisfying the requirements above.
