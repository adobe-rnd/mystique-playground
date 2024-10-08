import asyncio
from abc import ABC, abstractmethod
from enum import Enum
import random
import string
import threading


class JobStatus(Enum):
    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    ERROR = 'error'


class Job(ABC):
    def __init__(self, job_id, **args):
        self.job_id = job_id
        self.status = JobStatus.QUEUED
        self.updates = [{"message": "Job queued. Processing will start soon..."}]
        self.result = None  # To store the result of the job

    @abstractmethod
    async def run(self):
        """Abstract method that must be implemented to perform the job task.
        Should return a result that will be stored after job completion."""
        pass

    def set_status(self, status):
        self.status = status

    def push_update(self, message, **kwargs):
        print(f"Job {self.job_id} update: {message}")  # Log job updates
        if message:
            update = {'message': message}
            update.update(kwargs)
            self.updates.append(update)
        else:
            self.updates.append({'message': 'Ugh! Something went wrong...'})

    def set_result(self, result):
        self.result = result


class JobManager:
    def __init__(self):
        self.job_queue = asyncio.Queue()
        self.job_status = {}
        self.worker_thread = None
        self.loop = None

    def start_worker_thread(self):
        self.worker_thread = threading.Thread(target=self.run_worker_loop_in_thread, daemon=True)
        self.worker_thread.start()

    def run_worker_loop_in_thread(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.worker_loop())

    async def worker_loop(self):
        while True:
            job = await self.job_queue.get()
            job.set_status(JobStatus.PROCESSING)
            job.push_update('Job processing started')
            try:
                # Run the job and store its result
                result = await job.run()
                print(f"Job {job.job_id} processing completed successfully with result: {result}")
                job.set_result(result)
                job.set_status(JobStatus.COMPLETED)
                job.push_update('Job processing completed successfully')
            except Exception as e:
                print(f"Job {job.job_id} processing failed: {e}")
                job.set_status(JobStatus.ERROR)
                job.push_update(f'Job processing failed: {e}')
            finally:
                print(f"Removing job {job.job_id} from queue")
                self.job_queue.task_done()

    def add_job(self, job):
        self.job_status[job.job_id] = job
        # Schedule the job to be put in the queue from the main thread
        if self.loop:
            self.loop.call_soon_threadsafe(self.job_queue.put_nowait, job)

    def get_job_status(self, job_id):
        return self.job_status.get(job_id)

    def get_job_result(self, job_id):
        """Retrieve the result of a completed job by its ID."""
        job = self.job_status.get(job_id)
        if job and job.status == JobStatus.COMPLETED:
            return job.result
        return None

    def generate_job_id(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))
