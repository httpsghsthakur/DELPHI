import argparse
import requests
import time
import statistics
import concurrent.futures

def run_benchmark(url: str, requests_count: int, concurrency: int):
    print(f"Starting benchmark on {url} with {requests_count} requests and concurrency {concurrency}...")
    latencies = []
    failures = 0
    
    payload = {
        "text": "The government announced a new trade policy.",
        "publication_timestamp": "2026-08-30T00:00Z",
        "prediction_information_cutoff": "2026-09-01T00:00Z",
        "domain": "geopolitics",
        "forecast_horizon": 30
    }
    
    def make_request(i):
        headers = {"Idempotency-Key": f"bench_{time.time()}_{i}"}
        start = time.time()
        try:
            resp = requests.post(f"{url}/analysis", json=payload, headers=headers)
            resp.raise_for_status()
            success = True
        except Exception:
            success = False
        duration = time.time() - start
        return success, duration

    start_total = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        results = list(executor.map(make_request, range(requests_count)))
    
    total_duration = time.time() - start_total
    
    for success, duration in results:
        if success:
            latencies.append(duration)
        else:
            failures += 1
            
    if not latencies:
        print("All requests failed.")
        return
        
    latencies.sort()
    count = len(latencies)
    median = statistics.median(latencies)
    
    def percentile(data, p):
        k = (len(data) - 1) * p
        f = int(k)
        c = int(k) + 1 if int(k) + 1 < len(data) else f
        return data[f] + (data[c] - data[f]) * (k - f)

    p95 = percentile(latencies, 0.95)
    p99 = percentile(latencies, 0.99)
    failure_rate = (failures / requests_count) * 100
    
    print("\n--- API PERFORMANCE BENCHMARK ---")
    print(f"Total requests: {requests_count}")
    print(f"Concurrency:    {concurrency}")
    print(f"Total time:     {total_duration:.2f}s")
    print(f"Failure rate:   {failure_rate:.1f}% ({failures} failures)")
    print(f"Median latency: {median:.3f}s")
    print(f"P95 latency:    {p95:.3f}s")
    print(f"P99 latency:    {p99:.3f}s")
    print(f"Throughput:     {(count / total_duration):.2f} req/s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DELPHI API Benchmark")
    parser.add_argument("--url", type=str, default="http://localhost:8000", help="API URL")
    parser.add_argument("--requests", type=int, default=50, help="Number of requests")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrent workers")
    args = parser.parse_args()
    
    run_benchmark(args.url, args.requests, args.concurrency)
