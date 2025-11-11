import inspect
from functools import wraps


def check_kwargs(*allowed_params: set):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """ Check kwargs if it matches with default keys
                :param kwargs: variable to check
                """

            # Get parameters
            sig = inspect.signature(func)
            func_params = set(sig.parameters.keys())

            # If arg equals to set that means it's another params, add to review
            param_to_check = set()
            for arg in args:
                if isinstance(arg, set):
                    param_to_check |= arg

            if unknown_params := set(kwargs.keys() | param_to_check) - set(*allowed_params) - func_params:
                raise ValueError(f"Unknown params: {[*unknown_params]}. Allowed: {[*allowed_params]}")

            return func(*args, **kwargs)
        return wrapper
    return decorator