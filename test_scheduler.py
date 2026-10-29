from scheduler import Scheduler

scheduler = Scheduler()

scheduler.register_worker("W1")
scheduler.register_worker("W2")

scheduler.task_assigned("W1")
scheduler.task_assigned("W1")

scheduler.mark_worker_failed("W1")
pending = scheduler.recover_failed_worker("W1")

print("Tasks needing recovery:", pending)
print("Selected while W1 failed:", scheduler.choose_worker())

scheduler.restore_worker("W1")

print("After W1 is restored:", scheduler.workers)
print("Selected after restoration:", scheduler.choose_worker())
