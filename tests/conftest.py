"""Pytest top-level conftest.py."""

__author__ = "Wren J. Rudolph for Wrencode, LLC"
__email__ = "dev@wrencode.com"

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple

from pytest import fixture

from pyobjson.base import PythonObjectJson
from pyobjson.dao.mongo import PythonObjectJsonToMongo


def external_function(param1: str, param2: str):
    """Function for testing."""
    return f"{param1}.{param2}"


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
        self.first_class_set: Set[str] = first_class_set
        self.first_class_tuple: Tuple[str] = first_class_tuple
        self.first_class_bytes: bytes = first_class_bytes
        self.first_class_file: Path = first_class_file
        self.first_class_external_function: Optional[Callable] = first_class_external_function
        self.first_class_datetime: datetime = first_class_datetime


class FirstClassToMongo(PythonObjectJsonToMongo):
    def __init__(
        self,
        second_class_dict: Dict[str, SecondClass],
        second_class_list: List[SecondClass],
        first_class_set: Optional[Set[str]],
        first_class_tuple: Optional[Tuple[str]],
        first_class_bytes: Optional[bytes],
        first_class_file: Optional[Path],
        first_class_external_function: Optional[Callable],
        first_class_datetime: Optional[datetime],
        mongo_host: str,
        mongo_port: int,
        mongo_database: str,
        mongo_user: str,
        mongo_password: str,
    ):
        super().__init__(mongo_host, mongo_port, mongo_database, mongo_user, mongo_password)
        self.second_class_dict: Dict[str, SecondClass] = second_class_dict
        self.second_class_list: List[SecondClass] = second_class_list
        self.first_class_set: Set[str] = first_class_set
        self.first_class_tuple: Tuple[str] = first_class_tuple
        self.first_class_bytes: bytes = first_class_bytes
        self.first_class_file: Path = first_class_file
        self.first_class_external_function: Optional[Callable] = first_class_external_function
        self.first_class_datetime: datetime = first_class_datetime


@fixture(scope="module")
def mongo_connection_params() -> Dict[str, str]:
    """Create dictionary of MongoDB connection parameters.

    Returns:
        dict[str, str]: MongoDB connection parameters.

    """
    return {
        "mongo_host": os.environ.get("MONGO_HOST", "localhost"),
        "mongo_port": int(os.environ.get("MONGO_PORT", 27017)),
        "mongo_database": os.environ.get("MONGO_DATABASE", "pyobjson"),
        "mongo_user": os.environ.get("MONGO_ADMIN_USER", "pyobjson_admin"),
        "mongo_password": os.environ.get("MONGO_ADMIN_PASS", "<PASSWORD>"),
    }


@fixture(scope="module")
def first_class_with_nested_child_classes() -> FirstClass:
    """Create ParentClass instance for testing.

    Returns:
        FirstClass: Instance of ParentClass.

    """
    return FirstClass(
        {"second_class_1": SecondClass([ThirdClass("test_third_class_argument_in_dict")])},
        [SecondClass([ThirdClass("test_third_class_argument_in_list")])],
        {"test_first_class_collection_element"},
        ("test_first_class_collection_element",),
        b"test_first_class_collection_element",
        Path(__name__),
        external_function,
        datetime(2024, 1, 1, 0, 0, 0),
    )


@fixture(scope="module")
def first_class_to_mongo_with_nested_child_classes(mongo_connection_params) -> FirstClassToMongo:
    """Create FirstClassToMongo instance for testing.

    Returns:
        FirstClassToMongo: Instance of FirstClassToMongo.

    """
    return FirstClassToMongo(
        {"second_class_1": SecondClass([ThirdClass("test_third_class_argument_in_dict")])},
        [SecondClass([ThirdClass("test_third_class_argument_in_list")])],
        {"test_first_class_collection_element"},
        ("test_first_class_collection_element",),
        b"test_first_class_collection_element",
        Path(__name__),
        external_function,
        datetime(2024, 1, 1, 0, 0, 0),
        **mongo_connection_params,
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
                "collection:dict.second_class_dict": {
                    "second_class_1": {
                        "conftest.secondclass": {
                            "collection:list.third_class_list": [
                                {"conftest.thirdclass": {"third_class_param": "test_third_class_argument_in_dict"}}
                            ],
                            "collection:dict.third_class_list_dict": {
                                "third_class_list_1": [
                                    {"conftest.thirdclass": {"third_class_param": "test_third_class_argument_in_dict"}}
                                ]
                            },
                        }
                    }
                },
                "collection:list.second_class_list": [
                    {
                        "conftest.secondclass": {
                            "collection:list.third_class_list": [
                                {"conftest.thirdclass": {"third_class_param": "test_third_class_argument_in_list"}}
                            ],
                            "collection:dict.third_class_list_dict": {
                                "third_class_list_1": [
                                    {"conftest.thirdclass": {"third_class_param": "test_third_class_argument_in_list"}}
                                ]
                            },
                        }
                    }
                ],
                "collection:set.first_class_set": ["test_first_class_collection_element"],
                "collection:tuple.first_class_tuple": ["test_first_class_collection_element"],
                "collection:bytes.first_class_bytes": "dGVzdF9maXJzdF9jbGFzc19jb2xsZWN0aW9uX2VsZW1lbnQ=",
                "path.first_class_file": "conftest",
                "callable.first_class_external_function": "conftest.external_function::param1:str,param2:str",
                "datetime.first_class_datetime": "2024-01-01T00:00:00",
            }
        },
        ensure_ascii=False,
        indent=2,
    )


@fixture(scope="module")
def first_class_to_mongo_json_str(first_class_json_str) -> str:
    """Create JSON string from FirstClassToMongo instance for testing.

    Returns:
        str: JSON string derived from serialized FirstClassToMongo instance.

    """
    first_class_json = json.loads(first_class_json_str)

    return json.dumps(
        {"conftest.firstclasstomongo": first_class_json["conftest.firstclass"]}, ensure_ascii=False, indent=2
    )
