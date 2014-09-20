from threading import Timer, Lock
import random

def register_timer(seconds, func):
    t = Timer(seconds, func)
    t.start()

def fuzzy_seconds(seconds, fuzziness):
    if not fuzziness:
        return seconds

    return random.randrange(seconds - seconds*fuzziness, seconds + seconds*fuzziness)

def every(seconds, fuzziness=None):
    def decorator(func):
        def done():
            delegate.lock.release()
        
        def snooze(seconds):
            delegate.lock.release()
            register_timer(seconds, delegate)

        def delegate():
            # only call func if not already running
            if delegate.lock.acquire(False):
                func(done, snooze)

            register_timer(fuzzy_seconds(seconds, fuzziness), delegate)

        delegate.lock = Lock()
        register_timer(seconds, delegate)
        return func

    return decorator