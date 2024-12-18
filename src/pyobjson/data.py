"""Python Object JSON Tool pyobjson.json module.

Attributes:
    __author__ (str): Python package template author.
    __email__ (str): Python package template author email.

"""

__author__ = "Wren J. Rudolph for Wrencode, LLC"
__email__ = "dev@wrencode.com"

import json
import sys
from base64 import b64decode, b64encode
from datetime import datetime
from importlib import import_module
from inspect import getfullargspec
from logging import getLogger
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from pyobjson.constants import DELIMITER as DLIM, UNSERIALIZABLE
from pyobjson.utils import (
    derive_custom_callable_value,
    derive_custom_object_key,
)

logger = getLogger(__name__)


def unpack_custom_class_vars(
    custom_class_instance: Any, pyobjson_base_custom_subclasses: List[Type], excluded_attributes: List[str]
) -> Dict[str, Any]:
    """Recursive function to un-type custom class type objects for serialization.

    Args:
        custom_class_instance (Any): Custom Python class instance to be serialized.
        pyobjson_base_custom_subclasses (list[Type]): List of custom Python class subclasses.
        excluded_attributes (list[str]): List of attributes to exclude from serialization. Supports substring matching
            exclusions.

    Returns:
        dict[str, Any]: Dictionary that extracts serializable data from custom objects.

    """
    attributes = dict(vars(custom_class_instance).items())

    # filter out excluded attributes
    if excluded_attributes:
        excluded_att_keys = set()
        for att in attributes.keys():
            for excl_att in excluded_attributes:
                if att.startswith(excl_att):
                    excluded_att_keys.add(att)

        attributes = {att: val for att, val in attributes.items() if att not in excluded_att_keys}

    unpacked = {}
    for k, v in attributes.items():
        unpacked[k] = (
            {
                derive_custom_object_key(v): unpack_custom_class_vars(
                    v, pyobjson_base_custom_subclasses, excluded_attributes
                )
            }
            if type(v) in pyobjson_base_custom_subclasses
            else v
        )

    return unpacked


def extract_typed_key_value_pairs(
    json_dict: Dict[str, Any], pyobjson_base_custom_subclasses_by_key: Dict[str, Type]
) -> Dict[str, Any]:
    """Function to extract both keys and Python object types from specially formatted dictionary keys and make
    their respective values into Python objects of those types.

    Args:
        json_dict (Dict[str, Any]): JSON dictionary that may contain keys in the format type.key_name (e.g.
            path.root_directory) with corresponding string values representing Python objects of that type.
        pyobjson_base_custom_subclasses_by_key (dict[str, Type]): Dictionary with lowercase strings of all subclasses of
            PythonObjectJson as keys and subclasses as values.

    Returns:
        dict[str, Any]: Dictionary with both keys and Python object values derived from specially formatted JSON
            dictionary keys.

    """
    derived_key_value_pairs = {}
    for key, value in json_dict.items():
        # check if value is a custom object that will be deserialized as its respective object type or if key is
        # formatted with a custom delimiter to indicate a Python builtin value type
        if key not in pyobjson_base_custom_subclasses_by_key.keys() and (delimiters := key.count(DLIM)):
            # keys formatted with one custom delimiter indicate a value type
            if delimiters == 1:
                type_category = None
                type_name, key = key.split(DLIM)
            # keys formatted with two custom delimiters indicate a value type category and a value type
            elif delimiters == 2:
                type_category, type_name, key = key.split(DLIM)
            # keys formatted with more than two custom delimiters are not supported by pyobjson
            else:
                raise ValueError(f"JSON data ({key}: {value}) is not compatible with pyobjson.")

            if type_category == "collection":
                if type_name == "dict":
                    # do nothing because JSON supports dictionaries
                    pass
                elif type_name == "list":
                    # do nothing because JSON supports lists
                    pass
                elif type_name == "set":
                    value = set(value)
                elif type_name == "tuple":
                    value = tuple(value)
                elif type_name == "bytes" or type_name == "bytearray":
                    value = b64decode(value)

            elif type_name == "path":  # handle posix paths
                value = Path(value)
            elif type_name == "callable":  # handle callables (functions, methods, etc.)
                # extract the callable components from a value with format module.callable[DLIM]arg1:type1,arg2:type2
                callable_path, callable_args = value.split(DLIM, 1)
                # extract the callable module and name
                module, callable_name = callable_path.rsplit(".", 1)
                # use the callable module and name to import the callable itself and set it to the value
                value = getattr(import_module(module), callable_name)
            elif type_name == "datetime":  # handle datetime objects
                value = datetime.fromisoformat(value)
            else:
                raise ValueError(f"JSON data ({key}: {value}) is not compatible with pyobjson.")

        derived_key_value_pairs[key] = value

    return derived_key_value_pairs


