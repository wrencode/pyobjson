"""Python Object JSON Tool pyobjson.utils module.

Attributes:
    __author__ (str): Python package template author.
    __email__ (str): Python package template author email.

"""

__author__ = "Wren J. Rudolph for Wrencode, LLC"
__email__ = "dev@wrencode.com"

from inspect import getfullargspec
from re import compile, error
from typing import Callable, List, Type, Union

from pyobjson.constants import DELIMITER as DLIM


def validate_regex(regex: Union[str, List[str]]) -> None:
    """Utility function to check if a regular expression is valid.

    Args:
        regex (Union[str, list[str]]): Regular expression string or list of strings to validate.

    Returns:
        None

    """
    if isinstance(regex, str):
        regex = [regex]

    invalid_regex = []
    for expr in regex:
        try:
            compile(expr)
        except error:
            invalid_regex.append(expr)

    if invalid_regex:
        raise ValueError(f"Invalid regex provided: {invalid_regex}")


def derive_custom_object_key(custom_object: Union[Type, Callable], as_lower: bool = True) -> str:
    """Utility function to derive a key for a custom object representing the fully qualified name of that object.

    Args:
        custom_object (Type): The custom object for which to derive a key.
        as_lower (bool, optional): Whether the derived key should be returned as a lower case string.

    Returns:
        str: The fully qualified name of the object in lowercase (e.g. module.submodule.object).

    """
    if not hasattr(custom_object, "__qualname__"):
        custom_object = custom_object.__class__

    # avoid including module if no module exists or the object is in the Python builtins
    if (obj_module := getattr(custom_object, "__module__", None)) and obj_module != "builtins":
        return (
            f"{obj_module.lower()}.{custom_object.__qualname__.lower()}"
            if as_lower
            else f"{obj_module}.{custom_object.__qualname__}"
        )
    else:
        return custom_object.__qualname__.lower() if as_lower else custom_object.__qualname__


def derive_custom_callable_value(custom_callable: Callable) -> str:
    """Utility function to derive a string value from a custom callable object.

    Args:
        custom_callable (Callable): Custom callable object for which to derive a string representation value.

    Returns:
        str: A string representing the custom callable object that can be used to import and call that object.

    """
    arg_spec_str = ",".join(
        [
            f"{k}:{v.__name__ if hasattr(v, '__name__') else v.__class__.__name__}"
            for k, v in getfullargspec(custom_callable).annotations.items()
        ]
    )
    return f"{derive_custom_object_key(custom_callable)}{DLIM}{arg_spec_str}"


def get_nested_subclasses(custom_class: Type) -> List[Type]:
    """Recursive utility function to retrieve all nested subclasses of a custom class.

    Args:
        custom_class (Type): Custom class from which to recursively retrieve all nested subclasses.

    Returns:
        list(Type): A list of custom classes derived from the subclass tree of a custom class.

    """
    custom_subclasses = custom_class.__subclasses__()
    for custom_subclass in custom_subclasses:
        custom_subclasses.extend(get_nested_subclasses(custom_subclass))
    return list(set(custom_subclasses))
