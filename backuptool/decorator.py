import inspect
from functools import wraps


def check_kwargs(allowed_params: dict):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """ Check kwargs if it matches with default keys
                :param kwargs: variable to check
                """
            sig = inspect.signature(func)
            function_params = set(sig.parameters.keys())

            allowed_params_set = set(allowed_params.keys())
            if unknown_params := set(kwargs.keys()) - function_params  - allowed_params_set:
                raise ValueError(f"Unknown params: {unknown_params}. Allowed: {[*allowed_params.keys()]}")

            return func(*args, **kwargs)
        return wrapper
    return decorator