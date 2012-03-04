class attrdict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

import os
import subprocess
from model import model
from logger import log
try:
    import sublime
    import sublime_plugin
except:
    sublime = {}
    class EventListener: pass
    sublime_plugin = attrdict(EventListener=EventListener)


class Suggestion(object):
    def __init__(self, entity):
        self.entity = entity
        self.file_name = entity.file_name

    def get_display_value(self):
        return str(self)

    def get_snippet_value(self):
        name = self.entity.name
        if hasattr(self.entity, "arguments"):
            arguments = self.entity.arguments.replace(",", ", ")
            name += "(" + arguments + ")"
        return name

    def get_file_name_only(self):
        parts = self.file_name.split(os.sep)
        return parts[len(parts) - 1]

    def __repr__(self):
        return self.get_snippet_value() + " (" + self.get_file_name_only() + ")"


class ICanHasJavaScript(sublime_plugin.EventListener):
    def __init__(self):
        self.indexer = SubProcessIndexer()
        self.indexed = False
        self.model = None

    def index_project(self, view):
        if not self.indexed:
            if hasattr(view.window(), "folders"):
                directories = view.window().folders()
                if len(directories) > 0:
                    log("Indexing javascript files in " + str(len(directories)) + " directories")
                    self.indexer.index_directories(directories)
                    self.indexed = True

    def on_activated(self, view):
        self.index_project(view)

    def on_load(self, view):
        self.index_project(view)

    def on_post_save(self, view):
        self.model = None
        self.index_project(view)
        file_name = view.file_name()
        if file_name[-3:] == ".js":
            log("Re-indexing javascript file " + file_name)
            self.indexer.index_file(file_name)

    def get_javascript_files_in_directory(self, source_dir):
        fileList = []

        for root, subFolders, files in os.walk(source_dir):
            for file in files:
                if file[-3:] == ".js":
                    fileList.append(os.path.join(root, file))

        return fileList

    def on_query_completions(self, view, prefix, locations):
        is_view_matching = view.match_selector(locations[0], "source.js")
        if not is_view_matching:
            return []

        suggestions = self.get_suggestions(prefix, view.window().folders())
        return [(suggestion.get_display_value(), suggestion.get_snippet_value()) for suggestion in suggestions]

    def update_local_model(self, directories):
        log("Updating the local model from the DB")
        files = []
        for directory in directories:
            files += self.get_javascript_files_in_directory(directory)
        self.model = model.get_files_model(files)

    def get_suggestions(self, entry, directories):
        # On contextual menu open, only get the model if it was not here before
        # This happens only the first time it's used, and after a file is saved
        if not self.model:
            self.update_local_model(directories)

        suggestions = []
        for entity in self.model:
            if entity.name[0:len(entry)] == entry:
                suggestions.append(Suggestion(entity))
        return suggestions


class SubProcessIndexer(object):
    COMMAND_PREFIX = 'python "' + os.sep.join([sublime.packages_path(), "icanhasjavascript", "indexer", "indexerprocess.py"]) + '" -r "' + os.sep.join([sublime.packages_path(), "icanhasjavascript"]) + '"'

    def index_directories(self, directories):
        for directory in directories:
            command = SubProcessIndexer.COMMAND_PREFIX + ' -d "' + directory + '"'
            subprocess.Popen(command, shell=True)

    def index_file(self, file):
        command = SubProcessIndexer.COMMAND_PREFIX + ' -f "' + file + '"'
        subprocess.Popen(command, shell=True)
