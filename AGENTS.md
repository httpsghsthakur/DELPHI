DELPHI DEVELOPMENT RULES

1. Never introduce external LLM APIs into the application.
2. Never introduce pretrained model weights.
3. Never silently replace a custom model with BERT, GPT, Llama, Mistral, or another pretrained model.
4. Never fabricate datasets or metrics.
5. Never fabricate prediction results.
6. Build one layer at a time.
7. Do not modify completed layers unnecessarily.
8. Preserve model interfaces.
9. Preserve dataset versioning.
10. Prevent temporal data leakage.
11. Keep training and inference code separate.
12. Use configuration files instead of hard-coded hyperparameters.
13. Record experiment metadata.
14. Add tests for every new architectural contract.
15. Do not create unnecessary dependencies.
16. Explain architectural changes before making them.
17. Prefer simple deterministic components where learned intelligence is not required.
18. The final DELPHI system must be explainable and backtestable.
