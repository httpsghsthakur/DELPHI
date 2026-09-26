"""
DELPHI Phase 13 — Real Data Acquisition

Downloads multiple days of GDELT V2 export data for genuine multi-day 
temporal coverage. Produces an immutable dataset manifest.
"""
import os
import sys
import json
import hashlib
import zipfile
import io
import time
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw" / "gdelt"
PROCESSED_DIR = DATA_DIR / "processed" / "gdelt_multi"

# GDELT V2 exports are available every 15 minutes
# We'll download 4 exports per day (every 6 hours) across multiple days
# to get manageable but temporally diverse data.

# Date range: 7 days in January 2023 (diverse international events)
GDELT_BASE = "http://data.gdeltproject.org/gdeltv2/"

def get_gdelt_urls(start_date: str, num_days: int, exports_per_day: int = 4):
    """Generate GDELT V2 export URLs for date range."""
    urls = []
    dt = datetime.strptime(start_date, "%Y%m%d")
    # Hours to sample: spread across day
    hours = [0, 6, 12, 18][:exports_per_day]
    
    for day_offset in range(num_days):
        current_date = dt + timedelta(days=day_offset)
        for hour in hours:
            ts = current_date.strftime("%Y%m%d") + f"{hour:02d}0000"
            filename = f"{ts}.export.CSV.zip"
            url = GDELT_BASE + filename
            urls.append((ts, url, filename))
    return urls


