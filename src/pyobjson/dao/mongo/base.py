"""Python Object JSON Tool pyobjson.dao.mongo module.

Attributes:
    __author__ (str): Python package template author.
    __email__ (str): Python package template author email.

"""

__author__ = "Wren J. Rudolph for Wrencode, LLC"
__email__ = "dev@wrencode.com"

import os
import sys
from logging import getLogger
from typing import Any, Dict
from urllib.parse import quote_plus

from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

from pyobjson.base import PythonObjectJson
from pyobjson.data import deserialize, serialize

logger = getLogger(__name__)


class PythonObjectJsonToMongo(PythonObjectJson):
    """PythonObjectJson subclass with built-in save/load functionality to/from MongoDB."""

    def __init__(self, mongo_host: str, mongo_port: int, mongo_database: str, mongo_user: str, mongo_password: str):
        super().__init__()

        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_database = mongo_database
        self.mongo_user = mongo_user
        self.mongo_password = mongo_password

    def _get_mongo_client(self):
        """Create a MongoDB connection.

        Returns:
            MongoClient: A pymongo MongoClient instance.

        """
        return MongoClient(
            f"mongodb://{quote_plus(self.mongo_user)}:{quote_plus(self.mongo_password)}"
            f"@{self.mongo_host}:{self.mongo_port}/{self.mongo_database}"
            f"?authSource=admin",
            serverSelectionTimeoutMS=5000,
        )

    def _validate_or_create_collection(self, mongo_collection: str) -> Collection:
        """Create a pymongo Database instance from a pymongo MongoClient, check if a given MongoDB collection exists,
        and create the collection if it does not exist.

        Args:
            mongo_collection (str): The name of the MongoDB collection for which to check existence or create.

        Returns:
            Collection: A pymongo Collection instance.

        """
        db = self._get_mongo_client()[self.mongo_database]
        try:
            db.validate_collection(mongo_collection)
        except ServerSelectionTimeoutError:
            logger.warning(f'Unable to connect to MongoDB server at "{self.mongo_host}:{self.mongo_port}".')
            sys.exit(1)
        except OperationFailure:
            logger.debug(f'MongoDB collection "{mongo_collection}" does not exist.')
            db.create_collection(mongo_collection)

        return db.get_collection(mongo_collection)

    def serialize(self) -> Dict[str, Any]:
        """Create a serializable dictionary from the class instance that excludes MongoDB-related attributes.

        Returns:
            dict[str, Any]: Serializable dictionary representing the class instance without MongoDB-related attributes.

        """
        return serialize(self, list(self._base_subclasses().values()), ["mongo_"])

    def deserialize(self, serializable_dict: Dict[str, Any]) -> Any:
        """Load data to a class instance from a serializable dictionary and add in MongoDB-related attributes.

        Args:
            serializable_dict (dict[str, Any]): Serializable dictionary representing the class instance.

        Returns:
            Any: Class instance deserialized from data dictionary including MongoDB-related attributes.

        """
        extra_instance_attributes = {
            "mongo_host": self.mongo_host,
            "mongo_port": self.mongo_port,
            "mongo_database": self.mongo_database,
            "mongo_user": self.mongo_user,
            "mongo_password": self.mongo_password,
        }
        return deserialize(
            serializable_dict,
            self._base_subclasses(),
            base_class_instance=self,
            extra_instance_atts=extra_instance_attributes,
        )

    def save_to_mongo(self, mongo_collection: str) -> str:
        """Save the custom Python object to a specified MongoDB collection.

        Args:
            mongo_collection (str): The name of the MongoDB collection into which to save the custom Python object.

        Returns:
            The MongoDB document ID to which the custom Python object JSON was saved.

        """
        collection = self._validate_or_create_collection(mongo_collection)
        return str(collection.insert_one({"custom_class": self.serialize()}).inserted_id)

    def load_from_mongo(self, mongo_collection: str, document_id: str) -> None:
        """Load the JSON values from a specified MongoDB document ID to the custom Python object from a specified
        MongoDB collection.

        Args:
            mongo_collection (str): The name of the MongoDB collection from which to load the custom Python object data.
            document_id (str): The MongoDB document ID from which the custom Python object JSON was loaded.

        Returns:
            None

        """
        collection = self._validate_or_create_collection(mongo_collection)

        custom_class_dict = collection.find_one({"_id": ObjectId(document_id)}).get("custom_class")

        self.deserialize(custom_class_dict)


if __name__ == "__main__":
    from pathlib import Path

    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

    class CustomSecondClassToMongo(PythonObjectJsonToMongo):
        def __init__(
            self,
            message: str,
            mongo_host: str,
            mongo_port: int,
            mongo_database: str,
            mongo_user: str,
            mongo_password: str,
        ):
            super().__init__(mongo_host, mongo_port, mongo_database, mongo_user, mongo_password)
            self.message = message

        def set_message(self, message: str):
            self.message = message

    class CustomFirstClassToMongo(PythonObjectJsonToMongo):
        def __init__(
            self,
            first_class_message: str,
            second_class_message: str,
            mongo_host: str,
            mongo_port: int,
            mongo_database: str,
            mongo_user: str,
            mongo_password: str,
        ):
            super().__init__(mongo_host, mongo_port, mongo_database, mongo_user, mongo_password)
            self.message = first_class_message
            self.custom_second_class_to_mongo = CustomSecondClassToMongo(
                second_class_message, mongo_host, mongo_port, mongo_database, mongo_user, mongo_password
            )

        def set_messages(self, first_class_message: str, second_class_message: str):
            self.message = first_class_message
            self.custom_second_class_to_mongo.set_message(second_class_message)

    obj_to_mongo = CustomFirstClassToMongo(
        "Hello, World!",
        "Hello, World again!",
        mongo_host=os.environ.get("MONGO_HOST"),
        mongo_port=int(os.environ.get("MONGO_PORT")),
        mongo_database=os.environ.get("MONGO_DATABASE"),
        mongo_user=os.environ.get("MONGO_ADMIN_USER"),
        mongo_password=os.environ.get("MONGO_ADMIN_PASS"),
    )
    print(obj_to_mongo)
    print("-" * 100)

    saved_document_id = obj_to_mongo.save_to_mongo(os.environ.get("MONGO_COLLECTION"))

    obj_to_mongo.set_messages("", "")
    print(obj_to_mongo)
    print("-" * 100)

    obj_to_mongo.load_from_mongo(os.environ.get("MONGO_COLLECTION"), saved_document_id)
    print(obj_to_mongo)
    print("-" * 100)
