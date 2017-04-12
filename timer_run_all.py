from multiprocessing import Process, Queue
from queue import Empty

from run_search import run_search, PROBLEMS, SEARCHES, show


def run(fn, queue, *args, **kwargs):
    """ Helper function to wrap target function (this is required so
    that you can pass in/out of the target function call with a thread-safe
    queue) and catch errors (which would otherwise pass silently when
    the Process running them dies) """
    try:
        result = fn(*args, **kwargs)
        queue.put((result, None))
    except Exception as e:
        queue.put((None, e))  # pass exceptions out through the queue


def run_with_timeout(target_fn, timeout, args=(), kwargs={}):
    """
    target_fn : function to run in a separate process
    timeout : time (in seconds) before aborting

    raises queue.Empty error if the function times out
    """
    queue = Queue()
    p = None
    try:
        # Process is killable (unlike threads)
        _args = tuple([target_fn, queue] + list(args))
        p = Process(target=run, args=_args, kwargs=kwargs)
        p.start()
        p.join(timeout=timeout)  # join blocks execution in the main thread

        result, err = queue.get_nowait()
        if err:
            raise err
    except Empty as e:
        print("Timeout\n\n\n\n")
        return None
    finally:
        if p and p.is_alive():
            p.terminate()  # kill the process if it is still running

    return result

# Test function that throws an error to demonstrate the the timeout code
# catches the error in the Process and raises it back in the main thread
def fib_thrower(n):
    raise ValueError("fib_thrower doesn't like the value {}!".format(n))


# Test function used to demonstrate correct operation of the timeout runner
def fib(n):
    if n <= 2:
        return 1
    return fib(n - 1) + fib(n - 2)


if __name__ == "__main__":
    max_time = 600  # number of seconds before killing the process

    print("Testing fib_thrower:")
    # arbitrary_value = 8675309
    # try:
    #     print(run_with_timeout(fib_thrower, max_time, args=(arbitrary_value,)))
    # except Exception as e:
    #     print(e)
    #
    # print("\nTesting fib on n=1, 10, 20,...60")
    # for i in range(1, 7):
    #     n = i * 10
    #     fib_args = (n, )  # note the trailing comma, which forces this to be a tuple
    #     print("i: {}\t fib({}): {}".format(n, n, run_with_timeout(fib, max_time, args=fib_args)))


    for pname, p in PROBLEMS:
        for sname, s, h in SEARCHES:
            hstring = h if not h else " with {}".format(h)
            print("\nSolving {} using {}{}...".format(pname, sname, hstring))

            _p = p()
            _h = None if not h else getattr(_p, h)
            search_args = (_p, s, _h)
            result = run_with_timeout(run_search, max_time, args=search_args)
