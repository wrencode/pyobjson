# pyobjson - Python Object JSON Tool

Utility library for serializing/deserializing custom Python objects to/from JSON.

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/wrencode/pyobjson?color=yellowgreen&label=latest%20release&sort=semver)](https://github.com/wrencode/pyobjson/releases/latest)
[![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/wrencode/pyobjson?color=yellowgreen&label=latest%20version&sort=semver)](https://github.com/wrencode/pyobjson/tags)
[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/wrencode/pyobjson/python-package.yml?color=brightgreen&label=build)](https://github.com/wrencode/pyobjson/actions/workflows/python-package.yml)

[![PyPI](https://img.shields.io/pypi/v/pyobjson.svg?style=flat)](https://pypi.python.org/pypi/pyobjson)
[![PyPI](https://img.shields.io/pypi/dm/pyobjson.svg?style=flat)](https://pypi.python.org/pypi/pyobjson)
[![PyPI](https://img.shields.io/pypi/pyversions/pyobjson.svg?style=flat)](https://pypi.python.org/pypi/pyobjson)
[![PyPI](https://img.shields.io/pypi/l/pyobjson.svg?style=flat)](https://pypi.python.org/pypi/pyobjson)

---

<sub>***Do you like the Python Object JSON Tool? Star the repository on GitHub and please consider helping support its
ongoing development:***</sub>

[<img src="https://raw.githubusercontent.com/wrencode/pyobjson/refs/heads/main/docs/wrencode-donation-venmo-qr-code.jpg" width="300"/>](https://venmo.com/wrencode?txn=pay)

<!-- https://venmo.com/<USER_NAME_1>,<USER_NAME_2>...?txn=<charge|pay>&note=<NOTE>&amount=<AMOUNT> -->

---

<div class="hide-next-element"></div>

**[READ THE DOCS HERE!](https://pyobjson.wrencode.dev)**
<br/>
<sup>Detailed documentation can be found at [https://pyobjson.wrencode.dev](https://pyobjson.wrencode.dev).</sup>

<div class="hide-next-element"></div>

&nbsp;

<div class="hide-next-element"></div>

### Table of Contents

<div class="hide-next-element"></div>

* [About](#about)
    * [Installation](#installation)
    * [Dependencies](#dependencies)
    * [Toolchain](#toolchain)
* [Usage](#usage)
    * [JSON Example](#json-example)
        * [JSON Example Output](#json-example-output)
    * [Saving and Loading](#saving-and-loading)
        * [JSON Files](#json-files)
            * [JSON File Example](#json-file-example)
            * [JSON File Output](#json-file-output)
        * [MongoDB](#mongodb)
            * [MongoDB Example](#mongodb-example)
            * [MongoDB Output](#mongodb-output)
* [Custom Subclasses](#custom-subclasses)
    * [Serialization](#serialization)
    * [Deserialization](#deserialization)

<div class="hide-next-element"></div>

---

<a name="about"></a>

### About

The Python Object JSON Tool is a utility library for serializing/deserializing custom Python objects to/from JSON by
using `pyobjson` classes as superclasses/parent classes to your custom Python classes.

<a name="installation"></a>

#### Installation

You can install with `pip` by running:

```shell
pip install pyobjson
```

***Note***: If you wish to use `pyobjson` to serialize/deserialize custom Python objects to/from MongoDB, then you have
to install with the optional dependencies:

```shell
pip install pyobjson[mongo]
```

<a name="dependencies"></a>

#### Dependencies

The base Python Object JSON Tool does not have any third-party dependencies to run the code. It has several development
dependencies, which can be seen in the package `pyproject.toml`.

If you wish to use `pyobjson` to serialize/deserialize custom Python objects to/from MongoDB, then there is an
additional dependency on the [PyMongo](https://pymongo.readthedocs.io/en/stable/) package.

<a name="toolchain"></a>

#### Toolchain

The below tools and resources are used as part of pyobjson:

* [uv](https://github.com/astral-sh/uv) - package management
* [ruff](https://github.com/astral-sh/ruff) - code linting
* [bandit](https://bandit.readthedocs.io/en/latest/) - code security
* [make](https://www.gnu.org/software/make/manual/make.html) - Makefile build automation
* [MkDocs](https://www.mkdocs.org) - package documentation
* [python-dotenv](https://github.com/theskumar/python-dotenv) - programmatic access to environment variables defined in
  a `.env` file
* [pytest](https://docs.pytest.org/en/stable/) - code testing framework
* [GitHub Actions](https://docs.github.com/en/actions) - CI/CD
* [act](https://github.com/nektos/act) - GitHub Actions testing

---

<a name="usage"></a>

### Usage

The `pyobjson` package is designed to be used as a base class/parent class/superclass to your own custom Python classes
in order to provide built-in, convenient serialization/deserialization functionality. Child classes/subclasses of
`pyobjson.base.PythonObjectJson` will automatically have the following methods:

* `pyobjson.base.PythonObjectJson.serialize()`: Create a serializable dictionary from the class instance.
* `pyobjson.base.PythonObjectJson.to_json_str()`: Serialize the class instance to a JSON string.
* `pyobjson.base.PythonObjectJson.from_json_str(json_str)`: Load the class instance from a `pyobjson`-formatted JSON
  string.
* `pyobjson.base.PythonObjectJson.save_to_json_file(json_file_path)`: Save the class instance to a JSON file.
* `pyobjson.base.PythonObjectJson.load_from_json_file(json_file_path)`: Load the class instance from a `pyobjson`
  -formatted JSON file.

Please reference the **[documentation at https://pyobjson.wrencode.dev](https://pyobjson.wrencode.dev)** for more
detailed usage.

<a name="json-example"></a>

#### JSON Example

```python
from pyobjson.base import PythonObjectJson


class MyOtherClass(PythonObjectJson):

    def __init__(self):
        super().__init__()
        self.message = "Hello, World!"


class MyClass(PythonObjectJson):
    def __init__(self):
        super().__init__()
        self.my_other_classes = [MyOtherClass()]


my_class = MyClass()

print(my_class.to_json_str())
```

<a name="json-example-output"></a>

##### JSON Example Output

```json
{
  "__main__.myclass": {
    "collection::::list::::my_other_classes": [
      {
        "__main__.myotherclass": {
          "message": "Hello, World!"
        }
      }
    ]
  }
}
```

The above example shows how `pyobjson` can be used to serialize arbitrary custom Python classes into JSON. Additionally,
the above [JSON example output](#json-example-output) JSON can be used to recreate an equivalent class instance by
loading the JSON into a custom Python class instance.

<a name="saving-and-loading"></a>

#### Saving and Loading

The `pyobjson.base.PythonObjectJson` parent class *also* provides built-in methods to save/load arbitrary custom Python
classes to/from JSON in several ways.

<a name="json-files"></a>

##### JSON Files

* [JSON](https://www.json.org/json-en.html) files *(using **only** Python built-in libraries)*: Use the
  `PythonObjectJson.save_to_json_file(json_file_path)` and `PythonObjectJson.load_from_json_file(json_file_path)`
  methods to save/load your custom Python subclasses to JSON files.

<a name="json-file-example"></a>

###### JSON File Example

```python
from pathlib import Path

from dotenv import load_dotenv

from pyobjson.base import PythonObjectJson

root_dir = Path(__file__).parent

load_dotenv(root_dir / ".env")


class CustomClassToJsonFile(PythonObjectJson):
    def __init__(self, message: str):
        super().__init__()
        self.message = message


custom_class_to_json_file = CustomClassToJsonFile("Hello, World!")

output_dir = root_dir / "output"
if not output_dir.is_dir():
    output_dir.mkdir(parents=True, exist_ok=True)

custom_class_to_json_file.save_to_json_file(output_dir / "custom_class_to_json_file.json")

custom_class_to_json_file.load_from_json_file(output_dir / "custom_class_to_json_file.json")
```

<a name="json-file-output"></a>

###### JSON File Output

```json
{
  "__main__.customclasstojsonfile": {
    "message": "Hello, World!"
  }
}
```

<a name="mongodb"></a>

##### MongoDB

* [MongoDB](https://www.mongodb.com) *(using [`pymongo`](https://pymongo.readthedocs.io/en/stable/))*: The `pyobjson`
  library includes a class called `pyobjson.dao.PythonObjectJsonToMongo`, which can be used as a superclass for any
  custom class you wish to be able to easily serialized/deserialize to/from MongoDB. Use the
  `PythonObjectJsonToMongo.save_to_mongo(mongo_collection)` and
  `PythonObjectJsonToMongo.load_from_mongo(mongo_collection, document_id)` methods to save/load your custom Python
  subclasses to MongoDB.

<a name="mongodb-example"></a>

###### MongoDB Example

```python
import os
from pathlib import Path

from dotenv import load_dotenv

from pyobjson.dao.mongo.base import PythonObjectJsonToMongo

load_dotenv(Path(__file__).parent / ".env")


class CustomClassToMongo(PythonObjectJsonToMongo):
    def __init__(self, mongo_host: str, mongo_port: int, mongo_database: str, mongo_user: str, mongo_password: str):
        super().__init__(mongo_host, mongo_port, mongo_database, mongo_user, mongo_password)
        self.message = "Hello, World!"


custom_class_to_mongo = CustomClassToMongo(
    mongo_host=os.environ.get("MONGO_HOST"),
    mongo_port=int(os.environ.get("MONGO_PORT")),
    mongo_database=os.environ.get("MONGO_DATABASE"),
    mongo_user=os.environ.get("MONGO_ADMIN_USER"),
    mongo_password=os.environ.get("MONGO_ADMIN_PASS"),
)

saved_mongo_document_id = custom_class_to_mongo.save_to_mongo(os.environ.get("MONGO_COLLECTION"))

custom_class_to_mongo.load_from_mongo(os.environ.get("MONGO_COLLECTION"), saved_mongo_document_id)

```

<a name="mongodb-output"></a>

###### MongoDB Output

`print(custom_class_to_mongo)`:

```json
{
  "__main__.customclasstomongo": {
    "message": "Hello, World!"
  }
}
```

`print(repr(custom_class_to_mongo))`:

```shell
__main__.CustomClassToMongo(mongo_host=localhost,mongo_port=27017,mongo_database=pyobjson,mongo_user=<mongodb_user>,mongo_password=<mongodb_password>)
```

---

<a name="custom-subclasses"></a>

### Custom Subclasses

The `PythonObjectJson` base class in `pyobjson` is designed to be extended using your own custom subclasses. The
built-in `PythonObjectJsonToMongo` class is an example of this functionality, but it can be adapted to work for
additional use cases as well.

<a name="serialization"></a>

#### Serialization

If you have a custom class with attributes that contain data you wish to exclude from the `pyobjson` serialized output (
anything from sensitive data like credentials to objects that are not compatible with `pyobjson`), you can provide a
list of attribute names (or a list of valid regular expressions) to the `excluded_attributes` parameter in the
`PythonObjectJson.__init__(...)`, and `pyobjson` will automatically exclude any attributes that match those provided
during serialization.

If you *only* provide values for `excluded_attributes`, then `pyobjson` will exclude those attributes from *all* custom
classes being serialized within the root custom class. However, you can also provide a list of class identifiers (like
`pyobjson.dao.mongo.base.pythonobjectjsontomongo` to the `class_keys_for_excluded_attributes` parameter in the
`PythonObjectJson.__init__(...)`, as derived using the `pyobjson.utils.derive_custom_object_key` function), in which
case `pyobjson` will *only* exclude the provided `excluded_attributes` from the classes in
`class_keys_for_excluded_attributes`.

<a name="deserialization"></a>

#### Deserialization

Similar to the approach for [custom subclass serialization](#serialization), if you have a custom class with extra
attributes you wish to include during deserialization, you can provide a list of attribute names (or a list of valid
regular expressions) to the `extra_attributes` parameters in the `PythonObjectJson.__init__(...)`, and `pyobjson` will
attempt to re-apply those attributes during deserialization by pulling the values for those extra attributes from the
custom class instance onto which you are deserializing data.

If you *only* provide values for `extra_attributes`, then `pyobjson` will attempt to add those attributes to *all*
custom classes being deserialized onto the root custom class. However, you can also provide a list of class
identifiers (like `pyobjson.dao.mongo.base.pythonobjectjsontomongo` to the `class_keys_for_extra_attributes` parameter
in the `PythonObjectJson.__init__(...)`, as derived using the `pyobjson.utils.derive_custom_object_key` function), in
which case `pyobjson` will *only* attempt to add the provided `extra_attributes` to the classes in
`class_keys_for_extra_attributes`.
