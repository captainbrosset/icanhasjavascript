import sys
from logger import log
from jsparser import JSFileVisitorHandler
from visitor import EntitiesVisitor


def index_file(file_name, file_content=None):
    """Parse the file content and visit the AST to extract the model entities
    Do this in a separate python process for performance"""
    #subprocess.call(["ls", "-l"])
    log("Indexing " + file_name + " ...")

    if not file_content:
        file_content = open(file_name).read()

    visitor_handler = JSFileVisitorHandler(file_content)
    visitor = EntitiesVisitor()
    visitor_handler.add_visitor(visitor)
    try:
        visitor_handler.visit()
        log("Done indexing " + file_name)
        return visitor.functions + visitor.variables
    except:
        return []


def run_tests():
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

    print index_file("test.js", content)
    assert len(index_file("test.js", content)) == 3


if __name__ == "__main__":
    if len(sys.argv) == 2:
        file_name = sys.argv[1]
        index_file(file_name)
    else:
        run_tests()
