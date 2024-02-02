import queue
import threading

from streamlit.runtime.scriptrunner import add_script_run_ctx


# Observable class
class Observable:
    def __init__(self):
        self.observers = []
        # Create a new queue
        self.queue = queue.Queue()
        # Create a new worker thread
        self.worker_thread = threading.Thread(target=self.process_notifications)
        # Start the worker thread
        add_script_run_ctx(self.worker_thread)
        self.worker_thread.start()

    # Register an observer
    def register_observer(self, observer):
        self.observers.append(observer)

    # Notify the observer
    def notify_observer(self, data):
        self.queue.put(data)

    # Process the notifications
    def process_notifications(self):
        while True:
            # Get the data from the queue
            data = self.queue.get()
            # Notify the observers
            for observer in self.observers:
                observer.notify(data)
            # Check if the interview is over
            if data['how_many_questions'] == data['question_number'] and self.queue.empty():
                # End the interview
                print('Interview ended...')
                break
            # Mark the task as done
            self.queue.task_done()
