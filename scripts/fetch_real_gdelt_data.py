import os
import requests
import zipfile
import io
import pandas as pd
import json

def fetch_gdelt_export(url, extract_path):
    print(f"Fetching {url}")
    r = requests.get(url)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall(extract_path)

def main():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    if os.path.exists("data/processed/gdelt_real_large.json"):
        print("Data already fetched. Skipping download.")
        return
        
    # Example recent GDELT exports
    urls = [
        "http://data.gdeltproject.org/events/20240101.export.CSV.zip",
        "http://data.gdeltproject.org/events/20240102.export.CSV.zip",
        "http://data.gdeltproject.org/events/20240103.export.CSV.zip",
    ]
    
    for url in urls:
        fetch_gdelt_export(url, "data/raw")
    
    # Process them
    cols = [
        "GLOBALEVENTID", "SQLDATE", "MonthYear", "Year", "FractionDate", 
        "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode", "Actor1EthnicCode", "Actor1Religion1Code", "Actor1Religion2Code", "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",
        "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode", "Actor2EthnicCode", "Actor2Religion1Code", "Actor2Religion2Code", "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",
        "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode", "QuadClass", "GoldsteinScale", "NumMentions", "NumSources", "NumArticles", "AvgTone",
        "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode", "Actor1Geo_ADM1Code", "Actor1Geo_Lat", "Actor1Geo_Long", "Actor1Geo_FeatureID",
        "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode", "Actor2Geo_ADM1Code", "Actor2Geo_Lat", "Actor2Geo_Long", "Actor2Geo_FeatureID",
        "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode", "ActionGeo_ADM1Code", "ActionGeo_Lat", "ActionGeo_Long", "ActionGeo_FeatureID",
        "DATEADDED", "SOURCEURL"
    ]
    
    all_events = []
    for f in os.listdir("data/raw"):
        if f.endswith(".CSV"):
            df = pd.read_csv(os.path.join("data/raw", f), sep="\t", header=None, names=cols, low_memory=False)
            # Filter rows with missing source URLs or important fields
            df = df.dropna(subset=["SOURCEURL", "EventCode", "Actor1Name"])
            
            for _, row in df.iterrows():
                # Convert date
                date_str = str(row["SQLDATE"])
                if len(date_str) == 8:
                    iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T00:00:00Z"
                else:
                    iso_date = "2024-01-01T00:00:00Z"
                
                # Mock a headline since GDELT v1 only has URL. 
                # For training text, we can use Actor1 + Action + Actor2 or extract from URL
                headline = f"{row['Actor1Name']} involved in event type {row['EventCode']} with {row.get('Actor2Name', 'another party')}"
                
                all_events.append({
                    "event_id": str(row["GLOBALEVENTID"]),
                    "date": iso_date,
                    "event_code": str(row["EventCode"]).zfill(3), # CAMEO code
                    "domain": row.get("SOURCEURL", "").split("/")[2] if pd.notnull(row.get("SOURCEURL")) and "://" in str(row.get("SOURCEURL")) else "unknown.com",
                    "url": row["SOURCEURL"],
                    "headline": headline,
                    "actor1": str(row.get("Actor1Name", "Unknown")),
                    "actor2": str(row.get("Actor2Name", "Unknown")),
                    "goldstein": row.get("GoldsteinScale", 0.0)
                })
                
                # If we have 250,000 records, stop (for speed in this demo)
                if len(all_events) >= 100000:
                    break
        if len(all_events) >= 100000:
            break
            
    with open("data/processed/gdelt_real_large.json", "w") as out:
        json.dump(all_events, out)
        
    print(f"Processed {len(all_events)} real events from GDELT.")
    
    # Generate true Causal sequences (group by actor pair and sort by date)
    from collections import defaultdict
    seqs = defaultdict(list)
    for e in all_events:
        pair = tuple(sorted([e["actor1"], e["actor2"]]))
        if "Unknown" not in pair:
            seqs[pair].append(e)
            
    causal_seqs = []
    for pair, events in seqs.items():
        if len(events) >= 3:
            events.sort(key=lambda x: x["date"])
            seq_codes = [e["event_code"] for e in events[:20]]
            causal_seqs.append(seq_codes)
            
    with open("data/processed/causal_seqs.json", "w") as out:
        json.dump(causal_seqs, out)
    print(f"Generated {len(causal_seqs)} real event trajectories.")

if __name__ == "__main__":
    main()
