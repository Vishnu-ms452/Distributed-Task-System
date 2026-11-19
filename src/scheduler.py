
class Scheduler:

    def __init__(self):
        self.workers = {}

    def register_worker(self, worker_id):

        if worker_id not in self.workers:
            self.workers[worker_id] = {
                "active_tasks": 0,
                "failed": False
            }

    def choose_worker(self):

        available = [
            (worker_id, info)
            for worker_id, info in self.workers.items()
            if not info["failed"]
        ]

        if not available:
            return None

        worker_id, _ = min(
            available,
            key=lambda item: (
                item[1]["active_tasks"],
                item[0]
            )
        )

        return worker_id

    def task_assigned(self, worker_id):

        if worker_id not in self.workers:
            raise ValueError(
                f"Unknown worker: {worker_id}"
            )

        if self.workers[worker_id]["failed"]:
            raise ValueError(
                f"Worker {worker_id} has failed"
            )

        self.workers[worker_id]["active_tasks"] += 1

    def task_completed(self, worker_id):

        if worker_id not in self.workers:
            return

        if self.workers[worker_id]["active_tasks"] > 0:
            self.workers[worker_id]["active_tasks"] -= 1

    def mark_worker_failed(self, worker_id):

        if worker_id in self.workers:
            self.workers[worker_id]["failed"] = True

    def recover_failed_worker(self, worker_id):

        if worker_id not in self.workers:
            return 0

        pending = self.workers[worker_id]["active_tasks"]

        self.workers[worker_id]["active_tasks"] = 0

        return pending

    def restore_worker(self, worker_id):

        if worker_id in self.workers:
            self.workers[worker_id]["failed"] = False

