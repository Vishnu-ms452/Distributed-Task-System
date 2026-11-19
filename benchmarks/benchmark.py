import csv
import heapq
import time
from pathlib import Path
from scheduler import Scheduler

NUM_WORKERS = 4
NUM_TASKS = 1000
TRIALS = 5
ARRIVAL_INTERVAL = 0.001
DURATIONS = [0.002, 0.008, 0.003, 0.010,
             0.004, 0.006, 0.009, 0.002]


def simulate(strategy):
    scheduler = Scheduler()
    workers = [f"W{i + 1}" for i in range(NUM_WORKERS)]

    for wid in workers:
        scheduler.register_worker(wid)

    worker_available = {wid: 0.0 for wid in workers}
    distribution = {wid: 0 for wid in workers}
    active = []
    makespan = 0.0
    start = time.perf_counter()

    for i in range(NUM_TASKS):
        now = i * ARRIVAL_INTERVAL

        # Complete tasks whose simulated finish time has arrived.
        while active and active[0][0] <= now:
            finish, _, wid = heapq.heappop(active)
            scheduler.task_completed(wid)

        if strategy == "least_loaded":
            wid = scheduler.choose_worker()
            if wid is None:
                raise RuntimeError("No available worker")
        else:
            wid = workers[i % NUM_WORKERS]

        scheduler.task_assigned(wid)
        distribution[wid] += 1

        # A busy worker starts its next task only when available.
        task_start = max(now, worker_available[wid])
        finish = task_start + DURATIONS[i % len(DURATIONS)]
        worker_available[wid] = finish
        makespan = max(makespan, finish)

        heapq.heappush(active, (finish, i, wid))

    # Drain all remaining tasks.
    while active:
        finish, _, wid = heapq.heappop(active)
        scheduler.task_completed(wid)
        makespan = max(makespan, finish)

    runtime = time.perf_counter() - start
    return makespan, runtime, distribution


def main():
    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "benchmark_results.csv"

    with csv_path.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "trial", "strategy", "workers", "tasks",
            "simulated_makespan_seconds",
            "simulation_runtime_seconds", "worker_distribution"
        ])

        for trial in range(1, TRIALS + 1):
            for strategy in ("least_loaded", "round_robin"):
                makespan, runtime, distribution = simulate(strategy)

                writer.writerow([
                    trial, strategy, NUM_WORKERS, NUM_TASKS,
                    f"{makespan:.6f}", f"{runtime:.6f}",
                    str(distribution)
                ])

                print(f"\nTrial {trial} - {strategy}")
                print(f"Simulated makespan: {makespan:.6f} seconds")
                print(f"Simulation runtime: {runtime:.6f} seconds")
                print(f"Task assignments: {distribution}")

    print(f"\nResults saved to {csv_path}")
    print("NOTE: Makespan is simulated, not measured over Mininet.")


if __name__ == "__main__":
    main()
