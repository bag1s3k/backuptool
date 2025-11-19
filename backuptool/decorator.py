import inspect
from functools import wraps


def check_params(allowed: dict): # TODO: option to combinate multiple requirements

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """ Check kwargs if it matches with default keys
                :param kwargs: variable to check
                """

            # Get parameter names (excluding **kwargs)
            sig = inspect.signature(func)
            func_params = set(sig.parameters.keys())

            param_to_check = set()
            wrong_types = dict()
            print(args)
            for arg in args:
                if isinstance(arg, set):
                    param_to_check |= arg
                elif isinstance(arg, dict):
                    param_to_check |= arg.keys()
                    for arg_key, arg_value in arg.items():
                        # print(f"KEY: {arg_key} VALUE: {arg_value} TYPE: {type(arg_value)}")
                        if isinstance(arg_value, str) and isinstance(allowed[arg_key], list):
                            if arg_value not in allowed[arg_key]:
                                wrong_types = {arg_key : arg_value}
                        if isinstance(arg_value, list):
                            if specific_wrongs := [item for item in arg_value if not isinstance(item, str)]:
                                wrong_types |= {arg_key : specific_wrongs}
            wrong_keys = set(kwargs.keys() | param_to_check) - set(allowed) - func_params # Set of wrong keys (spelling)
            if wrong_keys:
                raise ValueError(f"Unknown params: {[*wrong_keys]}. Allowed: {allowed}")
            elif wrong_types:
                tmp = wrong_types.keys() & allowed.keys()
                raise ValueError(f"Invalid data types: {" ".join(f"{k}={v}" for k,v in wrong_types.items())}. Allowed: {" ".join(f"{k}={v}" for k,v in allowed.items() if k in tmp)}")

            return func(*args, **kwargs)
        return wrapper
    return decorator

# CONTINUE
# - discovery that list of allowed value e.g ["zip", "tar"] is never used in list it's always 1 string
# - list (that means [str])
# - value (that means ["zip", "tar"]) values have to exactly match with that's in list