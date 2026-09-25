SPECIAL_TOKENS = [
    "<PAD>", "<UNK>", "<BOS>", "<EOS>", "<SEP>", "<MASK>", 
    "<NUM>", "<DATE>", "<URL>", "<EMAIL>", "<PERCENT>", "<CURRENCY>",
    "<ACTOR>", "</ACTOR>", "<ACTION>", "</ACTION>", "<TARGET>", "</TARGET>",
    "<LOCATION>", "</LOCATION>", "<TIME>", "</TIME>", "<CAUSE>", "</CAUSE>",
    "<EVENT>", "</EVENT>", "<CAUSE_EVENT>", "</CAUSE_EVENT>", 
    "<OUTCOME_EVENT>", "</OUTCOME_EVENT>", "<SCENARIO>", "</SCENARIO>"
]

SPECIAL_TOKENS_MAP = {token: idx for idx, token in enumerate(SPECIAL_TOKENS)}
PAD_ID = SPECIAL_TOKENS_MAP["<PAD>"]
UNK_ID = SPECIAL_TOKENS_MAP["<UNK>"]
BOS_ID = SPECIAL_TOKENS_MAP["<BOS>"]
EOS_ID = SPECIAL_TOKENS_MAP["<EOS>"]