def serialize(obj: Any, pyobjson_base_custom_subclasses: List[Type], excluded_attributes: List[str]) -> Any:
    """Recursive function to serialize custom Python objects into nested dictionaries for conversion to JSON.

    Args:
        obj (Any): Python object to serialize.
        pyobjson_base_custom_subclasses (list[Type]): List of custom Python class subclasses.
        excluded_attributes (list[str]): List of attributes to exclude from serialization. Supports substring matching
            exclusions.

    Returns:
        dict[str, Any]: Serializable dictionary.

    """
    if type(obj) in pyobjson_base_custom_subclasses:
        serializable_obj = {}
        attributes = {
            k: v for k, v in unpack_custom_class_vars(obj, pyobjson_base_custom_subclasses, excluded_attributes).items()
        }

        for att, val in attributes.items():
            if isinstance(val, dict):
                # noinspection PyUnboundLocalVariable
                if (
                    len(val) == 1
                    and (single_key := next(iter(val.keys())))
                    and single_key
                    in [derive_custom_object_key(subclass) for subclass in pyobjson_base_custom_subclasses]
                ):
                    # do nothing because attribute key for custom Python object is already formatted correctly by
                    # unpack custom_class_vars()
                    pass
                else:
                    att = f"collection{DLIM}dict{DLIM}{att}"
            elif isinstance(val, (list, set, tuple, bytes, bytearray)):
                att = f"collection{DLIM}{derive_custom_object_key(val.__class__)}{DLIM}{att}"
            elif isinstance(val, Path):
                att = f"path{DLIM}{att}"
            elif isinstance(val, Callable):
                att = f"callable{DLIM}{att}"
            elif isinstance(val, datetime):
                att = f"datetime{DLIM}{att}"
            else:
                try:
                    json.dumps(val)
                except TypeError as e:
                    if str(e) == f"Object of type {type(val).__name__} is not JSON serializable":
                        att = f"repr{DLIM}{derive_custom_object_key(val.__class__)}"
                    else:
                        att = f"{UNSERIALIZABLE}{DLIM}{derive_custom_object_key(val.__class__)}"

            serializable_obj[att] = serialize(val, pyobjson_base_custom_subclasses, excluded_attributes)

        return {derive_custom_object_key(obj.__class__): serializable_obj}

    elif isinstance(obj, dict):
        return {k: serialize(v, pyobjson_base_custom_subclasses, excluded_attributes) for k, v in obj.items()}

    elif isinstance(obj, (list, set, tuple)):
        return [serialize(v, pyobjson_base_custom_subclasses, excluded_attributes) for v in obj]

    elif isinstance(obj, (bytes, bytearray)):
        return b64encode(obj).decode("utf-8")

    elif isinstance(obj, Path):
        return str(obj)

    elif isinstance(obj, Callable):
        return derive_custom_callable_value(obj)

    elif isinstance(obj, datetime):
        return obj.isoformat()

    else:
        try:
            json.dumps(obj)
        except TypeError as e:
            if str(e) == f"Object of type {type(obj).__name__} is not JSON serializable.":
                return repr(obj)
            else:
                return UNSERIALIZABLE
        return obj


