from typing import List

# Standard BIO Tags
BIO_TAGS = [
    "O",
    "B-ACTOR", "I-ACTOR",
    "B-ACTION", "I-ACTION",
    "B-TARGET", "I-TARGET",
    "B-LOCATION", "I-LOCATION",
    "B-TIME", "I-TIME",
    "B-CAUSE", "I-CAUSE",
    "B-EVENT_TRIGGER", "I-EVENT_TRIGGER"
]

BIO_TO_ID = {tag: i for i, tag in enumerate(BIO_TAGS)}
ID_TO_BIO = {i: tag for i, tag in enumerate(BIO_TAGS)}

# Event Types Configurable Base
EVENT_TYPES = [
    "TRADE",
    "DIPLOMACY",
    "CONFLICT",
    "SANCTIONS",
    "POLITICS",
    "ECONOMICS",
    "TECHNOLOGY",
    "ENERGY",
    "CLIMATE",
    "HEALTH",
    "SECURITY",
    "MILITARY",
    "RESOURCE",
    "DISASTER",
    "OTHER",
    "NONE"  # For sequences with no event
]

EVENT_TYPE_TO_ID = {event: i for i, event in enumerate(EVENT_TYPES)}
ID_TO_EVENT_TYPE = {i: event for i, event in enumerate(EVENT_TYPES)}
