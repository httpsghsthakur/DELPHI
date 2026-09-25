from .labels import BIO_TAGS, EVENT_TYPES

# Dataset Label to Canonical Mapping
MAVEN_TO_DELPHI_EVENT = {
    "Conflict": "CONFLICT",
    "Military": "MILITARY",
    "Politics": "POLITICS",
    # Mappings can be populated as needed
    # If no mapping exists:
    "DEFAULT": "UNMAPPED"
}

MAVEN_ARG_TO_DELPHI_BIO = {
    "subject": "ACTOR",
    "object": "TARGET",
    "location": "LOCATION",
    "time": "TIME",
    "reason": "CAUSE",
    # Mappings populated as needed
    "DEFAULT": "UNMAPPED"
}

def map_maven_event(maven_label: str) -> str:
    return MAVEN_TO_DELPHI_EVENT.get(maven_label, "UNMAPPED")

def map_maven_arg(maven_arg: str, is_begin: bool) -> str:
    mapped = MAVEN_ARG_TO_DELPHI_BIO.get(maven_arg, "UNMAPPED")
    if mapped == "UNMAPPED":
        return "O"
    prefix = "B-" if is_begin else "I-"
    return f"{prefix}{mapped}"
