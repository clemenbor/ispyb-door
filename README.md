# pydesydoor
A python API to DESY DOOR user portal

The project takes environment variables from a .env file. The variables are loaded into the scripts by using https://pypi.org/project/python-dotenv/

An example .env file would be like this:
```bash
# ISPyB DOOR API Development settings
DOOR_REST_ROOT=https://example.desy.de/api/v1.0
DOOR_REST_TOKEN=44b125547d126a6cc6343aa256754334d0007788c0c51ec3d8a40c297024b7
DOOR_SERVICE_ACCOUNT=xxyyzz
DOOR_SERVICE_PASSWORD=xxyyzz
DOOR_TESTUSER_USERNAME=xxyyzz
DOOR_TESTUSER_PASSWORD=xxyyzz
```


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pydesydoor.

```bash
pip install git+https://github.com/clemenbor/pydesydoor.git#egg=pydesydoor
```

## Examples
To play with the client check the examples folder.
