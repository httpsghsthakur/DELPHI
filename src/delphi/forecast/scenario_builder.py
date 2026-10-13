from typing import List, Dict, Any
import hashlib
from .schemas import ScenarioCandidate
from .config import ForecastConfig

class ScenarioBuilder:
    def __init__(self, config: ForecastConfig):
        self.config = config

    def _hash_trajectory(self, trajectory: List[Dict[str, Any]]) -> str:
        """
        Create a deterministic structural hash of a trajectory.
        Includes event_type, time_bin, actor, target, domain.
        """
        struct_repr = ""
        for step in trajectory:
            t_bin = step.get("time_bin", step.get("time_to_event_bin", 0))
            struct_repr += f"{step.get('event_type')}-{t_bin}-{step.get('actor')}-{step.get('target')}-{step.get('domain')}|"
        return hashlib.md5(struct_repr.encode()).hexdigest()

    def build_scenarios(self, generated_trajectories: List[Dict[str, Any]]) -> List[ScenarioCandidate]:
        """
        Deduplicates trajectories and constructs ScenarioCandidates.
        Returns up to config.max_scenarios distinct scenarios.
        """
        unique_scenarios = {}
        
        for idx, traj_bundle in enumerate(generated_trajectories):
            traj = traj_bundle.get("trajectory", [])
            score = traj_bundle.get("sequence_score", 0.0)
            branch_title = traj_bundle.get("branch_name") or (f"Scenario {idx+1}: {traj[0].get('event_type_code', 'Forecast')} Trajectory" if traj else f"Scenario {idx+1}")
            
            traj_hash = self._hash_trajectory(traj)
            
            if traj_hash not in unique_scenarios:
                unique_scenarios[traj_hash] = ScenarioCandidate(
                    scenario_id=f"SCENARIO_{idx+1}",
                    title=branch_title,
                    trajectory=traj,
                    supporting_evidence=[],
                    contradictory_evidence=[],
                    sequence_score=score,
                    raw_scenario_score=score # Will be overwritten by scorer
                )
            else:
                # Keep the one with the higher sequence score
                if score > unique_scenarios[traj_hash].sequence_score:
                    existing = unique_scenarios[traj_hash]
                    existing.sequence_score = score
                    existing.raw_scenario_score = score
                    
        # Sort by sequence score descending and take top K
        sorted_scenarios = sorted(unique_scenarios.values(), key=lambda x: x.sequence_score, reverse=True)
        return sorted_scenarios[:self.config.max_scenarios]
