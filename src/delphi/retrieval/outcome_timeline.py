from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .schemas import HistoricalEventDocument, OutcomeTimeline, HistoricalOutcome

class HistoricalOutcomeBuilder:
    def __init__(self, historical_events: List[HistoricalEventDocument], horizons: List[int] = None):
        """
        historical_events: The database of all historical events to scan for outcomes.
        horizons: List of days to check for outcomes.
        """
        self.historical_events = historical_events
        self.horizons = horizons if horizons is not None else [1, 7, 14, 30, 90, 180, 365]
        
        # Pre-sort events by date for efficient querying if needed, though a simple scan works for now.
        # But we need valid dates.
        self.valid_events = []
        for e in self.historical_events:
            try:
                date_obj = datetime.strptime(e.event_date[:10], "%Y-%m-%d").date()
                self.valid_events.append((date_obj, e))
            except (ValueError, TypeError):
                continue
                
    def build(self, analogue_event: HistoricalEventDocument, prediction_cutoff: str) -> List[OutcomeTimeline]:
        """
        Builds the outcome timeline for a historical analogue.
        Only considers outcomes strictly <= prediction_cutoff.
        """
        timelines = []
        try:
            t0_date = datetime.strptime(analogue_event.event_date[:10], "%Y-%m-%d").date()
            cutoff_date = datetime.strptime(prediction_cutoff[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return timelines
            
        for horizon_days in self.horizons:
            horizon_end = t0_date + timedelta(days=horizon_days)
            
            # If the horizon itself exceeds the prediction cutoff, we cannot safely look at this horizon
            # Wait, the prompt says "May inspect what happened AFTER that historical event because those outcomes are historical evidence. It must NOT inspect 2026-01-02 when constructing current query."
            # So outcomes must be <= cutoff_date.
            
            outcomes = []
            future_event_ids = []
            
            for ev_date, ev in self.valid_events:
                # Event must be strictly after T0, but within the horizon
                if t0_date < ev_date <= horizon_end:
                    # AND it MUST be <= prediction_cutoff to prevent temporal leakage!
                    if ev_date <= cutoff_date:
                        days_after = (ev_date - t0_date).days
                        outcome = HistoricalOutcome(
                            outcome_id=f"out_{ev.event_id}",
                            event_id=ev.event_id,
                            outcome_event_ids=[ev.event_id],
                            outcome_timestamp=ev.event_date,
                            days_after_event=days_after,
                            outcome_event_type=ev.event_type,
                            actors=ev.actor_ids,
                            targets=ev.target_ids,
                            description=ev.text if ev.text else f"{ev.event_type} event",
                            source_reference=ev.source_id
                        )
                        outcomes.append(outcome)
                        future_event_ids.append(ev.event_id)
                        
            if outcomes:
                timelines.append(OutcomeTimeline(
                    event_id=analogue_event.event_id,
                    time_horizon=f"{horizon_days} days",
                    future_events=future_event_ids,
                    outcomes=outcomes
                ))
                
        return timelines
