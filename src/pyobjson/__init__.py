"""Python Object JSON Tool pyobjson.__init__.

Attributes:
    __author__ (str): Python package template author.
    __email__ (str): Python package template author email.

"""

__author__ = "Wren J. Rudolph for Wrencode, LLC"
__email__ = "dev@wrencode.com"


from logging import WARNING, Formatter, Logger, StreamHandler, getLogger

from pyobjson.base import PythonObjectJson  # noqa: F401
from pyobjson.constants import DELIMITER, UNSERIALIZABLE  # noqa: F401
from pyobjson.data import deserialize, extract_typed_key_value_pairs, serialize, unpack_custom_class_vars  # noqa: F401
from pyobjson.utils import derive_custom_callable_value, derive_custom_object_key, get_nested_subclasses  # noqa: F401


def get_logger(name: str, level: int = WARNING) -> Logger:
    """Get customized Logger.

    Args:
        name (str): The module name for the logger.
        level (int): The log level for the logger. Default level set to WARNING.

    Returns:
        Logger: A Python Logger object with custom configuration and formatting.

    """
    logger = getLogger(name)
    if len(logger.handlers) > 0:
        logger.handlers = []
    if level:
        logger.setLevel(level)

    sh = StreamHandler()
    if level:
        sh.setLevel(level)

    formatter = Formatter(
        fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(filename)s - %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    sh.setFormatter(formatter)

    logger.addHandler(sh)

    return logger
