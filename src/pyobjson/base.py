"""Python Object JSON Tool pyobjson.base module.

Attributes:
    __author__ (str): Python package template author.
    __email__ (str): Python package template author email.

"""

__author__ = "Wren J. Rudolph for Wrencode, LLC"
__email__ = "dev@wrencode.com"

import json
from inspect import getfullargspec
from pathlib import Path
from re import search
from typing import Any, Dict, List, Optional, Type

from pyobjson.data import deserialize, serialize
from pyobjson.utils import derive_custom_object_key, get_nested_subclasses, validate_regex


class PythonObjectJson(object):
    """Base Python Object with JSON serialization and deserialization compatibility."""

    def __init__(
        self,
        excluded_attributes: Optional[List[str]] = None,
        class_keys_for_excluded_attributes: Optional[List[str]] = None,
        extra_attributes: Optional[List[str]] = None,
        class_keys_for_extra_attributes: Optional[List[str]] = None,
        **kwargs,
    ):
        """Instantiate the PythonObjectJson class with all keyword arguments.

        Args:
            excluded_attributes (Optional[list[str]], optional): List of Python class attributes to exclude during
                serialization. Defaults to None.
            class_keys_for_excluded_attributes (Optional[list[str]], optional): List of Python class keys for which to
                exclude attributes provided in excluded_attributes during serialization. If no class keys are provided,
                all attributes provided in excluded_attributes will be excluded from all classes during serialization.
            extra_attributes (Optional[list[str]], optional): List of Python class attributes to provide as additional
                Python class instantiation arguments during deserialization. If no extra attributes are provided,
                defaults to the values in excluded_attributes.
            class_keys_for_extra_attributes (Optional[list[str]], optional): List of Python class keys for which to
                provide additional Python class instantiation arguments provided in extra_attributes during
                deserialization. If no class keys are provided, any attributes provided in extra_attributes will be
                provided as Python class instantiation arguments to all classes during deserialization. If no class keys
                for extra attributes are provided, defaults to the values in class_keys_for_excluded_attributes.
            kwargs (dict): Key/value pairs to be passed to the PythonObjectJson class.

        """
        # always exclude pyobjson attributes during serialization and include them as extra attributes during
        # deserialization
        pyobjson_attributes = [
            "excluded_attributes",
            "class_keys_for_excluded_attributes",
            "extra_attributes",
            "class_keys_for_extra_attributes",
        ]
        self.excluded_attributes = pyobjson_attributes
        if excluded_attributes:
            # check if all excluded attributes are valid regex
            validate_regex(excluded_attributes)
            self.excluded_attributes.extend(excluded_attributes)
        self.class_keys_for_excluded_attributes = class_keys_for_excluded_attributes or []
        self.extra_attributes = pyobjson_attributes
        if extra_attributes:
            # check if all extra attributes are valid regex
            validate_regex(extra_attributes)
            self.extra_attributes.extend(extra_attributes)
        else:
            self.extra_attributes.extend(set(self.excluded_attributes).difference(pyobjson_attributes))
        self.class_keys_for_extra_attributes = (
            class_keys_for_extra_attributes or self.class_keys_for_excluded_attributes
        )
        vars(self).update(kwargs)

    def __str__(self):
        return self.to_json_str()

    def __repr__(self):
        return (
            f"{derive_custom_object_key(self.__class__, as_lower=False)}"
            f"({','.join([f'{k}={v}' for k, v in vars(self).items() if k in getfullargspec(self.__init__).args])})"
        )

    def __eq__(self, other):
        return type(self) is type(other) and vars(self) == vars(other)

    def _base_subclasses(self) -> Dict[str, Type]:
        """Create a dictionary with lowercase keys derived from custom class names in camelcase mapped to their
        respective custom classes.

        Returns:
            dict[str, Type]: Dictionary with lowercase strings of all subclasses of PythonObjectJson as keys and
            subclasses as values.

        """
        # retrieve all class subclasses (and their nested subclasses) after base class
        return {derive_custom_object_key(cls): cls for cls in get_nested_subclasses(self.__class__.__mro__[-2])}

    def serialize(self) -> Dict[str, Any]:
        """Create a serializable dictionary from the class instance.

        Returns:
            dict[str, Any]: Serializable dictionary representing the class instance.

        """
        return serialize(
            self,
            list(self._base_subclasses().values()),
            self.excluded_attributes,
            self.class_keys_for_excluded_attributes,
        )

    def deserialize(self, serializable_dict: Dict[str, Any]) -> Any:
        """Load data to a class instance from a serializable dictionary.

        Args:
            serializable_dict (dict[str, Any]): Serializable dictionary representing the class instance.

        Returns:
            Any: Class instance deserialized from data dictionary.

        """
        extra_attributes = {}
        for att in self.extra_attributes:
            instance_atts = vars(self)
            # include extra attribute if it is defined in instance onto which data is being deserialized
            if att in instance_atts.keys():
                extra_attributes[att] = vars(self).get(att)
            else:
                for inst_att in instance_atts.keys():
                    # include all attributes defined in instance onto which data is being deserialized that match the
                    # extra attribute regex
                    if search(rf"{att}", inst_att):
                        extra_attributes[inst_att] = vars(self).get(inst_att)

        return deserialize(
            serializable_dict,
            self._base_subclasses(),
            base_class_instance=self,
            extra_attributes=extra_attributes,
            class_keys_for_extra_attributes=self.class_keys_for_extra_attributes,
        )

    def to_json_str(self) -> str:
        """Serialize the class instance to a JSON string.

        Returns:
            str: JSON string derived from the serializable version of the class instance.

        """
        return json.dumps(self.serialize(), ensure_ascii=False, indent=2)

    def from_json_str(self, json_str: str) -> None:
        """Load a class instance deserialized from a JSON string to the current class instance.

        Args:
            json_str (str): JSON string to be deserialized into the class instance.

        Returns:
            None

        """
        self.deserialize(json.loads(json_str))

    def save_to_json_file(self, json_file_path: Path) -> None:
        """Save the class instance to a JSON file.

        Args:
            json_file_path (Path): Target JSON file path to which the class instance will be saved.

        Returns:
            None

        """
        if not json_file_path.exists():
            json_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(json_file_path, "w", encoding="utf-8") as json_file_out:
            # TODO: fix incorrect file input type warning for json.dump from PyCharm bug https://youtrack.jetbrains.com/issue/PY-73050/openfile.txt-r-return-type-should-be-inferred-as-TextIOWrapper-instead-of-TextIO
            # noinspection PyTypeChecker
            json.dump(self.serialize(), json_file_out, ensure_ascii=False, indent=2)

    def load_from_json_file(self, json_file_path: Path) -> None:
        """Load the class instance from a JSON file.

        Args:
            json_file_path (Path): Target JSON file path from which the class instance will be loaded.

        Returns:
            None

        """
        if not json_file_path.exists():
            raise FileNotFoundError(f"File {json_file_path} does not exist. Unable to load saved data.")

        with open(json_file_path, "r", encoding="utf-8") as json_file_in:
            self.deserialize(json.load(json_file_in))


if __name__ == "__main__":
    from logging import INFO
    from pathlib import Path

    from dotenv import load_dotenv

    from pyobjson import get_logger

    logger = get_logger(__file__, INFO)

    root_dir = Path(__file__).parent.parent.parent

    load_dotenv(root_dir / ".env")

    class CustomClassToJsonFile(PythonObjectJson):
        def __init__(self, message: str):
            super().__init__()
            self.message = message

    custom_class_to_json_file = CustomClassToJsonFile("Hello, World!")
    logger.info(f"\n{custom_class_to_json_file}")

    output_dir = root_dir / "tests" / "output"
    if not output_dir.is_dir():
        output_dir.mkdir(parents=True, exist_ok=True)

    custom_class_to_json_file.save_to_json_file(output_dir / "custom_class_to_json_file.json")

    custom_class_to_json_file.__init__("")
    logger.info(f"\n{custom_class_to_json_file}")

    custom_class_to_json_file.load_from_json_file(output_dir / "custom_class_to_json_file.json")
    logger.info(f"\n{custom_class_to_json_file}")
