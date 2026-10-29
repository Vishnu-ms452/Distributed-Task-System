
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scheduler import Scheduler


def test_least_loaded(num_new_tasks):
    scheduler = Scheduler()

    for worker in ["W1", "W2", "W3", "W4"]:
        scheduler.register_worker(worker)

    # Simulate workers that already have different workloads.
    for _ in range(8):
        scheduler.task_assigned("W1")

    for _ in range(2):
        scheduler.task_assigned("W2")

    # Assign new tasks using least-loaded scheduling.
    for _ in range(num_new_tasks):
        worker = scheduler.choose_worker()
        scheduler.task_assigned(worker)

    return {
        worker: info["active_tasks"]
        for worker, info in scheduler.workers.items()
    }


def test_round_robin(num_new_tasks):
    workers = ["W1", "W2", "W3", "W4"]

    # Use the same initial workloads as the least-loaded test.
    distribution = {
        "W1": 8,
        "W2": 2,
        "W3": 0,
        "W4": 0,
    }

    for i in range(num_new_tasks):
        worker = workers[i % len(workers)]
        distribution[worker] += 1

    return distribution


def main():
    num_new_tasks = 100

    least = test_least_loaded(num_new_tasks)
    rr = test_round_robin(num_new_tasks)

    print("Initial workloads: W1=8, W2=2, W3=0, W4=0")
    print(f"New tasks assigned: {num_new_tasks}")

    print("\nLeast-loaded final workloads:")
    print(least)

    print("\nRound-robin final workloads:")
    print(rr)


if __name__ == "__main__":
    main()
