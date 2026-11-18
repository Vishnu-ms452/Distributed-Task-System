
import unittest
from scheduler import Scheduler


class TestScheduler(unittest.TestCase):

    def setUp(self):
        self.scheduler = Scheduler()
        self.scheduler.register_worker("W1")
        self.scheduler.register_worker("W2")

    def test_least_loaded_worker(self):
        self.scheduler.task_assigned("W1")
        self.scheduler.task_assigned("W1")
        self.assertEqual(self.scheduler.choose_worker(), "W2")

    def test_failed_worker_is_skipped(self):
        self.scheduler.mark_worker_failed("W1")
        self.assertEqual(self.scheduler.choose_worker(), "W2")

    def test_task_completion_reduces_load(self):
        self.scheduler.task_assigned("W1")
        self.scheduler.task_assigned("W1")
        self.scheduler.task_completed("W1")
        self.assertEqual(
            self.scheduler.workers["W1"]["active_tasks"], 1
        )

    def test_failed_worker_recovery_count(self):
        self.scheduler.task_assigned("W1")
        self.scheduler.task_assigned("W1")
        self.scheduler.mark_worker_failed("W1")
        pending = self.scheduler.recover_failed_worker("W1")
        self.assertEqual(pending, 2)
        self.assertEqual(
            self.scheduler.workers["W1"]["active_tasks"], 0
        )

    def test_restore_worker(self):
        self.scheduler.mark_worker_failed("W1")
        self.scheduler.restore_worker("W1")
        self.assertEqual(self.scheduler.choose_worker(), "W1")


if __name__ == "__main__":
    unittest.main()
