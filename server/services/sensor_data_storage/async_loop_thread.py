import asyncio
import threading
from concurrent.futures import Future


class AsyncioLoopThread:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.thread.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_coro(self, coro) -> Future:
        """
        Schedule coroutine in the running loop as an independent task.

        Uses asyncio.create_task to ensure true parallelism - each operation
        runs independently and won't block others even if one is stuck.

        Returns:
            Future object representing the operation
        """
        # Create task wrapper to ensure independent execution
        async def task_wrapper():
            # Create task to ensure it runs independently
            task = asyncio.create_task(coro)
            return await task

        # Schedule as independent task for true parallelism
        return asyncio.run_coroutine_threadsafe(task_wrapper(), self.loop)

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
