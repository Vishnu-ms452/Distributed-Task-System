class Scheduler:
    def __init__(self):
        self.workers = {}

    def register_worker(self, worker_id):
        self.workers[worker_id] = {
            "active_tasks": 0,
            "status": "AVAILABLE",
        }

    def choose_worker(self):
        available = [
            (worker_id, info)
            for worker_id, info in self.workers.items()
            if info["status"] == "AVAILABLE"
        ]

        if not available:
            return None

        worker_id, _ = min(
            available,
            key=lambda item: item[1]["active_tasks"]
        )
        return worker_id

    def task_assigned(self, worker_id):
        if worker_id not in self.workers:
            raise ValueError("Unknown worker")

        if self.workers[worker_id]["status"] != "AVAILABLE":
            raise ValueError("Worker is not available")

        self.workers[worker_id]["active_tasks"] += 1
    def mark_worker_failed(self, worker_id):
        if worker_id not in self.workers:
            raise ValueError("Unknown worker")

        self.workers[worker_id]["status"] = "FAILED"
    def task_completed(self, worker_id):
        if worker_id not in self.workers:
            raise ValueError("Unknown worker")

        if self.workers[worker_id]["active_tasks"] <= 0:
            raise ValueError("No active task to complete")

        self.workers[worker_id]["active_tasks"] -= 1
    def recover_failed_worker(self, worker_id):
        if worker_id not in self.workers:
            raise ValueError("Unknown worker")

        if self.workers[worker_id]["status"] != "FAILED":
            raise ValueError("Worker has not failed")

        pending_tasks = self.workers[worker_id]["active_tasks"]

        self.workers[worker_id]["active_tasks"] = 0

        return pending_tasks
    def restore_worker(self, worker_id):
        if worker_id not in self.workers:
            raise ValueError("Unknown worker")

        self.workers[worker_id]["status"] = "AVAILABLE"
