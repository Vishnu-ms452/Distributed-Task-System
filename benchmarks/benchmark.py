
import csv
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scheduler import Scheduler


def run_least_loaded(num_workers, num_tasks):
    scheduler = Scheduler()

    for i in range(num_workers):
        scheduler.register_worker(f"W{i + 1}")

    start = time.perf_counter()

    for _ in range(num_tasks):
        worker_id = scheduler.choose_worker()
        scheduler.task_assigned(worker_id)

    elapsed = time.perf_counter() - start

    distribution = {
        worker_id: info["active_tasks"]
        for worker_id, info in scheduler.workers.items()
    }

    return elapsed, distribution


def run_round_robin(num_workers, num_tasks):
    workers = [f"W{i + 1}" for i in range(num_workers)]
    distribution = {worker_id: 0 for worker_id in workers}

    start = time.perf_counter()

    for i in range(num_tasks):
        worker_id = workers[i % num_workers]
        distribution[worker_id] += 1

    elapsed = time.perf_counter() - start

    return elapsed, distribution


def main():
    num_workers = 4
    num_tasks = 10000
    trials = 5

    results_dir = ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "benchmark_results.csv"

    with open(csv_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "trial",
            "strategy",
            "workers",
            "tasks",
            "assignment_time_seconds",
        ])

        for trial in range(1, trials + 1):
            least_time, least_distribution = run_least_loaded(
                num_workers, num_tasks
            )
            rr_time, rr_distribution = run_round_robin(
                num_workers, num_tasks
            )

            writer.writerow([
                trial, "least_loaded", num_workers, num_tasks,
                f"{least_time:.6f}"
            ])
            writer.writerow([
                trial, "round_robin", num_workers, num_tasks,
                f"{rr_time:.6f}"
            ])

            print(f"\nTrial {trial}")
            print(f"Least-loaded: {least_time:.6f} seconds")
            print(f"Round-robin:  {rr_time:.6f} seconds")
            print(f"Least-loaded distribution: {least_distribution}")
            print(f"Round-robin distribution:  {rr_distribution}")

    print(f"\nAll {trials} trials saved to {csv_path}")


if __name__ == "__main__":
    main()
