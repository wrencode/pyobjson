"""Pytest test for Python Object JSON Tool code.

Note:
    Tests pyobjson.base module.

"""

__author__ = "Wren J. Rudolph for Wrencode, LLC"
__email__ = "dev@wrencode.com"

from pathlib import Path

from conftest import FirstClass, FirstClassToMongo
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


class TestPythonObjectJson:
    """Pytest class for PythonObjectJson functionality."""

    def test_serialization_to_json_string(self, first_class_with_nested_child_classes, first_class_json_str):
        # confirm conftest.FirstClass instance as a JSON string is equal to the conftest FirstClass JSON string
        assert first_class_with_nested_child_classes.to_json_str() == first_class_json_str

    def test_deserialization_from_json_string(self, first_class_with_nested_child_classes, first_class_json_str):
        # create new FirstClass instance with all empty/None arguments
        first_class_instance = FirstClass({}, [], None, None, None, None, None, None)

        # confirm new empty FirstClass instance is not equivalent to conftest.FirstClass instance
        assert first_class_instance != first_class_with_nested_child_classes

        # load conftest FirstClass JSON string to new empty FirstClass instance
        first_class_instance.from_json_str(first_class_json_str)

        # confirm newly created FirstClass instance loaded from JSON is equivalent to conftest.FirstClass instance
        assert first_class_instance == first_class_with_nested_child_classes


class TestPythonObjectJsonToMongo:
    """Pytest class for PythonObjectJsonToMongo functionality."""

    def test_serialization_to_json_string(
        self, first_class_to_mongo_with_nested_child_classes, first_class_to_mongo_json_str
    ):
        # confirm conftest.FirstClassToMongo instance as a JSON string is equal to the conftest FirstClassToMongo JSON
        # string
        assert first_class_to_mongo_with_nested_child_classes.to_json_str() == first_class_to_mongo_json_str

    def test_deserialization_from_json_string(
        self, first_class_to_mongo_with_nested_child_classes, first_class_to_mongo_json_str, mongo_connection_params
    ):
        # create new FirstClassToMongo instance with all empty/None arguments
        first_class_to_mongo_instance = FirstClassToMongo(
            {}, [], None, None, None, None, None, None, **mongo_connection_params
        )

        # confirm new empty FirstClassToMongo instance is not equivalent to conftest.FirstClassToMongo instance
        assert first_class_to_mongo_instance != first_class_to_mongo_with_nested_child_classes

        # load conftest FirstClassToMongo JSON string to new empty FirstClass instance
        first_class_to_mongo_instance.from_json_str(first_class_to_mongo_json_str)

        # confirm newly created FirstClassToMongo instance loaded from JSON is equivalent to conftest.FirstClassToMongo
        # instance
        assert first_class_to_mongo_instance == first_class_to_mongo_with_nested_child_classes
