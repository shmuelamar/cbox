import pytest

from cbox import executors


def test_get_func_executor_undecorated_func():
    def f():
        pass

    with pytest.raises(ValueError):
        executors.get_func_executor(f)
