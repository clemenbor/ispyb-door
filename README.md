# ispyb-door
A python API to DOOR

The project takes environment variables from a .env file. The variables are loaded into the scripts by using https://pypi.org/project/python-dotenv/

An example .env file would be like this:
```
# ISPyB DOOR API Development settings
DOOR_REST_ROOT=https://example.desy.de/
DOOR_REST_TOKEN=44b125547d126a6cc6343aa256754334d0007788c0c51ec3d8a40c297024b7
```

To play with the script just adapt accordingly a username/password and then execute:

```
python desydoorauthclient.py
```
