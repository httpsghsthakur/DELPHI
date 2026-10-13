import os
import json
import urllib.request
import zipfile
from datetime import datetime
import pandas as pd
from pathlib import Path
import hashlib

def get_hash(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def setup_dirs():
    for d in ["data/raw", "data/interim", "data/processed", "data/manifests"]:
        os.makedirs(d, exist_ok=True)

def ingest_gdelt():
    print("Ingesting GDELT data...")
    # Get the latest GDELT master file (we'll just pull a known recent one or the 15-minute file)
    url = "http://data.gdeltproject.org/gdeltv2/20231101000000.export.CSV.zip"
    raw_zip = "data/raw/gdelt_20231101.zip"
    raw_csv = "data/raw/20231101000000.export.CSV"
    
    if not os.path.exists(raw_zip):
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, raw_zip)
    
    if not os.path.exists(raw_csv):
        print("Extracting zip...")
        with zipfile.ZipFile(raw_zip, 'r') as zip_ref:
            zip_ref.extractall("data/raw/")
            
    print("Parsing GDELT CSV...")
    # GDELT export columns are many; we'll take the first few
    cols = [
        "GLOBALEVENTID", "SQLDATE", "MonthYear", "Year", "FractionDate", 
        "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode", "Actor1EthnicCode", 
        "Actor1Religion1Code", "Actor1Religion2Code", "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",
        "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode", "Actor2EthnicCode", 
        "Actor2Religion1Code", "Actor2Religion2Code", "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",
        "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode", "QuadClass", 
        "GoldsteinScale", "NumMentions", "NumSources", "NumArticles", "AvgTone",
        "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode", "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code", "Actor1Geo_Lat", "Actor1Geo_Long", "Actor1Geo_FeatureID",
        "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode", "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code", "Actor2Geo_Lat", "Actor2Geo_Long", "Actor2Geo_FeatureID",
        "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode", "ActionGeo_ADM1Code", "ActionGeo_ADM2Code", "ActionGeo_Lat", "ActionGeo_Long", "ActionGeo_FeatureID",
        "DATEADDED", "SOURCEURL"
    ]
    df = pd.read_csv(raw_csv, sep='\t', header=None, names=cols, low_memory=False)
    
    # Filter out valid records with source URL
    df = df.dropna(subset=["SOURCEURL", "Actor1Name", "Actor2Name"])
    df = df.head(100) # Small sample for real training
    
    # Process into standard DELPHI format
    records = []
    for _, row in df.iterrows():
        records.append({
            "event_id": str(row["GLOBALEVENTID"]),
            "date": str(row["SQLDATE"]),
            "actor1": str(row["Actor1Name"]),
            "actor2": str(row["Actor2Name"]),
            "event_code": str(row["EventCode"]),
            "goldstein": float(row["GoldsteinScale"]) if pd.notnull(row["GoldsteinScale"]) else 0.0,
            "source_url": str(row["SOURCEURL"]),
            "text": f"{row['Actor1Name']} interacted with {row['Actor2Name']} in a type {row['EventCode']} event.",
            "domain": 1,
        })
        
    out_file = "data/processed/gdelt_sample.json"
    with open(out_file, "w") as f:
        json.dump(records, f, indent=2)
        
    # Manifest
    manifest = {
        "dataset_name": "GDELT_Ingest_Real",
        "source": "GDELT",
        "source_url": url,
        "retrieval_timestamp": datetime.utcnow().isoformat() + "Z",
        "record_count": len(records),
        "min_timestamp": min(r["date"] for r in records),
        "max_timestamp": max(r["date"] for r in records),
        "schema_version": "v1",
        "checksum": get_hash(out_file),
        "license/usage_notes": "Public Domain",
        "processing_version": "1.0"
    }
    with open("data/manifests/gdelt_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print("GDELT ingest complete.")
    
def ingest_wikipedia():
    print("Ingesting Wikipedia events...")
    # Fetch some real articles
    import requests
    queries = ["International relations", "Economic sanction", "Military conflict"]
    records = []
    for q in queries:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&utf8=&format=json&srlimit=10"
        try:
            resp = requests.get(url).json()
            for item in resp['query']['search']:
                records.append({
                    "event_id": f"WIKI_{item['pageid']}",
                    "date": item["timestamp"],
                    "actor1": "Unknown",
                    "actor2": "Unknown",
                    "event_code": "000",
                    "goldstein": 0.0,
                    "source_url": f"https://en.wikipedia.org/?curid={item['pageid']}",
                    "text": item['snippet'].replace('<span class=\"searchmatch\">', '').replace('</span>', ''),
                    "domain": 1,
                })
        except Exception as e:
            print(f"Failed wiki: {e}")
            
    out_file = "data/processed/wiki_sample.json"
    with open(out_file, "w") as f:
        json.dump(records, f, indent=2)
        
    manifest = {
        "dataset_name": "Wiki_Events",
        "source": "Wikipedia",
        "source_url": "https://en.wikipedia.org/w/api.php",
        "retrieval_timestamp": datetime.utcnow().isoformat() + "Z",
        "record_count": len(records),
        "min_timestamp": min([r["date"] for r in records]) if records else "",
        "max_timestamp": max([r["date"] for r in records]) if records else "",
        "schema_version": "v1",
        "checksum": get_hash(out_file) if os.path.exists(out_file) else "",
        "license/usage_notes": "CC-BY-SA",
        "processing_version": "1.0"
    }
    with open("data/manifests/wiki_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print("Wikipedia ingest complete.")

if __name__ == "__main__":
    setup_dirs()
    ingest_gdelt()
    ingest_wikipedia()
