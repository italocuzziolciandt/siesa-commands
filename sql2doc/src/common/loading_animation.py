import time
import threading
import sys


class LoadingAnimation:
    """
    A class for displaying a loading animation in the console.

    Attributes:
        message (str): The message to display before the loading animation.
        interval (float): The time interval between each frame of the animation.
        stop_event (threading.Event): An event to signal the animation thread to stop.
        thread (threading.Thread): The thread running the animation.
    """

    def __init__(self, message="Processing...", interval=0.1):
        """
        Initializes the LoadingAnimation with a message and interval.

        Args:
            message (str, optional): The message to display. Defaults to "Processing...".
            interval (float, optional): The interval between animation frames. Defaults to 0.1 seconds.
        """
        self.message = message
        self.interval = interval
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        """
        Starts the loading animation in a separate thread.
        """
        if self.thread is None:
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._animate)
            self.thread.daemon = True  # Allow the main program to exit even if the thread is still running
            self.thread.start()

    def stop(self):
        """
        Stops the loading animation and waits for the thread to finish.
        """
        if self.thread is not None:
            self.stop_event.set()
            self.thread.join()  # Wait for the thread to finish
            self.thread = None
            sys.stdout.write(
                "\r" + " " * (len(self.message) + 5) + "\r"
            )  # Clear the line
            sys.stdout.flush()

    def _animate(self):
        """
        Animates the loading indicator. This method should not be called directly.
        """
        animation = "|/-\\"
        idx = 0
        while not self.stop_event.is_set():
            print(
                f"\r{self.message} {animation[idx % len(animation)]}",
                end="",
                flush=True,
            )
            idx += 1
            time.sleep(self.interval)

    def __enter__(self):
        """
        Starts the animation when entering a 'with' block.
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Stops the animation when exiting a 'with' block.

        Args:
            exc_type: The type of the exception, if any.
            exc_val: The exception value, if any.
            exc_tb: The traceback, if any.
        """
        self.stop()
