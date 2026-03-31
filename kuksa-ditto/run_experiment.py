"""
run_experiment.py  — Iteration 2
Runs all three vehicle scenarios automatically and prints a summary table.

Usage:
    python3 run_experiment.py
"""

import subprocess
import sys
import os
import time
import csv

DURATION  = 60   # seconds of measurement per run
WARMUP    = 10   # seconds to let simulator stabilise before measuring
VEHICLES  = [1, 2, 3]


def run_scenario(num_vehicles):
    print(f'\n{"="*50}')
    print(f'SCENARIO: {num_vehicles} vehicle(s)')
    print(f'{"="*50}')

    sim = subprocess.Popen(
        [sys.executable, "multi_vehicle_simulator.py", str(num_vehicles)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print(f'Simulator PID {sim.pid} — warming up {WARMUP}s ...')
    time.sleep(WARMUP)

    output = f"results_{num_vehicles}v.csv"
    subprocess.run([
        sys.executable, "resource_monitor.py",
        str(num_vehicles), str(DURATION), output
    ])

    sim.terminate()
    sim.wait()
    print(f'Scenario {num_vehicles}v complete. Saved to {output}')
    time.sleep(5)


def summarize():
    print(f'\n{"="*50}')
    print('EXPERIMENT SUMMARY')
    print(f'{"="*50}')
    print(f'{"Vehicles":<12} {"Avg CPU %":<14} {"Avg Memory (MB)"}')
    print('-' * 42)
    for v in VEHICLES:
        fname = f"results_{v}v.csv"
        if not os.path.exists(fname):
            print(f'{v:<12} (no data)')
            continue
        with open(fname) as f:
            rows = list(csv.DictReader(f))
        if not rows:
            continue
        avg_cpu = sum(float(r["total_cpu_percent"]) for r in rows) / len(rows)
        avg_mem = sum(float(r["total_mem_mb"]) for r in rows) / len(rows)
        print(f'{v:<12} {avg_cpu:<14.2f} {avg_mem:.1f}')


if __name__ == "__main__":
    for v in VEHICLES:
        run_scenario(v)
    summarize()
    print('\nAll done. CSV files ready for the report.')
