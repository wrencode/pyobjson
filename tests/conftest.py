"""Pytest top-level conftest.py."""

__author__ = "Wren J. Rudolph for Wrencode, LLC"
__email__ = "dev@wrencode.com"

import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple

from pytest import fixture

from pyobjson.base import PythonObjectJson
from pyobjson.constants import DELIMITER as DLIM


def ext_func(param_1: str, param_2: str):
    """Function external_function for testing."""
    return f"{param_1}.{param_2}"


class ThirdClass(PythonObjectJson):
    """ThirdClass for testing."""

    def __init__(self, third_class_param: str):
        super().__init__()
        self.third_class_param: str = third_class_param


class SecondClass(PythonObjectJson):
    """SecondClass for testing."""

    def __init__(self, third_class_list: List[ThirdClass]):
        super().__init__()
        self.third_class_list: List[ThirdClass] = third_class_list
        self.third_class_list_dict: Dict[str, List[ThirdClass]] = {"third_class_list_1": third_class_list}


class FirstClass(PythonObjectJson):
    """FirstClass for testing."""

    def __init__(
        self,
        second_class_dict: Dict[str, SecondClass],
        second_class_list: List[SecondClass],
        first_class_attribute: Optional[str],
        first_class_set: Optional[Set[str]],
        first_class_tuple: Optional[Tuple[str]],
        first_class_bytes: Optional[bytes],
        first_class_file: Optional[Path],
        first_class_external_function: Optional[Callable],
        first_class_datetime: Optional[datetime],
    ):
        super().__init__()
        self.second_class_dict: Dict[str, SecondClass] = second_class_dict
        self.second_class_list: List[SecondClass] = second_class_list
        self.first_class_attribute: str = first_class_attribute
        self.first_class_set: Set[str] = first_class_set
        self.first_class_tuple: Tuple[str] = first_class_tuple
        self.first_class_bytes: bytes = first_class_bytes
        self.first_class_file: Path = first_class_file
        self.first_class_external_function: Optional[Callable] = first_class_external_function
        self.first_class_datetime: datetime = first_class_datetime


@fixture(scope="module")
def external_function() -> Callable:
    """External function for testing."""
    return ext_func


@fixture(scope="module")
def first_class_with_empty_arguments() -> FirstClass:
    """Create FirstClass instance with empty arguments for testing.

    Returns:
        FirstClass: Instance of FirstClass with all empty arguments.

    """
    return FirstClass({}, [], None, None, None, None, None, None, None)


@fixture(scope="module")
def first_class_with_nested_child_classes(external_function) -> FirstClass:
    """Create FirstClass instance for testing.

    Returns:
        FirstClass: Instance of FirstClass.

    """
    return FirstClass(
        {"second_class_1": SecondClass([ThirdClass("test_third_class_argument_in_dict")])},
        [SecondClass([ThirdClass("test_third_class_argument_in_list")])],
        "test_first_class_attribute_string",
        {"test_first_class_collection_element"},
        ("test_first_class_collection_element",),
        b"test_first_class_collection_element",
        Path(__name__),
        external_function,
        datetime(2024, 1, 1, 0, 0, 0),
    )


@fixture(scope="module")
def first_class_json_str() -> str:
    """Create JSON string from FirstClass instance for testing.

    Returns:
        str: JSON string derived from serialized FirstClass instance.

    """
    return json.dumps(
        {
            "conftest.firstclass": {
                f"collection{DLIM}dict{DLIM}second_class_dict": {
                    "second_class_1": {
                        "conftest.secondclass": {
                            f"collection{DLIM}list{DLIM}third_class_list": [
                                {"conftest.thirdclass": {"third_class_param": "test_third_class_argument_in_dict"}}
                            ],
                            f"collection{DLIM}dict{DLIM}third_class_list_dict": {
                                "third_class_list_1": [
                                    {"conftest.thirdclass": {"third_class_param": "test_third_class_argument_in_dict"}}
                                ]
                            },
                        }
                    }
                },
                f"collection{DLIM}list{DLIM}second_class_list": [
                    {
                        "conftest.secondclass": {
                            f"collection{DLIM}list{DLIM}third_class_list": [
                                {"conftest.thirdclass": {"third_class_param": "test_third_class_argument_in_list"}}
                            ],
                            f"collection{DLIM}dict{DLIM}third_class_list_dict": {
                                "third_class_list_1": [
                                    {"conftest.thirdclass": {"third_class_param": "test_third_class_argument_in_list"}}
                                ]
                            },
                        }
                    }
                ],
                "first_class_attribute": "test_first_class_attribute_string",
                f"collection{DLIM}set{DLIM}first_class_set": ["test_first_class_collection_element"],
                f"collection{DLIM}tuple{DLIM}first_class_tuple": ["test_first_class_collection_element"],
                f"collection{DLIM}bytes{DLIM}first_class_bytes": "dGVzdF9maXJzdF9jbGFzc19jb2xsZWN0aW9uX2VsZW1lbnQ=",
                f"path{DLIM}first_class_file": "conftest",
                f"callable{DLIM}first_class_external_function": f"conftest.ext_func{DLIM}param_1:str,param_2:str",
                f"datetime{DLIM}first_class_datetime": "2024-01-01T00:00:00",
            }
        },
        ensure_ascii=False,
        indent=2,
    )