def download_gdelt_file(url: str, output_path: str, max_retries: int = 3):
    """Download and extract a single GDELT export file."""
    for attempt in range(max_retries):
        try:
            req = Request(url, headers={"User-Agent": "DELPHI-Research/1.0"})
            response = urlopen(req, timeout=30)
            data = response.read()
            
            # Extract CSV from zip
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                csv_names = [n for n in zf.namelist() if n.endswith(".CSV")]
                if not csv_names:
                    print(f"  WARNING: No CSV in {url}")
                    return None
                csv_data = zf.read(csv_names[0])
            
            with open(output_path, "wb") as f:
                f.write(csv_data)
            
            return len(csv_data)
            
        except (URLError, HTTPError, zipfile.BadZipFile) as e:
            print(f"  Attempt {attempt+1}/{max_retries} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
    return None


def parse_gdelt_records(csv_path: str, timestamp: str):
    """Parse GDELT V2 export CSV into structured records."""
    records = []
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f):
            fields = line.strip().split("\t")
            if len(fields) < 58:
                continue
            
            try:
                record = {
                    "global_event_id": fields[0],
                    "event_date": fields[1],  # YYYYMMDD
                    "year": fields[3] if len(fields) > 3 else "",
                    "actor1_code": fields[5] if len(fields) > 5 else "",
                    "actor1_name": fields[6] if len(fields) > 6 else "",
                    "actor1_country": fields[7] if len(fields) > 7 else "",
                    "actor2_code": fields[15] if len(fields) > 15 else "",
                    "actor2_name": fields[16] if len(fields) > 16 else "",
                    "actor2_country": fields[17] if len(fields) > 17 else "",
                    "is_root_event": fields[25] if len(fields) > 25 else "0",
                    "event_code": fields[26] if len(fields) > 26 else "",
                    "event_base_code": fields[27] if len(fields) > 27 else "",
                    "event_root_code": fields[28] if len(fields) > 28 else "",
                    "quad_class": fields[29] if len(fields) > 29 else "",
                    "goldstein_scale": fields[30] if len(fields) > 30 else "0",
                    "num_mentions": fields[31] if len(fields) > 31 else "0",
                    "num_sources": fields[32] if len(fields) > 32 else "0",
                    "num_articles": fields[33] if len(fields) > 33 else "0",
                    "avg_tone": fields[34] if len(fields) > 34 else "0",
                    "source_url": fields[57] if len(fields) > 57 else "",
                    "gdelt_timestamp": timestamp,
                }
                # Extract domain from URL
                url = record["source_url"]
                if url:
                    from urllib.parse import urlparse
                    try:
                        parsed = urlparse(url)
                        record["source_domain"] = parsed.netloc
                    except Exception:
                        record["source_domain"] = ""
                else:
                    record["source_domain"] = ""
                    
                records.append(record)
            except (IndexError, ValueError):
                continue
    return records


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Download 7 days of GDELT data, 4 exports per day = 28 files
    print("=" * 60)
    print("DELPHI Phase 13 — GDELT Multi-Day Data Acquisition")
    print("=" * 60)
    
    # Use Jan 1-7 2023 for temporal diversity
    urls = get_gdelt_urls("20230101", num_days=7, exports_per_day=4)
    
    all_records = []
    download_log = []
    successful = 0
    failed = 0
    
    for ts, url, filename in urls:
        csv_path = os.path.join(RAW_DIR, filename.replace(".zip", ""))
        
        # Check if already downloaded
        if os.path.exists(csv_path):
            print(f"  [CACHED] {filename}")
            records = parse_gdelt_records(csv_path, ts)
            all_records.extend(records)
            download_log.append({"timestamp": ts, "status": "cached", "records": len(records)})
            successful += 1
            continue
        
        print(f"  [DOWNLOAD] {url}")
        size = download_gdelt_file(url, csv_path)
        
        if size is not None:
            records = parse_gdelt_records(csv_path, ts)
            all_records.extend(records)
            download_log.append({"timestamp": ts, "status": "downloaded", "size": size, "records": len(records)})
            successful += 1
            print(f"    -> {len(records)} records ({size} bytes)")
        else:
            download_log.append({"timestamp": ts, "status": "failed"})
            failed += 1
            print(f"    -> FAILED")
        
        # Rate limiting
        time.sleep(1)
    
    print(f"\nDownload complete: {successful} successful, {failed} failed")
    print(f"Total raw records: {len(all_records)}")
    
    if not all_records:
        print("ERROR: No records acquired. Exiting.")
        sys.exit(1)
    
    # Deduplicate by global_event_id
    seen_ids = set()
    unique_records = []
    for r in all_records:
        eid = r["global_event_id"]
        if eid not in seen_ids:
            seen_ids.add(eid)
            unique_records.append(r)
    
    dup_count = len(all_records) - len(unique_records)
    print(f"Deduplicated: {dup_count} duplicates removed")
    print(f"Unique records: {len(unique_records)}")
    
    # Compute statistics
    domains = set(r["source_domain"] for r in unique_records if r["source_domain"])
    actors = set(r["actor1_code"] for r in unique_records if r["actor1_code"])
    targets = set(r["actor2_code"] for r in unique_records if r["actor2_code"])
    event_types = set(r["event_code"] for r in unique_records if r["event_code"])
    dates = set(r["event_date"] for r in unique_records if r["event_date"])
    
    # Count missing
    missing_timestamp = sum(1 for r in unique_records if not r["event_date"])
    missing_source = sum(1 for r in unique_records if not r["source_domain"])
    
    # Event type distribution
    from collections import Counter
    event_dist = Counter(r["event_root_code"] for r in unique_records if r["event_root_code"])
    
    stats = {
        "total_records": len(unique_records),
        "unique_sources": len(domains),
        "unique_domains": len(domains),
        "unique_actors": len(actors),
        "unique_targets": len(targets),
        "unique_event_types": len(event_types),
        "unique_event_root_codes": len(event_dist),
        "date_range": sorted(list(dates))[:1] + ["..."] + sorted(list(dates))[-1:] if len(dates) > 2 else sorted(list(dates)),
        "date_count": len(dates),
        "duplicate_rate": f"{dup_count / max(len(all_records), 1) * 100:.1f}%",
        "missing_timestamp_rate": f"{missing_timestamp / max(len(unique_records), 1) * 100:.1f}%",
        "missing_source_rate": f"{missing_source / max(len(unique_records), 1) * 100:.1f}%",
        "event_root_distribution": dict(event_dist.most_common(20)),
    }
    
    print("\n--- Dataset Statistics ---")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    # Save processed records as JSON Lines
    processed_path = os.path.join(PROCESSED_DIR, "events.jsonl")
    with open(processed_path, "w", encoding="utf-8") as f:
        for r in unique_records:
            f.write(json.dumps(r) + "\n")
    
    # Compute checksum of processed file
    checksum = compute_sha256(processed_path)
    
    # Create immutable manifest
    manifest = {
        "dataset_id": "GDELT_MULTI_20230101_20230107",
        "dataset_name": "GDELT V2 Multi-Day Corpus (Jan 1-7 2023)",
        "dataset_version": "v2.0",
        "source": "http://data.gdeltproject.org/gdeltv2/",
        "download_timestamps": [d["timestamp"] for d in download_log if d["status"] != "failed"],
        "creation_date": datetime.utcnow().isoformat() + "Z",
        "time_range_start": min(dates) if dates else "unknown",
        "time_range_end": max(dates) if dates else "unknown",
        "gdelt_window_start": "20230101",
        "gdelt_window_end": "20230107",
        "record_count": len(unique_records),
        "unique_sources": len(domains),
        "unique_domains": len(domains),
        "unique_actors": len(actors),
        "unique_targets": len(targets),
        "unique_event_types": len(event_types),
        "sha256": checksum,
        "schema_version": "v2",
        "preprocessing_version": "v2",
        "split_version": "v2",
        "download_log": download_log,
        "statistics": stats
    }
    
    manifest_path = os.path.join(PROCESSED_DIR, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nManifest saved: {manifest_path}")
    print(f"Processed data: {processed_path}")
    print(f"SHA-256: {checksum}")
    print("\nDone.")


if __name__ == "__main__":
    main()
