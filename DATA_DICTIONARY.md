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
      "evidence_ids": []
    }
  ]
}
```
