# DELPHI Data Dictionary

## Datasets Versioning Schema
Every training dataset follows this schema:
- `dataset_name`: string
- `dataset_version`: string
- `creation_timestamp`: ISO 8601 string
- `source`: string
- `preprocessing_version`: string
- `label_schema_version`: string
- `train_split`: string (path or identifier)
- `validation_split`: string (path or identifier)
- `test_split`: string (path or identifier)
- `checksum`: string (SHA-256)

## Forecast Output Schema
```json
{
  "forecast_id": "uuid",
  "input_event_id": "string",
  "generated_at": "ISO 8601 string",
  "model_versions": {},
  "historical_matches": [],
  "evidence": [],
  "causal_graph": {},
  "scenarios": [],
  "indicators": [],
  "time_horizons": [],
  "confidence": {},
  "limitations": []
}
```

## Scenario Schema
```json
{
  "scenario_id": "string",
  "scenario_type": "string",
  "probability": 0.0,
  "time_horizon_days": 0,
  "next_events": [],
  "affected_actors": [],
  "affected_sectors": [],
  "indicators": [],
  "evidence_ids": []
}
```

## Causal Graph Data Schema
```json
{
  "nodes": [
    {
      "id": "string",
      "type": "string",
      "label": "string",
      "event_date": "ISO 8601 string",
      "confidence": 0.0
    }
  ],
  "edges": [
    {
      "source": "string",
      "target": "string",
      "relation": "string",
      "weight": 0.0,
  ]
}
```

## Layer 1 Canonical Schemas
- **NewsArticle**: Canonical model for news containing `article_id`, `content_hash`, `publication_datetime`, etc.
- **EventRecord**: Core extracted event containing `event_id`, `actor`, `action`, `target`, `event_date`.
- **EventRelation**: Directed edge between events (`source_event_id` to `target_event_id`) with a `relation_type`.
- **SourceRecord**: Information on data publishers, their domains, and visibility windows.
- **CredibilityFeatures**: 12-dimensional feature vector representations of source credibility.
- **EconomicObservation**: Normalized format for IMF/World Bank economic indicators.
- **TradeObservation**: UN Comtrade normalized import/export flow data.
- **EventSequence**: Ground truth sequences for `CausalSeq` dataset construction.
