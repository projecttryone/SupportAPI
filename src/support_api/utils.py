"""Shared functionality or resources."""


from functools import wraps 
import time
import structlog
from pathlib import Path
from contextlib import contextmanager
import os

_log = structlog.get_logger(__name__)


def timed(label: str | None = None):
    """Log the wall-clock duration of the decorated callable.
    
    Used as '@timed()' parantheses are required or '@timed(label='custom-label').
    The opetional label overrides the functions qualified name in the log event 
    """


    def decorator(func):
        event_label = label or func.__qualname__

        @wraps(func)
        def wrapper(*args , **kwargs):
            started = time.perf_counter()
            try:
                return func(*args , **kwargs)
            finally:
                duration_ms = round((time.perf_counter()-started) *1000 , 2)
                _log.info("timed", label =event_label , duration_ms = duration_ms)

        return wrapper
    return decorator


"""contextmanager is a special decoratir that you 
can use to essential handle all of your  file interaction """

@contextmanager
def atomic_write(path: Path , encoding: str = "utf-8"):
    """
    Write to a tempfile next to 'path' , then rename on clean exit .
    On exception , the tempfile is removed and the origianl file is left  untouched .
    Callers get awritable file handle as  the 'as' value.
    """

    tmp = path.with_suffix(path.suffix + ".tmp") # ralph.txt.tmp
    try:
        with tmp.open("w", encoding=encoding) as fh :
            yield fh # generator function
    except BaseException :
        if tmp.exists():
            tmp.unlink()
        raise
    else:
        os.replace(tmp,path) # final write that persists any changes made .



if __name__ == "__main__":
 import tempfile
 with tempfile.TemporaryDirectory() as tempdir:
     target = Path(tempdir) / "demo.txt"
     target.write_text("ORIGINAL")
     print(f"Original file content : {target.read_text()}")

     #Happy Path
     with atomic_write(target) as fh:
         fh.write("NEW CONTENTS")
     print(f"After happy path: {target.read_text()}")
     

     try:
         with atomic_write(target) as fh :
             fh.write("WOULD BE REPLACEMENT")
             raise RuntimeError("BOOM")
     except RuntimeError:
         print( f"After failure:    {target.read_text()}")

     leftover = target.with_suffix(".txt.tmp")
     print(f"Tempfile left behind:  {leftover.exists()}")



         



     #Sad Path(faulure)
 
 
 
 
 
 
    # import structlog

    # structlog.configure()

    # @timed()
    # def compute(n:int) -> int :
    #     """Sum 0.. n-1"""
    #     return sum(range(n))
    
    # @timed(label ="bid-compute")
    # def compute_big(n:int) -> int :
    #     """Sum 0.. n-1"""
    #     return sum(range(n))
    
    # print(f"computer result: {compute(1_000_000)}")