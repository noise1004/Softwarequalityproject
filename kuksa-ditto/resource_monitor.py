"""
resource_monitor.py  — Iteration 2 Non-Functional Experiment
Measures CPU and memory usage of the SDV pipeline Docker containers
at 5-second intervals and saves results to a CSV file.

Usage:
    python3 resource_monitor.py 1 60 results_1v.csv
    python3 resource_monitor.py 2 60 results_2v.csv
    python3 resource_monitor.py 3 60 results_3v.csv

Arguments:
    num_vehicles   Number of vehicles currently running (for labelling)
    duration       How many seconds to monitor
    output         Output CSV filename
"""

import csv
import subprocess
import sys
import time
from datetime import datetime

CONTAINERS = [
    "kuksa-databroker",
    "ditto-gateway",
    "ditto-things",
    "ditto-policies",
    "mongodb",
]


def get_docker_stats():
    result = subprocess.run(
        ["docker", "stats", "--no-stream", "--format",
         "{{.Name}},{{.CPUPerc}},{{.MemUsage}}"] + CONTAINERS,
        capture_output=True, text=True
    )
    stats = {}
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split(",")
        if len(parts) >= 3:
            name    = parts[0].strip()
            cpu     = parts[1].strip().replace("%", "")
            mem_raw = parts[2].strip().split("/")[0].strip()
            stats[name] = {"cpu": cpu, "mem": mem_raw}
    return stats


def parse_mem_mb(mem_str):
    mem_str = mem_str.strip()
    try:
        if "GiB" in mem_str:
            return float(mem_str.replace("GiB", "").strip()) * 1024
        elif "MiB" in mem_str:
            return float(mem_str.replace("MiB", "").strip())
        elif "kB" in mem_str or "KiB" in mem_str:
            return float(mem_str.replace("kB", "").replace("KiB", "").strip()) / 1024
        else:
            return float(mem_str)
    except ValueError:
        return 0.0


def main():
    num_vehicles = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    duration     = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    output       = sys.argv[3]     if len(sys.argv) > 3 else "results.csv"

    print(f'Monitoring {num_vehicles} vehicle(s) for {duration}s → {output}')

    fieldnames = ["timestamp", "elapsed_s", "vehicles",
                  "total_cpu_percent", "total_mem_mb"]
    for c in CONTAINERS:
        fieldnames += [f"{c}_cpu", f"{c}_mem_mb"]

    rows       = []
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > duration:
            break

        stats      = get_docker_stats()
        total_cpu  = 0.0
        total_mem  = 0.0
        row = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "elapsed_s": round(elapsed, 1),
            "vehicles":  num_vehicles,
        }

        for c in CONTAINERS:
            if c in stats:
                cpu = float(stats[c]["cpu"]) if stats[c]["cpu"] else 0.0
                mem = parse_mem_mb(stats[c]["mem"])
            else:
                cpu, mem = 0.0, 0.0
            row[f"{c}_cpu"]    = round(cpu, 2)
            row[f"{c}_mem_mb"] = round(mem, 1)
            total_cpu += cpu
            total_mem += mem

        row["total_cpu_percent"] = round(total_cpu, 2)
        row["total_mem_mb"]      = round(total_mem, 1)
        rows.append(row)

        print(f"[{row['timestamp']}] vehicles={num_vehicles}  "
              f"CPU={row['total_cpu_percent']}%  MEM={row['total_mem_mb']}MB")
        time.sleep(5)

    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f'\nSaved {len(rows)} samples to {output}')
    if rows:
        avg_cpu = sum(r["total_cpu_percent"] for r in rows) / len(rows)
        avg_mem = sum(r["total_mem_mb"] for r in rows) / len(rows)
        print(f'Average CPU: {avg_cpu:.2f}%  |  Average Memory: {avg_mem:.1f} MB')


if __name__ == "__main__":
    main()
