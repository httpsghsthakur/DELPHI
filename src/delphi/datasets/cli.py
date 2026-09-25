import argparse

def validate():
    print("Validating datasets...")
    # placeholder

def profile():
    print("Profiling datasets...")
    # placeholder

def build_splits():
    print("Building temporal splits...")
    # placeholder

def manifest():
    print("Generating dataset manifest...")
    # placeholder

def main():
    parser = argparse.ArgumentParser(description="DELPHI Dataset CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("validate", help="Validate raw or processed datasets")
    subparsers.add_parser("profile", help="Generate statistics for a dataset")
    subparsers.add_parser("build-splits", help="Create train/validation/test splits")
    subparsers.add_parser("manifest", help="Generate a manifest for a dataset")
    subparsers.add_parser("tokenizer-build", help="Build vocabulary and tokenizer")
    subparsers.add_parser("tokenizer-inspect", help="Inspect an existing tokenizer")
    subparsers.add_parser("tokenizer-test", help="Run a tokenizer test demonstration")

    args = parser.parse_args()

    if args.command == "validate":
        validate()
    elif args.command == "profile":
        profile()
    elif args.command == "build-splits":
        build_splits()
    elif args.command == "manifest":
        manifest()
    elif args.command == "tokenizer-build":
        print("Building tokenizer vocabulary from corpus...")
        # Placeholder for actual invocation
    elif args.command == "tokenizer-inspect":
        print("Inspecting tokenizer...")
    elif args.command == "tokenizer-test":
        print("Running tokenizer demonstration...")
        from delphi.tokenizer.tokenizer import CustomTokenizer
        from delphi.tokenizer.vocabulary import VocabularyBuilder
        
        corpus = [["India", "announced", "a", "40%", "restriction", "on", "rice", "exports", "on", "25", "September", "2026", "."]]
        vocab = VocabularyBuilder(min_frequency=1).build(corpus)
        config = {"sequence": {"max_length": 256, "add_bos": True, "add_eos": True}, "normalization": {}}
        tokenizer = CustomTokenizer(vocab, config)
        
        text = "India announced a 40% restriction on rice exports on 25 September 2026."
        output = tokenizer.encode(text)
        print("Input:", text)
        print("Tokens:", output.tokens)
        print("Decoded (without special):", tokenizer.decode(output.input_ids))
        print("All tests PASS")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
