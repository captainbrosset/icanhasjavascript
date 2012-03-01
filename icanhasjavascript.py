class attrdict(dict):
    """Used to easily mock modules dependencies"""
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

import os
import threading
from datetime import datetime
try:
    import sublime
    import sublime_plugin
except:
    # Mocking out dependencies in case of unit testing
    # FIXME: How to make this more elegant ???
    sublime = {}

    class EventListener:
        pass

    sublime_plugin = attrdict(EventListener=EventListener)
from jsparser import JSFileVisitorHandler
from visitor import EntitiesVisitor


class ModelFile(object):
    def __init__(self, file_name, entities):
        self.file_name = file_name
        self.entities = entities


class Model(object):
    def __init__(self):
        self.files = []

    def add_file(self, file_name, entities):
        self.files.append(ModelFile(file_name, entities))


class Suggestion(object):
    def __init__(self, entity, file_name):
        self.entity = entity
        self.file_name = file_name

    def get_display_value(self):
        return str(self)

    def get_snippet_value(self):
        name = self.entity.name
        if hasattr(self.entity, "arguments"):
            name += "(" + ", ".join(self.entity.arguments) + ")"
        return name

    def get_file_name_only(self):
        parts = self.file_name.split(os.sep)
        return parts[len(parts) - 1]

    def __repr__(self):
        return self.get_snippet_value() + " (" + self.get_file_name_only() + ")"


def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print "[ICANHASJAVASCRIPT][" + timestamp + "] " + message


def get_all_js_files_in_dir(source_dir):
    fileList = []
    for root, subFolders, files in os.walk(source_dir):
        for file in files:
            if file[-3:] == ".js":
                fileList.append(os.path.join(root, file))
    return fileList


def get_file_content(file_name):
    return open(file_name).read()


def get_file_content_entities(file_name, file_content):
    log("Parsing file " + file_name + " ...")
    visitor_handler = JSFileVisitorHandler(file_content)
    visitor = EntitiesVisitor()
    visitor_handler.add_visitor(visitor)
    try:
        visitor_handler.visit()
        log("Done parsing")
        return visitor.functions + visitor.variables
    except:
        return []


def get_suggestions(entry, model):
    suggestions = []
    for model_file in model.files:
        for entity in model_file.entities:
            if entity.name[0:len(entry)] == entry:
                suggestions.append(Suggestion(entity, model_file.file_name))
    return suggestions


def get_model(source_directories, callback):
    model = Model()
    log("Scanning " + str(len(source_directories)) + " project directories ...")
    total_file_number = 0
    start_time = datetime.now()
    for source_dir in source_directories:
        files = get_all_js_files_in_dir(source_dir)
        log("Scanning " + str(len(files)) + " javascript files in " + source_dir + "...")
        total_file_number += len(files)
        for file in files:
            content = get_file_content(file)
            entities = get_file_content_entities(file, content)
            model.add_file(file, entities)

    delta = datetime.now() - start_time
    time_diff = divmod(delta.days * 86400 + delta.seconds, 60)
    time_per_file = float(time_diff[0] * 60 + time_diff[1]) / float(total_file_number)
    log("Done parsing all " + str(total_file_number) + " files in " + str(time_diff[0]) + " minutes, " + str(time_diff[1]) + " seconds (" + str(time_per_file) + " seconds per file)")

    callback(model)


class ICanHasJavaScript(sublime_plugin.EventListener):
    def __init__(self):
        self.model = None
        self._is_constructing_model = False

    def construct_model(self, view):
        if not self._is_constructing_model:
            log("Building the model now ...")
            self._is_constructing_model = True
            model_construction_thread = threading.Thread(None, get_model, "model_construction_thread", (view.window().folders(), self.on_model_constructed))
            model_construction_thread.start()

    def on_model_constructed(self, model):
        log("Done building model")
        self.model = model
        self._is_constructing_model = False

    def on_query_completions(self, view, prefix, locations):
        is_view_matching = view.match_selector(locations[0], "source.js")
        if not is_view_matching or not self.model:
            return []

        # Only create the model the first time the auto-complete shows up
        #if not self.model:
        #    self.construct_model(view)

        suggestions = get_suggestions(prefix, self.model)
        return [(suggestion.get_display_value(), suggestion.get_snippet_value()) for suggestion in suggestions]

    def on_post_save(self, view):
        # just recompute the whole model at every file save for now
        self.construct_model(view)


if __name__ == "__main__":
    content = """
    function Test() {
        var a = 1;
    }
    var b = 2;
    function TestAgain() {
        var c = 3;
        var d = function() {

        }
    }
    """

    assert len(get_file_content_entities("test.js", content)) == 3

    files = get_all_js_files_in_dir("testdir")
    assert len(files) == 24
    assert files[0] == "testdir" + os.sep + "apple.js"
    assert files[23] == "testdir" + os.sep + "visibility.js"

    assert len(get_file_content(files[0])) == 182

    def assert_model_retrieved(model):
        print "[ICANHASJAVASCRIPT] Done"
        assert len(model.files) == 24
        assert len(model.files[3].entities) == 3
        assert model.files[3].entities[0].name == "MyClass"

        assert len(get_suggestions("tes", model)) == 3
        assert get_suggestions("tes", model)[1].file_name == "testdir" + os.sep + "syntaxerror.js"
        assert get_suggestions("tes", model)[2].entity.name == "test"
        assert get_suggestions("test", model)[2].get_display_value() == "test() (visibility.js)"
        assert get_suggestions("test", model)[1].get_snippet_value() == "test(a, b)"

    get_model(["..\\..\\jdevcc\\at_v1.1_int\\at1104_core\\at\\src\\main\\static"], assert_model_retrieved)
    #get_model(["testdir"], assert_model_retrieved)

    print "ALL TESTS OK"
