from multiprocessing import Process
import os
import sys
import threading
import traceback
from distutils.version import LooseVersion

import py
import pytest

DEFAULT_TIMEOUT_S = 10

# timeout routine using Process
def timeout(func, *args, **kwargs):
    test_process = Process(target=func, args=args, kwargs=kwargs)
    test_process.start()
    test_process.join(timeout=10)
    test_process.terminate()
    if test_process.exitcode is None:
        pytest.fail(msg='Test timeout test {}'.format(func.__name__))

def dump_stacks():
    """Dump the stacks of all threads except the current thread."""
    current_ident = threading.current_thread().ident
    for thread_ident, frame in sys._current_frames().items():
        if thread_ident == current_ident:
            continue
        for t in threading.enumerate():
            if t.ident == thread_ident:
                thread_name = t.name
                break
        else:
            thread_name = "<unknown>"
        write_title("Stack of %s (%s)" % (thread_name, thread_ident))
        write("".join(traceback.format_stack(frame)))


def write_title(title, stream=None, sep="~"):
    """Write a section title.
    If *stream* is None sys.stderr will be used, *sep* is used to
    draw the line.
    """
    if stream is None:
        stream = sys.stderr
    width = py.io.get_terminal_width()
    fill = int((width - len(title) - 2) / 2)
    line = " ".join([sep * fill, title, sep * fill])
    if len(line) < width:
        line += sep * (width - len(line))
    stream.write("\n" + line + "\n")


def write(text, stream=None):
    """Write text to stream.
    Pretty stupid really, only here for symetry with .write_title().
    """
    if stream is None:
        stream = sys.stderr
    stream.write(text)

def timeout_timer(item, timeout):
    try:
        capman = item.config.pluginmanager.getplugin("capturemanager")
        if capman:
            pytest_version = LooseVersion(pytest.__version__)
            if pytest_version >= LooseVersion("3.7.3"):
                capman.suspend_global_capture(item)
                stdout, stderr = capman.read_global_capture()
            else:
                stdout, stderr = capman.suspend_global_capture(item)
        else:
            stdout, stderr = None, None
        write_title("Timeout", sep="+")
        caplog = item.config.pluginmanager.getplugin("_capturelog")
        if caplog and hasattr(item, "capturelog_handler"):
            log = item.capturelog_handler.stream.getvalue()
            if log:
                write_title("Captured log")
                write(log)
        if stdout:
            write_title("Captured stdout")
            write(stdout)
        if stderr:
            write_title("Captured stderr")
            write(stderr)
        dump_stacks()
        write_title("Timeout", sep="+")
    except Exception:
        traceback.print_exc()
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(1)

def timeout_setup(item):
    timer = threading.Timer(DEFAULT_TIMEOUT_S, timeout_timer, (item, DEFAULT_TIMEOUT_S))
    timer.name = "%s %s" % (__name__, item.nodeid)

    def cancel():
        timer.cancel()
        timer.join()

    item.cancel_timeout = cancel
    timer.start()

def timeout_teardown(item):
    cancel = getattr(item, "cancel_timeout", None)
    if cancel:
        cancel()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    # print('Running pytest_runtest_call')
    # timeout(item.function)
    # print('item', item.__dict__)
    print('Timer hook wrapper start')
    timeout_setup(item)
    yield
    timeout_teardown(item)
    print('Timer hook wrapper end')
