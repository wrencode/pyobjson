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
from typing import Any, Dict, Optional, Union
from urllib.parse import quote_plus

from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection, ReturnDocument
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

from pyobjson.base import PythonObjectJson
from pyobjson.data import deserialize, serialize

logger = getLogger(__name__)


class PythonObjectJsonToMongo(PythonObjectJson):
    """PythonObjectJson subclass with built-in save/load functionality to/from MongoDB."""

    def __init__(self, mongo_host: str, mongo_port: int, mongo_database: str, mongo_user: str, mongo_password: str):
        super().__init__()

        self.mongo_host: str = mongo_host
        self.mongo_port: int = mongo_port
        self.mongo_database: str = mongo_database
        self.mongo_user: str = mongo_user
        self.mongo_password: str = mongo_password

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

    @staticmethod
    def _validate_document_id(mongo_document_id: Union[ObjectId, bytes, str]) -> None:
        """This method checks to see if a given MongoDB document ID is valid.

        Args:
            mongo_document_id (Union[ObjectId, bytes, str]): The MongoDB document ID to validate.

        Returns:
            None

        """
        if not ObjectId.is_valid(mongo_document_id):
            logger.error(
                f'Invalid MongoDb document ID "{mongo_document_id}". MongoDB requires document ObjectId values to '
                f"be either 12 bytes long or a 24-character hexadecimal string."
            )
            sys.exit(1)

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

    def save_to_mongo(
        self, mongo_collection: str, mongo_document_id: Optional[Union[ObjectId, bytes, str]] = None
    ) -> ObjectId:
        """Save the custom Python object to a specified MongoDB collection.

        Args:
            mongo_collection (str): The name of the MongoDB collection into which to save the custom Python object.
            mongo_document_id (Optional[ObjectId, bytes, str], optional): MongoDB document ID. Defaults to None, which
                will result in MongoDB automatically generating a unique document ID.

        Returns:
            ObjectId: The MongoDB document ID to which the custom Python object JSON was saved.

        """
        # only validate MongoDB document ID if one is provided
        if mongo_document_id:
            self._validate_document_id(mongo_document_id)

        collection = self._validate_or_create_collection(mongo_collection)
        document: Dict[str, Any] = collection.find_one_and_update(
            {"_id": ObjectId(mongo_document_id) if mongo_document_id else ObjectId()},
            {"$set": {"custom_class": self.serialize()}},
            projection={"_id": True},  # filter out all fields besides the document ID
            upsert=True,  # create a new document if it does not exist, otherwise update the existing document
            return_document=ReturnDocument.AFTER,  # return the updated or created document after the update/creation
        )
        return document["_id"]

    def load_from_mongo(self, mongo_collection: str, mongo_document_id: Union[ObjectId, bytes, str]) -> None:
        """Load the JSON values from a specified MongoDB document ID to the custom Python object from a specified
        MongoDB collection.

        Args:
            mongo_collection (str): The name of the MongoDB collection from which to load the custom Python object data.
            mongo_document_id (Union[ObjectId, bytes, str]): The MongoDB document ID from which the custom Python object
                JSON was loaded.

        Returns:
            None

        """
        self._validate_document_id(mongo_document_id)

        # get MongoDb collection
        collection = self._validate_or_create_collection(mongo_collection)

        self.deserialize(collection.find_one({"_id": ObjectId(mongo_document_id)}).get("custom_class"))


if __name__ == "__main__":
    from logging import INFO
    from pathlib import Path

    from dotenv import load_dotenv

    from pyobjson import get_logger

    load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

    logger = get_logger(__file__, INFO)

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

    custom_class_to_mongo = CustomFirstClassToMongo(
        "Hello, World!",
        "Hello, World again!",
        mongo_host=os.environ.get("MONGO_HOST"),
        mongo_port=int(os.environ.get("MONGO_PORT")),
        mongo_database=os.environ.get("MONGO_DATABASE"),
        mongo_user=os.environ.get("MONGO_ADMIN_USER"),
        mongo_password=os.environ.get("MONGO_ADMIN_PASS"),
    )
    logger.info(custom_class_to_mongo)

    saved_document_id = custom_class_to_mongo.save_to_mongo(os.environ.get("MONGO_COLLECTION"))
    # saved_document_id = custom_class_to_mongo.save_to_mongo(
    #     os.environ.get("MONGO_COLLECTION"), b"000000000000"
    # )  # 12 bytes
    # saved_document_id = custom_class_to_mongo.save_to_mongo(
    #     os.environ.get("MONGO_COLLECTION"), "abababababababababababab"
    # )  # 24-character hexadecimal string

    custom_class_to_mongo.set_messages("", "")
    logger.info(custom_class_to_mongo)

    custom_class_to_mongo.load_from_mongo(os.environ.get("MONGO_COLLECTION"), saved_document_id)
    logger.info(custom_class_to_mongo)
