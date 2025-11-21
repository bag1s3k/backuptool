import inspect
from functools import wraps
from typing import get_args, get_origin, Literal


def check_params(allowed: dict): # TODO: option to combinate multiple requirements

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """ Check kwargs if it matches with default keys
                :param kwargs: variable to check
                """
            keys_to_check, wrong_keys, wrong_values = set(), set(), set()

            # Get function's key parameters cuz these aren't in allowed
            sig = inspect.signature(func)
            ignore_keys = set(sig.parameters.keys())

            for arg in args:
                # Check keys in case it's set
                if isinstance(arg, set):
                    if wrong_keys := [k for k in arg if k not in set(allowed)]:
                        raise ValueError(f"Unknown keys: {wrong_keys} . Allowed: {list(set(allowed) - set(arg))}")

                if isinstance(arg, dict):
                    # Check keys in case it's dict
                    if wrong_keys := [k for k in set(arg) if k not in set(allowed)]:
                        raise ValueError(f"Unknown keys: {wrong_keys} . Allowed: {list(set(allowed) - set(arg))}")

                    # Check values
                    for arg_key, arg_value in arg.items():
                        # Are the *args an allowed dictionary? (no need to check)
                        if arg_value == allowed[arg_key]:
                            break

                        # Check generic
                        if which_generic := check_generic_type(allowed[arg_key]):
                            # Literal (Literal["item", "item"])
                            if which_generic == 1:
                                wrong_values |= {arg_value} if arg_value not in get_args(allowed[arg_key]) else set()
                            # List (list[str])
                            if which_generic == 2:
                                wrong_values |= {t for t in arg_value if not isinstance(t, get_args(allowed[arg_key])[0])}

                            continue

                        # Check remaining values
                        try:
                            if not isinstance(arg_value, allowed[arg_key]):
                                wrong_values.add(arg_value)
                        except:
                            raise Exception(f"Invalid data: {arg_value}")

                # Raise ValueError in case if keys aren't according to allowed
                if wrong_keys := [k for k in keys_to_check - ignore_keys if k not in set(allowed)]:
                    raise ValueError(f"Unknown keys: {wrong_keys} . Allowed: {list(set(allowed) - set(arg))}")
                if wrong_values and wrong_values != True:
                    raise ValueError(f"Unknown: {wrong_values}. Allowed: {...}")

            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_generic_type(value_type):
    """ Is value generic?
        :param value_type: allowed type
        :return integer which indicate type of literal"""
    origin = get_origin(value_type)
    if origin is Literal:
        return 1
    elif origin is list:
        return 2
    else:
        return 0