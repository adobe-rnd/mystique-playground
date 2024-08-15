import queue
import threading
import asyncio
from abc import ABC, abstractmethod
from enum import Enum
import random
import string


class JobStatus(Enum):
    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    ERROR = 'error'


class Job(ABC):
    def __init__(self, job_id):
        self.job_id = job_id
        self.status = JobStatus.QUEUED
        self.updates = [{"message": "Job queued. Processing will start soon..."}]

    @abstractmethod
    async def run(self):
        pass

    def set_status(self, status, message=None, **kwargs):
        self.status = status
        if message:
            update = {'message': message}
            update.update(kwargs)
            self.updates.append(update)


class JobManager:
    def __init__(self):
        self.job_queue = queue.Queue()
        self.job_status = {}
        self.worker_thread = None

    def start_worker_thread(self):
        self.worker_thread = threading.Thread(target=self.start_worker_loop, daemon=True)
        self.worker_thread.start()

    def start_worker_loop(self):
        asyncio.run(self.worker_loop())

    async def worker_loop(self):
        while True:
            job = await asyncio.to_thread(self.job_queue.get)
            job.set_status(JobStatus.PROCESSING, 'Job processing started')
            try:
                await job.run()
            except Exception as e:
                job.set_status(JobStatus.ERROR, error=str(e))
            finally:
                self.job_queue.task_done()

    def add_job(self, job):
        self.job_status[job.job_id] = job
        self.job_queue.put(job)

    def get_job_status(self, job_id):
        return self.job_status.get(job_id)

    def generate_job_id(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))
