# Current implementation is sqlite based
import sqlite
model_storage_impl = sqlite.Storage()


class Function(object):
    def __init__(self, file_name, name, arguments):
        self.file_name = file_name
        self.name = name
        self.arguments = arguments


class Variable(object):
    def __init__(self, file_name, name):
        self.file_name = file_name
        self.name = name


def get_files_model(files):
    """Get the model for a given list of files
    Returns a list of Function and Variable objects"""
    return model_storage_impl.get_files_model(files)


def update_file_model(file, entities):
    """Update the model of a given file"""
    model_storage_impl.update_file_model(file, entities)


def flush_model():
    """Deletes the entire model"""
    model_storage_impl.flush_model()
