import os
import datetime
import inspect


class MsgTypes(object):
    ERROR = "ERROR"
    INFO = "INFO"
    WARNING = "WARNING"


def get_app_dir():
    """
    Return the absolute path to the app
    """
    path = os.path.dirname(__file__)
    if ".zip" in path:
        path, zip_file = os.path.split(path)
    return path


def string_contains(string, *substrings):
    """
    Check if string contains any of the specified substrings

    Keyword arguments:
    string -- string to check
    substrings -- strings to find

    """
    for substring in substrings:
        if substring in string:
            return True
    return False


def get_time():
    return str(datetime.datetime.now()).split(" ")[1].split(".")[0]


def log(message, message_type):
    class_name = inspect.getouterframes(inspect.currentframe(), 2)[2][1].rsplit("/", 1)[1].split(".")[0]
    print(get_time()+" ["+message_type+"]["+class_name+"] " + str(message))