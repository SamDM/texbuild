import os
from contextlib import contextmanager
from typing import Optional, TypeVar


A = TypeVar("A")


def default(x: Optional[A], default_value: A) -> A:
    if x is None:
        return default_value
    else:
        return x


def makedir(*path, exists_ok=False, recursive=False, mode=0o777):
    d = os.path.join(*path)
    if recursive:
        os.makedirs(d, exist_ok=exists_ok, mode=mode)
    else:
        try:
            os.mkdir(d, mode=mode)
        except FileExistsError as e:
            if exists_ok:
                pass
            else:
                raise e
    return d


@contextmanager
def having_cwd(directory: str):
    """
    Run a block of code with a different cwd, once the code finishes the current cwd is restored.

    :param directory: Which cwd to use while running the code.
    """
    cur_dir = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(cur_dir)
