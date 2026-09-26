from typing import List, Dict, Any
from .schemas import Indicator, ScenarioCandidate
from .config import ForecastConfig

class IndicatorDetector:
    def __init__(self, config: ForecastConfig):
        self.config = config
        
    def generate_indicators(self, scenarios: List[ScenarioCandidate]) -> List[Indicator]:
        """
        Derives watchable real-world indicators strictly from generated trajectories.
        """
        indicators = []
        for scen in scenarios:
            for step_idx, step in enumerate(scen.trajectory):
                # Generate an indicator for each trajectory step
                ind = Indicator(
                    indicator_id=f"IND_{scen.scenario_id}_{step_idx}",
                    description=f"Monitor for event type {step.get('event_type')} involving actor {step.get('actor')}",
                    event_type=step.get('event_type', 0),
                    actor=step.get('actor', 0),
                    target=step.get('target', 0),
                    time_window=str(step.get('time_bin', 'unknown')),
                    source_requirement="High credibility news or official release",
                    expected_direction="supporting",
                    scenario_linkage=scen.scenario_id,
                    importance="High" if step_idx == 0 else "Medium"
                )
                indicators.append(ind)
                
        return indicators