def deserialize(
    json_data: Any,
    pyobjson_base_custom_subclasses_by_key: Dict[str, Type],
    base_class_instance: Optional[Any] = None,
    extra_instance_atts: Optional[Dict[str, Any]] = None,
) -> Any:
    """Recursive function to deserialize JSON into typed data structures for conversion to custom Python objects.

    Args:
        json_data (Any): JSON data to be deserialized.
        pyobjson_base_custom_subclasses_by_key (dict[str, Type]): Dictionary with lowercase strings of all subclasses of
            PythonObjectJson as keys and subclasses as values.
        base_class_instance (Optional[Any]): Target class instance into which to deserialize JSON data.
        extra_instance_atts (Optional[Dict[str, Any]]): Dictionary with extra required class attributes for custom
            Python objects.

    Returns:
        obj (Any): Object deserialized from JSON.
    """
    if not extra_instance_atts:
        extra_instance_atts = {}

    base_subclasses: Dict[str, Type] = pyobjson_base_custom_subclasses_by_key
    if isinstance(json_data, list):  # recursively deserialize all elements if json_data is a list
        return [deserialize(item, base_subclasses, extra_instance_atts=extra_instance_atts) for item in json_data]
    elif isinstance(json_data, dict):  # recursively deserialize all values if json_data is a dictionary
        # check if json_data is a dict with only one key that matches a custom subclass for object derivation
        # noinspection PyUnboundLocalVariable
        if len(json_data) == 1 and (single_key := next(iter(json_data.keys()))) and single_key in base_subclasses:
            # noinspection PyPep8Naming
            ClassObject = base_subclasses[single_key]  # retrieve custom subclass
            class_args = getfullargspec(ClassObject.__init__).args[1:]  # get __init__ arguments for custom subclass
            class_instance_attributes: Dict[str, Any] = json_data[single_key]  # get JSON to be deserialized

            if ClassObject == base_class_instance.__class__:
                # avoid creating a new class instance if an existing base class instance has been provided
                class_instance = base_class_instance
            else:
                # extract original attribute names from pyobjson formatted attribute keys
                extracted_class_instance_atts = {att.split(DLIM)[-1] for att in class_instance_attributes.keys()}
                # check if any required instance attributes are missing from the deserialized data
                if missing_instances_atts := set(class_args).difference(extracted_class_instance_atts):
                    if set(extra_instance_atts.keys()).issuperset(missing_instances_atts):
                        class_instance_attributes.update(extra_instance_atts)
                    else:
                        logger.warning(
                            f"Missing required instance attributes "
                            f'"{missing_instances_atts.difference(set(extra_instance_atts.keys()))}" for custom '
                            f'class "{ClassObject.__name__}".'
                        )
                        sys.exit(1)

                # create an instance of the custom subclass using the __init__ arguments
                class_instance = ClassObject(
                    **{
                        k: deserialize(v, base_subclasses, extra_instance_atts=extra_instance_atts)
                        for k, v in extract_typed_key_value_pairs(class_instance_attributes, base_subclasses).items()
                        if k in class_args
                    }
                )

            # assign the remaining class attributes to the class instance
            # noinspection PyUnresolvedReferences
            vars(class_instance).update(
                {
                    k: deserialize(v, base_subclasses, extra_instance_atts=extra_instance_atts)
                    for k, v in extract_typed_key_value_pairs(class_instance_attributes, base_subclasses).items()
                }
            )

            return class_instance if not base_class_instance else None
        else:
            return {
                k: deserialize(v, base_subclasses, extra_instance_atts=extra_instance_atts)
                for k, v in extract_typed_key_value_pairs(json_data, base_subclasses).items()
            }
    else:
        return json_data
