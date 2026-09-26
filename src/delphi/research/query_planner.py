from typing import List, Dict, Any, Set
import re

class QueryPlanner:
    """
    Deterministic Query Planner operating without an LLM.
    Generates structured queries based on EventNet output.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
    def normalize_query(self, query: str) -> str:
        """Normalize query to avoid duplicates."""
        q = query.lower()
        q = re.sub(r'[^\w\s]', '', q)
        q = re.sub(r'\s+', ' ', q).strip()
        return q
        
    def generate_queries(self, event_context: Dict[str, Any], max_queries: int = 5) -> List[str]:
        """
        Generate multiple deterministic query categories based on event extracted fields.
        Categories:
        - DIRECT_EVENT
        - ACTOR_RESPONSE
        - TARGET_IMPACT
        - POLICY_RESPONSE
        - OFFICIAL_CONFIRMATION
        """
        queries = []
        seen = set()
        
        # Extract basic elements
        event_code = event_context.get("event_type_code", "unknown event")
        # In a real setup, we'd map actor/target IDs back to names. 
        # For this prototype we will use the event_type_code and the text if available,
        # or a generalized placeholder if actor/target names aren't in the context.
        # Since the context usually just has IDs right now, we will construct simple queries 
        # based on the domain or available text chunks.
        
        # Assuming we can extract keywords from the source text if it exists
        # This is a proxy for having the actual entity names
        source_text = event_context.get("source_text", "")
        # A simple deterministic approach: take top words from source text if actor names are missing
        words = [w for w in re.findall(r'\b[A-Za-z]{4,}\b', source_text) if w.istitle()]
        key_entities = " ".join(list(dict.fromkeys(words))[:3])
        
        if not key_entities:
            key_entities = "international event"
            
        event_action = event_code.replace("_", " ")

        candidate_templates = [
            f"{key_entities} {event_action}", # DIRECT_EVENT
            f"{key_entities} {event_action} government response", # ACTOR_RESPONSE
            f"{key_entities} {event_action} impact", # TARGET_IMPACT
            f"{key_entities} {event_action} policy", # POLICY_RESPONSE
            f"{key_entities} {event_action} official statement", # OFFICIAL_CONFIRMATION
            f"{key_entities} {event_action} market impact", # MARKET_IMPACT
            f"{key_entities} {event_action} international response", # INTERNATIONAL_RESPONSE
            f"{key_entities} {event_action} historical context", # HISTORICAL_CONTEXT
            f"{key_entities} did not {event_action}" # CONTRADICTORY_SEARCH
        ]
        
        final_queries = []
        for q in candidate_templates:
            if len(final_queries) >= max_queries:
                break
                
            norm = self.normalize_query(q)
            if norm not in seen and norm:
                seen.add(norm)
                final_queries.append(q)
                
        return final_queries
